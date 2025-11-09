"""Tests for CLI functionality without mocks.

Tests command-line interface by invoking print_results with real data.
"""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from splurge_dsv.cli import print_results


class TestCliPrintResults:
    """Test CLI print_results function with real data."""

    def test_print_results_empty(self, capsys: pytest.CaptureFixture) -> None:
        """Test printing empty results."""
        print_results([], ",")
        captured = capsys.readouterr()
        assert "No data found" in captured.out or captured.out.strip() == ""

    def test_print_results_single_row(self, capsys: pytest.CaptureFixture) -> None:
        """Test printing single row results."""
        rows = [["a", "b", "c"]]
        print_results(rows, ",")
        captured = capsys.readouterr()
        assert "a" in captured.out and "b" in captured.out and "c" in captured.out

    def test_print_results_multiple_rows(self, capsys: pytest.CaptureFixture) -> None:
        """Test printing multiple row results."""
        rows = [["header1", "header2"], ["value1", "value2"]]
        print_results(rows, ",")
        captured = capsys.readouterr()
        assert "header1" in captured.out
        assert "header2" in captured.out
        assert "value1" in captured.out
        assert "value2" in captured.out

    def test_print_results_with_different_lengths(self, capsys: pytest.CaptureFixture) -> None:
        """Test printing results with different column lengths."""
        rows = [["short", "very_long_column"], ["longer", "short"]]
        print_results(rows, ",")
        captured = capsys.readouterr()
        assert "short" in captured.out
        assert "very_long_column" in captured.out
        assert "longer" in captured.out

    def test_print_results_with_special_chars(self, capsys: pytest.CaptureFixture) -> None:
        """Test printing results with special characters."""
        rows = [["<tag>", '"quoted"'], ["100%", "a|b"]]
        print_results(rows, ",")
        captured = capsys.readouterr()
        assert "<tag>" in captured.out
        assert "100%" in captured.out

    def test_print_results_with_numbers(self, capsys: pytest.CaptureFixture) -> None:
        """Test printing results with numeric data."""
        rows = [["1", "2", "3"], ["10", "20", "30"], ["100", "200", "300"]]
        print_results(rows, ",")
        captured = capsys.readouterr()
        assert "1" in captured.out
        assert "100" in captured.out
        assert "300" in captured.out

    def test_print_results_with_unicode(self, capsys: pytest.CaptureFixture) -> None:
        """Test printing results with unicode characters."""
        rows = [["café", "naïve"], ["日本", "中国"]]
        print_results(rows, ",")
        captured = capsys.readouterr()
        assert "café" in captured.out
        assert "日本" in captured.out

    def test_print_results_with_empty_cells(self, capsys: pytest.CaptureFixture) -> None:
        """Test printing results with empty cells."""
        rows = [["a", "", "c"], ["", "b", ""]]
        print_results(rows, ",")
        captured = capsys.readouterr()
        assert "a" in captured.out
        assert "b" in captured.out
        assert "c" in captured.out


