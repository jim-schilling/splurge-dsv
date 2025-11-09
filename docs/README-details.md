# splurge-dsv — Detailed Documentation

## Overview
**`splurge-dsv`** is a robust Python library for parsing and processing delimited-separated value (DSV) files with an emphasis on security, streaming performance, and clear error handling. It provides a clean public API for programmatic use and a simple CLI for command-line workflows.

## Features

- **Multi-format DSV Support**: Parse CSV, TSV, pipe-delimited, and custom delimiter separated value files/objects
- **Configurable Parsing**: Flexible options for delimiters, quote characters, escape characters, header/footer row(s) handling
- **Memory-Efficient Streaming**: Process large files without loading entire content into memory
- **Security & Validation**: Comprehensive path validation and file permission checks
- **Unicode Support**: Full Unicode character and encoding support
- **Type Safety**: Full type annotations with mypy validation
- **Deterministic Newline Handling**: Consistent handling of CRLF, CR, and LF newlines across platforms
- **CLI Tool**: Command-line interface for quick parsing and inspection of DSV files
- **Robust Error Handling**: Clear and specific exceptions for various error scenarios
- **Modern API**: Object-oriented API with `Dsv` and `DsvConfig` classes for easy configuration and reuse
- **Event Publishing**: Integrated event publishing using `splurge-pub-sub` for monitoring parsing progress and events
- **Comprehensive Documentation**: In-depth API reference and usage examples
- **Exhaustive Testing**: 297 tests with 87% code coverage including property-based testing, edge case testing, and cross-platform compatibility validation

## Architecture
- `splurge_dsv.dsv.DsvConfig`: Immutable configuration dataclass for DSV parsing parameters
- `splurge_dsv.dsv.Dsv`: Modern API class that encapsulates configuration and provides parsing methods
- `splurge_dsv.dsv_helper.DsvHelper`: High-level parsing utilities for strings, lists of strings, files, and streaming.
Note: low-level text/file helpers are provided by `splurge-safe-io` (preferred).
The `Dsv` and `DsvHelper` public APIs cover most file parsing needs.
- `splurge_dsv.string_tokenizer.StringTokenizer`: Core tokenization primitives and bookend handling.
- `splurge_dsv.path_validator.PathValidator`: Security-focused path validation and sanitation helpers.
- `splurge_dsv.exceptions`: Custom exception hierarchy for consistent, descriptive errors.
- `splurge_dsv.cli`: Command-line interface (`python -m splurge_dsv`).

## Installation
```bash
pip install splurge-dsv
```

## CLI Usage
Run the CLI using the module entrypoint:
```bash
python -m splurge_dsv <file_path> --delimiter "," [options]
```

### YAML configuration file (`--config` / `-c`)

The CLI accepts a YAML configuration file that mirrors the available CLI
options and `DsvConfig` fields. When provided, the YAML file is used as
the base configuration and any explicitly supplied CLI flags override the
values in the file.

Example `config.yaml`:

```yaml
delimiter: ","
strip: true
bookend: '"'
encoding: utf-8
skip_header_rows: 1
skip_footer_rows: 0
detect_columns: true
chunk_size: 500
max_detect_chunks: 5
raise_on_missing_columns: false
raise_on_extra_columns: false
```

Example usage:

```bash
# Use YAML file to supply most options, but override delimiter from CLI
python -m splurge_dsv data.csv --config config.yaml --delimiter "|"

# Use YAML file only (CLI can still require some flags like --delimiter depending on file)
python -m splurge_dsv data.csv --config config.yaml
```

Notes:

- The YAML file must contain a top-level mapping/dictionary.
- Keys that do not correspond to `DsvConfig` fields are ignored.
- The CLI will error with a non-zero exit status and a helpful message if the config
	file cannot be read or is invalid.

Supported options (current):
- `--delimiter, -d` Delimiter character (required)
- `--bookend, -b` Bookend character for quoted text fields
- `--no-strip` Disable whitespace stripping
- `--no-bookend-strip` Disable whitespace stripping before bookend removal
- `--encoding, -e` File encoding (default: utf-8)
- `--skip-header` Number of header rows to skip (default: 0) — maps to `DsvConfig.skip_header_rows`
- `--skip-footer` Number of footer rows to skip (default: 0) — maps to `DsvConfig.skip_footer_rows`
- `--stream, -s` Stream file in chunks instead of loading into memory
- `--chunk-size` Chunk size when streaming (default from `DsvHelper.DEFAULT_CHUNK_SIZE`)
- `--detect-columns` Auto-detect the expected column count from the first non-blank logical row and optionally normalize rows
- `--raise-on-missing-columns` Raise on rows with fewer columns than expected
- `--raise-on-extra-columns` Raise on rows with more columns than expected
- `--max-detect-chunks` When detecting columns while streaming, how many initial chunks to inspect
- `--output-format {table,json,ndjson}` Output format (default: table)
- `--version` Show version and exit

Examples:
```bash
# Parse a CSV file
python -m splurge_dsv data.csv --delimiter ,

# Parse a TSV file with bookends
python -m splurge_dsv data.tsv --delimiter "\t" --bookend '"'

# Stream a large file in chunks
python -m splurge_dsv large.csv --delimiter , --stream --chunk-size 1000

# Skip header rows and use custom encoding
python -m splurge_dsv data.csv --delimiter , --skip-header 1 --encoding utf-16

# Parse pipe-delimited data without stripping whitespace
python -m splurge_dsv data.txt --delimiter "|" --no-strip

# Parse a DSV file and normalize rows to detected column count
python -m splurge_dsv maybe-has-metadata.csv --delimiter , --stream --detect-columns
```

