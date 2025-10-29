"""Coverage improvement tests for splurge-dsv.

This module contains tests designed to improve code coverage for edge cases
and error conditions without using mocks. Tests focus on real data and
actual error paths.
"""

from pathlib import Path

import pytest

from splurge_dsv import (
    Dsv,
    DsvConfig,
    DsvHelper,
)
from splurge_dsv.exceptions import (
    SplurgeDsvColumnMismatchError,
    SplurgeDsvOSError,
    SplurgeDsvRuntimeError,
    SplurgeDsvTypeError,
    SplurgeDsvValueError,
)


class TestDsvHelperParseFileEdgeCases:
    """Test parse_file with edge cases to increase coverage."""

    def test_parse_file_empty_delimiter_raises(self, tmp_path: Path) -> None:
        """Test parse_file raises when delimiter is empty."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("abc\n")

        with pytest.raises(SplurgeDsvValueError):
            DsvHelper.parse_file(test_file, delimiter="")

    def test_parse_file_none_delimiter_raises(self, tmp_path: Path) -> None:
        """Test parse_file raises when delimiter is None."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("abc\n")

        with pytest.raises(SplurgeDsvValueError):
            DsvHelper.parse_file(test_file, delimiter=None)  # type: ignore

    def test_parse_file_with_tab_delimiter(self, tmp_path: Path) -> None:
        """Test parse_file with tab delimiter."""
        test_file = tmp_path / "test.tsv"
        test_file.write_text("a\tb\tc\n1\t2\t3\n")

        result = DsvHelper.parse_file(test_file, delimiter="\t")
        assert result[0] == ["a", "b", "c"]
        assert result[1] == ["1", "2", "3"]

    def test_parse_file_with_pipe_delimiter(self, tmp_path: Path) -> None:
        """Test parse_file with pipe delimiter."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("a|b|c\n1|2|3\n")

        result = DsvHelper.parse_file(test_file, delimiter="|")
        assert result[0] == ["a", "b", "c"]

    def test_parse_file_raise_on_missing_columns(self, tmp_path: Path) -> None:
        """Test parse_file raises on missing columns when flag is set."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("a,b,c\n1,2\n")

        with pytest.raises(SplurgeDsvColumnMismatchError) as exc_info:
            DsvHelper.parse_file(
                test_file,
                delimiter=",",
                detect_columns=True,
                raise_on_missing_columns=True,
            )
        assert "missing" in exc_info.value.message.lower()

    def test_parse_file_raise_on_extra_columns(self, tmp_path: Path) -> None:
        """Test parse_file raises on extra columns when flag is set."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("a,b,c\n1,2,3,4,5\n")

        with pytest.raises(SplurgeDsvColumnMismatchError) as exc_info:
            DsvHelper.parse_file(
                test_file,
                delimiter=",",
                detect_columns=True,
                raise_on_extra_columns=True,
            )
        assert "extra" in exc_info.value.message.lower()

    def test_parse_file_empty_file(self, tmp_path: Path) -> None:
        """Test parse_file with empty file."""
        test_file = tmp_path / "empty.csv"
        test_file.write_text("")

        result = DsvHelper.parse_file(test_file, delimiter=",")
        assert result == []

    def test_parse_file_single_line(self, tmp_path: Path) -> None:
        """Test parse_file with single line."""
        test_file = tmp_path / "single.csv"
        test_file.write_text("a,b,c")

        result = DsvHelper.parse_file(test_file, delimiter=",")
        assert len(result) == 1
        assert result[0] == ["a", "b", "c"]

    def test_parse_file_with_skip_header_rows(self, tmp_path: Path) -> None:
        """Test parse_file with skip_header_rows."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("header1,header2\na,b\n1,2\n")

        result = DsvHelper.parse_file(
            test_file,
            delimiter=",",
            skip_header_rows=1,
        )
        assert len(result) == 2
        assert result[0] == ["a", "b"]

    def test_parse_file_with_skip_footer_rows(self, tmp_path: Path) -> None:
        """Test parse_file with skip_footer_rows."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("a,b\n1,2\nfooter1,footer2\n")

        result = DsvHelper.parse_file(
            test_file,
            delimiter=",",
            skip_footer_rows=1,
        )
        assert len(result) == 2
        assert result[1] == ["1", "2"]

    def test_parse_file_normalize_columns_pads(self, tmp_path: Path) -> None:
        """Test parse_file pads rows with normalize_columns."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("a,b\n1,2,3,4\n")

        result = DsvHelper.parse_file(
            test_file,
            delimiter=",",
            normalize_columns=3,
        )
        assert result[0] == ["a", "b", ""]
        assert result[1] == ["1", "2", "3"]

    def test_parse_file_detect_columns_normalizes(self, tmp_path: Path) -> None:
        """Test parse_file with detect_columns normalizes all rows."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("a,b,c\n1,2\n3,4,5,6\n")

        result = DsvHelper.parse_file(
            test_file,
            delimiter=",",
            detect_columns=True,
        )
        # All normalized to 3 columns (first row)
        assert result[0] == ["a", "b", "c"]
        assert result[1] == ["1", "2", ""]
        assert result[2] == ["3", "4", "5"]

    def test_parse_file_skip_empty_lines(self, tmp_path: Path) -> None:
        """Test parse_file skips empty lines when flag is set."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("a,b\n\n1,2\n\n3,4\n")

        result = DsvHelper.parse_file(
            test_file,
            delimiter=",",
            skip_empty_lines=True,
        )
        assert len(result) == 3
        assert result[0] == ["a", "b"]


