# Splurge DSV — API Reference

This document provides a concise reference for the public API exposed by
splurge-dsv. It focuses on the primary classes, helpers, CLI surface, and
the package's exception hierarchy. Use the module docstrings for the most
up-to-date, detailed explanations.

---

## Table of contents

- Overview
- Configuration
  - `DsvConfig`
- Core parser
  - `Dsv`
  - `DsvHelper`
- File & token helpers
  - `StringTokenizer`
- CLI
  - `parse_arguments` and `run_cli`
- Exceptions and Error Mapping
- Examples
  - Quick API examples
  - Streaming large files
  - Handling encodings and newline policy

---

## Overview

Splurge DSV provides a compact, well-typed API for parsing delimited string
value (DSV) content. The library emphasizes:

- deterministic newline normalization across platforms,
- memory-efficient streaming parsing with small in-memory buffers,
- a clear package-level exception hierarchy so callers can handle specific
  error categories, and
- small, composable utilities that are useful both programmatically and via
  the bundled CLI.

Public API objects are exported from the package root and can be imported as:

```python
from splurge_dsv import Dsv, DsvConfig, DsvHelper, StringTokenizer

## Table of contents

- Overview
- Package exports
- Configuration: `DsvConfig`
- Core parser: `Dsv` and `DsvHelper`
- Tokenization: `StringTokenizer`
- File & I/O helpers (integration notes)
- CLI reference: options / behavior
- Exceptions: full list and descriptions
- Examples
- Migration notes (2025.3.0)

---

## Overview

This reference documents the public API exported by the `splurge_dsv` package.
It is organized module-by-module and provides concise signatures, parameter
descriptions, return values, and the exceptions raised by each public
construct.

Importing the common public symbols:

```python
from splurge_dsv import (
    Dsv,
    DsvConfig,
    DsvHelper,
    StringTokenizer,
    PubSubSolo,
    # exceptions
    SplurgeDsvError,
    SplurgeDsvColumnMismatchError,
)
```

Note: lower-level file reading and path validation functionality is provided
by the `splurge-safe-io` dependency and is referenced where appropriate.

### Event Publishing and Correlation IDs

Splurge DSV integrates **event-driven architecture** through `PubSubSolo`, a
lightweight in-memory publish-subscribe system. Each parsing operation publishes
events throughout its lifecycle, allowing callers to monitor and trace execution
across an entire end-to-end workflow using **correlation IDs**.

Key concepts:

- **correlation_id**: A unique identifier attached to all events for a particular
  parsing operation or workflow. Use correlation IDs to trace a complete request
  across multiple parsing steps, service boundaries, or integration points.
- **PubSubSolo**: Global in-memory event bus. Use to subscribe to parsing events
  (begin, end, error) and consume them in real-time callbacks.
- **Event topics**: Structured as `"<service>.<operation>.<phase>"` (e.g.,
  `"dsv.parse.begin"`, `"dsv.parse.end"`, `"dsv.parse.error"`).
- **Scope**: Events are organized by scope (default: `"splurge-dsv"`). Use scopes
  to isolate event streams in multi-component systems.

---

## Package exports

Public top-level exports (available from `splurge_dsv`):

- Classes and helpers: `Dsv`, `DsvConfig`, `DsvHelper`, `StringTokenizer`
- CLI helpers: `parse_arguments`, `run_cli`, `print_results` (in `splurge_dsv.cli`)
- Exceptions: all `SplurgeDsv*` classes from `splurge_dsv.exceptions`

Always prefer the higher-level `Dsv` / `DsvHelper` APIs rather than
reimplementing tokenization or low-level file reads unless you need special
control.

---

## Configuration

### DsvConfig

Signature:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class DsvConfig:
    delimiter: str
    strip: bool = True
    bookend: str | None = None
    bookend_strip: bool = True
    encoding: str = "utf-8"
    skip_header_rows: int = 0
    skip_footer_rows: int = 0
    chunk_size: int = DsvHelper.DEFAULT_CHUNK_SIZE
    skip_empty_lines: bool = False
    detect_columns: bool = False
    raise_on_missing_columns: bool = False
    raise_on_extra_columns: bool = False
    max_detect_chunks: int = DsvHelper.MAX_DETECT_CHUNKS

    @classmethod
    def csv(cls, **overrides) -> "DsvConfig":
        ...

    @classmethod
    def tsv(cls, **overrides) -> "DsvConfig":
        ...
```

