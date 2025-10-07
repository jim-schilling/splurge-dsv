# splurge-dsv — Detailed Documentation

> **⚠️ DEPRECATION WARNING in v2025.2.1**
>
> - **DsvHelper.parse_stream**: This method is deprecated in favor of `DsvHelper.parse_file_stream`.
> - **Dsv.parse_stream**: This method is deprecated in favor of `Dsv.parse_file_stream`.
>
> See the [CHANGELOG](CHANGELOG.md) for migration guidance.

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

# Skip header rows and use custom encoding
python -m splurge_dsv data.csv --delimiter , --skip-header 1 --encoding utf-16

# Parse pipe-delimited data without stripping whitespace
python -m splurge_dsv data.txt --delimiter "|" --no-strip
```

## CLI Options Reference

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--delimiter` | `-d` | Field delimiter character | Required |
| `--bookend` | `-b` | Quote character for fields | None |
| `--no-strip` | | Disable whitespace stripping | False |
| `--no-bookend-strip` | | Disable whitespace stripping before bookend removal | False |
| `--encoding` | `-e` | File encoding | utf-8 |
| `--skip-header` | | Number of header rows to skip | 0 |
| `--skip-footer` | | Number of footer rows to skip | 0 |
| `--stream` | `-s` | Stream file in chunks | False |
| `--chunk-size` | | Chunk size for streaming | 500 |
| `--version` | | Show version and exit | |

## Programmatic Usage

### Basic String Parsing

```python
from splurge_dsv import DsvHelper

# Parse a simple CSV string
data = DsvHelper.parse("a,b,c", delimiter=",")
print(data)  # ['a', 'b', 'c']

# Parse with quoted values
data = DsvHelper.parse('"hello","world"', delimiter=",", bookend='"')
print(data)  # ['hello', 'world']

# Parse without stripping whitespace
data = DsvHelper.parse(" a , b ", delimiter=",", strip=False)
print(data)  # [' a ', ' b ']
```

### Parsing Multiple Strings

```python
from splurge_dsv import DsvHelper

# Parse a list of strings
rows = DsvHelper.parses(["a,b,c", "d,e,f", "g,h,i"], delimiter=",")
for row in rows:
    print(row)
# Output:
# ['a', 'b', 'c']
# ['d', 'e', 'f']
# ['g', 'h', 'i']
```

### File Parsing

```python
from splurge_dsv import DsvHelper

# Parse a CSV file
rows = DsvHelper.parse_file("data.csv", delimiter=",")
for row in rows:
    print(row)

# Parse with options
rows = DsvHelper.parse_file(
    "data.csv",
    delimiter=",",
    skip_header_rows=1,  # Skip header row
    skip_footer_rows=2,  # Skip last 2 rows
    encoding="utf-8"
)
```

### Streaming Large Files

```python
from splurge_dsv import DsvHelper

# Stream parse a large file in chunks
for chunk in DsvHelper.parse_file_stream("large_file.csv", delimiter=",", chunk_size=1000):
    for row in chunk:
        process_row(row)

# Stream with header/footer skipping
for chunk in DsvHelper.parse_file_stream(
    "large_file.csv",
    delimiter=",",
    skip_header_rows=1,
    skip_footer_rows=1,
    chunk_size=500
):
    for row in chunk:
        process_row(row)
```

### Text File Operations

```python
from splurge_dsv import TextFileHelper

# Count lines in a file
line_count = TextFileHelper.line_count("data.txt")
print(f"File has {line_count} lines")

# Preview first N lines
preview_lines = TextFileHelper.preview("data.txt", max_lines=10)
for line in preview_lines:
    print(line)

# Read entire file with options
lines = TextFileHelper.read(
    "data.txt",
    strip=True,
    skip_header_rows=1,
    skip_footer_rows=1,
    encoding="utf-8"
)

# Stream file content for large files
for chunk in TextFileHelper.read_as_stream("large_file.txt", chunk_size=500):
    for line in chunk:
        process_line(line)
```

### Path Validation

