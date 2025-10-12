# Splurge DSV — API Reference

This document provides a comprehensive reference for the public API exposed by
splurge-dsv. It focuses on the primary classes, helper functions, and the
exception mapping used across the library. Each entry contains a short
reference, examples, and expected errors.

> Note: This reference documents the current stable public API in the
> `release/2025.2.0` branch. For the most up-to-date docs consult the
> module-level docstrings or the package README.

---

## Table of contents

- Overview
- Configuration
  - `DsvConfig`
- Core parser
  - `Dsv`
  - `DsvHelper`
- File helpers
  - `StringTokenizer`
  - `SafeTextFileReader` / `open_text`
  - `SafeTextFileWriter` / `open_text_writer`
- Tokenization
  - `StringTokenizer`
- Path validation
  - `PathValidator`
- CLI
  - `run_cli` and `parse_arguments`
- Exceptions and Error Mapping
- Examples
  - Quick API examples
  - Streaming large files
  - Handling encodings and newline policy

---

## Overview

Splurge DSV provides a thin, typed API for parsing delimited string value
(DSV) content. The library focuses on:

- Deterministic newline normalization across platforms.
- Memory-efficient streaming parsers.
- Clear, centralized exception types to make error handling straightforward.
- Small, well-typed building blocks that can be used as library or CLI.

All public APIs in this document are exposed from the package root and are
importable using:

```python
from splurge_dsv import Dsv, DsvConfig, DsvHelper
from splurge_dsv import StringTokenizer
```

---

## Configuration

### DsvConfig

DsvConfig is a dataclass used to describe parsing configuration (delimiter,
bookend, skip header rows, etc.). Typical factory helpers are provided such as
`DsvConfig.csv()` and `DsvConfig.tsv()`.

Fields (high-level):

- `delimiter: str` — Field delimiter, e.g. `,` or `\t`.
- `bookend: str | None` — Optional field bookend, e.g. `"`.
- `skip_header_rows: int` — Number of header rows to skip when parsing files.
- `skip_footer_rows: int` — Number of footer rows to skip when parsing files.
- `encoding: str` — File encoding to use for file-based parsers.

Example:

```python
from splurge_dsv import DsvConfig

cfg = DsvConfig.csv(skip_header_rows=1)
```

Error modes:

- Invalid parameters raise `SplurgeDsvParameterError` (for example when the
  delimiter is empty).

---

## Core parser

### Dsv

`Dsv` is a small, stateful wrapper around the parsing helpers. You typically
instantiate a `Dsv` with a `DsvConfig` and call `parse`, `parse_file`, or
`parse_file_stream`.

> Note: `parse_stream()` remains available for backward compatibility but is
> deprecated and will emit a DeprecationWarning; prefer `parse_file_stream()`.

API surface (abridged):

- `Dsv(config: DsvConfig)` — Create a parser instance.
- `parse(text: str) -> list[str]` — Parse a single line.
- `parse_file(path: str, ...) -> list[list[str]]` — Parse an entire file.
- `parse_stream(path: str, ...) -> Iterator[list[list[str]]]` — Stream-parse a
  file in chunks.
 - `parse_file_stream(path: str, ...) -> Iterator[list[list[str]]]` — Preferred stream-parse method; yields parsed chunks and aligns naming with `parse_file()`.

> Deprecated: `parse_stream()` is deprecated. Use `parse_file_stream()` instead.
> `parse_stream()` will emit a DeprecationWarning when called and will be
> removed in a future release. See `parse_file_stream()` below for the
> preferred API.

Example — parse a file with headers:

```python
from splurge_dsv import Dsv, DsvConfig

cfg = DsvConfig.csv(skip_header_rows=1)
parser = Dsv(cfg)
rows = parser.parse_file("data.csv")
```

Error handling:

- File access errors raise `SplurgeDsvFileNotFoundError` or
  `SplurgeDsvFilePermissionError`.
- Encoding issues raise `SplurgeDsvFileEncodingError`.

### DsvHelper

`DsvHelper` provides lightweight stateless helpers for parsing when you
prefer not to instantiate `Dsv`.

Key methods:

- `DsvHelper.parse(content: str, *, delimiter: str, bookend: str|None = None, strip: bool=True) -> list[str]`
- `DsvHelper.parses(content: list[str], *, delimiter: str, ...) -> list[list[str]]`
- `DsvHelper.parse_file(file_path: str, *, delimiter: str, encoding: str='utf-8', ...) -> list[list[str]]`
 - `DsvHelper.parse_stream(file_path: str, *, delimiter: str, chunk_size: int=500, ...) -> Iterator[list[list[str]]]`
   
   Deprecated: `DsvHelper.parse_stream()` will emit a DeprecationWarning and
   delegates to `DsvHelper.parse_file_stream()`. Use `parse_file_stream()` for
   a clearer name and consistent error handling across the API.

 - `DsvHelper.parse_file_stream(file_path: str, *, delimiter: str, chunk_size: int=500, ...) -> Iterator[list[list[str]]]` — Preferred streaming API. Yields parsed chunks of rows read from the file. Parameters and behavior match `parse_stream()` but with a clearer name that aligns with `parse_file()`.

