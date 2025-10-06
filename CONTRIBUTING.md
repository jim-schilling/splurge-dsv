# Contributing to splurge-dsv

Thank you for your interest in contributing to splurge-dsv! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Standards](#testing-standards)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. By participating, you agree to:

- Be respectful and inclusive
- Focus on constructive feedback
- Accept responsibility for mistakes
- Show empathy towards other contributors
- Help create a positive community

## Getting Started

### Prerequisites

- Python 3.10 or later
- Git
- Familiarity with pytest, Hypothesis, and modern Python development

### Development Setup

1. **Fork and Clone** the repository:
   ```bash
   git clone https://github.com/your-username/splurge-dsv.git
   cd splurge-dsv
   ```

2. **Set up the development environment**:
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install development dependencies
   pip install -e ".[dev,test]"
   ```

3. **Verify setup**:
   ```bash
   # Run tests to ensure everything works
   pytest tests/ -v

   # Check code quality
   ruff check .
   mypy splurge_dsv/
   ```

## Development Workflow

### Branching Strategy

- **main**: Production-ready code
- **release/v*.*.***: Release branches for specific versions
- **feature/**: New features (e.g., `feature/add-csv-validation`)
- **bugfix/**: Bug fixes (e.g., `bugfix/fix-encoding-issue`)
- **hotfix/**: Critical fixes for production

### Commit Guidelines

Follow conventional commit format:

```bash
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/modifications
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(parser): add support for custom quote characters
fix(validator): resolve path traversal vulnerability
test(helper): add property tests for text processing
docs(api): update CLI usage examples
```

### Pre-commit Hooks

The project uses pre-commit hooks for code quality:

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Coding Standards

### Python Standards

- **PEP 8 Compliance**: Follow PEP 8 style guidelines
- **Type Annotations**: Use type hints for all function signatures
- **Google-Style Docstrings**: Document all public functions and classes
- **Modern Python**: Target Python 3.10+ features (e.g., `|` for unions)

### Code Quality Tools

```bash
# Linting and formatting
ruff check .                    # Lint code
ruff format .                   # Format code

# Type checking
mypy splurge_dsv/               # Type validation

# Security scanning
ruff check --select S .         # Security checks
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `DsvHelper`, `PathValidator`)
- **Functions/Methods**: `snake_case` (e.g., `parse_file`, `validate_path`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_DELIMITER`)
- **Modules**: `snake_case` (e.g., `dsv_helper.py`)

### Error Handling

- **Custom Exceptions**: Use domain-specific exceptions from `splurge_dsv.exceptions`
- **Descriptive Messages**: Provide clear, actionable error messages
- **Fail Fast**: Validate inputs early and raise appropriate exceptions

## Testing Standards

### Test Organization

```
tests/
├── unit/                    # Unit tests (300+ tests)
├── integration/            # End-to-end tests (50+ tests)
├── property/               # Hypothesis tests (50+ tests)
├── platform/               # Cross-platform tests
└── performance/            # Performance benchmarks
```

### Testing Requirements

- **94%+ Coverage**: All public APIs must be tested
- **Property-Based Testing**: Use Hypothesis for complex scenarios
- **Cross-Platform**: Tests must pass on Windows, Linux, and macOS
- **Edge Cases**: Comprehensive testing of error conditions

### Writing Tests

#### Unit Tests
```python
import pytest
from splurge_dsv import DsvHelper

class TestDsvHelper:
    def test_parse_basic_csv(self):
        """Test basic CSV parsing functionality."""
        result = DsvHelper.parse("a,b,c", delimiter=",")
        assert result == ["a", "b", "c"]
        assert isinstance(result, list)
```

#### Property Tests
```python
from hypothesis import given, strategies as st

class TestDsvHelperProperties:
    @given(st.text(min_size=0, max_size=500))
    def test_parse_consistency(self, input_text):
        """Test that parsing is consistent for same input."""
        result1 = DsvHelper.parse(input_text, delimiter="|")
        result2 = DsvHelper.parse(input_text, delimiter="|")
        assert result1 == result2
```

#### Integration Tests
```python
def test_end_to_end_workflow(self, tmp_path):
    """Test complete workflow from file to processed data."""
    # Create test file
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("name,value\nJohn,100\nJane,200")

    # Test complete workflow
    config = DsvConfig.csv(has_header=True)
    result = Dsv.parse_file(str(csv_file), config)

    assert len(result) == 2
    assert result[0]["name"] == "John"
```

### Running Tests

```bash
# Full test suite
pytest tests/ --cov=splurge_dsv --cov-report=html

# Specific categories
pytest tests/unit/ -v
pytest tests/property/ -v
pytest tests/integration/ -v

# With parallel execution
pytest tests/ -n auto

# Performance testing
pytest tests/ --durations=10
```

## Documentation

### Documentation Standards

- **README.md**: Project overview, installation, quick start
- **docs/**: Detailed documentation, API reference, guides
- **Code Comments**: Explain complex logic, not obvious behavior
- **Type Hints**: Serve as documentation for function signatures

### Documentation Files

- **docs/README-details.md**: Complete API reference and examples
- **docs/testing_best_practices.md**: Testing guidelines and patterns
- **docs/hypothesis_usage_patterns.md**: Property-based testing guide
- **CHANGELOG.md**: Release notes and migration guides

### Updating Documentation

When making changes:

1. Update relevant documentation files
2. Add examples for new features
3. Update API documentation for signature changes
4. Test documentation examples

## Pull Request Process

### Before Submitting

1. **Run Full Test Suite**:
   ```bash
   pytest tests/ --cov=splurge_dsv
   ruff check .
   mypy splurge_dsv/
   ```

2. **Update Documentation**: Ensure docs reflect your changes

3. **Check Coverage**: Maintain or improve code coverage

4. **Test Cross-Platform**: Verify on multiple platforms if possible

### PR Template

Use the following template for pull requests:

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Property tests added/updated
- [ ] Cross-platform tests verified
- [ ] Coverage maintained/improved

## Documentation
- [ ] README updated
- [ ] API docs updated
- [ ] Examples added/updated

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Commit messages follow conventions
```

### Review Process

1. **Automated Checks**: CI runs tests, linting, and coverage
2. **Peer Review**: At least one maintainer reviews the code
3. **Approval**: PR approved and merged by maintainer
4. **Release**: Changes included in next release

## Reporting Issues

### Bug Reports

Use the issue template for bug reports:

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Windows 10, Ubuntu 20.04]
- Python version: [e.g., 3.11.0]
- splurge-dsv version: [e.g., 2025.2.0]

## Additional Context
Any other relevant information
```

### Feature Requests

Use the issue template for feature requests:

```markdown
## Feature Summary
Brief description of the feature

## Problem Statement
What problem does this solve?

## Proposed Solution
How should it work?

## Alternative Solutions
Other approaches considered

## Additional Context
Mockups, examples, or references
```

## Recognition

Contributors are recognized in:
- **CHANGELOG.md**: Release notes
- **Git History**: Commit attribution
- **GitHub Contributors**: Repository contributor statistics

## Getting Help

- **Issues**: Use GitHub issues for bugs and features
- **Discussions**: Use GitHub discussions for questions
- **Documentation**: Check docs/ for detailed guides
- **Code**: Read the source code and tests for examples

Thank you for contributing to splurge-dsv! 🎉