class TestDsvParseStream:
    """Test parse_file_stream with various configurations."""

    def test_parse_file_stream_basic(self, tmp_path: Path) -> None:
        """Test parse_file_stream basic functionality."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("a,b,c\n1,2,3\n4,5,6\n")

        chunks = list(DsvHelper.parse_file_stream(test_file, delimiter=","))
        # parse_file_stream returns chunks (lists of row lists)
        assert len(chunks) >= 1
        # First chunk should have rows
        assert chunks[0][0] == ["a", "b", "c"]


class TestDsvConfigValidation:
    """Test DsvConfig validation edge cases."""

    def test_config_defaults(self) -> None:
        """Test DsvConfig has correct defaults."""
        config = DsvConfig(delimiter=",")
        assert config.strip is True
        assert config.bookend is None
        assert config.encoding == "utf-8"
        assert config.skip_header_rows == 0
        assert config.skip_footer_rows == 0
        assert config.raise_on_missing_columns is False
        assert config.raise_on_extra_columns is False
        assert config.detect_columns is False
        assert config.skip_empty_lines is False
        assert config.delimiter == ","


class TestDsvConfigFromFile:
    """Test DsvConfig.from_file with YAML configs."""

    def test_from_file_valid_config(self, tmp_path: Path) -> None:
        """Test from_file loads valid YAML config."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            """
