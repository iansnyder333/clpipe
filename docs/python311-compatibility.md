# Python 3.11 Compatibility Scan

The repository pins several third-party dependencies in
[`clpipe/config/package.py`](../clpipe/config/package.py).  Python 3.11
introduced tighter requirements for binary wheels, so older pinned versions
can prevent `pip` from resolving the environment.

Run the helper script below to check the current pins against the minimum
versions that publish Python 3.11 wheels:

```bash
python tools/scan_py311_compatibility.py
```

At the time of writing, the scan reports the following blockers:

- `numpy==1.21.6` needs to be upgraded to at least `1.23.0` for Python 3.11
  wheels.
- `pandas==1.3.5` needs to be upgraded to at least `1.5.0` to support Python
  3.11.
- `scipy==1.2.2` predates Python 3.11 wheel builds; update to `1.9.0` or
  newer.
- `matplotlib==3.5.3` only supports Python up to 3.10; upgrade to `3.6.0` or
  newer.

Upgrading these packages (and re-testing any downstream tools that depend on
them) is a prerequisite for building `clpipe` on Python 3.11 or newer.

## Upgrade readiness assessment

The repository already exercises these libraries in a mostly modern way, so
only limited code changes were required to become compatible with the Python
3.11-capable release lines:

- **NumPy** – the only deprecated construct discovered during the audit was the
  legacy `np.object` alias that NumPy removed in 1.24.  The code path in
  `clpipe/tabularutils/codebook.py` now relies on pandas dtype helpers instead,
  which keeps the behaviour and remains compatible with both old and new NumPy
  releases.【F:clpipe/tabularutils/codebook.py†L1-L70】
- **pandas** – all tabular helpers use `read_csv`, `read_table`, and DataFrame
  concatenation APIs that are stable in pandas 1.5+.  No usage of APIs removed
  in recent pandas versions (e.g. `Panel`, `.ix`, or `.append`) was found during
  the repository scan.【F:clpipe/beta_series_reg.py†L1-L120】【F:clpipe/legacy_postprocess.py†L1-L220】
- **SciPy** – existing imports (`scipy.signal`, `scipy.sparse.spdiags`, and
  `scipy.linalg.toeplitz`) are still present in SciPy 1.9+, so raising the pin
  should not require additional code changes.  These routines are used in
  `clpipe/beta_series_reg.py` and `clpipe/postprocutils/utils.py` without
  deprecated arguments.【F:clpipe/beta_series_reg.py†L1-L120】【F:clpipe/postprocutils/utils.py†L150-L210】
- **Matplotlib** – the project only imports `matplotlib.pyplot` for figure
  generation in the beta-series regression script and in tests.  Those call
  sites rely on plotting primitives that have not changed between 3.5 and 3.6,
  so updating the pin is expected to be safe.【F:clpipe/beta_series_reg.py†L1-L120】【F:tests/conftest.py†L70-L110】

After bumping the dependency pins in `clpipe/config/package.py`, re-run the
test suite (`pytest`) to confirm the newer versions work end-to-end.
