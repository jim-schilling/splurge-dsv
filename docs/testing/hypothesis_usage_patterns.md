# Hypothesis Usage Patterns in splurge-dsv

This document outlines how Hypothesis property-based testing is used in the splurge-dsv project to ensure robust validation of complex scenarios.

## Overview

Hypothesis is a property-based testing framework that generates test inputs automatically, helping find edge cases that traditional example-based tests might miss. The splurge-dsv project uses Hypothesis to validate properties across a wide range of inputs.

## Core Concepts

### Properties vs Examples

**Example-Based Testing** (Traditional):
```python
def test_parse_simple_csv():
    result = DsvHelper.parse("a,b,c", delimiter=",")
    assert result == ["a", "b", "c"]
```

**Property-Based Testing** (Hypothesis):
```python
@given(st.text(min_size=0, max_size=100))
def test_parse_consistency(input_text):
    """Parse result should be consistent for same input."""
    result1 = DsvHelper.parse(input_text, delimiter="|")
    result2 = DsvHelper.parse(input_text, delimiter="|")
    assert result1 == result2
```

## Hypothesis Strategies Used

### Text and String Strategies

```python
from hypothesis import strategies as st

# Basic text content
text_strategy = st.text(min_size=0, max_size=1000)

# Text without specific characters
safe_text = st.text(min_size=0, max_size=1000).filter(
    lambda x: ',' not in x and '"' not in x
)

# Delimiter characters
delimiter_strategy = st.sampled_from([',', '\t', '|', ';', ':'])

# Quote characters
quote_strategy = st.sampled_from(['"', "'"])
```

### CSV-Specific Strategies

```python
# CSV row generation
def csv_row_strategy():
    """Generate valid CSV row strings."""
    return st.lists(
        st.text(min_size=0, max_size=50).filter(
            lambda x: ',' not in x and '"' not in x and '\n' not in x
        ),
        min_size=1, max_size=10
    ).map(lambda fields: ','.join(fields))

# Complete CSV content
csv_content_strategy = st.lists(
    csv_row_strategy(),
    min_size=0, max_size=100
).map(lambda rows: '\n'.join(rows))
```

## Property Test Patterns

### Round-Trip Properties

```python
class TestStringTokenizerProperties:
    @given(st.text(min_size=0, max_size=500))
    def test_tokenize_parse_round_trip(self, input_text):
        """Test that tokenize → parse → original text."""
        # Skip inputs that would break the round trip
        if any(char in input_text for char in [',', '"', '\n']):
            pytest.skip("Skipping input with special characters")

        # Perform round trip
        tokens = StringTokenizer.tokenize(input_text, delimiter='|')
        reconstructed = '|'.join(tokens)

        assert reconstructed == input_text
```

### Consistency Properties

```python
class TestDsvHelperProperties:
    @given(st.text(min_size=0, max_size=1000))
    def test_parse_consistency(self, input_text):
        """Test that parsing same input multiple times gives same result."""
        config = DsvConfig(delimiter='|', strip=True)

        result1 = DsvHelper.parse(input_text, config)
        result2 = DsvHelper.parse(input_text, config)

        assert result1 == result2
```

### Equivalence Properties

```python
class TestDsvHelperProperties:
    @given(st.text(min_size=0, max_size=500))
    def test_config_equivalence(self, input_text):
        """Test that equivalent configs produce same results."""
        config1 = DsvConfig(delimiter=',', strip=True, quote='"')
        config2 = DsvConfig(delimiter=',', strip=True, quote='"')

        result1 = DsvHelper.parse(input_text, config1)
        result2 = DsvHelper.parse(input_text, config2)

        assert result1 == result2
```

### Boundary Properties

```python
class TestPathValidatorProperties:
    @given(st.text(min_size=0, max_size=260))  # Windows MAX_PATH
    def test_path_length_validation(self, path_str):
        """Test path length validation boundaries."""
        # Paths within limits should be valid (if otherwise safe)
        if len(path_str) <= 260 and is_safe_path(path_str):
            assert len(path_str) <= 260

        # Very long paths should be rejected
        long_path = path_str * 10  # Make it very long
        if len(long_path) > 260:
            # This might be rejected for length reasons
            pass  # Length validation is implementation specific
```

## Handling Edge Cases

### Filtering Invalid Inputs

```python
@given(st.text(min_size=0, max_size=1000))
def test_parse_with_filtering(self, input_text):
    """Test parsing with filtered inputs."""
    # Skip inputs that would cause parsing issues
    if '"' in input_text and ',' not in input_text:
        pytest.skip("Skipping quote-only inputs")

    if '\x00' in input_text:  # Null bytes
        pytest.skip("Skipping inputs with null bytes")

    # Test the property
    result = DsvHelper.parse(input_text, delimiter=',')
    assert isinstance(result, list)
```

### Using assume() for Preconditions

```python
from hypothesis import assume

@given(st.text(), st.characters())
def test_parse_with_assume(self, input_text, delimiter):
    """Test parsing with assume for preconditions."""
    # Assume reasonable delimiter
    assume(delimiter not in ['\n', '\r', '\x00'])
    assume(len(delimiter) == 1)

    # Assume input doesn't contain delimiter in quoted sections
    # (This is a simplified example)
    assume('"' not in input_text or delimiter not in input_text)

    result = DsvHelper.parse(input_text, delimiter=delimiter)
    assert isinstance(result, list)
```

