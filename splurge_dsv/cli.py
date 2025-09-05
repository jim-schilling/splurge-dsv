"""
Command-line interface for splurge-dsv.

This module provides a command-line interface for the splurge-dsv library,
allowing users to parse DSV files from the command line.

Copyright (c) 2025 Jim Schilling

This module is licensed under the MIT License.

Please preserve this header and all related material when sharing!
"""

# Standard library imports
import argparse
import json
import sys
from pathlib import Path

# Local imports
from splurge_dsv import __version__
from splurge_dsv.dsv_helper import DsvHelper
from splurge_dsv.exceptions import SplurgeDsvError


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Parse DSV (Delimited String Values) files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m splurge_dsv data.csv --delimiter ,
  python -m splurge_dsv data.tsv --delimiter "\\t"
  python -m splurge_dsv data.txt --delimiter "|" --bookend '"'
        """,
    )

    parser.add_argument("file_path", type=str, help="Path to the DSV file to parse")

    parser.add_argument("--delimiter", "-d", type=str, required=True, help="Delimiter character to use for parsing")

    parser.add_argument("--bookend", "-b", type=str, help="Bookend character for text fields (e.g., '\"')")

    parser.add_argument("--no-strip", action="store_true", help="Don't strip whitespace from values")

    parser.add_argument("--no-bookend-strip", action="store_true", help="Don't strip whitespace from bookends")

    parser.add_argument("--encoding", "-e", type=str, default="utf-8", help="File encoding (default: utf-8)")

    parser.add_argument("--skip-header", type=int, default=0, help="Number of header rows to skip (default: 0)")

    parser.add_argument("--skip-footer", type=int, default=0, help="Number of footer rows to skip (default: 0)")

    parser.add_argument(
        "--stream", "-s", action="store_true", help="Stream the file in chunks instead of loading entirely into memory"
    )

    parser.add_argument("--chunk-size", type=int, default=500, help="Chunk size for streaming (default: 500)")

    parser.add_argument(
        "--output-format",
        choices=["table", "json"],
        default="table",
        help="Output format for results (default: table)",
    )

    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    return parser.parse_args()


def print_results(rows: list[list[str]], delimiter: str) -> None:
    """Print parsed results in a formatted way."""
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
    """Run the command-line interface for DSV file parsing.

    This function serves as the main entry point for the splurge-dsv CLI tool.
    It parses command-line arguments, validates the input file, and processes
    DSV files according to the specified options. Supports both regular parsing
    and streaming modes for large files.

    Returns:
        int: Exit code indicating success or failure:
            - 0: Success
            - 1: Generic error (file not found, parsing error, etc.)
            - 2: Invalid arguments
            - 130: Operation interrupted (Ctrl+C)

    Raises:
        SystemExit: Terminates the program with the appropriate exit code.
            This is handled internally and should not be caught by callers.
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

        # Parse the file
        if args.stream:
            if args.output_format != "json":
                print(f"Streaming file '{args.file_path}' with delimiter '{args.delimiter}'...")
            chunk_count = 0
            total_rows = 0

            for chunk in DsvHelper.parse_stream(
                file_path,
                delimiter=args.delimiter,
                strip=not args.no_strip,
                bookend=args.bookend,
                bookend_strip=not args.no_bookend_strip,
                encoding=args.encoding,
                skip_header_rows=args.skip_header,
                skip_footer_rows=args.skip_footer,
                chunk_size=args.chunk_size,
            ):
                chunk_count += 1
                total_rows += len(chunk)
                if args.output_format == "json":
                    print(json.dumps(chunk, ensure_ascii=False))
                else:
                    print(f"Chunk {chunk_count}: {len(chunk)} rows")
                    print_results(chunk, args.delimiter)
                    print()

            if args.output_format != "json":
                print(f"Total: {total_rows} rows in {chunk_count} chunks")
        else:
            if args.output_format != "json":
                print(f"Parsing file '{args.file_path}' with delimiter '{args.delimiter}'...")
            rows = DsvHelper.parse_file(
                file_path,
                delimiter=args.delimiter,
                strip=not args.no_strip,
                bookend=args.bookend,
                bookend_strip=not args.no_bookend_strip,
                encoding=args.encoding,
                skip_header_rows=args.skip_header,
                skip_footer_rows=args.skip_footer,
            )

            if args.output_format == "json":
                print(json.dumps(rows, ensure_ascii=False))
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
