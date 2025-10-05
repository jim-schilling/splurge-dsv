# splurge-dsv

[![PyPI version](https://badge.fury.io/py/splurge-dsv.svg)](https://pypi.org/project/splurge-dsv/)
[![Python versions](https://img.shields.io/pypi/pyversions/splurge-dsv.svg)](https://pypi.org/project/splurge-dsv/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Coverage](https://img.shields.io/badge/coverage-96%25-brightgreen.svg)](https://github.com/jim-schilling/splurge-dsv)

A robust Python library for parsing and processing delimited-separated value (DSV) files with advanced features for data validation, streaming, and error handling.

## Features

### 🔧 Core Functionality
- **Multi-format DSV Support**: Parse CSV, TSV, pipe-delimited, semicolon-delimited, and custom delimiter files
- **Flexible Parsing Options**: Configurable whitespace handling, bookend removal, and encoding support
- **Memory-Efficient Streaming**: Process large files without loading entire content into memory
- **Header/Footer Skipping**: Skip specified numbers of rows from start or end of files
- **Unicode Support**: Full Unicode character and delimiter support

### 🛡️ Security & Validation
- **Path Validation**: Comprehensive file path security validation with traversal attack prevention
- **File Permission Checks**: Automatic file accessibility and permission validation
- **Encoding Validation**: Robust encoding error detection and handling
- **Resource Management**: Automatic file handle cleanup and resource management

### 📊 Advanced Processing
- **Chunked Processing**: Configurable chunk sizes for streaming large datasets
- **Mixed Content Handling**: Support for quoted and unquoted values in the same file
- **Line Ending Flexibility**: Automatic handling of different line ending formats
- **Error Recovery**: Graceful error handling with detailed error messages

### 🧪 Testing & Quality
- **Comprehensive Test Suite**: 250+ tests with 85%+ coverage gate
- **Cross-Platform Support**: Tested on Windows, and should pass on Linux and macOS
- **Type Safety**: Full type annotations and validation
- **Documentation**: Complete API documentation with examples

## Installation

```bash
pip install splurge-dsv
```

## Quick Start

### Basic CSV Parsing

```python
from splurge_dsv import DsvHelper

# Parse a simple CSV string
data = DsvHelper.parse("a,b,c", delimiter=",")
print(data)  # ['a', 'b', 'c']

# Parse a CSV file
rows = DsvHelper.parse_file("data.csv", delimiter=",")
for row in rows:
    print(row)  # ['col1', 'col2', 'col3']
```

### Streaming Large Files

```python
from splurge_dsv import DsvHelper

# Stream a large CSV file in chunks
for chunk in DsvHelper.parse_stream("large_file.csv", delimiter=",", chunk_size=1000):
    for row in chunk:
        process_row(row)
```

### Advanced Parsing Options

```python
from splurge_dsv import DsvHelper

# Parse with custom options
data = DsvHelper.parse(
    '"a","b","c"',
    delimiter=",",
    bookend='"',
    strip=True,
    bookend_strip=True
)
print(data)  # ['a', 'b', 'c']

# Skip header and footer rows
rows = DsvHelper.parse_file(
    "data.csv",
    delimiter=",",
    skip_header_rows=1,
    skip_footer_rows=2
)
```

### Text File Operations

```python
from splurge_dsv import TextFileHelper

# Count lines in a file
line_count = TextFileHelper.line_count("data.txt")

# Preview first N lines
preview = TextFileHelper.preview("data.txt", max_lines=10)

# Read entire file with options
lines = TextFileHelper.read(
    "data.txt",
    strip=True,
    skip_header_rows=1,
    skip_footer_rows=1
)

# Stream file content
for chunk in TextFileHelper.read_as_stream("large_file.txt", chunk_size=500):
    process_chunk(chunk)
```

### Path Validation

```python
from splurge_dsv import PathValidator

# Validate a file path
valid_path = PathValidator.validate_path(
    "data.csv",
    must_exist=True,
    must_be_file=True,
    must_be_readable=True
)

# Check if path is safe
is_safe = PathValidator.is_safe_path("user_input_path.txt")
```

## API Reference

### DsvHelper

Main class for DSV parsing operations.

#### Methods

- `parse(content, delimiter, strip=True, bookend=None, bookend_strip=True)` - Parse a single string
- `parses(content_list, delimiter, strip=True, bookend=None, bookend_strip=True)` - Parse multiple strings
- `parse_file(file_path, delimiter, strip=True, bookend=None, bookend_strip=True, skip_header_rows=0, skip_footer_rows=0, encoding='utf-8')` - Parse a file
- `parse_stream(file_path, delimiter, strip=True, bookend=None, bookend_strip=True, skip_header_rows=0, skip_footer_rows=0, encoding='utf-8', chunk_size=500)` - Stream parse a file

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

### ResourceManager

Context managers for safe resource handling.

#### Classes

- `FileResourceManager` - Context manager for file operations
- `StreamResourceManager` - Context manager for stream operations

#### Functions

- `safe_file_operation(file_path, mode='r', encoding='utf-8', ...)` - Safe file operation context manager
- `safe_stream_operation(stream, auto_close=True)` - Safe stream operation context manager

## Error Handling

The library provides comprehensive error handling with custom exception classes:

- `SplurgeDsvParameterError` - Invalid parameter values
- `SplurgeFileNotFoundError` - File not found
- `SplurgeFilePermissionError` - File permission issues
- `SplurgeFileEncodingError` - File encoding problems
- `SplurgePathValidationError` - Path validation failures

Deterministic newline policy
----------------------------

This library enforces deterministic newline handling for text files. The reader
normalizes CRLF (`\r\n`), CR (`\r`) and LF (`\n`) to LF internally and
returns logical lines. The writer utilities normalize any input newlines to LF
before writing. This avoids platform-dependent differences when reading files
produced by diverse sources.

Recommended usage:

- When creating files inside the project, prefer the `open_text_writer` context
    manager or `SafeTextFileWriter` which will normalize to LF.
- When reading unknown files, the `open_text` / `SafeTextFileReader` will
    provide deterministic normalization regardless of the source.
- `SplurgeResourceAcquisitionError` - Resource acquisition failures
- `SplurgeResourceReleaseError` - Resource cleanup failures

## Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=splurge_dsv --cov-report=html

# Run specific test file
pytest tests/test_dsv_helper.py -v
```

### Code Quality

The project follows strict coding standards:
- PEP 8 compliance
- Type annotations for all functions
- Google-style docstrings
- 85%+ coverage gate enforced via CI
- Comprehensive error handling

## Changelog

See the [CHANGELOG](CHANGELOG.md) for full release notes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## More Documentation

- Detailed docs: [docs/README-details.md](docs/README-details.md)
- E2E testing coverage: [docs/e2e_testing_coverage.md](docs/e2e_testing_coverage.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## Support

For support, please open an issue on the GitHub repository or contact the maintainers.