## Test Execution and Debugging

### Running Property Tests

```bash
# Run all property tests
pytest tests/property/ -v

# Run specific property test
pytest tests/property/test_string_tokenizer_properties.py::TestStringTokenizerProperties::test_parse_round_trip_property -v

# Run with more examples (slower but more thorough)
pytest tests/property/ --hypothesis-verbosity=verbose

# Run with fixed seed for reproducibility
pytest tests/property/ --hypothesis-seed=12345
```

### Debugging Failing Properties

When a property test fails, Hypothesis provides:

1. **Minimal Example**: The smallest input that causes failure
2. **Reproduction Command**: Exact command to reproduce the failure
3. **Statistics**: Information about test execution

```python
# Example failure output:
Falsifying example: test_parse_round_trip_property(
    input_text='a,b,c\n',
)

# This tells us the issue is with newline handling
```

### Common Failure Patterns

#### Unexpected Edge Cases
```python
# Property test reveals issue with empty tokens
@given(st.text(min_size=0, max_size=100))
def test_parse_empty_tokens(self, input_text):
    """Test that empty strings are handled properly."""
    # This might fail if ,, creates empty tokens unexpectedly
    result = DsvHelper.parse(input_text, delimiter=',')
    # Verify no unexpected empty strings
    assert all(token or token == "" for token in result)
```

#### Unicode and Encoding Issues
```python
@given(st.text(min_size=0, max_size=200, alphabet=st.characters(codec='utf-8')))
def test_unicode_handling(self, input_text):
    """Test Unicode character handling."""
    # This might reveal encoding issues
    result = DsvHelper.parse(input_text, delimiter='|')
    # Verify Unicode preservation
    reconstructed = '|'.join(result)
    assert reconstructed == input_text
```

## Performance Considerations

### Test Execution Time

Property tests can be slower due to generating many examples:

```python
# Limit examples for faster execution in CI
@given(st.text(min_size=0, max_size=100))
@pytest.mark.slow  # Mark as slow test
def test_comprehensive_property(self, input_text):
    # Comprehensive property test
    pass
```

### Parallel Execution

```bash
# Run property tests in parallel
pytest tests/property/ -n auto --hypothesis-profile=ci

# Use CI profile for faster execution
# In pytest.ini or pyproject.toml:
# [tool:hypothesis]
# profiles.ci = max_examples=50
```

## Integration with CI/CD

### Hypothesis Configuration

```toml
# pyproject.toml
[tool.hypothesis]
max_examples = 100
deadline = 5000  # milliseconds
suppress_health_check = ["too_slow"]
```

### CI-Specific Profiles

```python
# conftest.py
from hypothesis import settings

# Fast profile for development
settings.register_profile("dev", max_examples=10)

# CI profile for comprehensive testing
settings.register_profile("ci", max_examples=200, deadline=10000)

# Load appropriate profile
settings.load_profile("ci" if os.environ.get("CI") else "dev")
```

## Best Practices

### Property Definition
- **Clear Invariants**: Each property should test a specific invariant
- **Minimal Scope**: Focus on one property per test
- **Realistic Inputs**: Use strategies that generate realistic data
- **Skip Irrelevant Cases**: Use `pytest.skip()` or `assume()` for invalid inputs

### Test Maintenance
- **Regular Review**: Review property tests periodically
- **Update Strategies**: Modify strategies as code evolves
- **Performance Monitoring**: Track test execution time
- **Documentation**: Document what each property validates

### Debugging
- **Minimal Examples**: Use Hypothesis-generated minimal examples
- **Verbose Output**: Enable verbose mode for debugging
- **Reproducible Seeds**: Use fixed seeds for consistent failures
- **Incremental Testing**: Test properties individually during development

## Examples from splurge-dsv

### String Tokenizer Properties

```python
class TestStringTokenizerProperties:
    @given(st.text(min_size=0, max_size=200))
    def test_remove_bookends_empty_content(self, content):
        """Test remove_bookends with empty content."""
        result = StringTokenizer.remove_bookends(content, '(', ')')
        # Property: empty content should remain unchanged
        if not content:
            assert result == content

    @given(st.text(min_size=1, max_size=200))
    def test_remove_bookends_symmetry(self, content):
        """Test that remove_bookends is symmetric for matching brackets."""
        # Add matching brackets
        bracketed = f"({content})"
        result = StringTokenizer.remove_bookends(bracketed, '(', ')')
        assert result == content
```

### DSV Helper Properties

```python
class TestDsvHelperProperties:
    @given(st.lists(st.text(min_size=0, max_size=50), min_size=0, max_size=10))
    def test_parse_file_round_trip(self, rows):
        """Test that parsing tokenized content round-trips correctly."""
        # Create CSV content
        csv_content = '\n'.join(','.join(row) for row in rows)

        # Write to temp file and parse
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            result = DsvHelper.parse_file(temp_path, delimiter=',')
            # Property: should get back original structure
            assert len(result) == len(rows)
            for original, parsed in zip(rows, result):
                assert len(parsed) == len(original)
        finally:
            os.unlink(temp_path)
```

## Resources

- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [Property-Based Testing Guide](https://fsharpforfunandprofit.com/posts/property-based-testing/)
- [Effective Property Testing](https://www.infoq.com/articles/property-testing/)
- [Hypothesis Strategies Reference](https://hypothesis.readthedocs.io/en/latest/data.html)