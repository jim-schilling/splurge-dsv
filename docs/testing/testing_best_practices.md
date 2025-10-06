# Testing Best Practices Guide

This guide outlines the testing standards and best practices for the splurge-dsv project.

## Testing Philosophy

The splurge-dsv project follows a comprehensive testing approach that combines multiple testing methodologies:

- **Behavior-Driven Development (BDD)**: Tests validate expected behavior, not implementation details
- **Test-Driven Development (TDD)**: Tests are written before or alongside implementation
- **Property-Based Testing**: Uses Hypothesis to test properties across a wide range of inputs
- **Cross-Platform Testing**: Ensures consistent behavior across Windows, Linux, and macOS

## Test Organization

### Directory Structure

```
tests/
├── unit/                    # Unit tests for individual components
├── integration/            # End-to-end workflow tests
├── property/               # Hypothesis property-based tests
├── platform/               # Cross-platform compatibility tests
└── performance/            # Performance and stress tests
```

### Test Naming Conventions

- **Test Files**: `test_[module_name].py` or `test_[feature_description].py`
- **Test Classes**: `Test[ComponentName]` (e.g., `TestDsvHelper`)
- **Test Methods**: `test_[condition]_[expected_result]` (e.g., `test_parse_valid_csv_returns_data`)
- **Property Tests**: `test_[property_name]_property` (e.g., `test_parse_round_trip_property`)

## Testing Standards

### Unit Testing

#### Test Structure
```python
import pytest
from splurge_dsv import DsvHelper

class TestDsvHelper:
    def test_parse_basic_csv_returns_list(self):
        """Test that basic CSV parsing returns a list of tokens."""
        result = DsvHelper.parse("a,b,c", delimiter=",")
        assert result == ["a", "b", "c"]
        assert isinstance(result, list)

    def test_parse_empty_string_returns_empty_list(self):
        """Test that parsing empty string returns empty list."""
        result = DsvHelper.parse("", delimiter=",")
        assert result == []
```

#### Best Practices
- **One Assertion Per Test**: Each test should verify one specific behavior
- **Descriptive Names**: Test names should clearly describe what is being tested
- **Arrange-Act-Assert**: Structure tests with clear setup, execution, and verification phases
- **Test Public APIs Only**: Avoid testing private methods or implementation details
- **Use Fixtures**: Leverage pytest fixtures for common test setup

### Property-Based Testing

#### Using Hypothesis
```python
import pytest
from hypothesis import given, strategies as st
from splurge_dsv import DsvHelper

class TestDsvHelperProperties:
    @given(st.text(min_size=0, max_size=1000))
    def test_parse_round_trip_property(self, input_text):
        """Test that parsing tokenized text returns the original input."""
        # Skip if input contains problematic characters for this test
        if ',' in input_text or '"' in input_text:
            pytest.skip("Skipping input with delimiters or quotes")

        # Tokenize and re-parse
        tokens = DsvHelper.parse(input_text, delimiter="|")
        reconstructed = "|".join(tokens)

        assert reconstructed == input_text
```

#### Property Test Guidelines
- **Clear Property Definition**: Each property test should validate a specific invariant
- **Appropriate Strategies**: Use Hypothesis strategies that generate relevant inputs
- **Skip Invalid Cases**: Use `pytest.skip()` for inputs that don't apply to the property
- **Minimal Examples**: Hypothesis will find minimal failing examples automatically

### Integration Testing

#### End-to-End Testing
```python
import tempfile
from pathlib import Path
from splurge_dsv import Dsv, DsvConfig

class TestEndToEndWorkflows:
    def test_csv_parsing_workflow(self, tmp_path):
        """Test complete CSV parsing workflow from file to processed data."""
        # Create test CSV file
        csv_content = "name,age,city\nJohn,30,NYC\nJane,25,LA\n"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        # Configure and parse
        config = DsvConfig.csv(has_header=True)
        dsv = Dsv(config)
        result = dsv.parse_file(str(csv_file))

        # Verify complete workflow
        assert len(result) == 2
        assert result[0]["name"] == "John"
        assert result[0]["age"] == "30"
        assert result[1]["name"] == "Jane"
```

#### Integration Test Best Practices
- **Real File Operations**: Use actual file I/O rather than mocks where possible
- **Temporary Files**: Use `tmp_path` fixture for test file creation
- **Complete Workflows**: Test end-to-end user scenarios
- **Realistic Data**: Use representative data sizes and formats

### Cross-Platform Testing

