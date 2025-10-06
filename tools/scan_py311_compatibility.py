#!/usr/bin/env python3
"""Report dependencies that block Python 3.11+ builds.

The script imports the package metadata defined in ``clpipe.config.package``
and compares the pinned dependency versions with a curated list of the
minimum versions known to provide Python 3.11 wheels (or otherwise document
Python 3.11 compatibility).

Because the repository purposely pins many dependencies, a stale pin can be
an immediate source of ``pip`` resolution failures on Python 3.11+.  Running
this script surfaces those problematic pins so that they can be reviewed and
updated alongside a broader dependency refresh.
"""
from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

try:
    from packaging.version import Version
except ModuleNotFoundError as exc:  # pragma: no cover - helpful error
    raise SystemExit(
        "The 'packaging' library is required to run this scan. Install it with "
        "'python -m pip install packaging' and retry."
    ) from exc

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_CONFIG = ROOT / "clpipe" / "config" / "package.py"


@dataclass(frozen=True)
class CompatibilityRule:
    """Defines the minimum version that supports Python 3.11."""

    minimum_version: str
    rationale: str


# The table below is sourced from the respective projects' release notes and
# build matrices.  Each entry reflects the first release series that shipped
# official Python 3.11 wheels on PyPI.
PY311_COMPATIBILITY_RULES: Dict[str, CompatibilityRule] = {
    "numpy": CompatibilityRule(
        minimum_version="1.23.0",
        rationale=(
            "NumPy 1.23 was the first release line to publish Python 3.11 "
            "binary wheels; earlier releases only support up to Python 3.10."
        ),
    ),
    "pandas": CompatibilityRule(
        minimum_version="1.5.0",
        rationale=(
            "Pandas formally added Python 3.11 support in the 1.5 series; "
            "1.3.x targets Python 3.7–3.10."
        ),
    ),
    "matplotlib": CompatibilityRule(
        minimum_version="3.6.0",
        rationale=(
            "Matplotlib 3.6 introduced Python 3.11 compatibility; "
            "3.5.x releases are capped at Python 3.10."
        ),
    ),
    "scipy": CompatibilityRule(
        minimum_version="1.9.0",
        rationale=(
            "SciPy 1.9 began shipping Python 3.11 wheels; "
            "1.2.2 predates even Python 3.9 support."
        ),
    ),
}


def load_install_requires() -> Iterable[str]:
    """Load the ``INSTALL_REQUIRES`` sequence from the package config."""

    spec = importlib.util.spec_from_file_location("clpipe_package_config", PACKAGE_CONFIG)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load clpipe.config.package module")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        requirements = getattr(module, "INSTALL_REQUIRES")
    except AttributeError as exc:  # pragma: no cover - defensive coding
        raise RuntimeError("INSTALL_REQUIRES is not defined in package config") from exc

    if not isinstance(requirements, Iterable):
        raise TypeError("INSTALL_REQUIRES should be an iterable of requirement strings")

    if (
        len(requirements) == 1
        and isinstance(requirements[0], Iterable)
        and not isinstance(requirements[0], (str, bytes))
    ):
        # ``INSTALL_REQUIRES`` is stored as a single nested list in the
        # repository (because of a trailing comma in the assignment).  This
        # branch smooths that quirk so the rest of the script can treat the
        # requirements as a flat sequence of strings.
        nested = requirements[0]
        if all(isinstance(item, str) for item in nested):
            return list(nested)

    return list(requirements)


def parse_pinned_requirement(requirement: str) -> Optional[Tuple[str, str]]:
    """Return (name, version) when the requirement is pinned with ``==``."""

    if "==" not in requirement:
        return None

    name, version = requirement.split("==", 1)
    return name.strip(), version.strip()


def main(argv: List[str]) -> int:
    install_requires = list(load_install_requires())
    issues: List[str] = []

    for requirement in install_requires:
        parsed = parse_pinned_requirement(requirement)
        if not parsed:
            continue

        name, pinned_version = parsed
        normalized_name = name.lower().replace("_", "-")
        rule = PY311_COMPATIBILITY_RULES.get(normalized_name)
        if rule is None:
            continue

        if Version(pinned_version) < Version(rule.minimum_version):
            issues.append(
                f"{name}=={pinned_version} pins below the Python 3.11 compatible "
                f"minimum ({rule.minimum_version}).\n    {rule.rationale}"
            )

    if issues:
        print("Python 3.11 compatibility issues detected:\n")
        for entry in issues:
            print(f"- {entry}\n")
        return 1

    print("No Python 3.11 compatibility issues detected in pinned dependencies.")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main(sys.argv[1:]))