Key fields and behavior:

- `delimiter` (str): required field delimiter like "," or "\t". Must be a
  non-empty string; an empty delimiter raises `SplurgeDsvValueError`.
- `strip` (bool): whether tokens are stripped (default True).
- `bookend` (str|None): optional quoting character, e.g. `"` or `'`.
- `bookend_strip` (bool): whether to strip whitespace after removing bookends.
- `encoding` (str): file encoding used by file-reading helpers (default
  "utf-8").
- `skip_header_rows` / `skip_footer_rows` (int >= 0): number of logical rows
  to skip from the start/end of the file.
- `chunk_size` (int): number of logical rows (lines) yielded per streamed
  chunk; has a minimum enforced by `DsvHelper.DEFAULT_MIN_CHUNK_SIZE`.
- `detect_columns` (bool): when True, parsing helpers will attempt to
  discover the expected column count from the first non-blank logical row.
- `raise_on_missing_columns` / `raise_on_extra_columns` (bool): when True,
  strict validation will raise `SplurgeDsvColumnMismatchError` for rows with
  too few / too many columns than expected.
- `max_detect_chunks` (int): when streaming with detection enabled, the
  maximum number of initial chunks to buffer and inspect while searching for
  the first non-blank logical row used to detect the column count.

Validation:

- Construction or helper entrypoints will raise `SplurgeDsvValueError`
  for invalid configuration (for example empty `delimiter`, `chunk_size`
  below minimum, or negative skip counts).

Example construction:

```python
cfg = DsvConfig.csv(skip_header_rows=1, detect_columns=True)
parser = Dsv(cfg)
```

---

## Core parser

This section documents the two primary entry points for parsing: the
instance-based `Dsv` and the stateless `DsvHelper` helpers. Both produce the
same parsing semantics. Prefer `Dsv` when you have a repeated configuration
and `DsvHelper` for one-off parsing.

### Dsv

Constructor:

```py
Dsv(config: DsvConfig, correlation_id: str | None = None)
```

Parameters:

- `config` (DsvConfig): Configuration object containing parsing parameters.
- `correlation_id` (str | None): Optional unique identifier for tracing this
  parser instance's operations. If not provided, a UUID is automatically
  generated. All events emitted by this parser will carry this correlation_id,
  allowing callers to track a complete parsing workflow and correlate it with
  other operations in a distributed system.

Public properties:

- `correlation_id` (str): Read-only property returning the current instance's
  correlation ID.
- `config` (DsvConfig): Read-only property returning the configuration.

- `parse(self, content: str, *, normalize_columns: int | None = None) -> list[str]`
  - Parse a single logical record (a line). If `normalize_columns` is None
    or 0 the row is returned as parsed; if a positive int is passed, the
    returned row will be padded with empty strings or truncated to match the
    length.
  - **Events published**: `"dsv.parse.begin"` (at start), `"dsv.parse.end"` (on
    success), `"dsv.parse.error"` (on failure). All events carry the instance's
    `correlation_id`.
  - Raises: `SplurgeDsvValueError` for invalid args, `SplurgeDsvRuntimeError`
    for tokenization errors.

- `parses(self, content: list[str], *, detect_columns: bool = False, normalize_columns: int | None = None) -> list[list[str]]`
  - Parse a list of logical records. When `detect_columns=True`, the helper
    will determine `normalize_columns` from the first non-blank logical row
    if not explicitly provided.
  - **Events published**: `"dsv.parses.begin"` and `"dsv.parses.end"` (or error).

- `parse_file(self, file_path, *, normalize_columns: int | None = None) -> list[list[str]]`
  - Read and parse the entire file into memory. Uses `DsvConfig.encoding`.
  - Honors `DsvConfig.skip_empty_lines`: when True the underlying reader will filter out raw empty logical lines (line.strip() == "") before parsing; when False blank lines are passed through and parsed normally.
  - **Events published**: `"dsv.parse.file.begin"`, `"dsv.parse.file.end"`,
    and error events.
  - Raises file-related exceptions (see Exceptions section) for IO issues.

