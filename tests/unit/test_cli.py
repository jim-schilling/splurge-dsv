"""
Tests for the CLI module.

Tests the command-line interface functionality including argument parsing,
result formatting, and error handling.
"""

# Standard library imports
import sys

# Third-party imports
import pytest

# Local imports
from splurge_dsv.cli import parse_arguments, print_results, run_cli
from splurge_dsv.exceptions import SplurgeDsvError


class TestCliParseArguments:
    """Test argument parsing functionality."""

    def test_parse_arguments_basic(self, mocker) -> None:
        """Test basic argument parsing."""
        mocker.patch.object(sys, "argv", ["script", "test.csv", "--delimiter", ","])
        args = parse_arguments()
        assert args.file_path == "test.csv"
        assert args.delimiter == ","
        assert args.encoding == "utf-8"
        assert args.skip_header == 0
        assert args.skip_footer == 0
        assert not args.stream
        assert args.chunk_size == 500

    def test_parse_arguments_with_options(self, mocker) -> None:
        """Test argument parsing with various options."""
        mocker.patch.object(
            sys,
            "argv",
            [
                "script",
                "test.tsv",
                "--delimiter",
                "\t",
                "--encoding",
                "latin-1",
                "--skip-header",
                "2",
                "--skip-footer",
                "1",
                "--stream",
                "--chunk-size",
                "100",
            ],
        )
        args = parse_arguments()
        assert args.file_path == "test.tsv"
        assert args.delimiter == "\t"
        assert args.encoding == "latin-1"
        assert args.skip_header == 2
        assert args.skip_footer == 1
        assert args.stream
        assert args.chunk_size == 100

    def test_parse_arguments_with_output_format(self, mocker) -> None:
        """Test argument parsing with output format option."""
        mocker.patch.object(
            sys,
            "argv",
            [
                "script",
                "test.csv",
                "--delimiter",
                ",",
                "--output-format",
                "json",
            ],
        )
        args = parse_arguments()
        assert args.file_path == "test.csv"
        assert args.delimiter == ","
        assert args.output_format == "json"

    def test_parse_arguments_with_bookend(self, mocker) -> None:
        """Test argument parsing with bookend option."""
        mocker.patch.object(sys, "argv", ["script", "test.txt", "--delimiter", "|", "--bookend", '"'])
        args = parse_arguments()
        assert args.bookend == '"'

    def test_parse_arguments_with_new_flags(self, mocker) -> None:
        """Test new CLI flags are parsed correctly."""
        mocker.patch.object(
            sys,
            "argv",
            [
                "script",
                "test.csv",
                "--delimiter",
                ",",
                "--detect-columns",
                "--raise-on-missing-columns",
                "--raise-on-extra-columns",
            ],
        )
        args = parse_arguments()
        assert args.detect_columns
        assert args.raise_on_missing_columns
        assert args.raise_on_extra_columns

    def test_parse_arguments_with_no_strip_options(self, mocker) -> None:
        """Test argument parsing with no-strip options."""
        mocker.patch.object(sys, "argv", ["script", "test.csv", "--delimiter", ",", "--no-strip", "--no-bookend-strip"])
        args = parse_arguments()
        assert args.no_strip
        assert args.no_bookend_strip


class TestCliPrintResults:
    """Test result printing functionality."""

    def test_print_results_empty(self, capsys: pytest.CaptureFixture) -> None:
        """Test printing empty results."""
        print_results([], ",")
        captured = capsys.readouterr()
        assert captured.out == "No data found.\n"

    def test_print_results_single_row(self, capsys: pytest.CaptureFixture) -> None:
        """Test printing single row results."""
        rows = [["a", "b", "c"]]
        print_results(rows, ",")
        captured = capsys.readouterr()
        assert "| a | b | c |" in captured.out
        assert "---" in captured.out

    def test_print_results_multiple_rows(self, capsys: pytest.CaptureFixture) -> None:
        """Test printing multiple row results."""
        rows = [["header1", "header2"], ["value1", "value2"]]
        print_results(rows, ",")
        captured = capsys.readouterr()
        assert "| header1 | header2 |" in captured.out
        assert "| value1  | value2  |" in captured.out

    def test_print_results_with_different_lengths(self, capsys: pytest.CaptureFixture) -> None:
        """Test printing results with different column lengths."""
        rows = [["short", "very_long_column"], ["longer", "short"]]
        print_results(rows, ",")
        captured = capsys.readouterr()
        assert "| short  | very_long_column |" in captured.out
        assert "| longer | short            |" in captured.out


