"""Tests for CLI functionality without mocks.

Tests command-line interface by invoking print_results with real data.
"""

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
