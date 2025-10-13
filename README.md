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

- **Multi-format DSV Support**: Parse CSV, TSV, pipe-delimited, and custom delimiter separated value files/objects
- **Configurable Parsing**: Flexible options for delimiters, quote characters, escape characters, header/footer row(s) handling
- **Memory-Efficient Streaming**: Process large files without loading entire content into memory
- **Security & Validation**: Comprehensive path validation and file permission checks
- **Unicode Support**: Full Unicode character and encoding support
- **Type Safety**: Full type annotations with mypy validation
- **Deterministic Newline Handling**: Consistent handling of CRLF, CR, and LF newlines across platforms
- **CLI Tool**: Command-line interface for quick parsing and inspection of DSV files
- **Robust Error Handling**: Clear and specific exceptions for various error scenarios
- **Modern API**: Object-oriented API with `Dsv` and `DsvConfig` classes for easy configuration and reuse
- **Comprehensive Documentation**: In-depth API reference and usage examples
- **Exhaustive Testing**: 273 tests with 94% code coverage including property-based testing, edge case testing, and cross-platform compatibility validation

**⚠️ CHANGES in v2025.3.0**
> - The legacy `parse_stream()` helpers were removed in release 2025.3.0.
>   - Use `parse_file_stream()` on `Dsv`/`DsvHelper` for stream-based parsing of files. This standardizes the API naming and clarifies that streaming helpers accept file paths rather than arbitrary iterables.
> - TextFileHelper, SafeTextFileReader, SafeTextFileWriter, and PathValidator, as well as all their associated tests have been removed in this release.
>   - Their functionality has been migrated in favor of the `splurge-safe-io` package, which provides robust and secure file I/O operations.
>   - This change reduces code duplication and improves maintainability by leveraging the functionality of `splurge-safe-io`.
>   - Users should refer to the `splurge-safe-io` documentation for details on its usage and features.
> - **See API-REFERENCE.md for migration guidance and complete reference documentation, with usage examples.**

**⚠️ CHANGES in v2025.2.2**
> - **Deprecated Warning**: The following modules and their associated classes and functions are deprecated and will be removed in a future release (2025.3.0). Users are encouraged to transition to the `splurge-safe-io` package for these functionalities:
>   - `splurge_dsv.safe_text_file_reader`
>   - `splurge_dsv.safe_text_file_writer`
>   - `splurge_dsv.path_validator`
>   - `splurge_dsv.text_file_helper`
> - **New Exception**: Added `SplurgeDsvFileExistsError` to handle file existence errors.
> - **Fixed Exception Mapping**: Many errors were incorrectly mapped to SplurgeDsvEncodingError; this has been corrected to use appropriate exception types. 
>   - Some exceptions were not mapped to any SplurgeDsv* exception; these have also been corrected.
> - **3rd-Party Dependency Additions**: Added `splurge-safe-io (v2025.0.4)`.
>   - `splurge-safe-io` is a new dependency that provides robust and secure file I/O operations, including safe text file reading and writing with deterministic newline handling and path validation.
>   - This change reduces code duplication and improves maintainability by leveraging the functionality of `splurge-safe-io`.
>   - Users should refer to the `splurge-safe-io` documentation for details on its usage and features.
> - **Code Refactoring**: Refactored `SafeTextFileReader`, `SafeTextFileWriter`, and `PathValidator` to utilize `splurge-safe-io` implementations internally, ensuring consistent behavior and reducing maintenance overhead.
> - **This release maintains backward compatibility** for existing users, but users are encouraged to transition to `splurge-safe-io` for future-proofing their codebases.
>   - **_This release is a commit-only release and will not be published to PyPI._**

**⚠️ BREAKING CHANGES in v2025.2.0**
>
> - **Exception Names Changed**: All exceptions now use `SplurgeDsv*` prefix (e.g., `SplurgeParameterError` → `SplurgeDsvParameterError`)
> - **Resource Manager Removed**: The `ResourceManager` module and all related classes have been completely removed
>
> See the [CHANGELOG](CHANGELOG.md) for migration guidance.

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
- **[Testing Best Practices](docs/testing_best_practices.md)**: Comprehensive testing guidelines and patterns
- **[Hypothesis Usage Patterns](docs/hypothesis_usage_patterns.md)**: Property-based testing guide
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

### Testing Suite

splurge-dsv features a comprehensive testing suite designed for robustness and reliability:

#### Test Categories
- **Unit Tests**: Core functionality testing (300+ tests)
- **Integration Tests**: End-to-end workflow validation (50+ tests)
- **Property-Based Tests**: Hypothesis-driven testing for edge cases (50+ tests)
- **Edge Case Tests**: Malformed input, encoding issues, filesystem anomalies
- **Cross-Platform Tests**: Path handling, line endings, encoding consistency

#### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=splurge_dsv --cov-report=html

# Run specific test categories
pytest tests/unit/ -v                    # Unit tests only
pytest tests/integration/ -v            # Integration tests only
pytest tests/property/ -v               # Property-based tests only
pytest tests/platform/ -v               # Cross-platform tests only

# Run with parallel execution
pytest tests/ -n 4 --cov=splurge_dsv

# Run performance benchmarks
pytest tests/ --durations=10
```

#### Test Quality Standards
- **94%+ Code Coverage**: All public APIs and critical paths covered
- **Property-Based Testing**: Hypothesis framework validates complex scenarios
- **Cross-Platform Compatibility**: Tests run on Windows, Linux, and macOS
- **Performance Regression Detection**: Automated benchmarks prevent slowdowns
- **Zero False Positives**: All property tests pass without spurious failures

#### Testing Best Practices
- Tests use `pytest-mock` for modern mocking patterns
- Property tests use Hypothesis strategies for comprehensive input generation
- Edge case tests validate error handling and boundary conditions
- Cross-platform tests ensure consistent behavior across operating systems

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

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for detailed information on:

- Development setup and workflow
- Coding standards and best practices
- Testing requirements and guidelines
- Pull request process and review criteria

For major changes, please open an issue first to discuss what you would like to change.

## Support

For support, please open an issue on the GitHub repository or contact the maintainers.