- `parse_file_stream(self, file_path, *, normalize_columns: int | None = None) -> Iterator[list[list[str]]]`
  - Stream-parse a file. Yields chunks (lists of rows) according to
    `DsvConfig.chunk_size`. When `detect_columns=True` and
    `normalize_columns` is falsy, the stream will buffer and scan up to
    `max_detect_chunks` chunks to find the first non-blank logical row and
    detect the expected column count; buffered chunks are replayed to the
    caller so the file is yielded in-order.
  - The streaming API also respects `DsvConfig.skip_empty_lines`. If
    `skip_empty_lines` is True the underlying `SafeTextFileReader` will
    remove blank logical lines (where `line.strip() == ""`) before the
    stream reaches the parser; otherwise blank logical lines are provided to
    the parser and will be tokenized/normalized/validated according to the
    configured `strip`, `normalize_columns`, and strict validation flags.
  - **Events published**: `"dsv.parse.file.stream.begin"`,
    `"dsv.parse.file.stream.end"`, and error events.
  - Raises: file errors, decoding errors, and `SplurgeDsvColumnMismatchError`
    when strict validation flags are set and violated.

Notes:

- `Dsv` methods forward to `DsvHelper` under the hood — behavior and
  exceptions are consistent between the two.
- All events are published with `correlation_id=self.correlation_id` and
  `scope="splurge-dsv"`, enabling end-to-end workflow tracing.

### DsvHelper

`DsvHelper` is a stateless collection of classmethods that perform parsing.
Use these when you don't want to create a `Dsv` instance.

Selected public classmethods:

- `parse(content: str, *, delimiter: str, bookend: str | None = None, strip: bool = True, normalize_columns: int | None = None, raise_on_missing_columns: bool = False, raise_on_extra_columns: bool = False) -> list[str]`
  - Parse a single logical record string and return list[str]. Supports
    optional normalization and strict validation flags. Preserves empty
    tokens and handles bookend removal when provided.
  - Raises: `SplurgeDsvValueError` for invalid args, `SplurgeDsvRuntimeError`
    for tokenization issues.

- `parses(content: Iterable[str], *, delimiter: str, detect_columns: bool = False, normalize_columns: int | None = None, raise_on_missing_columns: bool = False, raise_on_extra_columns: bool = False, strip: bool = True, bookend: str | None = None) -> list[list[str]]`
  - Parse multiple logical records. If `detect_columns=True` and
    `normalize_columns` is falsy, the helper determines the expected column
    count from the first non-blank logical row.

- `parse_file(file_path, *, delimiter: str, encoding: str = 'utf-8', skip_header_rows: int = 0, skip_footer_rows: int = 0, normalize_columns: int | None = None, detect_columns: bool = False, raise_on_missing_columns: bool = False, raise_on_extra_columns: bool = False, strip: bool = True, bookend: str | None = None) -> list[list[str]]`
  - Read file to memory and parse. Path validation and file I/O errors are
    mapped to package exceptions.
  - Note: callers can control blank-line handling by passing
    `skip_empty_lines` (bool) which is forwarded to the underlying
    `SafeTextFileReader` and will cause raw blank logical lines to be
    filtered before parsing when True.

- `parse_file_stream(file_path, *, delimiter: str, encoding: str = 'utf-8', chunk_size: int = DsvHelper.DEFAULT_CHUNK_SIZE, normalize_columns: int | None = None, detect_columns: bool = False, max_detect_chunks: int = DsvHelper.MAX_DETECT_CHUNKS, raise_on_missing_columns: bool = False, raise_on_extra_columns: bool = False, strip: bool = True, bookend: str | None = None) -> Iterator[list[list[str]]]`
  - Preferred streaming API. Behavior mirrors `Dsv.parse_file_stream`.
  - Implementation notes: when detection is enabled the method may buffer
    several initial chunks (bounded by `max_detect_chunks`) to find the
    first non-blank logical row and compute `normalize_columns`. It then
    replays the buffered chunks to the caller so the caller receives the
    entire file stream starting at the first chunk.

Error mapping:

- File and path validation errors are mapped to `SplurgeDsvOSError` and
  `SplurgeDsvPathValidationError` exceptions.
- Tokenization or parsing problems raise `SplurgeDsvRuntimeError`.
- Column mismatch conditions raise `SplurgeDsvColumnMismatchError` when the
  corresponding strict flags are set.

