## Action Plan - Implement DsvConfig Dataclass Refactor - 2025-10-05

####### Phase 3: Comprehensive Testing
- [x] Create `tests/unit/test_dsv.py` with complete test coverage:
  - Test `DsvConfig` creation with all parameter combinations
  - Test `DsvConfig` factory methods (`csv()`, `tsv()`, `from_params()`)
  - Test validation errors for invalid configurations
  - Test `Dsv` class instantiation and all parsing methods
  - Test method delegation produces identical results to `DsvHelper`
- [x] Create `tests/integration/test_dsv_integration.py`:
  - Test end-to-end file parsing with various configurations
  - Test streaming functionality
  - Test error handling and propagation
- [x] Run full test suite to ensure no regressions: `pytest tests/ -v`
- [x] Verify coverage: `pytest --cov=splurge_dsv.dsv --cov-report=term-missing`
- [x] Run static analysis: `mypy splurge_dsv/dsv.py`nt a `DsvConfig` dataclass and `Dsv` class to provide a more ergonomic API for DSV parsing, enabling configuration reuse and better type safety while maintaining full backwards compatibility with existing `DsvHelper` static methods.

### Requirements
- Create `splurge_dsv/dsv.py` module with `DsvConfig` frozen dataclass and `Dsv` class
- `DsvConfig` must encapsulate all parsing configuration parameters with validation
- `Dsv` class must provide instance methods that delegate to `DsvHelper` static methods
- Maintain 100% backwards compatibility with existing `DsvHelper` API
- Add convenience factory methods for common configurations (CSV, TSV)
- Include `from_params()` classmethod for migration-friendly parameter filtering
- Update `__init__.py` to export new classes
- Add comprehensive tests covering all new functionality
- Update documentation and examples

### Acceptance Criteria
- [ ] `from splurge_dsv import Dsv, DsvConfig` imports successfully
- [ ] `DsvConfig(delimiter=",")` creates valid configuration object
- [ ] `DsvConfig.csv()` and `DsvConfig.tsv()` factory methods work
- [ ] `DsvConfig.from_params(delimiter=",", invalid_param="ignored")` filters invalid parameters
- [ ] `Dsv(DsvConfig(delimiter=",")).parse_file("test.csv")` produces same output as `DsvHelper.parse_file("test.csv", delimiter=",")`
- [ ] Configuration validation raises appropriate errors for invalid values
- [ ] All existing `DsvHelper` tests still pass (backwards compatibility)
- [ ] New unit tests achieve 85%+ coverage for `dsv.py`
- [ ] Integration tests verify `Dsv` class works with real files
- [ ] Documentation examples show both old and new API usage
- [ ] CLI internally uses `Dsv` class (no breaking changes to CLI interface)

### Testing Strategy
- **Unit Tests** (`tests/unit/test_dsv.py`):
  - `DsvConfig` dataclass creation and validation
  - `DsvConfig` factory methods (`csv()`, `tsv()`, `from_params()`)
  - `Dsv` class instantiation and method delegation
  - Configuration validation edge cases
  - Error handling for invalid configurations
- **Integration Tests** (`tests/integration/test_dsv_integration.py`):
  - End-to-end parsing with `Dsv` class matches `DsvHelper` results
  - File parsing with various configurations
  - Streaming parsing functionality
  - Error propagation from underlying `DsvHelper` methods
- **Backwards Compatibility Tests**:
  - All existing `DsvHelper` tests continue to pass
  - No regressions in CLI functionality
- **Coverage Requirements**:
  - `dsv.py` module: ≥85% coverage
  - Overall project: maintain existing ≥76% coverage

### Implementation Steps

#### Phase 1: Core Module Creation
- [x] Create `splurge_dsv/dsv.py` with proper module docstring and imports
- [x] Implement `DsvConfig` frozen dataclass with all configuration fields:
  - `delimiter: str`
  - `strip: bool = True`
  - `bookend: str | None = None`
  - `bookend_strip: bool = True`
  - `encoding: str = "utf-8"`
  - `skip_header_rows: int = 0`
  - `skip_footer_rows: int = 0`
  - `chunk_size: int = 500`