```python
from splurge_dsv import PathValidator

# Validate a file path with security checks
try:
    valid_path = PathValidator.validate_path(
        "data.csv",
        must_exist=True,
        must_be_file=True,
        must_be_readable=True,
        allow_relative=False
    )
    print(f"Path is valid: {valid_path}")
except Exception as e:
    print(f"Path validation failed: {e}")

# Check if path is safe (no traversal attacks)
is_safe = PathValidator.is_safe_path("../../../etc/passwd")
print(f"Path is safe: {is_safe}")  # False

# Sanitize filename
safe_name = PathValidator.sanitize_filename("file<>with|bad:chars?.txt")
print(f"Sanitized name: {safe_name}")  # 'filewithbadchars.txt'
```

## API Reference

### DsvConfig

Immutable configuration dataclass for DSV parsing parameters.

#### Factory Methods

- `csv(skip_header=0, skip_footer=0, strip=True, bookend='"', bookend_strip=True, encoding='utf-8', chunk_size=500)` - Create CSV configuration
- `tsv(skip_header=0, skip_footer=0, strip=True, bookend='"', bookend_strip=True, encoding='utf-8', chunk_size=500)` - Create TSV configuration
- `from_params(delimiter, skip_header=0, skip_footer=0, strip=True, bookend=None, bookend_strip=True, encoding='utf-8', chunk_size=500)` - Create from parameters

#### Properties

- `delimiter` - Field delimiter character
- `skip_header` - Number of header rows to skip
- `skip_footer` - Number of footer rows to skip
- `strip` - Whether to strip whitespace
- `bookend` - Quote character for fields
- `bookend_strip` - Whether to strip whitespace before bookend removal
- `encoding` - File encoding
- `chunk_size` - Chunk size for streaming operations

### Dsv

Modern object-oriented API class that encapsulates configuration and provides parsing methods.

#### Constructor

- `Dsv(config)` - Create Dsv instance with DsvConfig

#### Methods

- `parse(content)` - Parse a single string
- `parses(content_list)` - Parse multiple strings
- `parse_file(file_path)` - Parse a file
- `parse_file_stream(file_path)` - Stream parse a file

### DsvHelper

Main class for DSV parsing operations.

#### Methods

- `parse(content, delimiter, strip=True, bookend=None, bookend_strip=True)` - Parse a single string
- `parses(content_list, delimiter, strip=True, bookend=None, bookend_strip=True)` - Parse multiple strings
- `parse_file(file_path, delimiter, strip=True, bookend=None, bookend_strip=True, skip_header_rows=0, skip_footer_rows=0, encoding='utf-8')` - Parse a file
- `parse_file_stream(file_path, delimiter, strip=True, bookend=None, bookend_strip=True, skip_header_rows=0, skip_footer_rows=0, encoding='utf-8', chunk_size=500)` - Stream parse a file

### TextFileHelper

Utility class for text file operations.

#### Methods

- `line_count(file_path, encoding='utf-8')` - Count lines in a file
- `preview(file_path, max_lines=100, strip=True, encoding='utf-8', skip_header_rows=0)` - Preview file content
- `read(file_path, strip=True, encoding='utf-8', skip_header_rows=0, skip_footer_rows=0)` - Read entire file
- `read_as_stream(file_path, strip=True, encoding='utf-8', skip_header_rows=0, skip_footer_rows=0, chunk_size=500)` - Stream read file

### PathValidator

Security-focused path validation utilities.

#### Methods

- `validate_path(file_path, must_exist=False, must_be_file=False, must_be_readable=False, allow_relative=False, base_directory=None)` - Validate file path
- `is_safe_path(file_path)` - Check if path is safe
- `sanitize_filename(filename, default_name='file')` - Sanitize filename

### StringTokenizer

Core tokenization primitives and bookend handling.

#### Methods

- `parse(content, delimiter, strip=True, bookend=None, bookend_strip=True)` - Parse a single string
- `parses(content_list, delimiter, strip=True, bookend=None, bookend_strip=True)` - Parse multiple strings
- `remove_bookends(content, bookend, strip=True)` - Remove bookend characters from string

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
for chunk in dsv.parse_file_stream("large.csv"):
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

The library provides comprehensive error handling with custom exception classes for different types of failures:

### Parameter & Configuration Errors
- `SplurgeDsvParameterError` - Invalid parameter values or missing required parameters
- `SplurgeDsvValidationError` - Data validation failures (malformed content, invalid formats)
- `SplurgeDsvConfigurationError` - Configuration validation failures