---

## Tokenization helpers

### StringTokenizer

Signatures:

- `StringTokenizer.parse(content: str | None, *, delimiter: str, strip: bool = True) -> list[str]`
  - Parse a single logical record into tokens. Preserves empty tokens.

- `StringTokenizer.parses(content: Iterable[str], *, delimiter: str, strip: bool = True) -> list[list[str]]`
  - Parse multiple records.

- `StringTokenizer.remove_bookends(token: str, *, bookend: str, strip: bool = True) -> str`
  - Remove symmetric bookend characters from a token if present and
    optionally strip surrounding whitespace.

Notes:

- These helpers are deterministic and intended for direct use in
  applications that perform custom parsing pipelines. They are the
  underlying tokenization primitives used by `DsvHelper`.

---

## File & I/O helpers (integration notes)

Low-level file reading, newline normalization, and secure path handling are
provided by the `splurge-safe-io` dependency. The library uses:

- `SafeTextFileReader` for robust file reads and decoding
  - `SafeTextFileReader` for robust file reads and decoding. Note: the
    reader supports a `skip_empty_lines` option which, when enabled, will
    remove logical blank lines (where `line.strip() == ""`) after
    header/footer trimming and before the parser receives the lines.
- `SafeTextFileWriter` for robust writes
- `PathValidator` for secure path checks

The `splurge_dsv` package maps errors from `splurge-safe-io` into its own
exceptions (see Exceptions section). If you need fine-grained control over
file reading (for example, to stream over non-file sources), use
`splurge-safe-io` directly.

---

## Event Publishing with PubSubSolo

### Overview

Splurge DSV emits structured events throughout the parsing lifecycle via
**PubSubSolo**, a lightweight global in-memory publish-subscribe system. This
enables real-time monitoring, distributed tracing, and end-to-end workflow
correlation using **correlation IDs**.

### PubSubSolo Public API

**Subscription:**

```python
from splurge_dsv import PubSubSolo

def event_callback(message: Message) -> None:
    """Handle an event."""
    print(f"Topic: {message.topic}, Correlation ID: {message.correlation_id}")

# Subscribe to all events for a specific correlation_id
PubSubSolo.subscribe(
    topic="*",
    callback=event_callback,
    correlation_id="my-trace-id",
    scope="splurge-dsv"
)
```

Signature:

```python
PubSubSolo.subscribe(
    topic: str,
    callback: Callable[[Message], None],
    correlation_id: str | None = None,
    scope: str = "splurge-dsv"
) -> None
```

Parameters:

- `topic` (str): Event topic to subscribe to. Use `"*"` as wildcard to match
  all topics within the scope. Topics follow the pattern
  `"<service>.<operation>.<phase>"` (e.g., `"dsv.parse.begin"`).
- `callback` (Callable[[Message], None]): Function invoked when an event
  matching the topic and correlation_id is published.
- `correlation_id` (str | None): Filter events to a specific correlation ID.
  If None, subscribe to all events matching the topic regardless of
  correlation_id.
- `scope` (str): Event namespace. Default `"splurge-dsv"` isolates DSV events
  from other components.

**Draining (flushing) events:**

```python
# Process all pending events in the queue (blocking, with timeout)
PubSubSolo.drain(timeout_ms=2000, scope="splurge-dsv")
```

Signature:

```python
PubSubSolo.drain(timeout_ms: int, scope: str = "splurge-dsv") -> None
```

Parameters:

- `timeout_ms` (int): Maximum time to wait for events to be processed
  (milliseconds).
- `scope` (str): Event namespace to drain.

### Published Events

The following events are published by `Dsv` and `DsvHelper` instances:

**Dsv lifecycle events:**

- `dsv.init` — Published when a `Dsv` instance is created.
- `dsv.parse.begin` — Published when `parse()` starts.
- `dsv.parse.end` — Published when `parse()` completes successfully.
- `dsv.parse.error` — Published when `parse()` fails; includes error data.
- `dsv.parses.begin` — Published when `parses()` starts.
- `dsv.parses.end` — Published when `parses()` completes successfully.
- `dsv.parses.error` — Published when `parses()` fails.
- `dsv.parse.file.begin` — Published when `parse_file()` starts.
- `dsv.parse.file.end` — Published when `parse_file()` completes successfully.
- `dsv.parse.file.error` — Published when `parse_file()` fails.
- `dsv.parse.file.stream.begin` — Published when `parse_file_stream()` starts.
- `dsv.parse.file.stream.chunk` — Published when a chunk is yielded.
- `dsv.parse.file.stream.end` — Published when streaming completes.
- `dsv.parse.file.stream.error` — Published when streaming fails.

