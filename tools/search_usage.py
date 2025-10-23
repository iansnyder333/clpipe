"""Utilities to locate string usage throughout the repository.

The module exposes :func:`search_usage_in_repo`, which walks the repository
root and records every line where the provided search term occurs.  It is a
lightweight alternative to shelling out to tools such as ``grep`` when running
inside Python-only environments.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List, Sequence

__all__ = ["UsageMatch", "search_usage_in_repo", "main"]


DEFAULT_IGNORE_DIRS: Sequence[str] = (
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".eggs",
    "build",
    "dist",
)


@dataclass(frozen=True)
class UsageMatch:
    """Representation of a single search result."""

    path: Path
    line_number: int
    line_text: str


def _iter_repository_files(root: Path, ignore_dirs: Sequence[str]) -> Iterator[Path]:
    """Yield all text-like files under *root* while skipping *ignore_dirs*.

    The function walks the directory tree with :func:`os.walk` and prunes
    directories that typically contain generated or binary artifacts (``.git``,
    ``build`` and similar).  Binary files are not filtered explicitly; instead,
    we open files in text mode with ``errors="ignore"`` so that undecodable
    bytes are silently skipped.
    """

    ignore_set = {name for name in ignore_dirs}

    for current_dir, dirnames, filenames in os.walk(root):
        current_path = Path(current_dir)

        # Remove ignored directories in-place so ``os.walk`` does not descend
        # into them.
        dirnames[:] = [name for name in dirnames if name not in ignore_set]

        for filename in filenames:
            yield current_path / filename


def search_usage_in_repo(
    search_term: str,
    *,
    root: Path | None = None,
    case_sensitive: bool = True,
    ignore_dirs: Sequence[str] = DEFAULT_IGNORE_DIRS,
) -> List[UsageMatch]:
    """Return matches for *search_term* within *root* (defaults to repo root).

    Args:
        search_term: The substring to look for.
        root: Optional repository root.  When ``None`` the project root is
            inferred by taking the directory one level above this file
            (``tools`` → project root).
        case_sensitive: When ``False`` the search is performed in a
            case-insensitive manner.
        ignore_dirs: Additional directory names to skip while walking.

    Returns:
        A list of :class:`UsageMatch` objects ordered by file path and line
        number.
    """

    if not search_term:
        raise ValueError("search_term must be a non-empty string")

    if root is None:
        root = Path(__file__).resolve().parents[1]

    search_term_to_use = search_term if case_sensitive else search_term.lower()

    matches: List[UsageMatch] = []
    for file_path in _iter_repository_files(root, ignore_dirs):
        try:
            with file_path.open("r", encoding="utf-8", errors="ignore") as f:
                for line_number, line in enumerate(f, start=1):
                    haystack = line if case_sensitive else line.lower()
                    if search_term_to_use in haystack:
                        matches.append(
                            UsageMatch(
                                path=file_path.relative_to(root),
                                line_number=line_number,
                                line_text=line.rstrip("\n"),
                            )
                        )
        except OSError:
            # Skip unreadable files silently; they are most likely FIFOs or
            # other special files that cannot be opened as text.
            continue

    matches.sort(key=lambda match: (match.path.as_posix(), match.line_number))
    return matches


def _format_match(match: UsageMatch) -> str:
    return f"{match.path}:{match.line_number}: {match.line_text}".rstrip()


def main(args: Sequence[str] | None = None) -> int:
    """Entry point used when executing the module as a script."""

    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("search_term", help="Substring to search for")
    parser.add_argument(
        "--ignore-dir",
        action="append",
        default=[],
        dest="ignore_dirs",
        help="Additional directory name to ignore (can be provided multiple times)",
    )
    parser.add_argument(
        "--case-insensitive",
        action="store_false",
        dest="case_sensitive",
        help="Perform a case-insensitive search",
    )

    namespace = parser.parse_args(args=args)

    ignore_dirs = tuple(DEFAULT_IGNORE_DIRS) + tuple(namespace.ignore_dirs)
    matches = search_usage_in_repo(
        namespace.search_term,
        case_sensitive=namespace.case_sensitive,
        ignore_dirs=ignore_dirs,
    )

    for match in matches:
        print(_format_match(match))

    return 0 if matches else 1


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
