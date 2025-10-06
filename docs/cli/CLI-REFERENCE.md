# Splurge DSV — CLI Reference

This document describes the command-line interface provided by the
`splurge_dsv` package (entrypoint: `python -m splurge_dsv`). It covers flags,
usage patterns, environment variables, examples, error handling, and exit codes.

> Note: CLI behavior is governed by `splurge_dsv.cli` and will evolve across
> releases — consult the module docstring for the authoritative runtime
> behavior.

---

## Invocation

Run the CLI as a module (recommended, uses installed package):

```bash
python -m splurge_dsv [path] [options]
```

Or directly if you have the package installed as an executable entry point:

```bash
splurge-dsv [path] [options]
```

If ``path`` is ``-`` the CLI reads from stdin.

---

## Common options

The CLI supports the following top-level options (abridged):

- `--delimiter <char>` (required unless autodetected): Field delimiter.
- `--bookend <char>`: Optional bookend character (e.g. `"`).
- `--encoding <enc>`: File encoding (default: `utf-8`).
- `--skip-header <N>`: Number of header rows to skip.
- `--skip-footer <N>`: Number of footer rows to skip.
- `--stream` / `--no-stream`: Stream rows in chunks (useful for large files).
- `--chunk-size <N>`: Number of lines per chunk when streaming (default: 500).
- `--output-format {table,json,ndjson}`: Output format. Defaults to `table`.
- `--help`: Print help and exit.
- `--version`: Print version and exit.

### Environment variables

The CLI respects environment variable overrides with the `SPLURGE_DSV_` prefix.
For example, `SPLURGE_DSV_ENCODING` will be used unless `--encoding` is
specified on the command line. This follows the project's CLI standards.

---

## Usage examples

### Parse a CSV file to table output

```bash
python -m splurge_dsv data.csv --delimiter ,
```

### Stream a large file and output JSON lines

```bash
python -m splurge_dsv large.csv --delimiter , --stream --chunk-size 1000 --output-format ndjson
```

### Read from stdin and output NDJSON

```bash
cat data.csv | python -m splurge_dsv - --delimiter , --output-format ndjson
```

### Use environment variable for encoding

```bash
export SPLURGE_DSV_ENCODING="latin-1"
python -m splurge_dsv data.csv --delimiter ','
```

---

## Output formats

- `table`: Human-friendly aligned table printed to stdout.
- `json`: A single JSON array written to stdout.
- `ndjson`: Newline-delimited JSON — one JSON object per row.

Notes:
- When using `json`/`ndjson`, the CLI will never mix other stdout logging
  text with the JSON output. Errors and logs go to stderr.
- Use `--output-format ndjson` for streaming outputs to downstream tools.

---

## Error handling and exit codes

The CLI maps exceptions to non-zero exit codes and prints concise messages to
stderr. The following exit codes are used:

- `0`: Success
- `1`: Generic error
- `2`: Invalid arguments or missing required parameters
- `3`: File not found / cannot open input file
- `4`: Permission denied / file not writable
- `5`: Encoding/decoding error
- `130`: Interrupted by user (Ctrl+C)

Examples of CLI error messages and suggested handling:

- Missing delimiter:
  - Error: "Missing required parameter: --delimiter"
  - Exit code: 2
  - Suggestion: Provide `--delimiter` or use a known file extension with
    automatic detection (if implemented).

- File not found:
  - Error: "File not found: data.csv"
  - Exit code: 3
  - Suggestion: Verify the path and permissions.

- Encoding error:
  - Error: "Unable to decode file with encoding 'utf-8'"
  - Exit code: 5
  - Suggestion: Try another encoding, e.g. `--encoding latin-1`.

---

## Advanced patterns

### Pipelining and streaming to other tools

Use `--output-format ndjson` for efficient streaming to `jq` or other JSON
processors:

```bash
python -m splurge_dsv big.csv --delimiter , --stream --output-format ndjson | jq '.'
```

### Logging and verbosity

The CLI will write diagnostic and error messages to stderr. You can capture
stdout in pipelines while still viewing errors in the terminal.

---

## Security and safe defaults

- File paths are validated using `PathValidator` to prevent path traversal and
  other unsafe patterns.
- By default, newline handling is normalized to LF to avoid platform
  inconsistencies in downstream tools.

---

## Where to look in the codebase

- CLI implementation: `splurge_dsv/cli.py`
- Argument parsing helpers: `splurge_dsv/cli.py` (see `parse_arguments`)
- Main entrypoint: `splurge_dsv/__main__.py`

---