- [x] Add `__post_init__` validation method for configuration constraints
- [x] Implement `DsvConfig.csv()` classmethod for CSV defaults
- [x] Implement `DsvConfig.tsv()` classmethod for TSV defaults
- [x] Implement `DsvConfig.from_params(**kwargs)` for parameter filtering
- [x] Implement `Dsv` class with `config: DsvConfig` parameter
- [x] Add `Dsv.parse()`, `Dsv.parses()`, `Dsv.parse_file()`, `Dsv.parse_stream()` methods
- [x] Ensure all `Dsv` methods delegate correctly to `DsvHelper` with config

#### Phase 2: Module Integration
- [x] Update `splurge_dsv/__init__.py` to export `Dsv` and `DsvConfig`
- [x] Add type hints and ensure mypy compatibility
- [x] Run `ruff format` and `ruff check --fix` on new module
- [x] Verify imports work: `from splurge_dsv import Dsv, DsvConfig`

#### Phase 3: Comprehensive Testing
- [ ] Create `tests/unit/test_dsv.py` with complete test coverage:
  - Test `DsvConfig` creation with all parameter combinations
  - Test factory methods (`csv()`, `tsv()`, `from_params()`)
  - Test validation errors for invalid configurations
  - Test `Dsv` class instantiation and all parsing methods
  - Test method delegation produces identical results to `DsvHelper`
- [ ] Create `tests/integration/test_dsv_integration.py`:
  - Test end-to-end file parsing with various configurations
  - Test streaming functionality
  - Test error handling and propagation
- [ ] Run full test suite to ensure no regressions: `pytest tests/ -v`
- [ ] Verify coverage: `pytest --cov=splurge_dsv.dsv --cov-report=term-missing`
- [ ] Run static analysis: `mypy splurge_dsv/dsv.py`

#### Phase 4: Documentation and Examples
- [ ] Update `docs/README-details.md` with new API examples
- [ ] Add migration guide showing old vs new API usage
- [ ] Update `examples/api_usage_example.py` to demonstrate `Dsv` class
- [ ] Add docstring examples for all new methods
- [ ] Update any relevant research/specification documents

#### Phase 5: CLI Integration (Optional Enhancement)
- [ ] Refactor `splurge_dsv/cli.py` to use `Dsv` class internally:
  - Replace direct `DsvHelper` calls with `Dsv(DsvConfig.from_params(...))`
  - Ensure CLI interface remains unchanged for users
  - Add tests to verify CLI still works identically
- [ ] Update CLI-related tests if needed

#### Phase 6: Final Validation
- [ ] Run complete test suite: `pytest tests/ --tb=short`
- [ ] Run coverage analysis: `pytest --cov=splurge_dsv --cov-report=html`
- [ ] Run linting: `ruff format && ruff check`
- [ ] Run type checking: `mypy splurge_dsv/`
- [ ] Test both entry points: `splurge-dsv --help` and `python -m splurge_dsv --help`
- [ ] Manual testing with various file formats and configurations
- [ ] Update `CHANGELOG.md` with new feature description

### Risk Mitigation
- **Backwards Compatibility**: Keep all existing `DsvHelper` methods unchanged
- **Incremental Implementation**: Each phase can be tested independently
- **Comprehensive Testing**: Extensive test coverage prevents regressions
- **Type Safety**: Full mypy coverage ensures runtime safety
- **Documentation**: Clear migration path for existing users

### Success Metrics
- ✅ All acceptance criteria met
- ✅ Zero regressions in existing functionality
- ✅ 85%+ test coverage for new code
- ✅ Clean mypy and ruff results
- ✅ Documentation updated with examples
- ✅ Both old and new APIs work seamlessly

### Dependencies
- Python 3.10+ (for dataclass features)
- Existing `DsvHelper` functionality (no changes required)
- All existing test infrastructure

### Timeline Estimate
- Phase 1: 2-3 hours (core implementation)
- Phase 2: 30 minutes (integration)
- Phase 3: 3-4 hours (comprehensive testing)
- Phase 4: 1 hour (documentation)
- Phase 5: 1-2 hours (CLI integration, optional)
- Phase 6: 1 hour (final validation)
- **Total**: 8-11 hours for complete implementation