Example — parse streaming file in chunks:

```python
from splurge_dsv import DsvHelper

for chunk in DsvHelper.parse_file_stream("big.csv", delimiter=","):
    for row in chunk:
        process(row)
```

---

## File helpers

### File readers

Reading and streaming text files is provided by the separate dependency
`splurge-safe-io` (the package exposes `SafeTextFileReader`, `open_text`,
and related helpers). `DsvHelper` uses these readers internally; callers
should prefer the high-level `Dsv`/`DsvHelper` APIs unless they need the
lower-level reader primitives directly.

### SafeTextFileReader / open_text

A robust reader that centralizes newline normalization, encoding handling and
streaming behavior. Preferred for reading files in library code.

Key usage:

```python
from splurge_dsv.safe_text_file_reader import SafeTextFileReader, open_text

with open_text("data.csv", encoding="utf-8") as reader:
    lines = reader.read()
```

Raises the same file/access/encoding exceptions described in the Exceptions
section below.

### SafeTextFileWriter / open_text_writer

Utility writer that normalizes newlines to LF and exposes an in-memory writer
that can be flushed to disk.

Example:

```python
from splurge_dsv.safe_text_file_writer import open_text_writer

with open_text_writer("out.csv", encoding="utf-8") as writer:
    writer.write("a,b,c\n")
```

---

## Tokenization

### StringTokenizer

Provides tokenization helpers used by higher-level parsers.

API summary:

- `StringTokenizer.parse(content: str|None, *, delimiter: str, strip: bool=True) -> list[str]`
- `StringTokenizer.parses(content: list[str], *, delimiter: str, strip: bool=True) -> list[list[str]]`
- `StringTokenizer.remove_bookends(content: str, *, bookend: str, strip: bool=True) -> str`

Notes:

- `parse` preserves empty tokens (e.g. "a,,c" -> ["a", "", "c"]).
- `remove_bookends` removes symmetric bookend characters when present.

Example:

```python
from splurge_dsv import StringTokenizer

StringTokenizer.parse('a,b,c', delimiter=',')
```

---

## Path validation

Path validation and secure path utilities are provided by the `splurge-safe-io`
dependency; callers can use `splurge_safe_io.path_validator.PathValidator` for
consistent behavior in application code. The library maps path validation
errors from that dependency into `SplurgeDsvPathValidationError`.

---

## CLI

The CLI is implemented in `splurge_dsv.cli` and exposed via
`python -m splurge_dsv`.

Key functions:

- `parse_arguments(argv: list[str] | None = None) -> Namespace` — Parse CLI
  flags into configuration.
- `run_cli(argv: list[str] | None = None) -> int` — Run the CLI and return
  exit code.

Example:

```bash
python -m splurge_dsv data.csv --delimiter , --stream --chunk-size 1000
```

---

## Exceptions and Error Mapping

This project centralizes exceptions under `splurge_dsv.exceptions`. Common
errors and how to handle them:

- `SplurgeDsvError` — Base class for all package errors.
- `SplurgeDsvParameterError` — Invalid function parameter (e.g. empty
  delimiter).
- `SplurgeDsvFileNotFoundError` — File not found.
- `SplurgeDsvFilePermissionError` — File cannot be read/written due to
  permissions.
- `SplurgeDsvFileDecodingError` — File decoding / encoding issues.
- `SplurgeDsvPathValidationError` — Path validation failed (unsafe path,
  traversal attempts, etc.).
- `SplurgeDsvParsingError` — Generic parsing failure.
- `SplurgeDsvColumnMismatchError` — When a row has a different number of columns than expected.
- `SplurgeDsvStreamingError` — Errors while streaming large files.

Handling pattern:

```python
from splurge_dsv import SplurgeDsvFileNotFoundError, SplurgeDsvParameterError

try:
    rows = DsvHelper.parse_file("data.csv", delimiter=",")
except SplurgeDsvFileNotFoundError:
    # Handle missing file
    ...
except SplurgeDsvParameterError as exc:
    # Validate config and report to user
    ...
```

---

## Examples

### Quick API examples

Parse a CSV string:

```python
from splurge_dsv import DsvHelper

print(DsvHelper.parse("a,b,c", delimiter=","))
# ['a', 'b', 'c']
```

Parse a CSV file with header skip:

```python
from splurge_dsv import Dsv, DsvConfig

cfg = DsvConfig.csv(skip_header_rows=1)
parser = Dsv(cfg)
rows = parser.parse_file("data.csv")
```

### Streaming large files

```python
from splurge_dsv import DsvHelper

for chunk in DsvHelper.parse_file_stream("big.csv", delimiter=","):
    for row in chunk:
        # process row
        pass
```

### Handling encodings and newline policy

- Use `encoding` parameters to set the expected file encoding.
- The library normalizes line endings to LF when reading and writing.

---

## Reference: quick lookup

- Public classes: `Dsv`, `DsvConfig`, `DsvHelper`, `TextFileHelper`,
  `StringTokenizer`, `PathValidator`.
- Exceptions: All `SplurgeDsv*` exceptions live in
  `splurge_dsv.exceptions`.

---
