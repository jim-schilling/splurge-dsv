# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and the versioning follows CalVer.

## 2025.2.1 - 2025-10-07
### Deprecated
- **Deprecated `parse_stream` API**: `Dsv.parse_stream()` and `DsvHelper.parse_stream()` now emit a deprecation warning and will be removed in a future release. Use the new `parse_file_stream()` method on `Dsv`/`DsvHelper` instead for stream-based parsing of files (preserves chunked/streaming behavior). This change was made to standardize the naming and make the streaming API surface consistent across helpers and the `Dsv` class.


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