**DsvHelper lifecycle events:**

- `dsv.helper.parse.begin`, `dsv.helper.parse.end`, `dsv.helper.parse.error`
- `dsv.helper.parses.begin`, `dsv.helper.parses.end`, `dsv.helper.parses.error`
- `dsv.helper.parse.file.begin`, `dsv.helper.parse.file.end`,
  `dsv.helper.parse.file.error`
- `dsv.helper.parse.file.stream.begin`, `dsv.helper.parse.file.stream.end`,
  `dsv.helper.parse.file.stream.error`

All events carry:

- `topic` (str): The event topic.
- `correlation_id` (str | None): The associated correlation ID (if any).
- `data` (dict | None): Optional event data (e.g., error details).
- `metadata` (dict | None): Optional event metadata (e.g., error details).
- `timestamp` (datetime): Event publication time.

### Message Class

```python
from splurge_dsv._vendor.splurge_pub_sub.message import Message

class Message:
    topic: str
    data: dict | None
    metadata: dict | None
    correlation_id: str | None
    timestamp: datetime
    scope: str
```

---

## CLI reference

The CLI entry point is implemented in `splurge_dsv.cli`. Run it as a module
(`python -m splurge_dsv`) or via the installed console script.

Top-level functions:

- `parse_arguments(argv: list[str] | None = None) -> argparse.Namespace`
  - Parse CLI flags. When `argv` is None, `sys.argv[1:]` is used.
- `run_cli(argv: list[str] | None = None) -> int`
  - Execute the CLI and return an exit status code (0 on success).

Primary command-line options / flags (long + short forms when available):

- `--delimiter DELIM` / `-d DELIM`
  - Field delimiter string. Required unless the input file uses a known
    extension and the CLI infers (not recommended). Empty delimiter is
    rejected.

- `--stream` / `-s`
  - Enable streaming mode. When set the CLI will use `parse_file_stream` and
    may print progress and chunk-level output instead of materializing the
    entire file.

- `--chunk-size N` / `-c N`
  - Number of logical rows per chunk in streaming mode. Must be >= the
    internal minimum; invalid values cause the CLI to fail with a
    `SplurgeDsvValueError`.

- `--detect-normalize-columns` (boolean flag)
  - When used without an explicit `--normalize-columns`, enables automatic
    detection of the expected column count from the first non-blank logical
    row for normalization purposes.

- `--normalize-columns N`
  - Force normalization to a fixed width: pad rows with empty strings or
    truncate rows to match `N` columns.

- `--raise-on-missing-columns`
  - When set, rows with fewer fields than the expected width raise
    `SplurgeDsvColumnMismatchError`.

- `--raise-on-extra-columns`
  - When set, rows with more fields than the expected width raise
    `SplurgeDsvColumnMismatchError`.

- `--skip-empty-lines`
  - When set, raw blank logical lines (where `line.strip() == ""`) are
    skipped before parsing. This is forwarded to the underlying
    `SafeTextFileReader` and affects both streaming and non-streaming modes.

- `--max-detect-chunks N`
  - When detection is enabled, the maximum number of initial chunks to
    inspect while searching for the first non-blank logical row. Smaller
    values limit memory used by detection; larger values increase the
    chance of finding a non-blank row in files with many blank/metadata rows.

- `--encoding ENCODING`
  - File encoding (defaults to `utf-8`).

- `--skip-header-rows N`
  - Skip the first N logical rows before parsing/detection.

- `--skip-footer-rows N`
  - Skip the last N logical rows before parsing/detection.

- `--output-format {table,json,ndjson}`
  - Output format for the CLI:
    - `table` (default): human-friendly table output
    - `json`: one JSON array with all records
    - `ndjson`: newline-delimited JSON objects/arrays per row or chunk

Behavior notes:

