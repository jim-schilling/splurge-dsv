# splurge-dsv

[![PyPI version](https://badge.fury.io/py/splurge-dsv.svg)](https://pypi.org/project/splurge-dsv/)
[![Python versions](https://img.shields.io/pypi/pyversions/splurge-dsv.svg)](https://pypi.org/project/splurge-dsv/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/jim-schilling/splurge-dsv/actions/workflows/ci-quick-test.yml/badge.svg)](https://github.com/jim-schilling/splurge-dsv/actions/workflows/ci-quick-test.yml)
[![Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen.svg)](https://github.com/jim-schilling/splurge-dsv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy](https://img.shields.io/badge/mypy-checked-black)](https://mypy-lang.org/)

A robust Python library for parsing and processing delimited-separated value (DSV) files with advanced features for data validation, streaming, and error handling.

## Features

- **Multi-format DSV Support**: Parse CSV, TSV, pipe-delimited, and custom delimiter files
- **Memory-Efficient Streaming**: Process large files without loading entire content into memory
- **Security & Validation**: Comprehensive path validation and file permission checks
- **Unicode Support**: Full Unicode character and encoding support
- **Type Safety**: Full type annotations with mypy validation
- **Comprehensive Testing**: 396 tests with 94% code coverage

## Installation

```bash
pip install splurge-dsv
```

## Quick Start

### CLI Usage

```bash
# Parse a CSV file
python -m splurge_dsv data.csv --delimiter ,

# Stream a large file
python -m splurge_dsv large_file.csv --delimiter , --stream --chunk-size 1000
```

### API Usage

```python
from splurge_dsv import DsvHelper

# Parse a CSV string
data = DsvHelper.parse("a,b,c", delimiter=",")
print(data)  # ['a', 'b', 'c']

# Parse a CSV file
rows = DsvHelper.parse_file("data.csv", delimiter=",")
```

### Modern API

```python
from splurge_dsv import Dsv, DsvConfig

# Create configuration and parser
config = DsvConfig.csv(skip_header=1)
dsv = Dsv(config)

# Parse files
rows = dsv.parse_file("data.csv")
```

## Documentation

- **[Detailed Documentation](docs/README-details.md)**: Complete API reference, CLI options, and examples
- **[Changelog](CHANGELOG.md)**: Release notes and migration guides

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
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
