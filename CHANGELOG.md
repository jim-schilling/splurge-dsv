# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and the versioning follows CalVer.

## [2025.5.1] - 2025-10-30

### Updated
- **Vendored Dependencies Update**: `splurge-exceptions` and `splurge-safe-io` have been updated.
- **Bumped Versions**:
  - Updated version to 2025.5.1 in `__init__.py` and `pyproject.toml`.
- **MyPy Configuration Update**:
  - Updated MyPy configuration to relax strictness on examples.
  - Updated `ci-lint-and-typecheck.yml` to run MyPy on the entire codebase.
  - Updated pre-commit hook for MyPy to check the full codebase.
- **Pytest Coverage Configuration Update**:
  - Updated coverage configuration to omit vendor and test files from reports.


## [2025.5.0] - 2025-10-29

### Updated
- Bumped version to 2025.5.0 in `__init__.py` and `pyproject.toml`.
- Refactored imports in `__init__.py` and `splurge_dsv/__init__.py` to remove runtime dependency checks for `splurge-safe-io`, as it is now vendored.
- Refactored tests in `tests/integration/test_file_operations.py` to replace updated exception usage with the correct `SplurgeDsvUnicodeError`.
- Refactored all imports in `splurge_dsv/*` modules to use vendored `splurge-safe-io` instead of the pip-installed package.
- Refactored all imports in `tests/*` modules to use vendored `splurge-safe-io` instead of the pip-installed package.
- Refactored all imports in `splurge_dsv/*` modules to use vendored `splurge-exceptions` instead of the pip-installed package.
- Refactored all package absolute imports to use relative imports within the `splurge_dsv` package, where applicable.
- File encoding/decoding errors are now raised as `SplurgeDsvUnicodeError` to align with the `splurge-safe-io` behavior.
- Codecs related errors are now raised as `SplurgeDsvLookupError` to align with the `splurge-safe-io` behavior.

### Changed/Added
- Added vendored `splurge-exceptions` to v2025.3.0 to incorporate latest fixes and features.
- Added vendored `splurge-safe-io` to v2025.4.1 to incorporate latest fixes and features.

### Removed
- Removed pip dependency on `splurge-exceptions` in favor of vendored copy.
- Removed pip dependency on `splurge-safe-io` in favor of vendored copy.

## [2025.4.0] - 2025-10-26

### Added
- Added `splurge-exceptions` v2025.1.0 as a dependency to standardize exception handling across Splurge libraries.
- `SplurgeDsvError` exception was refactored to inherit from `SplurgeFrameworkException` class from `splurge-exceptions`.

### Refactored/Added
- `SplurgeDsv*` exceptions include:
  - `SplurgeDsvError`: Base exception for all splurge-dsv errors, inheriting from `SplurgeFrameworkException`.
  - `SplurgeDsvOSError`: For OS-related errors.
  - `SplurgeDsvValueError`: For invalid value errors.
  - `SplurgeDsvTypeError`: For type-related errors.
  - `SplurgeDsvLookupError`: For lookup failures.
  - `SplurgeDsvRuntimeError`: For runtime errors.
  - `SplurgeDsvPathValidationError`: For path validation issues.
  - `SplurgeDsvDataProcessingError`: For data processing errors.
  - `SplurgeDsvColumnMismatchError`: For column count mismatches in rows.

### Removed
- Removed custom exception handling logic in favor of standardized exceptions from `splurge-exceptions`.
- Removed deprecated exceptions that are now covered by `splurge-exceptions`.

### Updated
- Updated pyproject.toml to include `splurge-exceptions` v2025.1.0 as a dependency.
- Updated pyproject.toml to latest versions of other dependencies.
- Updated documentation to reflect new exception hierarchy and usage.
- Bumped version to 2025.4.0.

## [2025.3.2] - 2025-10-14
### Updated
- Updated test mocks to use `readlines()` instead of deprecated `read()` method, ensuring compatibility with `splurge-safe-io` updates.
- Updated test mocks to use `readlines_as_stream()` instead of deprecated `read_as_stream()` method, ensuring compatibility with `splurge-safe-io` updates.
- Updated tests to use `readlines()` and `readlines_as_stream()` for consistency with new reader APIs.
- Updated dependency versions in test environments to ensure compatibility with latest `splurge-safe-io` release.
- Updated DsvHelper and Dsv classes to ensure full compatibility with `splurge-safe-io` v2025.0.6+.
- Updated pyproject.toml and setup.cfg to reflect latest dependency versions.
- Updated README and documentation to reflect changes in dependencies and APIs.

## [2025.3.1/2025.3.0] - 2025-10-13