- CLI flags map into a `DsvConfig` instance which is used by the internal
  `Dsv` object. CLI argument validation is strict and invalid combinations
  (for example streaming plus an output format that requires full
  materialization) will produce informative error messages and non-zero exit
  codes.

### `--config` / `-c` YAML configuration file

The CLI accepts a YAML configuration file containing keys that mirror
`DsvConfig` fields. When supplied, the YAML file is used as the base
configuration and explicitly provided CLI flags override values from the
file.

Rules and behavior:

- The YAML file must be a top-level mapping/dictionary. Non-mapping YAML
  will cause the CLI to fail with a helpful error message.
- Keys that don't match `DsvConfig` field names are ignored by the loader.
- The CLI overlays values on top of the YAML mapping; any CLI-specified
  value takes precedence.
- If PyYAML is not installed and `--config` is used, the CLI will exit
  with an error instructing the user to install `PyYAML`.

Example `config.yaml`:

```yaml
delimiter: ","
strip: true
bookend: '"'
encoding: utf-8
skip_header_rows: 1
skip_footer_rows: 0
skip_empty_lines: false
detect_columns: true
chunk_size: 500
max_detect_chunks: 5
raise_on_missing_columns: false
raise_on_extra_columns: false
```

Example usage:

```bash
# Base config from YAML, CLI overrides delimiter
python -m splurge_dsv data.csv --config config.yaml --delimiter "|"

# Use only YAML for configuration
python -m splurge_dsv data.csv --config config.yaml
```

Library usage:

```python
from splurge_dsv.dsv import DsvConfig

# Construct from a YAML file programmatically
cfg = DsvConfig.from_file('config.yaml')
```

---

## Exceptions

All package exceptions are defined in `splurge_dsv.exceptions` and re-exported
from the package root for convenience. They inherit from `SplurgeDsvError`
which inherits from `SplurgeFrameworkError` (from the `splurge-exceptions`
library). This provides a clear, practical hierarchy so callers can catch
broad or narrow categories of errors.

Hierarchy and descriptions:

- `SplurgeDsvError` (base class for all package exceptions; inherits from `SplurgeFrameworkError`)

  - `SplurgeDsvTypeError` — raised when a value has the wrong type
    - Example: passing a non-list to `parses()` when a list is required

  - `SplurgeDsvValueError` — raised when a value has the right type but inappropriate content
    - Example: empty delimiter string
    - Example: negative chunk size

  - `SplurgeDsvLookupError` — raised for lookup failures and codec-related errors
    - Maps from `SplurgeSafeIoLookupError` for codec/encoding issues
    - Example: unknown codec specified
    - Example: incorrect file encoding specified

  - `SplurgeDsvUnicodeError` — raised for Unicode-related errors such as encoding/decoding failures
    - Maps from `SplurgeSafeIoUnicodeError` when file decoding fails
    - Example: file contains invalid byte sequences for the specified encoding
    - Example: decoding error during text processing

  - `SplurgeDsvOSError` — raised for file I/O and OS-related errors
    - Maps from `SplurgeSafeIoOSError` for file not found, permission denied, and other OS failures
    - Example: attempting to parse a non-existent file
    - Example: permission denied when reading a file

  - `SplurgeDsvRuntimeError` — raised for general runtime errors not covered by other categories
    - Maps from `SplurgeSafeIoRuntimeError` for unexpected runtime issues
    - Example: unexpected errors during file streaming

  - `SplurgeDsvPathValidationError` — raised when a filesystem path fails validation checks
    - Maps from `SplurgeSafeIoPathValidationError`
    - Example: path traversal attempts or dangerous characters detected

  - `SplurgeDsvDataProcessingError` — base exception for data processing errors (parsing, conversion)
    - `SplurgeDsvColumnMismatchError` — raised when row column count doesn't match expected
      - Only raised when strict validation flags are enabled
      - Example: row has 5 columns but expected 4, and `raise_on_extra_columns=True`

Error mapping from `splurge-safe-io`:

The library maps exceptions from the underlying `splurge-safe-io` dependency
into the `SplurgeDsv*` exception hierarchy:

