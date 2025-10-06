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