### Added
- **YAML configuration support**: Add `DsvConfig.from_file()` to load parser configuration from a YAML file and allow users to provide a `--config / -c` YAML file to the CLI. Unknown keys in the YAML are ignored and CLI args override YAML values.
- **`skip_empty_lines` integration**: Support `skip_empty_lines` (reader-level) throughout the API:
  - `DsvConfig.skip_empty_lines` field was added (default: False).
  - `--skip-empty-lines` CLI flag added; merged with YAML config and CLI precedence rules.
  - `DsvHelper` and `Dsv` forward `skip_empty_lines` into the underlying `splurge_safe_io.SafeTextFileReader` so the reader can perform blank-line filtering when requested.
- **Examples & docs**: Added an example config file (`examples/config.yaml`) and updated README and API reference docs to document YAML configuration and the new flag.
- **Large-file streaming semantics**: Stream parsing behavior was clarified and simplified to rely on the reader for empty-line suppression; the stream now yields parsed chunks directly and the reader controls whether empty logical lines are presented.

### Changed
- **CLI merging and options**: CLI `--config` (YAML) now merges with CLI args; CLI arguments always override YAML settings. The CLI accepts more configuration via YAML (encoding, skip counts, chunk-size, skip_empty_lines, etc.).
- **Tests converted to end-to-end style**: Several fragile tests that previously mocked internals were converted to end-to-end style (temporary files + real `run_cli()`/`Dsv` usage) to improve reliability.
- **Updated dependency**: Bumped `splurge-safe-io` integration to use the reader's `skip_empty_lines` capability when available (work with v2025.0.5+).
- **Yield behavior**: The streaming layer now yields parsed chunks unconditionally (instead of suppressing empty parsed-chunks) and relies on the reader's `skip_empty_lines` to remove meaningless empty logical rows when requested.

### Fixed
- **Lint and minor code cleanups**: Minor ruff fixes (including replacing an unnecessary list-comprehension with `list()`), type hints, and small test refactors.
- **Test harness & compatibility**: Adjusted `tests/conftest.py` to prefer the installed `splurge_safe_io` package (and fallbacks/shims used during development), stabilizing CI and developer test runs.

### Tests
- Added unit tests to validate the new `skip_empty_lines` behavior across encodings and stream/file APIs (utf-8 and utf-16; skip True/False). Added and updated multiple CLI and parsing tests to exercise the YAML/CLI merging and streaming behaviors.

### Notes
- These releases consolidate a number of refactors around streaming, configuration, and test hardening. Backwards compatibility is preserved by default configuration values; new behaviors (for example, skipping empty lines) are opt-in via `DsvConfig.skip_empty_lines` or the CLI flag.

### Removed
- **Removed internal file helpers and tests**: The following modules and their associated tests were removed from the `splurge_dsv` library as functionality moved to the `splurge-safe-io` package:
  - `text_file_helper.py`
  - `path_validator.py`
  - `safe_text_file_writer.py`
  - `safe_text_file_reader.py`
  - Associated unit tests for the above modules were removed or migrated to rely on `splurge-safe-io` behavior.
  - **Functionality has been preserved via the `splurge-safe-io` package, and users are encouraged to transition to that package for low-level file I/O and path validation needs.**

> **Note**: v2025.3.0 is a commit-only release and will not be published to PyPI.

## [2025.2.2] - 2025-10-11
### Deprecated
- **Deprecated `SafeTextFileReader`**: The `SafeTextFileReader` class is deprecated and will be removed in a future release. Users are encouraged to transition to the `splurge-safe-io` package for file reading operations.
- **Deprecated `SafeTextFileWriter`**: The `SafeTextFileWriter` class is deprecated and will be removed in a future release. Users are encouraged to transition to the `splurge-safe-io` package for file writing operations.
- **Deprecated `PathValidator`**: The `PathValidator` class is deprecated and will be removed in a future release. Users are encouraged to transition to the `splurge-safe-io` package for path validation functionalities.
- **Deprecated `TextFileHelper`**: The `TextFileHelper` class is deprecated and will be removed in a future release. Users are encouraged to transition to the `splurge-safe-io` package for text file handling functionalities.
### Added
- **New Exception**: Added `SplurgeDsvFileExistsError` to handle file existence errors.
### Fixed
- **Fixed Exception Mapping**: Many errors were incorrectly mapped to `SplurgeDsvEncodingError`; this has been corrected to use appropriate exception types. Some exceptions were not mapped to any `SplurgeDsv*` exception; these have also been corrected.
### Changed
- **3rd-Party Dependency Additions**: Added `splurge-safe-io (v2025.0.4)`.
  - `splurge-safe-io` is a new dependency that provides robust and secure file I/O operations, including safe text file reading and writing with deterministic newline handling and path validation.
  - This change reduces code duplication and improves maintainability by leveraging the functionality of `splurge-safe-io`.
  - Users should refer to the `splurge-safe-io` documentation for details on its usage and features.
