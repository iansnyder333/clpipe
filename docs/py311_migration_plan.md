# clpipe Python 3.11 Migration Plan

## 1. What `pip3 install --user --upgrade git+https://github.com/cohenlabUNC/clpipe.git` Does

### High-Level Behavior
- `pip` downloads the `clpipe` source from GitHub, builds a wheel in an isolated build environment, installs the declared runtime dependencies, and then installs the built wheel into the invoking Python environment (the `--user` flag targets the user site-packages directory).
- Because the repository currently exposes only a classic `setup.py`, pip follows its legacy setuptools build path rather than the fully modern PEP 517 backend, although the build still happens in isolation.
- The `clpipe` command that appears on `$PATH` after installation is registered through the package's `console_scripts` entry point defined in the project metadata.
- The published installation instructions target Python 3.7 and recommend the Git-backed pip invocation above for manual installs on UNC-CH systems, reinforcing that this flow is the canonical distribution mechanism today.【F:README.md†L1-L30】【F:docs/install.rst†L10-L37】

### Step-by-Step Pipeline for a VCS Installation
1. **Clone the repository:** pip parses the Git URL (honoring optional branch, tag, or commit fragments) and clones it into a temporary directory before any build steps run.
2. **Determine the build backend:** pip inspects the source tree. Finding only `setup.py`, it selects the legacy setuptools builder instead of the modern PEP 517 interface (`pyproject.toml`).
3. **Build in isolation:** pip creates an isolated build environment, installs build requirements, and invokes setuptools to build a wheel from the cloned source.
4. **Install artifacts:** pip installs the newly built wheel into the target environment alongside all dependencies declared in `install_requires`, then registers the `console_scripts` entry points so that `clpipe` is invokable from the command line.

## 2. Roadmap for Migrating to Python 3.11 and Local/Fork-Based Installs

### Phase A — Establish the Baseline
- Clone your fork and create a working branch (for example, `py311-migration`).
- Reproduce the current Python 3.7 environment documented in the installation guide and capture CLI smoke tests (e.g., `clpipe --help`, representative subcommands) to anchor expected behavior.【F:docs/install.rst†L10-L37】
- Freeze the dependency graph from the existing `requirements.txt` with tooling such as `pipdeptree` for later comparisons.【F:requirements.txt†L1-L68】

### Phase B — Modernize Packaging
- Introduce a `pyproject.toml` that declares `setuptools` as the build backend while temporarily retaining `setup.py` for compatibility during the transition.【F:setup.py†L1-L72】
- Move project metadata (name, version, entry points, dependencies) into declarative configuration (`pyproject.toml` and optionally `setup.cfg`) and raise `Requires-Python` to cover Python 3.9–3.11.
- Validate editable installs via `pip install -e .` under Python 3.11 once the modern build configuration is in place.
- Establish a `requirements/` directory and adopt `pip-tools` (or similar) to derive compiled constraint files for reproducible environments.

### Phase C — Audit and Upgrade Dependencies
- Inventory first-party imports throughout the codebase to identify active dependencies and drop unreferenced packages.
- Select Python 3.11–compatible versions of core scientific libraries (`numpy`, `scipy`, `pandas`, `nibabel`, etc.) that provide prebuilt wheels for supported platforms.
- Replace or upgrade any legacy packages that fail to provide Python 3.11 wheels (e.g., swap deprecated CLI parsers for `click` if necessary—`clpipe` already aggregates its CLI into a single entry point).【F:docs/install.rst†L10-L37】
- Keep broad version lower bounds in packaging metadata while pinning exact versions only in environment-specific constraint files.
- Validate the dependency graph under Python 3.11 to ensure no Python 3.7–only artifacts remain.

### Phase D — Update Code for Python 3.11
- Replace uses of deprecated modules such as `distutils` or `pkg_resources` with modern alternatives (`importlib.metadata`, `pathlib`, and `setuptools`).
- Adopt Python 3.11 language features where appropriate (native generics, `typing.Self`, improved exception grouping) and remove Python 3.7 backports.
- Review subprocess interactions that orchestrate external tools (fMRIPrep, BIDS Validator, Singularity) to confirm shell and environment handling remains stable across Python versions.【F:docs/install.rst†L39-L86】
- Improve error handling and logging to leverage modern exception chaining and structured logging as needed.

### Phase E — Testing and Continuous Integration
- Expand automated coverage with CLI smoke tests, configuration parsers, and representative pipeline segments to guard against regressions.
- Configure CI to run on Python 3.9, 3.10, and 3.11 across Linux (and macOS if possible).
- Add documentation build checks (Sphinx/Read the Docs) to ensure the doc pipeline remains functional under Python 3.11.【F:docs/install.rst†L10-L86】

### Phase F — Packaging Polish
- Audit `MANIFEST.in` and packaging data directives so that templates, configuration files, and other runtime assets are shipped reliably.【F:MANIFEST.in†L1-L13】
- Switch runtime resource access to `importlib.resources` (or `importlib.resources.files` in Python 3.11) to avoid deprecated resource loaders.
- Introduce version automation (for example, `setuptools-scm`) to derive releases from Git tags and eliminate manual version bumps.

### Phase G — Transition to Fork/Local Installations
- **Editable development:** `python3.11 -m venv .venv && source .venv/bin/activate`, followed by `pip install -e . -c requirements/base.txt` from the fork.
- **Branch or tag installation:** `pip install --upgrade git+https://github.com/<your-org>/clpipe.git@py311-migration` once the migration branch is ready.
- **Wheel distribution:** Build wheels with `python -m build` and install via `pip install dist/clpipe-*.whl` to keep production systems off GitHub while retaining reproducibility.

### Phase H — Documentation Updates
- Revise the installation documentation to advertise the supported Python versions (>=3.9, tested on 3.11) and include instructions for editable/local installs alongside the current Git-based command.【F:docs/install.rst†L10-L37】
- Highlight new dependency floors, testing expectations, and upgrade steps so downstream users understand the migration path.

---

## Migration Checklist
- [ ] Create `py311-migration` branch from the latest mainline.
- [ ] Capture current Python 3.7 behavior (`clpipe --help`, representative commands).
- [ ] Introduce `pyproject.toml`/`setup.cfg`, raise `Requires-Python`.
- [ ] Establish reproducible dependency management (`requirements/`, constraints).
- [ ] Audit imports and modernize dependency set for Python 3.11.
- [ ] Replace deprecated stdlib/package APIs (distutils, pkg_resources, etc.).
- [ ] Expand automated tests and configure CI matrix for 3.9–3.11.
- [ ] Verify packaging data and resource loading pathways.
- [ ] Test editable, Git-based, and wheel installs from your fork.
- [ ] Update documentation to reflect the new Python baseline and install paths.
