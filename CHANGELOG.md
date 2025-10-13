# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and the versioning follows CalVer.

## [2025.3.0] - 2025-10-11


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


