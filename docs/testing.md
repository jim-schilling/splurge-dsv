# Testing Guide - splurge-dsv

## Overview

The splurge-dsv project uses a comprehensive testing strategy that combines traditional unit testing with advanced property-based testing and fuzzing. This guide explains our testing approach and how to contribute tests.

## Testing Strategy

### Test Types

1. **Unit Tests** (`tests/unit/`)
   - Test individual functions and classes in isolation
   - Use pytest-mock for dependency mocking
   - Focus on edge cases and error conditions

2. **Integration Tests** (`tests/integration/`)
   - Test component interactions and file I/O
   - End-to-end CLI workflows
   - Real file system operations

3. **Property-Based Tests** (`tests/property/`)
   - Use Hypothesis to generate test inputs automatically
   - Validate mathematical properties and invariants
   - Discover edge cases through automated exploration

4. **Fuzz Tests** (`tests/fuzz/`)
   - Automated input generation to find crashes
   - Random data testing for robustness
   - Crash detection and analysis

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=splurge_dsv --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/property/
```

### Hypothesis Configuration

Property-based tests are configured in `pyproject.toml`:

```toml
[tool.hypothesis]
max_examples = 100
deadline = 5000  # 5 seconds per test
suppress_health_check = ["too_slow"]
verbosity = "normal"
```

### Parallel Execution

Tests run in parallel by default (`-n 4` in pytest configuration). For debugging, run sequentially:

```bash
pytest -n 0  # Disable parallel execution
```

## Writing Tests

### Unit Tests with pytest-mock

**Before (unittest.mock):**
```python
from unittest.mock import patch, MagicMock

def test_example(self):
    with patch('module.function') as mock_func:
        mock_func.return_value = 'mocked'
        # test code
```

**After (pytest-mock):**
```python
def test_example(mocker):
    mock_func = mocker.patch('module.function')
    mock_func.return_value = 'mocked'
    # test code
```

### Property-Based Tests with Hypothesis

```python
import pytest
from hypothesis import given, strategies as st
from tests.conftest import delimiter_strategy, csv_content_strategy

class TestPropertyExample:
    @given(delimiter=delimiter_strategy(), content=csv_content_strategy())
    def test_parsing_consistency(self, delimiter, content):
        """Test that parsing is consistent across multiple calls."""
        from splurge_dsv.dsv_helper import DsvHelper

        result1 = DsvHelper.parse(content, delimiter=delimiter)
        result2 = DsvHelper.parse(content, delimiter=delimiter)

        assert result1 == result2

    @given(content=csv_content_strategy())
    def test_round_trip_parsing(self, content):
        """Test that parsing followed by formatting returns equivalent result."""
        # Property test implementation
        pass
```

### Common Hypothesis Strategies

Available in `tests/conftest.py`:

- `delimiter_strategy()` - Valid delimiter characters
- `quote_strategy()` - Quote characters
- `csv_content_strategy()` - Random CSV content
- `file_path_strategy()` - File path strings
- `dsv_config_strategy()` - DsvConfig instances

## Test Organization

### File Naming Conventions

- Unit tests: `test_{module}.py`
- Integration tests: Descriptive names like `test_cli_json_output.py`
- Property tests: `test_{module}_properties.py`
- Fuzz tests: `test_{module}_fuzz.py`

### Test Class Organization

```python
class TestFeatureGroup:
    """Test cases for specific feature or module."""

    def test_basic_functionality(self):
        """Test basic expected behavior."""
        pass

    def test_edge_case_empty_input(self):
        """Test behavior with empty inputs."""
        pass

    def test_error_condition_invalid_input(self):
        """Test error handling for invalid inputs."""
        pass
```

## Coverage Requirements

- **Overall target**: ≥98% coverage
- **Core modules**: 100% coverage required
- **New features**: Must include comprehensive tests before merge
- **Regression protection**: All tests must pass in CI

### Coverage Exclusions

Some code is intentionally not covered due to:
- Exception handling for rare system conditions
- Debug-only code paths
- Platform-specific code not testable on all platforms

## CI/CD Integration

### GitHub Actions

Tests run automatically on:
- Pull requests
- Pushes to main branch
- Scheduled runs (weekly)

### Coverage Reporting

- Coverage reports generated and uploaded
- Coverage badges updated automatically
- Minimum coverage enforced

## Contributing Tests

### When to Add Tests

1. **New features**: Always include tests with feature implementation
2. **Bug fixes**: Add regression tests for fixed bugs
3. **Refactoring**: Ensure existing tests still pass
4. **Edge cases**: When discovering new edge cases in production

### Test Quality Guidelines

1. **Descriptive names**: Test names should explain what they're testing
2. **Single responsibility**: Each test should verify one behavior
3. **Independent**: Tests should not depend on each other
4. **Fast**: Tests should complete quickly (< 5 seconds each)
5. **Deterministic**: Tests should produce consistent results

### Property-Based Testing Guidelines

1. **Clear properties**: Each property test should validate a clear invariant
2. **Minimal examples**: Use `@example` decorators for known edge cases
3. **Appropriate scopes**: Use different strategies for different test scopes
4. **Performance**: Balance thoroughness with execution time

## Debugging Test Failures

### Common Issues

1. **Flaky tests**: Use `--tb=short` for cleaner output
2. **Hypothesis failures**: Look for minimal failing examples
3. **Mock issues**: Verify mock targets and return values
4. **Parallel execution**: Run with `-n 0` to isolate issues

### Debugging Commands

```bash
# Run single failing test
pytest tests/unit/test_specific.py::TestClass::test_method -v

# Run with hypothesis verbose output
pytest tests/property/ -v --hypothesis-verbosity=verbose

# Run with coverage for specific module
pytest tests/unit/test_module.py --cov=splurge_dsv.module --cov-report=term-missing
```

## Advanced Topics

### Custom Hypothesis Strategies

Create domain-specific strategies for your tests:

```python
@st.composite
def custom_strategy(draw):
    """Generate custom test data."""
    # Strategy implementation
    pass
```

### Test Fixtures

Use fixtures for common test setup:

```python
@pytest.fixture
def sample_data():
    """Provide sample test data."""
    return {"key": "value"}

def test_using_fixture(sample_data):
    assert sample_data["key"] == "value"
```

### Parametrized Tests

Test multiple scenarios with one function:

```python
@pytest.mark.parametrize("input,expected", [
    ("a,b,c", ["a", "b", "c"]),
    ("x,y,z", ["x", "y", "z"]),
])
def test_parsing(input, expected):
    result = parse(input)
    assert result == expected
```

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [pytest-mock Documentation](https://pytest-mock.readthedocs.io/)
- [Testing Best Practices](docs/research/research-testing-review-2025-10-05.md)