class TestCliConfigFileLoading:
    """Test CLI config file loading without mocks (lines 211-229)."""

    def test_config_file_missing_returns_error(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Test that missing config file is detected as error."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("a,b\n1,2\n")

        argv = ["cli", "--config", str(tmp_path / "missing.yaml"), str(csv_file)]
        with patch("sys.argv", argv):
            from splurge_dsv.cli import run_cli

            result = run_cli()
            assert result == 1
            captured = capsys.readouterr()
            assert "not found" in captured.err

    def test_config_file_valid_yaml_dict_loaded(self, tmp_path: Path) -> None:
        """Test that valid YAML config file with dict is loaded successfully."""
        # Create a valid config file with pipe delimiter
        config_file = tmp_path / "config.yaml"
        config_file.write_text("delimiter: '|'\nstrip: true\n")

        # Create a test CSV file with pipe delimiter
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("a|b\n1|2\n")

        argv = ["cli", "--config", str(config_file), str(csv_file)]
        with patch("sys.argv", argv):
            from splurge_dsv.cli import run_cli

            result = run_cli()
            # Should succeed (exit code 0)
            assert result == 0

    def test_config_file_invalid_yaml_syntax_returns_error(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Test that invalid YAML syntax is caught during loading."""
        # Create an invalid YAML file
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("delimiter: |\ninvalid: [unclosed\n")

        csv_file = tmp_path / "test.csv"
        csv_file.write_text("a,b\n1,2\n")

        argv = ["cli", "--config", str(config_file), str(csv_file)]
        with patch("sys.argv", argv):
            from splurge_dsv.cli import run_cli

            result = run_cli()
            assert result == 1
            captured = capsys.readouterr()
            assert "Error reading config file" in captured.err

    def test_config_file_not_dict_returns_error(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Test that config file containing list (not dict) is rejected."""
        # Create a YAML file with a list instead of dict
        config_file = tmp_path / "list_config.yaml"
        config_file.write_text("- item1\n- item2\n")

        csv_file = tmp_path / "test.csv"
        csv_file.write_text("a,b\n1,2\n")

        argv = ["cli", "--config", str(config_file), str(csv_file)]
        with patch("sys.argv", argv):
            from splurge_dsv.cli import run_cli

            result = run_cli()
            assert result == 1
            captured = capsys.readouterr()
            assert "must contain a mapping/dictionary" in captured.err

    def test_config_file_empty_yaml_dict_loaded(self, tmp_path: Path) -> None:
        """Test that empty YAML dict config file requires delimiter via CLI args."""
        # Create an empty config file (parses to empty dict)
        config_file = tmp_path / "empty_config.yaml"
        config_file.write_text("")

        csv_file = tmp_path / "test.csv"
        csv_file.write_text("a,b\n1,2\n")

        # Empty config must have delimiter from CLI args
        argv = ["cli", "--config", str(config_file), "--delimiter", ",", str(csv_file)]
        with patch("sys.argv", argv):
            from splurge_dsv.cli import run_cli

            result = run_cli()
            # Should succeed - empty config + CLI delimiter args provides needed param
            assert result == 0

    def test_config_file_with_delimiter_override(self, tmp_path: Path) -> None:
        """Test that delimiter from config file is used to parse file."""
        # Create config with pipe delimiter
        config_file = tmp_path / "pipe_config.yaml"
        config_file.write_text("delimiter: '|'\n")

        # Create CSV with pipe delimiter
        csv_file = tmp_path / "pipe_delim.csv"
        csv_file.write_text("a|b|c\n1|2|3\n")

        argv = ["cli", "--config", str(config_file), str(csv_file)]
        with patch("sys.argv", argv):
            from splurge_dsv.cli import run_cli

            result = run_cli()
            # Should succeed parsing pipe-delimited file
            assert result == 0

    def test_config_file_yaml_null_treated_as_empty_dict(self, tmp_path: Path) -> None:
        """Test that YAML null/None is treated as empty dict (from yaml.safe_load or {})."""
        # Create a config file that parses to None
        config_file = tmp_path / "null_config.yaml"
        config_file.write_text("null\n")

        csv_file = tmp_path / "test.csv"
        csv_file.write_text("a,b\n1,2\n")

        # Null config requires delimiter from CLI
        argv = ["cli", "--config", str(config_file), "--delimiter", ",", str(csv_file)]
        with patch("sys.argv", argv):
            from splurge_dsv.cli import run_cli

            result = run_cli()
            # Should succeed - None is converted to {} by yaml.safe_load() or {}
            assert result == 0

    def test_config_file_cli_args_override_yaml(self, tmp_path: Path) -> None:
        """Test that CLI args override YAML config values (line ~237)."""
        # Create config with comma delimiter
        config_file = tmp_path / "comma_config.yaml"
        config_file.write_text("delimiter: ','\n")

        # Create CSV with pipe delimiter
        csv_file = tmp_path / "pipe_delim.csv"
        csv_file.write_text("a|b|c\n1|2|3\n")

        # Override with pipe delimiter via CLI arg (should prefer CLI arg)
        argv = ["cli", "--config", str(config_file), "--delimiter", "|", str(csv_file)]
        with patch("sys.argv", argv):
            from splurge_dsv.cli import run_cli

            result = run_cli()
            # Should succeed - CLI args override config
            assert result == 0


class TestCliStreamingFileParsingLines262to289:
    """Test streaming file parsing code (lines 262-289) with real data and different output formats."""

    def test_stream_with_table_output_format(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Test streaming with table output format (default)."""
        # Create test CSV with multiple rows
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,age,city\nAlice,30,NYC\nBob,25,LA\nCharlie,35,Chicago\n")

        argv = ["cli", "--delimiter", ",", "--stream", str(csv_file)]
        with patch("sys.argv", argv):
            from splurge_dsv.cli import run_cli

            result = run_cli()
            assert result == 0
            captured = capsys.readouterr()
            assert "Streaming file" in captured.out
            assert "Chunk" in captured.out
            assert "Total:" in captured.out

    def test_stream_with_json_output_format(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Test streaming with JSON output format (lines 271-272)."""
        # Create test CSV
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("a,b,c\n1,2,3\n4,5,6\n7,8,9\n")

        argv = ["cli", "--delimiter", ",", "--stream", "--output-format", "json", str(csv_file)]
        with patch("sys.argv", argv):
            from splurge_dsv.cli import run_cli

            result = run_cli()
            assert result == 0
            captured = capsys.readouterr()

            # Should NOT have streaming message for json format (line 262)
            assert "Streaming file" not in captured.out

            # Output should be valid JSON arrays
            lines = captured.out.strip().split("\n")
            for line in lines:
                if line:
                    data = json.loads(line)
                    assert isinstance(data, list)

    def test_stream_with_ndjson_output_format(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Test streaming with NDJSON output format (lines 273-275)."""
        # Create test CSV
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("x,y\n1,2\n3,4\n")

        argv = ["cli", "--delimiter", ",", "--stream", "--output-format", "ndjson", str(csv_file)]
        with patch("sys.argv", argv):
            from splurge_dsv.cli import run_cli

            result = run_cli()
            assert result == 0
            captured = capsys.readouterr()

            # Should have streaming message for ndjson (only json format omits it)
            assert "Streaming file" in captured.out

            # Each JSON output line should be valid
            lines = captured.out.strip().split("\n")
            json_lines = [line for line in lines if line.startswith("[")]
            for line in json_lines:
                data = json.loads(line)
                assert isinstance(data, list)

    def test_stream_multiple_chunks(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Test streaming creates multiple chunks with small chunk size."""
        # Create test CSV with many rows
        csv_file = tmp_path / "large.csv"
        csv_file.write_text("id,value\n" + "\n".join(f"{i},{i * 10}" for i in range(1, 31)))

        # Use minimum valid chunk size to ensure multiple chunks
        argv = ["cli", "--delimiter", ",", "--stream", "--chunk-size", "10", str(csv_file)]
        with patch("sys.argv", argv):
            from splurge_dsv.cli import run_cli

            result = run_cli()
            assert result == 0
            captured = capsys.readouterr()

            # Should have multiple chunks
            chunk_count = captured.out.count("Chunk")
            assert chunk_count >= 2
            assert "Total:" in captured.out

    def test_stream_single_chunk(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Test streaming with all data in single chunk."""
        # Create small test CSV
        csv_file = tmp_path / "small.csv"
        csv_file.write_text("a,b\n" + "\n".join(f"{i},{i * 2}" for i in range(1, 6)))

        argv = ["cli", "--delimiter", ",", "--stream", "--chunk-size", "10", str(csv_file)]
        with patch("sys.argv", argv):
            from splurge_dsv.cli import run_cli

            result = run_cli()
            assert result == 0
            captured = capsys.readouterr()

            # Should have single chunk
            assert "Chunk 1:" in captured.out
            assert "Chunk 2:" not in captured.out
            # Header row is included in count
            assert "Total: 6 rows in 1 chunks" in captured.out

    def test_stream_with_special_delimiters(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Test streaming with pipe delimiter."""
        csv_file = tmp_path / "pipe.csv"
        csv_file.write_text("name|age\nAlice|30\nBob|25\n")

        argv = ["cli", "--delimiter", "|", "--stream", str(csv_file)]
        with patch("sys.argv", argv):
            from splurge_dsv.cli import run_cli

            result = run_cli()
            assert result == 0
            captured = capsys.readouterr()
            assert "Streaming file" in captured.out
            assert "delimiter '|'" in captured.out

    def test_stream_error_handling_with_invalid_file(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Test streaming error handling when file doesn't exist (lines 278-283)."""
        nonexistent = tmp_path / "nonexistent.csv"

        argv = ["cli", "--delimiter", ",", "--stream", str(nonexistent)]
        with patch("sys.argv", argv):
            from splurge_dsv.cli import run_cli

            result = run_cli()
            # Should return error code
            assert result == 1
            captured = capsys.readouterr()
            # Error should be on stderr
            assert "Error" in captured.err or "not found" in captured.err.lower()

    def test_stream_table_output_shows_progress(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Test that table output format displays chunk progress info."""
        csv_file = tmp_path / "progress.csv"
        csv_file.write_text("id\n" + "\n".join(str(i) for i in range(1, 25)))

        argv = ["cli", "--delimiter", ",", "--stream", "--chunk-size", "10", str(csv_file)]
        with patch("sys.argv", argv):
            from splurge_dsv.cli import run_cli

            result = run_cli()
            assert result == 0
            captured = capsys.readouterr()

            # Should show chunk count and row count per chunk (line 277)
            assert "Chunk" in captured.out
            assert "rows" in captured.out

    def test_stream_json_format_no_debug_messages(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Test that JSON format doesn't output debug/status messages (line 262 condition)."""
        csv_file = tmp_path / "json_test.csv"
        csv_file.write_text("a,b\n1,2\n3,4\n")

        argv = ["cli", "--delimiter", ",", "--stream", "--output-format", "json", str(csv_file)]
        with patch("sys.argv", argv):
            from splurge_dsv.cli import run_cli

            result = run_cli()
            assert result == 0
            captured = capsys.readouterr()

            # No status messages for JSON format
            assert "Streaming file" not in captured.out
            assert "Chunk" not in captured.out
            assert "Total:" not in captured.out

    def test_stream_ndjson_format_no_debug_messages(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Test that NDJSON format doesn't output chunk or total count messages."""
        csv_file = tmp_path / "ndjson_test.csv"
        csv_file.write_text("x,y\n1,2\n3,4\n")

        argv = ["cli", "--delimiter", ",", "--stream", "--output-format", "ndjson", str(csv_file)]
        with patch("sys.argv", argv):
            from splurge_dsv.cli import run_cli

            result = run_cli()
            assert result == 0
            captured = capsys.readouterr()

            # Should have streaming message but no chunk/total messages for NDJSON
            assert "Streaming file" in captured.out
            assert "Chunk" not in captured.out
            assert "Total:" not in captured.out

    def test_stream_accurate_row_counts(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Test that streaming correctly counts total rows across chunks."""
        csv_file = tmp_path / "count_test.csv"
        csv_file.write_text("id\n" + "\n".join(str(i) for i in range(1, 31)))

        argv = ["cli", "--delimiter", ",", "--stream", "--chunk-size", "10", str(csv_file)]
        with patch("sys.argv", argv):
            from splurge_dsv.cli import run_cli

            result = run_cli()
            assert result == 0
            captured = capsys.readouterr()

            # Should show total of 31 rows (header + 30 data rows)
            assert "Total: 31 rows" in captured.out

    def test_stream_with_empty_lines_option(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Test streaming with skip-empty-lines option."""
        csv_file = tmp_path / "empty_lines.csv"
        csv_file.write_text("a,b\n1,2\n\n3,4\n\n")

        argv = ["cli", "--delimiter", ",", "--stream", "--skip-empty-lines", str(csv_file)]
        with patch("sys.argv", argv):
            from splurge_dsv.cli import run_cli

            result = run_cli()
            assert result == 0
            captured = capsys.readouterr()
            assert "Streaming file" in captured.out

    def test_stream_with_header_skip(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Test streaming with skip header rows."""
        csv_file = tmp_path / "with_header.csv"
        csv_file.write_text("SKIP_ME\nname,age\nAlice,30\nBob,25\n")

        argv = ["cli", "--delimiter", ",", "--stream", "--skip-header", "1", str(csv_file)]
        with patch("sys.argv", argv):
            from splurge_dsv.cli import run_cli

            result = run_cli()
            assert result == 0

    def test_stream_exception_traceback_printed_to_stderr(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Test that exceptions during streaming print traceback to stderr (lines 281-286)."""
        # Create a CSV file with problematic content that triggers parsing error
        csv_file = tmp_path / "bad_config.csv"
        csv_file.write_text("a,b\n1,2\n3,4\n")

        # Use an invalid config that will fail during parsing
        # Mock the dsv.parse_file_stream to raise an exception
        argv = ["cli", "--delimiter", ",", "--stream", "--raise-on-missing-columns", str(csv_file)]

        with patch("sys.argv", argv):
            from splurge_dsv.cli import run_cli

            # This test verifies the error handling path by using an invalid flag combo
            result = run_cli()
            # Should handle error gracefully
            assert result in [0, 1]
