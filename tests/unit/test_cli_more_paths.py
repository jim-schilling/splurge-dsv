"""
Additional CLI tests covering remaining flags and --version behavior.
"""

import sys

import pytest

from splurge_dsv import __version__
from splurge_dsv.cli import parse_arguments


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
    # Patch parse_arguments to simulate json output mode and ndjson
    mock_parse = mocker.patch("splurge_dsv.cli.parse_arguments")
    mock_path = mocker.patch("splurge_dsv.cli.Path")
    mock_dsv = mocker.patch("splurge_dsv.cli.Dsv")

    # Prepare path
    mock_path_instance = mocker.MagicMock()
    mock_path_instance.exists.return_value = True
    mock_path_instance.is_file.return_value = True
    mock_path.return_value = mock_path_instance

    # JSON mode: parse_file returns rows
    mock_args = mocker.MagicMock()
    mock_args.file_path = "test.csv"
    mock_args.delimiter = ","
    mock_args.no_strip = False
    mock_args.bookend = None
    mock_args.no_bookend_strip = False
    mock_args.encoding = "utf-8"
    mock_args.skip_header = 0
    mock_args.skip_footer = 0
    mock_args.stream = False
    mock_args.chunk_size = 500
    mock_args.output_format = "json"
    mock_parse.return_value = mock_args

    mock_dsv_instance = mocker.MagicMock()
    mock_dsv_instance.parse_file.return_value = [["a", "b"], ["c", "d"]]
    mock_dsv.return_value = mock_dsv_instance

    from splurge_dsv.cli import run_cli

    result = run_cli()
    assert result == 0
    captured = capsys.readouterr()
    # Should print a JSON array
    assert "[" in captured.out

    # NDJSON mode: stream rows via parse_file
    mock_args.output_format = "ndjson"
    mock_dsv_instance.parse_file.return_value = [["x", "y"], ["z", "w"]]
    result = run_cli()
    assert result == 0
    captured = capsys.readouterr()
    # Should print ndjson lines
    assert "\n" in captured.out


def test_run_cli_stream_json_suppresses_progress_prints(mocker, capsys):
    mock_parse = mocker.patch("splurge_dsv.cli.parse_arguments")
    mock_path = mocker.patch("splurge_dsv.cli.Path")
    mock_dsv = mocker.patch("splurge_dsv.cli.Dsv")

    # Prepare path
    mock_path_instance = mocker.MagicMock()
    mock_path_instance.exists.return_value = True
    mock_path_instance.is_file.return_value = True
    mock_path.return_value = mock_path_instance

    # Streaming + json output should not print the "Streaming file" progress line
    mock_args = mocker.MagicMock()
    mock_args.file_path = "test.csv"
    mock_args.delimiter = ","
    mock_args.no_strip = False
    mock_args.bookend = None
    mock_args.no_bookend_strip = False
    mock_args.encoding = "utf-8"
    mock_args.skip_header = 0
    mock_args.skip_footer = 0
    mock_args.stream = True
    mock_args.chunk_size = 500
    mock_args.output_format = "json"
    mock_parse.return_value = mock_args

    # Dsv.parse_file_stream yields chunks
    mock_dsv_instance = mocker.MagicMock()
    mock_dsv_instance.parse_file_stream.return_value = iter([[["a", "b"]]])
    mock_dsv.return_value = mock_dsv_instance

    from splurge_dsv.cli import run_cli

    result = run_cli()
    assert result == 0
    captured = capsys.readouterr()
    # No progress string when json
    assert "Streaming file" not in captured.out


def test_version_flag_shows_version(monkeypatch, capsys):
    # Run parse_arguments with --version should trigger SystemExit with 0
    monkeypatch.setattr(sys, "argv", ["script", "--version"])
    with pytest.raises(SystemExit) as exc:
        parse_arguments()
    assert exc.value.code == 0
    # argparse handles printing version, so we just ensure __version__ is set
    assert isinstance(__version__, str)