## CLI Options Reference

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--delimiter` | `-d` | Field delimiter character | Required |
| `--bookend` | `-b` | Quote character for fields | None |
| `--no-strip` | | Disable whitespace stripping | False |
| `--no-bookend-strip` | | Disable whitespace stripping before bookend removal | False |
| `--encoding` | `-e` | File encoding | utf-8 |
| `--skip-header` | | Number of header rows to skip (maps to DsvConfig.skip_header_rows) | 0 |
| `--skip-footer` | | Number of footer rows to skip (maps to DsvConfig.skip_footer_rows) | 0 |
| `--stream` | `-s` | Stream file in chunks | False |
| `--chunk-size` | | Chunk size for streaming (maps to DsvConfig.chunk_size) | `DsvHelper.DEFAULT_CHUNK_SIZE` |
| `--detect-columns` | | Attempt to auto-detect column count from first non-blank logical row | False |
| `--raise-on-missing-columns` | | Raise on rows with fewer fields than expected | False |
| `--raise-on-extra-columns` | | Raise on rows with more fields than expected | False |
| `--max-detect-chunks` | | For streaming detection, how many initial chunks to inspect | `DsvHelper.MAX_DETECT_CHUNKS` |
| `--output-format` | | Output format | table |
| `--version` | | Show version and exit | |

### CLI examples

Basic parse (print table):

```bash
python -m splurge_dsv data.csv --delimiter ,
```

Stream and process in chunks (streaming, 500 rows per chunk):

```bash
python -m splurge_dsv large.csv --delimiter , --stream --chunk-size 500
```

Detect columns and output NDJSON (useful for piping to other tools):

```bash
python -m splurge_dsv maybe-has-metadata.csv --delimiter , --stream --detect-columns --output-format ndjson
```

Export full JSON array (materializes file; not for very large inputs):

```bash
python -m splurge_dsv data.csv --delimiter , --output-format json
```


## Programmatic Usage


## API Reference Summary
A compact summary of the public API. For complete signatures, examples, and the full exception hierarchy see `docs/api/API-REFERENCE.md`.

Key public symbols (importable from the package root):

- `DsvConfig` — immutable dataclass that captures parsing options (delimiter, bookend, strip, encoding, header/footer skips, chunk size, and column-detection / validation flags). Use `DsvConfig.csv()` or `DsvConfig.tsv()` for common presets.
- `Dsv` — instance-based parser that holds a `DsvConfig` and provides `parse`, `parses`, `parse_file`, and `parse_file_stream` methods. Prefer when reusing a configuration.
- `DsvHelper` — stateless classmethods with the same parsing semantics as `Dsv` (ideal for one-off parsing): `parse`, `parses`, `parse_file`, and `parse_file_stream` (streaming yields chunked lists of rows).
- `StringTokenizer` — low-level, deterministic tokenization primitives (single-row `parse` / multi-row `parses` and `remove_bookends`) used by the higher-level helpers.

File I/O and secure path handling are provided by the `splurge-safe-io` integration (e.g., `SafeTextFileReader` / `open_text`, `SafeTextFileWriter` / `open_text_writer`, and `PathValidator`). `splurge-dsv` maps those errors into its own `SplurgeDsv*` exceptions.

CLI surface: `parse_arguments` and `run_cli` (run as `python -m splurge_dsv`). Important CLI flags map directly to `DsvConfig` fields: `--delimiter`, `--bookend`, `--encoding`, `--stream`, `--chunk-size`, `--skip-header`, `--skip-footer`, `--detect-columns` / `--normalize-columns`, and strict validation flags `--raise-on-missing-columns` / `--raise-on-extra-columns`.

Exceptions: the package exposes a small, practical hierarchy (re-exported from the package root) with `SplurgeDsvError` as the base, plus specialized subclasses for parameter validation, file I/O, decoding/encoding, and column-mismatch errors. Use these to handle specific error categories.

For full signatures, examples (including streaming and column-detection), and migration notes for v2025.3.0 see `docs/api/API-REFERENCE.md`.

### API Examples

Parse a single logical row (in-memory):

```python
from splurge_dsv import Dsv, DsvConfig

cfg = DsvConfig.csv()  # delimiter=',' with sensible defaults
parser = Dsv(cfg)
row = parser.parse('  "Alice, A" ,  30 , "NY"  ', normalize_columns=None)
# -> list[str] with bookends removed and whitespace stripped (by default)
```

Stream-parse a large file in chunks (streaming uses file paths):

```python
from splurge_dsv import Dsv, DsvConfig

cfg = DsvConfig.csv(chunk_size=500, detect_columns=False)
parser = Dsv(cfg)
for chunk in parser.parse_file_stream('big-data.csv'):
	# chunk is a list[list[str]] with up to cfg.chunk_size rows
	process(chunk)
```

Detect columns from the first non-blank logical row and normalize rows:

```python
from splurge_dsv import DsvConfig, Dsv

cfg = DsvConfig.csv(detect_columns=True)
parser = Dsv(cfg)
# When detect_columns=True and normalize_columns not set, the stream
# will inspect initial chunks to determine expected width and then
# replay buffered chunks so the caller receives the full stream.
for chunk in parser.parse_file_stream('maybe-has-metadata.csv'):
	# rows are normalized to the detected column width
	process(chunk)
```

## Versioning
CalVer scheme is used: `YYYY.MINOR.PATCH` (e.g., `2025.3.0`).

## License
MIT License. See `LICENSE`.