### File System Errors
- `SplurgeDsvFileNotFoundError` - File not found or doesn't exist
- `SplurgeDsvFilePermissionError` - File permission issues (read/write access denied)
- `SplurgeDsvFileEncodingError` - File encoding problems or invalid byte sequences
- `SplurgeDsvPathValidationError` - Path validation failures (unsafe paths, traversal attacks)

### Data Processing Errors
- `SplurgeDsvDataProcessingError` - General data processing failures
- `SplurgeDsvParsingError` - Data parsing failures (malformed CSV, invalid delimiters)
- `SplurgeDsvTypeConversionError` - Type conversion failures

### Resource & Streaming Errors
- `SplurgeDsvStreamingError` - Streaming operation failures
- `SplurgeDsvResourceAcquisitionError` - Resource acquisition failures (file handles, memory)
- `SplurgeDsvResourceReleaseError` - Resource cleanup failures

### Other Errors
- `SplurgeDsvPerformanceWarning` - Performance-related warnings (not errors)

### Exception Hierarchy

All exceptions inherit from `SplurgeDsvError` (which inherits from `Exception`). This allows you to catch all library-specific errors:

```python
from splurge_dsv import DsvHelper
from splurge_dsv.exceptions import SplurgeDsvError

try:
    rows = DsvHelper.parse_file("nonexistent.csv", delimiter=",")
except SplurgeDsvError as e:
    print(f"DSV processing failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Error Handling Examples

```python
from splurge_dsv import DsvHelper
from splurge_dsv.exceptions import (
    SplurgeDsvFileNotFoundError,
    SplurgeDsvFileEncodingError,
    SplurgeDsvParsingError
)