class TestCliMain:
    """Test main CLI functionality."""

    def test_main_success_parse_file(self, mocker) -> None:
        """Test successful file parsing."""
        mock_path = mocker.patch("splurge_dsv.cli.Path")
        mock_dsv = mocker.patch("splurge_dsv.cli.Dsv")

        # Mock file path validation
        mock_path_instance = mocker.MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_file.return_value = True
        mock_path.return_value = mock_path_instance

        # Mock Dsv instance and its parse_file method
        mock_dsv_instance = mocker.MagicMock()
        mock_dsv_instance.parse_file.return_value = [["header1", "header2"], ["value1", "value2"]]
        mock_dsv.return_value = mock_dsv_instance

        # Mock command line arguments
        mock_parse = mocker.patch("splurge_dsv.cli.parse_arguments")
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
        mock_args.output_format = "table"
        mock_parse.return_value = mock_args

        # Mock print_results to avoid output during testing
        mocker.patch("splurge_dsv.cli.print_results")
        result = run_cli()

        assert result == 0
        mock_dsv_instance.parse_file.assert_called_once()

    def test_main_file_not_found(self, mocker) -> None:
        """Test handling of non-existent file."""
        mock_path = mocker.patch("splurge_dsv.cli.Path")
        mock_path_instance = mocker.MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance

        mock_parse = mocker.patch("splurge_dsv.cli.parse_arguments")
        mock_args = mocker.MagicMock()
        mock_args.file_path = "nonexistent.csv"
        mock_args.delimiter = ","
        mock_parse.return_value = mock_args

        mock_print = mocker.patch("splurge_dsv.cli.print")
        result = run_cli()

        assert result == 1
        mock_print.assert_called()

    def test_main_not_a_file(self, mocker) -> None:
        """Test handling of path that is not a file."""
        mock_path = mocker.patch("splurge_dsv.cli.Path")
        mock_path_instance = mocker.MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_file.return_value = False
        mock_path.return_value = mock_path_instance

        mock_parse = mocker.patch("splurge_dsv.cli.parse_arguments")
        mock_args = mocker.MagicMock()
        mock_args.file_path = "directory/"
        mock_args.delimiter = ","
        mock_parse.return_value = mock_args

        mock_print = mocker.patch("splurge_dsv.cli.print")
        result = run_cli()

        assert result == 1
        mock_print.assert_called()

    def test_main_streaming_mode(self, mocker) -> None:
        """Test streaming mode functionality."""
        mock_path = mocker.patch("splurge_dsv.cli.Path")
        mock_dsv = mocker.patch("splurge_dsv.cli.Dsv")

        # Mock file path validation
        mock_path_instance = mocker.MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_file.return_value = True
        mock_path.return_value = mock_path_instance

        # Mock Dsv instance and its parse_file_stream method
        mock_dsv_instance = mocker.MagicMock()
        mock_dsv_instance.parse_file_stream.return_value = iter([[["a", "b"], ["c", "d"]]])
        mock_dsv.return_value = mock_dsv_instance

        # Mock command line arguments
        mock_parse = mocker.patch("splurge_dsv.cli.parse_arguments")
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
        mock_args.output_format = "table"
        mock_parse.return_value = mock_args

        # Mock print_results to avoid output during testing
        mocker.patch("splurge_dsv.cli.print_results")
        mocker.patch("splurge_dsv.cli.print")
        result = run_cli()

        assert result == 0

    def test_main_splurge_error(self, mocker) -> None:
        """Test handling of SplurgeDsvError."""
        mock_path = mocker.patch("splurge_dsv.cli.Path")
        mock_dsv = mocker.patch("splurge_dsv.cli.Dsv")

        # Mock file path validation
        mock_path_instance = mocker.MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_file.return_value = True
        mock_path.return_value = mock_path_instance

        # Mock Dsv instance and its parse_file method to raise an error
        mock_dsv_instance = mocker.MagicMock()
        mock_dsv_instance.parse_file.side_effect = SplurgeDsvError("Test error", details="Test details")
        mock_dsv.return_value = mock_dsv_instance

        # Mock command line arguments
        mock_parse = mocker.patch("splurge_dsv.cli.parse_arguments")
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
        mock_args.output_format = "table"
        mock_parse.return_value = mock_args

        mock_print = mocker.patch("splurge_dsv.cli.print")
        result = run_cli()

        assert result == 1
        mock_print.assert_called()

    def test_main_keyboard_interrupt(self, mocker) -> None:
        """Test handling of keyboard interrupt."""
        mock_path = mocker.patch("splurge_dsv.cli.Path")

        # Mock file path validation
        mock_path_instance = mocker.MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_file.return_value = True
        mock_path.return_value = mock_path_instance

        # Mock command line arguments
        mock_parse = mocker.patch("splurge_dsv.cli.parse_arguments")
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
        mock_args.output_format = "table"
        mock_parse.return_value = mock_args

        # Mock Dsv instance and its parse_file method to raise KeyboardInterrupt
        mock_dsv = mocker.patch("splurge_dsv.cli.Dsv")
        mock_dsv_instance = mocker.MagicMock()
        mock_dsv_instance.parse_file.side_effect = KeyboardInterrupt()
        mock_dsv.return_value = mock_dsv_instance

        mock_print = mocker.patch("splurge_dsv.cli.print")
        result = run_cli()

        assert result == 130
        mock_print.assert_called()

    def test_main_unexpected_error(self, mocker) -> None:
        """Test handling of unexpected errors."""
        mock_path = mocker.patch("splurge_dsv.cli.Path")

        # Mock file path validation
        mock_path_instance = mocker.MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_file.return_value = True
        mock_path.return_value = mock_path_instance

        # Mock command line arguments
        mock_parse = mocker.patch("splurge_dsv.cli.parse_arguments")
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
        mock_args.output_format = "table"
        mock_parse.return_value = mock_args

        # Mock Dsv instance and its parse_file method to raise an unexpected error
        mock_dsv = mocker.patch("splurge_dsv.cli.Dsv")
        mock_dsv_instance = mocker.MagicMock()
        mock_dsv_instance.parse_file.side_effect = RuntimeError("Unexpected error")
        mock_dsv.return_value = mock_dsv_instance

        mock_print = mocker.patch("splurge_dsv.cli.print")
        result = run_cli()

        assert result == 1
        mock_print.assert_called()
