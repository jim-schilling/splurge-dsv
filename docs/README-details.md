# splurge-dsv — Detailed Documentation

> **⚠️ BREAKING CHANGES in v2025.2.0**
>
> - **Exception Names Changed**: All exceptions now use `SplurgeDsv*` prefix (e.g., `SplurgeParameterError` → `SplurgeDsvParameterError`)
> - **Resource Manager Removed**: The `ResourceManager` module and all related classes have been completely removed
>
> See the [CHANGELOG](CHANGELOG.md) for migration guidance.

## Overview
`splurge-dsv` is a robust Python library for parsing and processing delimited-separated value (DSV) files with an emphasis on security, streaming performance, and clear error handling. It provides a clean public API for programmatic use and a simple CLI for command-line workflows.

## Architecture
- `splurge_dsv.dsv.DsvConfig`: Immutable configuration dataclass for DSV parsing parameters
- `splurge_dsv.dsv.Dsv`: Modern API class that encapsulates configuration and provides parsing methods
- `splurge_dsv.dsv_helper.DsvHelper`: High-level parsing utilities for strings, lists of strings, files, and streaming.
- `splurge_dsv.text_file_helper.TextFileHelper`: Memory-efficient text file utilities (line counting, preview, read, stream).
- `splurge_dsv.string_tokenizer.StringTokenizer`: Core tokenization primitives and bookend handling.
- `splurge_dsv.path_validator.PathValidator`: Security-focused path validation and sanitation helpers.
- `splurge_dsv.exceptions`: Custom exception hierarchy for consistent, descriptive errors.
- `splurge_dsv.cli`: Command-line interface (`python -m splurge_dsv`).

## Installation
```bash
pip install splurge-dsv
```

## CLI Usage
Run the CLI using the module entrypoint:
```bash
python -m splurge_dsv <file_path> --delimiter "," [options]
```

Supported options:
- `--delimiter, -d` Delimiter character (required)
- `--bookend, -b` Bookend character for quoted text fields
- `--no-strip` Disable whitespace stripping
- `--no-bookend-strip` Disable whitespace stripping before bookend removal
- `--encoding, -e` File encoding (default: utf-8)
- `--skip-header` Number of header rows to skip (default: 0)
- `--skip-footer` Number of footer rows to skip (default: 0)
- `--stream, -s` Stream file in chunks instead of loading into memory
- `--chunk-size` Chunk size when streaming (default: 500)
- `--version` Show version and exit

Examples:
```bash
# Parse a CSV file
python -m splurge_dsv data.csv --delimiter ,

# Parse a TSV file with bookends
python -m splurge_dsv data.tsv --delimiter "\t" --bookend '"'

# Stream a large file in chunks
python -m splurge_dsv large.csv --delimiter , --stream --chunk-size 1000
```

## Programmatic Usage
### Parse string
```python
from splurge_dsv import DsvHelper

tokens = DsvHelper.parse("a,b,c", delimiter=",")
```

### Parse list of strings
```python
rows = DsvHelper.parses(["a,b,c", "d,e,f"], delimiter=",")
```

### Parse file
```python
rows = DsvHelper.parse_file(
    "data.csv",
    delimiter=",")
```

### Stream parse file
```python
for chunk in DsvHelper.parse_stream(
    "large.csv",
    delimiter=","):
    for row in chunk:
        process_row(row)
```

## Modern Dsv API

The library provides a modern, object-oriented API through the `Dsv` class and `DsvConfig` dataclass for better configuration management and reusability.

### Configuration with DsvConfig
```python
from splurge_dsv import DsvConfig, Dsv

# Create configuration for CSV parsing
config = DsvConfig(
    delimiter=",",
    skip_header=1,
    strip=True
)

# Use factory methods for common formats
csv_config = DsvConfig.csv(skip_header=1)
tsv_config = DsvConfig.tsv(bookend='"')
```

### Parsing with Dsv class
```python
# Create a Dsv instance with configuration
dsv = Dsv(config)

# Parse strings
tokens = dsv.parse("a,b,c")

# Parse multiple strings
rows = dsv.parses(["a,b,c", "d,e,f"])

# Parse files
rows = dsv.parse_file("data.csv")

# Stream parse large files
for chunk in dsv.parse_stream("large.csv"):
    for row in chunk:
        process_row(row)
```

### Configuration Reuse
```python
# Create one configuration and reuse it
config = DsvConfig.csv(skip_header=1, skip_footer=1)
dsv = Dsv(config)

# Use the same config for multiple operations
data1 = dsv.parse_file("file1.csv")
data2 = dsv.parse_file("file2.csv")
data3 = dsv.parse_file("file3.csv")
```

### Backwards Compatibility
The original `DsvHelper` static methods remain fully supported and unchanged for existing code.

## Security & Validation
- All file paths are validated via `PathValidator.validate_path(...)` to prevent traversal and unsafe inputs.
- File operations use `safe_file_operation` which wraps `open()` with consistent error translation into custom exceptions.
- Dangerous characters and invalid path patterns are rejected early with descriptive errors.

## Error Handling
The library raises domain-specific exceptions for clarity:
- `SplurgeDsvParameterError`, `SplurgeDsvValidationError`
- `SplurgeDsvFileNotFoundError`, `SplurgeDsvFilePermissionError`, `SplurgeDsvFileEncodingError`, `SplurgeDsvPathValidationError`
- `SplurgeDsvResourceAcquisitionError`, `SplurgeDsvResourceReleaseError`

## Testing
This project uses `pytest` with a coverage gate (>=94%).
```bash
pytest -x -v --cov=splurge_dsv --cov-report=term-missing --cov-report=html
```

The test suite includes:
- **Unit Tests**: 300+ tests covering all core functionality, CLI, and error handling
- **Integration Tests**: End-to-end workflows, file operations, and CLI integration
- **Property-Based Tests**: Hypothesis-driven tests for invariant verification across string_tokenizer, dsv_helper, path_validator, and text_file_helper modules
- **Edge Case Tests**: Comprehensive coverage of malformed CSV structures, encoding edge cases (UTF-8/16, BOM handling), and filesystem edge cases (concurrent access, file modifications during operations)

See `docs/e2e_testing_coverage.md` for integration and end-to-end coverage notes.

## Versioning
CalVer scheme is used: `YYYY.MINOR.PATCH` (e.g., `2025.2.0`).

## License
MIT License. See `LICENSE`.


