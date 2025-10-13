"""
Additional CLI tests covering remaining flags and --version behavior.
"""

import sys
from pathlib import Path

import pytest

from splurge_dsv import __version__
from splurge_dsv.cli import parse_arguments, run_cli


def test_parse_arguments_max_detect_chunks_and_output_formats(mocker):
    mocker.patch.object(
        sys,
        "argv",
        [
            "script",
            "test.csv",
            "--delimiter",
            ",",
            "--max-detect-chunks",
            "5",
            "--output-format",
            "ndjson",
        ],
    )
    args = parse_arguments()
    assert args.max_detect_chunks == 5
    assert args.output_format == "ndjson"


def test_run_cli_json_and_ndjson_modes(mocker, capsys):
    # End-to-end: create a temp file and run run_cli in json and ndjson modes
    # JSON mode prints a single JSON array
    td = Path("tmp")
    td.mkdir(exist_ok=True)
    p = td / "json_mode.csv"
    p.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")

    monkeypatch = __import__("pytest").MonkeyPatch()
    try:
        monkeypatch.setattr(sys, "argv", ["splurge-dsv", str(p), "--delimiter", ",", "--output-format", "json"])
        rc = run_cli()
        assert rc == 0
        captured = capsys.readouterr()
        assert "[" in captured.out

        # NDJSON mode prints one JSON object per line
        monkeypatch.setattr(sys, "argv", ["splurge-dsv", str(p), "--delimiter", ",", "--output-format", "ndjson"])
        rc = run_cli()
        assert rc == 0
        captured = capsys.readouterr()
        # Should contain multiple lines
        assert "\n" in captured.out
    finally:
        monkeypatch.undo()


def test_run_cli_stream_json_suppresses_progress_prints(mocker, capsys):
    # End-to-end: create a file large enough to stream and run with --stream --output-format json
    td = Path("tmp")
    td.mkdir(exist_ok=True)
    p = td / "stream_json.csv"
    rows = ["h1,h2"] + [f"v{i},w{i}" for i in range(1, 20)]
    p.write_text("\n".join(rows) + "\n", encoding="utf-8")

    monkeypatch = __import__("pytest").MonkeyPatch()
    try:
        monkeypatch.setattr(
            sys, "argv", ["splurge-dsv", str(p), "--delimiter", ",", "--stream", "--output-format", "json"]
        )
        rc = run_cli()
        assert rc == 0
        captured = capsys.readouterr()
        assert "Streaming file" not in captured.out
    finally:
        monkeypatch.undo()


def test_version_flag_shows_version(monkeypatch, capsys):
    # Run parse_arguments with --version should trigger SystemExit with 0
    monkeypatch.setattr(sys, "argv", ["script", "--version"])
    with pytest.raises(SystemExit) as exc:
        parse_arguments()
    assert exc.value.code == 0
    # argparse handles printing version, so we just ensure __version__ is set
    assert isinstance(__version__, str)
