"""
Integration tests for CLI JSON output.
"""

# Standard library imports
import json
import sys
from pathlib import Path
import subprocess

# Third-party imports
import pytest


@pytest.fixture
def cli_command() -> str:
    """Return the CLI invocation."""
    return f"{sys.executable} -m splurge_dsv"


def run_cli(cli_command: str, args: list[str]) -> tuple[int, str, str]:
    try:
        cmd_parts = cli_command.split() + args
        result = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=30)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", f"Command execution error: {e}"


def test_cli_json_output_basic(cli_command: str, tmp_path: Path) -> None:
    """CLI should output valid JSON when requested."""
    content = "a,b,c\nd,e,f"
    file_path = tmp_path / "data.csv"
    file_path.write_text(content)

    code, stdout, stderr = run_cli(cli_command, [str(file_path), "--delimiter", ",", "--output-format", "json"])

    assert code == 0, f"stderr: {stderr}"
    parsed = json.loads(stdout)
    assert parsed == [["a", "b", "c"], ["d", "e", "f"]]


def test_cli_json_output_streaming(cli_command: str, tmp_path: Path) -> None:
    """CLI should output valid JSON per chunk in streaming mode."""
    lines = ["a,b,c"] + [f"{i},{i+1},{i+2}" for i in range(0, 10, 3)]
    file_path = tmp_path / "data.csv"
    file_path.write_text("\n".join(lines))

    code, stdout, stderr = run_cli(
        cli_command,
        [str(file_path), "--delimiter", ",", "--stream", "--chunk-size", "2", "--output-format", "json"],
    )

    assert code == 0, f"stderr: {stderr}"
    # Output will contain multiple JSON arrays, one per chunk, separated by newlines
    chunks = [line for line in stdout.splitlines() if line and not line.startswith("Streaming ")]
    # Each chunk should be valid JSON list
    for chunk in chunks:
        json_chunk = json.loads(chunk)
        assert isinstance(json_chunk, list)