delimiter: ","
strip: false
bookend: '"'
encoding: utf-8
skip_header_rows: 1
"""
        )

        config = DsvConfig.from_file(config_file)
        assert config.delimiter == ","
        assert config.strip is False
        assert config.skip_header_rows == 1

    def test_from_file_missing_file_raises(self, tmp_path: Path) -> None:
        """Test from_file raises when file doesn't exist."""
        missing_file = tmp_path / "nonexistent.yaml"

        with pytest.raises(SplurgeDsvOSError):
            DsvConfig.from_file(missing_file)

    def test_from_file_missing_delimiter_raises(self, tmp_path: Path) -> None:
        """Test from_file raises when delimiter is missing."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("strip: false\n")

        with pytest.raises(SplurgeDsvValueError) as exc_info:
            DsvConfig.from_file(config_file)
        assert "delimiter" in exc_info.value.message.lower()

    def test_from_file_invalid_yaml_raises(self, tmp_path: Path) -> None:
        """Test from_file raises on invalid YAML syntax."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("invalid: [yaml: {structure:\n")

        with pytest.raises(SplurgeDsvRuntimeError):
            DsvConfig.from_file(config_file)

    def test_from_file_non_dict_raises(self, tmp_path: Path) -> None:
        """Test from_file raises when YAML is not a dictionary."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("- item1\n- item2\n")

        with pytest.raises(SplurgeDsvTypeError):
            DsvConfig.from_file(config_file)

    def test_from_file_with_extra_fields(self, tmp_path: Path) -> None:
        """Test from_file ignores unknown YAML fields."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            """
delimiter: ","
unknown_field: "ignored"
another_unknown: 123
"""
        )

        config = DsvConfig.from_file(config_file)
        assert config.delimiter == ","


class TestDsvHelperParses:
    """Test DsvHelper.parses with various configurations."""

    def test_parses_basic(self) -> None:
        """Test parses with basic content."""
        lines = ["a,b,c", "1,2,3"]
        result = DsvHelper.parses(lines, delimiter=",")
        assert result[0] == ["a", "b", "c"]

    def test_parses_with_strip(self) -> None:
        """Test parses with strip enabled."""
        lines = ["  a  ,  b  "]
        result = DsvHelper.parses(lines, delimiter=",", strip=True)
        assert result[0] == ["a", "b"]

    def test_parses_without_strip(self) -> None:
        """Test parses without strip."""
        lines = ["  a  ,  b  "]
        result = DsvHelper.parses(lines, delimiter=",", strip=False)
        assert result[0] == ["  a  ", "  b  "]

    def test_parses_with_bookend(self) -> None:
        """Test parses removes bookend characters."""
        lines = ['"a","b"']
        result = DsvHelper.parses(lines, delimiter=",", bookend='"')
        assert result[0] == ["a", "b"]

    def test_parses_with_normalize_columns(self) -> None:
        """Test parses with normalize_columns."""
        lines = ["a,b", "1,2,3,4"]
        result = DsvHelper.parses(lines, delimiter=",", normalize_columns=3)
        assert result[0] == ["a", "b", ""]
        assert result[1] == ["1", "2", "3"]

    def test_parses_with_detect_columns(self) -> None:
        """Test parses with detect_columns."""
        lines = ["a,b,c", "1,2", "3,4,5,6"]
        result = DsvHelper.parses(lines, delimiter=",", detect_columns=True)
        assert len(result[0]) == 3
        assert len(result[1]) == 3
        assert result[1] == ["1", "2", ""]
        assert result[2] == ["3", "4", "5"]


class TestDsvInstance:
    """Test Dsv instance methods."""

    def test_dsv_parse_file(self, tmp_path: Path) -> None:
        """Test Dsv.parse_file convenience method."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("a,b\n1,2\n")

        config = DsvConfig(delimiter=",")
        parser = Dsv(config)
        result = parser.parse_file(test_file)
        assert result[0] == ["a", "b"]

    def test_dsv_parse_file_stream(self, tmp_path: Path) -> None:
        """Test Dsv.parse_file_stream convenience method."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("a,b\n1,2\n")

        config = DsvConfig(delimiter=",")
        parser = Dsv(config)
        chunks = list(parser.parse_file_stream(test_file))
        assert len(chunks) >= 1

    def test_dsv_parses(self) -> None:
        """Test Dsv.parses convenience method."""
        config = DsvConfig(delimiter=",")
        parser = Dsv(config)
        lines = ["a,b", "1,2"]
        result = parser.parses(lines)
        assert result[0] == ["a", "b"]

    def test_dsv_parse_single_line(self) -> None:
        """Test Dsv.parse convenience method for single line."""
        config = DsvConfig(delimiter=",")
        parser = Dsv(config)
        result = parser.parse("a,b,c")
        assert result == ["a", "b", "c"]


class TestInitImport:
    """Test __init__.py module imports."""

    def test_all_exports_available(self) -> None:
        """Test that all exports are available from splurge_dsv."""
        import splurge_dsv

        # Main classes
        assert hasattr(splurge_dsv, "Dsv")
        assert hasattr(splurge_dsv, "DsvConfig")
        assert hasattr(splurge_dsv, "DsvHelper")
        assert hasattr(splurge_dsv, "StringTokenizer")

        # Exceptions
        assert hasattr(splurge_dsv, "SplurgeDsvError")
        assert hasattr(splurge_dsv, "SplurgeDsvTypeError")
        assert hasattr(splurge_dsv, "SplurgeDsvValueError")
        assert hasattr(splurge_dsv, "SplurgeDsvLookupError")
        assert hasattr(splurge_dsv, "SplurgeDsvOSError")
        assert hasattr(splurge_dsv, "SplurgeDsvRuntimeError")
        assert hasattr(splurge_dsv, "SplurgeDsvPathValidationError")
        assert hasattr(splurge_dsv, "SplurgeDsvDataProcessingError")
        assert hasattr(splurge_dsv, "SplurgeDsvColumnMismatchError")

    def test_version_available(self) -> None:
        """Test that version is available."""
        import splurge_dsv

        assert hasattr(splurge_dsv, "__version__")
        assert isinstance(splurge_dsv.__version__, str)
