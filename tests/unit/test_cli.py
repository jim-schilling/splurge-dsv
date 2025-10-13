"""
Tests for the CLI module.

Tests the command-line interface functionality including argument parsing,
result formatting, and error handling.
"""

# Standard library imports
import sys
from pathlib import Path

# Third-party imports
import pytest

# Local imports
from splurge_dsv.cli import parse_arguments, print_results, run_cli


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

    def test_main_success_parse_file(self, tmp_path: Path, monkeypatch, capsys) -> None:
        """Test successful file parsing via end-to-end CLI invocation."""
        # Create a small CSV for the CLI to parse
        data_file = tmp_path / "data.csv"
        data_file.write_text("h1,h2\n1,2\n", encoding="utf-8")

        # Use the CLI with real argv (end-to-end)
        monkeypatch.setattr("sys.argv", ["splurge-dsv", str(data_file), "--delimiter", ","])

        # Run CLI and capture output
        rc = run_cli()
        captured = capsys.readouterr()
        assert rc == 0
        assert "Parsed" in captured.out or "Chunk" in captured.out

    def test_main_file_not_found(self, tmp_path: Path, monkeypatch, capsys) -> None:
        """Test handling of non-existent file using real argv."""
        missing = tmp_path / "does_not_exist.csv"
        monkeypatch.setattr("sys.argv", ["splurge-dsv", str(missing), "--delimiter", ","])
        rc = run_cli()
        captured = capsys.readouterr()
        assert rc == 1
        assert "not found" in captured.err.lower()

    def test_main_not_a_file(self, tmp_path: Path, monkeypatch, capsys) -> None:
        """Test handling of path that is not a file using end-to-end argv."""
        p = tmp_path / "somedir"
        p.mkdir()
        monkeypatch.setattr("sys.argv", ["splurge-dsv", str(p), "--delimiter", ","])
        rc = run_cli()
        captured = capsys.readouterr()
        assert rc == 1
        assert "not a file" in captured.err.lower()

    def test_main_streaming_mode(self, tmp_path: Path, monkeypatch, capsys) -> None:
        """Test streaming mode end-to-end using a real file and stream flag."""
        data_file = tmp_path / "stream.csv"
        rows = ["h1,h2"] + [f"v{i},w{i}" for i in range(1, 5)]
        data_file.write_text("\n".join(rows) + "\n", encoding="utf-8")

        monkeypatch.setattr("sys.argv", ["splurge-dsv", str(data_file), "--delimiter", ",", "--stream"])
        rc = run_cli()
        captured = capsys.readouterr()
        assert rc == 0
        assert "Chunk" in captured.out or "Total:" in captured.out

    def test_main_splurge_error(self, mocker) -> None:
        """Test handling of SplurgeDsvError by provoking a column-mismatch.

        Create a real temporary CSV where one row has an extra column. Invoke
        the CLI end-to-end with --raise-on-extra-columns so the library raises
        a SplurgeDsvColumnMismatchError (a subclass of SplurgeDsvError) and
        the CLI should return exit code 1 and print an error to stderr.
        """
        # create a temp file with inconsistent columns (second data row has 3 cols)
        from pathlib import Path

        p = Path.cwd() / "test_cli_extra_cols.csv"
        try:
            p.write_text("a,b\n1,2\n1,2,3\n", encoding="utf-8")

            # Use real argv to invoke run_cli end-to-end
            import sys

            monkeypatch = __import__("pytest").MonkeyPatch()
            try:
                monkeypatch.setattr(
                    sys, "argv", ["splurge-dsv", str(p), "--delimiter", ",", "--raise-on-extra-columns"]
                )
                rc = run_cli()
            finally:
                monkeypatch.undo()

            # CLI should report an error and return non-zero
            assert rc == 1
        finally:
            try:
                p.unlink()
            except Exception:
                pass

    def test_main_keyboard_interrupt(self, tmp_path: Path, monkeypatch) -> None:
        """Test handling of keyboard interrupt by causing the reader to raise KeyboardInterrupt.

        We monkeypatch only the SafeTextFileReader to raise KeyboardInterrupt when read() is called.
        The CLI should catch KeyboardInterrupt and return exit code 130.
        """
        p = tmp_path / "kb.csv"
        p.write_text("a,b\n1,2\n", encoding="utf-8")

        class FakeReader:
            def __init__(self, *args, **kwargs):
                pass

            def read(self):
                raise KeyboardInterrupt()

        # Patch the SafeTextFileReader used by DsvHelper
        import splurge_dsv.dsv_helper as dh

        monkeypatch.setattr(dh.safe_io_text_file_reader, "SafeTextFileReader", FakeReader)

        # Run CLI with real argv
        monkeypatch.setattr("sys.argv", ["splurge-dsv", str(p), "--delimiter", ","])
        rc = run_cli()
        assert rc == 130

    def test_main_unexpected_error(self, tmp_path: Path, monkeypatch) -> None:
        """Test handling of unexpected errors by causing the reader to raise a runtime error.

        The reader's unexpected exception should be wrapped by DsvHelper into a
        SplurgeDsvError and the CLI should return exit code 1.
        """
        p = tmp_path / "boom.csv"
        p.write_text("a,b\n1,2\n", encoding="utf-8")

        class FakeReader2:
            def __init__(self, *args, **kwargs):
                pass

            def read(self):
                raise RuntimeError("boom")

        import splurge_dsv.dsv_helper as dh

        monkeypatch.setattr(dh.safe_io_text_file_reader, "SafeTextFileReader", FakeReader2)

        monkeypatch.setattr("sys.argv", ["splurge-dsv", str(p), "--delimiter", ","])
        rc = run_cli()
        assert rc == 1
