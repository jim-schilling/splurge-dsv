# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and the versioning follows CalVer.

## 2025.2.0 - (Release Date TBD)
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