#### Platform-Specific Considerations
```python
import os
from splurge_dsv.path_validator import is_safe_path

class TestCrossPlatformCompatibility:
    def test_path_validation_consistency(self):
        """Test that path validation works consistently across platforms."""
        # Safe paths should work everywhere
        safe_paths = [
            "file.csv",
            "subdir/file.csv",
            "data/file.csv"
        ]

        for path in safe_paths:
            assert is_safe_path(path)

        # Unsafe paths should be rejected everywhere
        unsafe_paths = [
            "../file.csv",
            "..\\file.csv",  # Windows-style
            "path/../../../file.csv"
        ]

        for path in unsafe_paths:
            assert not is_safe_path(path)
```

#### Cross-Platform Guidelines
- **Path Handling**: Test both forward and backward slashes
- **Line Endings**: Test CRLF, LF, and mixed line endings
- **Encoding**: Test UTF-8, UTF-16, and platform-specific encodings
- **File Permissions**: Test readable/writable file scenarios

## Mocking and Fixtures

### Modern Mocking with pytest-mock

```python
def test_file_operation_with_mock(self, mocker):
    """Test file operations using pytest-mock."""
    # Mock pathlib.Path operations
    mock_path = mocker.patch('pathlib.Path.exists')
    mock_path.return_value = True

    # Test the functionality
    result = validate_file_path("test.csv")
    assert result is True
```

### Fixture Usage

```python
@pytest.fixture
def sample_csv_data():
    """Fixture providing sample CSV data."""
    return "name,value\nJohn,100\nJane,200"

@pytest.fixture
def temp_csv_file(tmp_path, sample_csv_data):
    """Fixture creating a temporary CSV file."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(sample_csv_data)
    return csv_file

def test_parse_file_with_fixture(temp_csv_file):
    """Test file parsing using fixtures."""
    config = DsvConfig.csv(has_header=True)
    result = Dsv.parse_file(str(temp_csv_file), config)

    assert len(result) == 2
    assert result[0]["name"] == "John"
```

## Test Execution and Quality

### Running Tests

```bash
# Basic test run
pytest tests/

# With coverage
pytest tests/ --cov=splurge_dsv --cov-report=html

# Parallel execution
pytest tests/ -n auto

# Specific test categories
pytest tests/unit/ tests/integration/

# Performance profiling
pytest tests/ --durations=10
```

### Coverage Requirements

- **Overall Coverage**: ≥94%
- **Core Modules**: 100% coverage
- **Public APIs**: 100% coverage
- **Error Paths**: Comprehensive coverage

### Continuous Integration

Tests run automatically on:
- **Pull Requests**: Full test suite with coverage
- **Main Branch**: Extended test suite including performance tests
- **Releases**: Complete validation including cross-platform testing

## Debugging Test Failures

### Common Issues and Solutions

#### Flaky Property Tests
```python
@given(st.text())
def test_some_property(self, input_text):
    # Skip edge cases that don't apply
    if len(input_text) > 1000:
        pytest.skip("Input too large")

    # Use assume() for preconditions
    assume(',' not in input_text)

    # Test the property
    result = process_text(input_text)
    assert some_property(result)
```

#### Platform-Specific Failures
```python
def test_path_handling(self):
    # Handle platform differences
    if os.name == 'nt':  # Windows
        expected_path = "C:\\path\\to\\file.csv"
    else:  # Unix-like
        expected_path = "/path/to/file.csv"

    result = normalize_path(input_path)
    assert result == expected_path
```

## Performance Testing

### Benchmarking
```python
import pytest_benchmark

def test_parse_performance(self, benchmark, large_csv_file):
    """Benchmark CSV parsing performance."""
    config = DsvConfig.csv()

    # Benchmark the parsing operation
    result = benchmark(Dsv.parse_file, str(large_csv_file), config)

    # Verify correctness
    assert len(result) > 0
    assert "name" in result[0]
```

### Performance Guidelines
- **Regression Detection**: Benchmarks prevent performance degradation
- **Memory Usage**: Monitor memory consumption for large files
- **Scalability**: Test with files of increasing size
- **Baseline Comparison**: Compare against established performance baselines

## Contributing to Tests

### Adding New Tests

1. **Identify Test Category**: Determine if test belongs in unit/, integration/, property/, or platform/
2. **Follow Naming Conventions**: Use descriptive, consistent naming
3. **Add Documentation**: Include docstrings explaining test purpose
4. **Verify Coverage**: Ensure new code is adequately tested
5. **Run Full Suite**: Confirm all tests pass before submitting

### Test Maintenance

- **Regular Review**: Periodically review and update test cases
- **Remove Obsolete Tests**: Delete tests for removed functionality
- **Update for API Changes**: Modify tests when APIs change
- **Performance Monitoring**: Track test execution time and optimize slow tests

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [pytest-mock Documentation](https://pytest-mock.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)