def safe_parse_file(file_path, delimiter):
    try:
        return DsvHelper.parse_file(file_path, delimiter=delimiter)
    except SplurgeDsvFileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except SplurgeDsvFileEncodingError as e:
        print(f"Encoding error in {file_path}: {e}")
        return []
    except SplurgeDsvParsingError as e:
        print(f"Parsing error in {file_path}: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []
```

## Advanced Usage

### Custom Delimiters and Unicode Support

```python
from splurge_dsv import DsvHelper

# Parse with Unicode delimiter
data = DsvHelper.parse("a→b→c", delimiter="→")
print(data)  # ['a', 'b', 'c']

# Parse with multi-character delimiters (not recommended for CSV)
data = DsvHelper.parse("aSEP bSEP c", delimiter="SEP ")
print(data)  # ['a', 'b', 'c']

# Handle Unicode content
unicode_content = "café, naïve, résumé"
data = DsvHelper.parse(unicode_content, delimiter=", ")
print(data)  # ['café', 'naïve', 'résumé']
```

### Complex Quoted Values

```python
from splurge_dsv import DsvHelper

# Handle nested quotes
content = '"Field with ""nested"" quotes","Normal field"'
data = DsvHelper.parse(content, delimiter=",", bookend='"')
print(data)  # ['Field with "nested" quotes', 'Normal field']

# Mixed quoted and unquoted
content = '"Quoted field",Unquoted field,"Another quoted"'
data = DsvHelper.parse(content, delimiter=",", bookend='"')
print(data)  # ['Quoted field', 'Unquoted field', 'Another quoted']
```

### Configuration Reuse Patterns

```python
from splurge_dsv import DsvConfig, Dsv

# Create reusable configurations
csv_config = DsvConfig.csv(skip_header=1, bookend='"')
tsv_config = DsvConfig.tsv(skip_header=1)

# Use for multiple files
csv_parser = Dsv(csv_config)
tsv_parser = Dsv(tsv_config)

# Process multiple files with same config
for file_path in ["data1.csv", "data2.csv", "data3.csv"]:
    rows = csv_parser.parse_file(file_path)
    process_rows(rows)
```

### Memory-Efficient Processing

```python
from splurge_dsv import DsvHelper

# For very large files, use streaming with small chunks
def process_large_file(file_path):
    total_rows = 0
    for chunk in DsvHelper.parse_file_stream(file_path, delimiter=",", chunk_size=100):
        for row in chunk:
            total_rows += 1
            # Process row immediately to save memory
            yield row
    print(f"Processed {total_rows} rows")

# Use iterator pattern for memory efficiency
for row in process_large_file("huge_file.csv"):
    # Process each row
    pass
```

## Performance Considerations

### Streaming vs. Loading

- **Use streaming** for files > 100MB or when memory is limited
- **Use loading** for small files or when you need random access to rows
- **Default chunk size (500)** works well for most use cases
- **Smaller chunks** reduce memory usage but increase I/O overhead
- **Larger chunks** improve performance but use more memory

### Encoding Performance

- **UTF-8** is fastest and most compatible
- **UTF-16/32** have higher memory overhead
- **Latin-1** is fastest for ASCII-only content
- **BOM detection** adds small overhead but ensures correctness

### Optimization Tips

```python
# Fast path for simple CSV
rows = DsvHelper.parse_file("simple.csv", delimiter=",")

# Optimized for large files
for chunk in DsvHelper.parse_stream("large.csv", delimiter=",", chunk_size=1000):
    for row in chunk:
        # Process immediately
        pass

# Reuse parsers for multiple files
config = DsvConfig.csv()
parser = Dsv(config)
for file in file_list:
    data = parser.parse_file(file)
```

## Examples and Use Cases

### Data Import Pipeline

```python
from splurge_dsv import Dsv, DsvConfig
import sqlite3

def import_csv_to_database(csv_path, db_path, table_name):
    # Configure for CSV with header
    config = DsvConfig.csv(skip_header=1)
    parser = Dsv(config)

    # Create database table
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get column count from first row
    first_rows = parser.parse_file(csv_path)
    if first_rows:
        col_count = len(first_rows[0])
        placeholders = ','.join(['?'] * col_count)
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({','.join([f'col{i} TEXT' for i in range(col_count)])})")

        # Import all data
        for row in first_rows:
            cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", row)

    conn.commit()
    conn.close()
```

### Log File Processing

```python
from splurge_dsv import TextFileHelper
from datetime import datetime

def process_access_log(log_path):
    """Process web server access logs with custom format"""
    # Access logs often use spaces as separators
    # Format: IP - - [timestamp] "method path protocol" status size

    for line in TextFileHelper.read_as_stream(log_path, chunk_size=1000):
        if line.strip():
            # Custom parsing logic for log format
            parts = line.split()
            if len(parts) >= 7:
                ip = parts[0]
                timestamp = parts[3] + ' ' + parts[4]  # [timestamp]
                request = ' '.join(parts[5:8])  # "method path protocol"
                status = parts[8]
                size = parts[9] if len(parts) > 9 else '-'

                yield {
                    'ip': ip,
                    'timestamp': timestamp.strip('[]'),
                    'request': request.strip('"'),
                    'status': int(status),
                    'size': int(size) if size != '-' else 0
                }
```

## Testing

This project uses `pytest` with a coverage gate (>=94%).
```bash
pytest -x -v --cov=splurge_dsv --cov-report=term-missing --cov-report=html
```

The test suite includes:
- **Unit Tests**: 396 tests covering all core functionality, CLI, and error handling
- **Integration Tests**: End-to-end workflows, file operations, and CLI integration
- **Property-Based Tests**: Hypothesis-driven tests for invariant verification across string_tokenizer, dsv_helper, path_validator, and text_file_helper modules
- **Edge Case Tests**: Comprehensive coverage of malformed CSV structures, encoding edge cases (UTF-8/16, BOM handling), and filesystem edge cases (concurrent access, file modifications during operations)

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=splurge_dsv --cov-report=html

# Run specific test file
pytest tests/test_dsv_helper.py -v

# Run tests in parallel (if pytest-xdist installed)
pytest tests/ -n 4
```

### Test Categories

- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - Integration tests for end-to-end workflows
- `tests/property/` - Property-based tests using Hypothesis
- `tests/e2e/` - End-to-end tests (if applicable)

See `docs/e2e_testing_coverage.md` for integration and end-to-end coverage notes.

## Versioning
CalVer scheme is used: `YYYY.MINOR.PATCH` (e.g., `2025.2.0`).

## License
MIT License. See `LICENSE`.