- `SplurgeSafeIoLookupError` → `SplurgeDsvLookupError` (codec and lookup issues)
- `SplurgeSafeIoUnicodeError` → `SplurgeDsvUnicodeError` (encoding/decoding failures)
- `SplurgeSafeIoOSError` → `SplurgeDsvOSError` (file not found, permissions, etc.)
- `SplurgeSafeIoPathValidationError` → `SplurgeDsvPathValidationError` (invalid paths)
- `SplurgeSafeIoRuntimeError` → `SplurgeDsvRuntimeError` (other runtime errors)

Usage guidance:

- Prefer catching specific exceptions when you want targeted recovery behavior:
  ```python
  try:
      rows = DsvHelper.parse_file("data.csv", delimiter=",")
  except SplurgeDsvOSError:
      print("File not found or not readable")
  except SplurgeDsvUnicodeError:
      print("Encoding error - file contains invalid byte sequences")
  except SplurgeDsvLookupError:
      print("Codec error - unknown or unsupported encoding")
  ```

- Use `SplurgeDsvError` as a catch-all only for generic error reporting:
  ```python
  try:
      rows = DsvHelper.parse_file("data.csv", delimiter=",")
  except SplurgeDsvError as e:
      print(f"Failed to parse: {e}")
  ```

Migration from v2025.3.x:

- In v2025.3.x and earlier, the library exposed many specialized exception classes:
  - `SplurgeDsvFileNotFoundError`, `SplurgeDsvFilePermissionError`, etc.
- In v2025.4.0+, these have been consolidated into the new hierarchy:
  - `SplurgeDsvFileNotFoundError` → catch `SplurgeDsvOSError`
  - `SplurgeDsvFilePermissionError` → catch `SplurgeDsvOSError`
  - `SplurgeDsvFileDecodingError` → catch `SplurgeDsvLookupError`
  - Other file operation errors → catch `SplurgeDsvOSError`

Example migration:

```python
# Old code (v2025.3.x)
try:
    rows = DsvHelper.parse_file("data.csv", delimiter=",")
except SplurgeDsvFileNotFoundError:
    print("File not found")
except SplurgeDsvFileDecodingError:
    print("Encoding error")

# New code (v2025.4.0+)
try:
    rows = DsvHelper.parse_file("data.csv", delimiter=",")
except SplurgeDsvOSError:
    print("File not found or other OS error")
except SplurgeDsvLookupError:
    print("Encoding error")
```

---

## Examples

Quick string parse:

```python
from splurge_dsv import DsvHelper

row = DsvHelper.parse("a,b,c", delimiter=",")
assert row == ["a", "b", "c"]
```

Parsing multiple lines with detection:

```python
from splurge_dsv import DsvHelper

lines = ["", "a,b,c", "d,e,f"]
rows = DsvHelper.parses(lines, delimiter=",", detect_columns=True)
```

Streaming with normalization and strict validation:

```python
from splurge_dsv import Dsv, DsvConfig

cfg = DsvConfig.csv(detect_columns=True, max_detect_chunks=5, raise_on_extra_columns=True)
parser = Dsv(cfg)
for chunk in parser.parse_file_stream("big.csv"):
    for row in chunk:
        # row is already normalized to the detected width
        pass
```

### Event Publishing and Correlation ID Tracing

Trace a complete parsing workflow end-to-end using correlation IDs and event
subscriptions. This enables distributed tracing and monitoring across service
boundaries.

**Example: Subscribe to all events for a specific workflow**

```python
from splurge_dsv import Dsv, DsvConfig, PubSubSolo
from uuid import uuid4

# Create a unique identifier for this workflow
workflow_id = str(uuid4())

# Define an event callback
def on_parse_event(message):
    """Handle parsing events."""
    print(f"[{message.topic}] Correlation: {message.correlation_id} | Time: {message.timestamp}")
    if message.data:
        print(f"  Data: {message.data}")

# Subscribe to all events for this workflow
PubSubSolo.subscribe(
    topic="*",
    callback=on_parse_event,
    correlation_id=workflow_id,
    scope="splurge-dsv"
)

# Create a parser with the same correlation ID
config = DsvConfig(delimiter=",")
parser = Dsv(config=config, correlation_id=workflow_id)

# Perform parsing operations — all events will be captured
result = parser.parse("name,age,city")
print(f"Result: {result}")

# Drain the event queue to ensure all callbacks are processed
PubSubSolo.drain(timeout_ms=2000, scope="splurge-dsv")
```