- **Code Refactoring**: Refactored `SafeTextFileReader`, `SafeTextFileWriter`, and `PathValidator` to utilize `splurge-safe-io` implementations internally, ensuring consistent behavior and reducing maintenance overhead.
- **Backward Compatibility**: This release maintains backward compatibility for existing users, but users are encouraged to transition to `splurge-safe-io` for future-proofing their codebases.
  - **_This release is a commit-only release and will not be published to PyPI._**

## 2025.2.1 - 2025-10-07
### Deprecated
- **Streaming API rename**: The streaming helpers were renamed to `parse_file_stream()` to better communicate the file-based streaming semantics. Callers should migrate code that used `parse_stream()` to `parse_file_stream()`.

## 2025.3.0 - 2025-10-11
### Removed
- **Removed `parse_stream`**: The legacy `parse_stream()` helpers were removed in this release. Use `parse_file_stream()` on `Dsv`/`DsvHelper` instead. The removal standardizes streaming APIs and avoids ambiguity about the input types accepted by streaming functions.


## 2025.2.0 - 2025-10-06
### Added
- **Comprehensive Property-Based Testing**: Added Hypothesis framework tests for invariant verification
  - `test_string_tokenizer_properties.py`: 6 tests covering parsing consistency and edge cases
  - `test_dsv_helper_properties.py`: 2 tests covering token count preservation and file round-trip
  - `test_path_validator_properties.py`: 10 tests covering path normalization and security validation
  - `test_text_file_helper_properties.py`: 6 tests covering streaming and encoding consistency
- **Malformed Input Testing**: Added comprehensive edge case testing for CSV parsing robustness
  - `test_malformed_csv.py`: 13 tests covering quote handling issues, nested quotes, escaped quotes, and delimiter conflicts
- **Encoding Edge Cases Testing**: Added thorough testing for encoding and BOM handling
  - `test_encoding_edge_cases.py`: 9 tests covering UTF-8/16 sequences, BOM detection, and encoding mismatches
- **Filesystem Edge Cases Testing**: Added testing for file system anomalies and concurrent operations
  - `test_filesystem_edge_cases.py`: 10 tests covering concurrent reads, file modifications during streaming, and permission scenarios
- **Enhanced Test Coverage**: Achieved 94% code coverage with 396 passing tests (11 skipped for platform-specific scenarios)

### Changed
- **Streaming Logic Improvements**: Fixed chunking behavior in `SafeTextFileReader.read_as_stream()` to properly handle small chunk sizes for testing
- **Test Infrastructure**: Updated test expectations and property test constraints to handle edge cases and improve reliability

### Added
- **New DsvConfig dataclass and Dsv class**: Implemented modern, object-oriented API for DSV parsing with configuration encapsulation
  - `DsvConfig`: Frozen dataclass with comprehensive validation for all DSV parsing parameters
  - `Dsv`: Main parsing class that delegates to existing `DsvHelper` while providing configuration reuse
  - Factory methods: `DsvConfig.csv()`, `DsvConfig.tsv()`, and `DsvConfig.from_params()`
  - Type safety, immutability, and backwards compatibility maintained
- **CLI integration**: Refactored CLI to internally use new `Dsv` class while preserving external interface
- **Comprehensive testing**: Added 28 unit tests covering all new functionality with 100% coverage
- **Documentation updates**: Enhanced README-details.md and created modern API examples

### Changed
- CLI now uses `Dsv` class internally for consistency while maintaining backwards compatibility

## 2025.1.5 (Patch) - 2025-09-25
### Changed
- Updated version to 2025.1.5.

## 2025.1.5 - 2025-09-05
### Changed
- Align project with updated GitHub Copilot instructions.

## 2025.1.4 - 2025-09-05
### Changed
- Align project with updated Cursor rules; added detailed research and plan docs.

### Added
- CLI now supports ndjson output format for newline-delimited JSON

## 2025.1.3 - 2025-09-03
### Maintenance & Consistency
- Version alignment and CLI validation improvements.

## 2025.1.2 - 2025-09-02
### Testing
- Added comprehensive end-to-end and integration test coverage.

## 2025.1.1 - 2025-08-25
### Improvements
- Refactors, exception handling consistency, and linting fixes.

## 2025.1.0 - 2025-08-25
### Added
- Initial release with DSV parsing, streaming, path validation, resource management, and robust testing.


