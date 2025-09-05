"""
Example usage of the splurge-dsv CLI from Python.

This script demonstrates how to:
- Invoke the CLI for table output
- Invoke the CLI for JSON output and parse the result
- Use streaming mode with JSON output and parse chunks
"""

# Standard library imports
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def create_sample_csv_file(target_path: Path) -> None:
    """Create a small CSV file for demonstration purposes."""
    content = """name,age,city\nJohn Doe,30,New York\nJane Smith,25,Los Angeles"""
    target_path.write_text(content)


def run_cli_command(args: list[str]) -> tuple[int, str, str]:
    """Run the splurge-dsv CLI and capture outputs.

    Returns (returncode, stdout, stderr).
    """
    cmd_parts = [sys.executable, "-m", "splurge_dsv", *args]
    result = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=30)
    return result.returncode, result.stdout, result.stderr


def demonstrate_table_output(data_file: Path) -> None:
    """Show formatted table output from the CLI."""
    print("\n=== Table Output ===")
    code, stdout, stderr = run_cli_command([str(data_file), "--delimiter", ","])
    if code != 0:
        print(f"Error (table): {stderr}")
        return
    print(stdout)


def demonstrate_json_output(data_file: Path) -> None:
    """Show JSON output and parse it back into Python objects."""
    print("\n=== JSON Output ===")
    code, stdout, stderr = run_cli_command([str(data_file), "--delimiter", ",", "--output-format", "json"])
    if code != 0:
        print(f"Error (json): {stderr}")
        return
    rows = json.loads(stdout)
    print(f"Parsed {len(rows)} rows from JSON. First row: {rows[0] if rows else '[]'}")


def demonstrate_streaming_json_output(data_file: Path) -> None:
    """Show streaming mode with JSON output (one JSON array per chunk)."""
    print("\n=== Streaming JSON Output ===")
    code, stdout, stderr = run_cli_command(
        [
            str(data_file),
            "--delimiter",
            ",",
            "--stream",
            "--chunk-size",
            "1",
            "--output-format",
            "json",
        ]
    )
    if code != 0:
        print(f"Error (stream json): {stderr}")
        return

    # Each non-empty line in stdout is a JSON array chunk
    json_lines = [line for line in stdout.splitlines() if line.strip()]
    print(f"Received {len(json_lines)} JSON chunk(s)")
    for idx, line in enumerate(json_lines, start=1):
        chunk = json.loads(line)
        print(f"Chunk {idx}: {chunk}")


def main() -> int:
    """Entry point for the CLI usage demonstration."""
    examples_dir = Path(__file__).resolve().parent
    data_file = examples_dir / "example.csv"

    create_sample_csv_file(data_file)

    try:
        demonstrate_table_output(data_file)
        demonstrate_json_output(data_file)
        demonstrate_streaming_json_output(data_file)
        return 0
    finally:
        # Clean up the example file
        try:
            if data_file.exists():
                data_file.unlink()
        except OSError:
            # Non-fatal if cleanup fails in an example script
            pass


if __name__ == "__main__":
    raise SystemExit(main())