Output:
```
[dsv.init] Correlation: abc-123-xyz | Time: 2025-11-08 10:30:45.123456
[dsv.parse.begin] Correlation: abc-123-xyz | Time: 2025-11-08 10:30:45.123489
[dsv.parse.end] Correlation: abc-123-xyz | Time: 2025-11-08 10:30:45.123512
Result: ['name', 'age', 'city']
```

**Example: Subscribe to specific event topics**

```python
from splurge_dsv import Dsv, DsvConfig, PubSubSolo

def on_error(message):
    """Handle only error events."""
    print(f"ERROR in {message.topic}: {message.data}")

def on_completion(message):
    """Handle completion events."""
    print(f"Completed: {message.topic}")

# Subscribe to error events only
PubSubSolo.subscribe(
    topic="dsv.*.error",
    callback=on_error,
    correlation_id=None,  # Receive errors for any correlation_id
    scope="splurge-dsv"
)

# Subscribe to completion events only
PubSubSolo.subscribe(
    topic="dsv.*.end",
    callback=on_completion,
    scope="splurge-dsv"
)

config = DsvConfig(delimiter=",")
parser = Dsv(config)

# Perform parsing
try:
    result = parser.parse("a,b,c")
except Exception as e:
    print(f"Exception: {e}")

# Drain events
PubSubSolo.drain(timeout_ms=1000, scope="splurge-dsv")
```

**Example: Stream processing with event monitoring**

```python
from splurge_dsv import Dsv, DsvConfig, PubSubSolo
from uuid import uuid4

# Create workflow correlation ID
correlation_id = str(uuid4())

# Track streaming progress via events
chunk_count = 0

def on_stream_event(message):
    global chunk_count
    if message.topic == "dsv.parse.file.stream.chunk":
        chunk_count += 1
        print(f"Processed chunk {chunk_count}")

PubSubSolo.subscribe(
    topic="dsv.parse.file.stream.*",
    callback=on_stream_event,
    correlation_id=correlation_id,
    scope="splurge-dsv"
)

# Create parser and stream a file
config = DsvConfig(delimiter=",", chunk_size=100)
parser = Dsv(config, correlation_id=correlation_id)

for chunk in parser.parse_file_stream("large_file.csv"):
    for row in chunk:
        # Process row
        pass

# Ensure all events are processed
PubSubSolo.drain(timeout_ms=2000, scope="splurge-dsv")
print(f"Total chunks processed: {chunk_count}")
```

**Example: Error handling with correlation tracking**

```python
from splurge_dsv import Dsv, DsvConfig, PubSubSolo, SplurgeDsvOSError

correlation_id = "critical-import-123"
errors = []

def capture_errors(message):
    """Capture error events."""
    if "error" in message.topic:
        errors.append({
            "topic": message.topic,
            "correlation_id": message.correlation_id,
            "error_details": message.data,
            "timestamp": message.timestamp
        })

PubSubSolo.subscribe(
    topic="*",
    callback=capture_errors,
    correlation_id=correlation_id,
    scope="splurge-dsv"
)

config = DsvConfig(delimiter=",")
parser = Dsv(config, correlation_id=correlation_id)

try:
    # Attempt to parse a non-existent file
    rows = parser.parse_file("missing.csv")
except SplurgeDsvOSError as e:
    print(f"File error: {e}")

PubSubSolo.drain(timeout_ms=1000, scope="splurge-dsv")

# Review all errors captured during this workflow
for error in errors:
    print(f"Error [{error['topic']}]: {error['error_details']}")
```

---

## Migration notes — release 2025.3.0

Key changes and migration guidance:

- Column detection and normalization: use `normalize_columns` or
  `detect_columns=True` rather than hand-rolling padding/truncation logic.
- Streaming detection: set `max_detect_chunks` to control how many initial
  chunks the parser will buffer while searching for the first non-blank
  logical row. This trades small additional memory use for robustness when
  files contain many blank lines or metadata before actual data.
- CLI flags: `--detect-normalize-columns`, `--raise-on-missing-columns`,
  `--raise-on-extra-columns`, and `--max-detect-chunks` were added — see
  CLI reference above for details.
- Deprecation: the legacy `parse_stream()` helpers were removed — use
  `parse_file_stream()` on `Dsv` / `DsvHelper` instead.
