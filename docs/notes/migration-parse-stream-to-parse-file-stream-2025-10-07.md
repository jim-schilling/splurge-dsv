# Migration: `parse_stream` -> `parse_file_stream` (2025-10-07)

As of release 2025.2.1 the `parse_stream()` method is deprecated in favor of
`parse_file_stream()`. The runtime behavior is unchanged — both methods yield
parsed chunks of rows — but the new name better aligns with `parse_file()` and
clarifies that the operation reads from files.

Why the change
- Standardizes API naming across file-based operations (`parse_file`,
  `parse_file_stream`).
- Improves discoverability and clarity for new users.

Compatibility
- `parse_stream()` will continue to work for a short deprecation window but will
  emit a `DeprecationWarning` when called. Please update usage to avoid
  breakage when the method is removed in a future release.

How to migrate

Old usage (deprecated):

```python
from splurge_dsv import DsvHelper

for chunk in DsvHelper.parse_stream("big.csv", delimiter=","):
    for row in chunk:
        process(row)
```

New usage (preferred):

```python
from splurge_dsv import DsvHelper

for chunk in DsvHelper.parse_file_stream("big.csv", delimiter=","):
    for row in chunk:
        process(row)
```

If you use the object-oriented API:

```python
from splurge_dsv import Dsv, DsvConfig

cfg = DsvConfig.csv()
parser = Dsv(cfg)

# Deprecated
for chunk in parser.parse_stream("big.csv"):
    ...

# Preferred
for chunk in parser.parse_file_stream("big.csv"):
    ...
```

Notes
- The CLI `--stream` option is unchanged; this migration concerns the Python API.
- If you rely on `DeprecationWarning`s being visible in test runs, configure
  pytest (or other test runners) to show them (e.g., `pytest -W default`).
