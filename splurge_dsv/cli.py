"""Command-line interface utilities for splurge-dsv.

This module provides the CLI entry points and helpers for parsing DSV
files from the command line. It exposes a thin wrapper around the
library API suitable for use as ``python -m splurge_dsv``.

Public API:
    - parse_arguments: Build and parse the CLI argument parser.
    - print_results: Nicely format parsed rows to stdout.
    - run_cli: Main entrypoint invoked by ``__main__``.

License: MIT

Copyright (c) 2025 Jim Schilling
"""

# Standard library imports
import argparse
import json
import sys
from pathlib import Path

# Local imports
from . import __version__
from .dsv import Dsv, DsvConfig
from .dsv_helper import DsvHelper
from .exceptions import SplurgeDsvError


def parse_arguments() -> argparse.Namespace:
    """Construct and parse command-line arguments for the CLI.

    Returns:
        argparse.Namespace: Parsed arguments with attributes matching the
            defined options.
    """
    parser = argparse.ArgumentParser(
        description="Parse DSV (Delimited String Values) files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m splurge_dsv data.csv --delimiter ,
  python -m splurge_dsv data.tsv --delimiter "\t"
  python -m splurge_dsv data.txt --delimiter "|" --bookend '"'
  # Auto-detect the expected column count and normalize rows
  python -m splurge_dsv data.csv --delimiter , --detect-columns --max-detect-chunks 5
  # Stream a large file while attempting to detect the column count from the first non-blank logical row
  python -m splurge_dsv large.csv --delimiter , --stream --detect-columns --max-detect-chunks 10
    """,
    )

    parser.add_argument("file_path", type=str, help="Path to the DSV file to parse")

    parser.add_argument(
        "--config",
        "-c",
        dest="config",
        type=str,
        help="Path to a YAML config file that mirrors CLI options (values overridden by CLI args)",
    )

    parser.add_argument(
        "--delimiter",
        "-d",
        type=str,
        help="Delimiter character to use for parsing (may also be provided via --config)",
    )

    parser.add_argument("--bookend", "-b", type=str, help="Bookend character for text fields (e.g., '\"')")

    parser.add_argument("--no-strip", action="store_true", help="Don't strip whitespace from values")

    parser.add_argument("--no-bookend-strip", action="store_true", help="Don't strip whitespace from bookends")

    parser.add_argument("--encoding", "-e", type=str, default="utf-8", help="File encoding (default: utf-8)")

    parser.add_argument("--skip-header", type=int, default=0, help="Number of header rows to skip (default: 0)")

    parser.add_argument("--skip-footer", type=int, default=0, help="Number of footer rows to skip (default: 0)")

    parser.add_argument(
        "--stream", "-s", action="store_true", help="Stream the file in chunks instead of loading entirely into memory"
    )

    parser.add_argument(
        "--detect-columns",
        action="store_true",
        help=(
            "Auto-detect the expected column count from the first non-blank logical row "
            "and normalize subsequent rows to that count. For streamed parsing, the "
            "detector may scan up to --max-detect-chunks chunks from the start of the file."
        ),
    )

    parser.add_argument(
        "--raise-on-missing-columns",
        action="store_true",
        help="Raise an error if a row has fewer columns than the detected/expected count",
    )

    parser.add_argument(
        "--raise-on-extra-columns",
        action="store_true",
        help="Raise an error if a row has more columns than the detected/expected count",
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DsvHelper.DEFAULT_CHUNK_SIZE,
        help=(
            f"Chunk size for streaming (minimum: {DsvHelper.DEFAULT_MIN_CHUNK_SIZE}, "
            f"default: {DsvHelper.DEFAULT_CHUNK_SIZE})"
        ),
    )

    parser.add_argument(
        "--max-detect-chunks",
        type=int,
        default=DsvHelper.MAX_DETECT_CHUNKS,
        help=(
            "When detecting columns while streaming (use --detect-normalize-columns), "
            f"scan up to N chunks from the start of the stream before giving up (default: {DsvHelper.MAX_DETECT_CHUNKS})."
        ),
    )

    parser.add_argument(
        "--skip-empty-lines",
        action="store_true",
        help="Have the underlying reader skip raw empty logical lines (line.strip() == '') before parsing",
    )

    parser.add_argument(
        "--output-format",
        choices=["table", "json", "ndjson"],
        default="table",
        help="Output format for results (default: table)",
    )

    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    return parser.parse_args()


def print_results(rows: list[list[str]], delimiter: str) -> None:
    """Print parsed rows in a human-readable table format.

    The function computes column widths and prints a simple ASCII table.

    Args:
        rows: Parsed rows to print (first row is treated as header).
        delimiter: Delimiter used (included here for compatibility; printing
            does not depend on it directly).
    """
    if not rows:
        print("No data found.")
        return

    # Find the maximum width for each column
    if rows:
        max_widths = []
        for col_idx in range(len(rows[0])):
            max_width = max(len(str(row[col_idx])) for row in rows)
            max_widths.append(max_width)

        # Print header separator
        print("-" * (sum(max_widths) + len(max_widths) * 3 - 1))

        # Print each row
        for row_idx, row in enumerate(rows):
            formatted_row = []
            for col_idx, value in enumerate(row):
                formatted_value = str(value).ljust(max_widths[col_idx])
                formatted_row.append(formatted_value)
            print(f"| {' | '.join(formatted_row)} |")

            # Print separator after header
            if row_idx == 0:
                print("-" * (sum(max_widths) + len(max_widths) * 3 - 1))


def run_cli() -> int:
    """Main entry point for running the splurge-dsv CLI.

    The function handles argument parsing, basic path validation, constructing
    the ``DsvConfig`` and ``Dsv`` objects, and printing results in the
    requested format. Designed to be invoked from ``__main__``.

    Returns:
        Exit code (0 success, non-zero error codes on failure).

    Raises:
        SystemExit: On argument parser termination (handled internally).
    """
    try:
        args = parse_arguments()

        # Validate file path (kept local to maintain test compatibility)
        file_path = Path(args.file_path)
        if not file_path.exists():
            print(f"Error: File '{args.file_path}' not found.", file=sys.stderr)
            return 1

        if not file_path.is_file():
            print(f"Error: '{args.file_path}' is not a file.", file=sys.stderr)
            return 1

        # Build base config either from YAML file (if provided) or from CLI args
        base_params = {}
        if args.config:
            try:
                import yaml  # type: ignore

                cfg_path = Path(args.config)
                if not cfg_path.exists():
                    print(f"Error: Config file '{args.config}' not found.", file=sys.stderr)
                    return 1

                with cfg_path.open("r", encoding="utf-8") as fh:
                    file_cfg = yaml.safe_load(fh) or {}

                if not isinstance(file_cfg, dict):
                    print(f"Error: Config file '{args.config}' must contain a mapping/dictionary.", file=sys.stderr)
                    return 1

                base_params.update(file_cfg)
            except Exception as e:
                print(f"Error reading config file '{args.config}': {e}", file=sys.stderr)
                return 1

        # CLI args override YAML values when provided. Build the parameter map
        cli_params = {
            "delimiter": args.delimiter,
            "strip": not args.no_strip,
            "bookend": args.bookend,
            "bookend_strip": not args.no_bookend_strip,
            "encoding": args.encoding,
            "skip_header_rows": args.skip_header,
            "skip_footer_rows": args.skip_footer,
            "chunk_size": args.chunk_size,
            "detect_columns": args.detect_columns,
            "raise_on_missing_columns": args.raise_on_missing_columns,
            "raise_on_extra_columns": args.raise_on_extra_columns,
            "max_detect_chunks": args.max_detect_chunks,
            "skip_empty_lines": args.skip_empty_lines,
        }

        # Merge: start from file (if any), then overlay CLI-provided values
        merged = {**base_params, **{k: v for k, v in cli_params.items() if v is not None}}

        # Create configuration and Dsv instance for parsing
        try:
            config = DsvConfig.from_params(**merged)
        except Exception as e:
            print(f"Error building configuration: {e}", file=sys.stderr)
            return 1
        dsv = Dsv(config)
        dsv = Dsv(config)

        # Parse the file
        if args.stream:
            if args.output_format != "json":
                print(f"Streaming file '{args.file_path}' with delimiter '{args.delimiter}'...")
            chunk_count = 0
            total_rows = 0

            try:
                for chunk in dsv.parse_file_stream(file_path):
                    chunk_count += 1
                    total_rows += len(chunk)

                    if args.output_format == "json":
                        print(json.dumps(chunk, ensure_ascii=False))
                    elif args.output_format == "ndjson":
                        for row in chunk:
                            print(json.dumps(row, ensure_ascii=False))
                    else:
                        print(f"Chunk {chunk_count}: {len(chunk)} rows")
                        print_results(chunk, args.delimiter)
                        print()
            except Exception as e:
                print(f"Error during streaming: {e}", file=sys.stderr)
                import traceback

                traceback.print_exc(file=sys.stderr)
                return 1

            if args.output_format not in ["json", "ndjson"]:
                print(f"Total: {total_rows} rows in {chunk_count} chunks")
        else:
            if args.output_format not in ["json", "ndjson"]:
                print(f"Parsing file '{args.file_path}' with delimiter '{args.delimiter}'...")
            rows = dsv.parse_file(file_path)

            if args.output_format == "json":
                print(json.dumps(rows, ensure_ascii=False))
            elif args.output_format == "ndjson":
                for row in rows:
                    print(json.dumps(row, ensure_ascii=False))
            else:
                print(f"Parsed {len(rows)} rows")
                print_results(rows, args.delimiter)

        return 0

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        return 130
    except SplurgeDsvError as e:
        print(f"Error: {e.message}", file=sys.stderr)
        if e.details:
            print(f"Details: {e.details}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1
