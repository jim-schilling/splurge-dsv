# Installation

## Requirements

- Python 3.10 or later
- pip (for package installation)

## Installation Methods

### From PyPI (Recommended)

```bash
pip install splurge-dsv
```

### From Source

1. Clone the repository:
```bash
git clone https://github.com/jim-schilling/splurge-dsv.git
cd splurge-dsv
```

2. Install in development mode:
```bash
pip install -e .
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

## Development Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install pre-commit hooks (optional):
```bash
pre-commit install
```

## Verification

After installation, you can verify it works by running:

```python
import splurge_dsv
print(splurge_dsv.__version__)
```

Or test the command-line interface:

```bash
python -m splurge_dsv --help
```
