"""
Integration tests for file operations.

These tests verify the interaction between multiple components
and test actual file system operations.
"""

import os
import platform
from pathlib import Path

import pytest

from splurge_dsv.dsv_helper import DsvHelper
from splurge_dsv.text_file_helper import TextFileHelper
from splurge_dsv.resource_manager import FileResourceManager
from splurge_dsv.exceptions import (
    SplurgeFileNotFoundError,
    SplurgeFilePermissionError,
    SplurgeFileEncodingError,
    SplurgePathValidationError,
    SplurgeParameterError,
)


class TestFileParsingIntegration:
    """Test file parsing with actual files."""

    def test_parse_file_basic_csv(self, tmp_path: Path) -> None:
        """Test parsing basic CSV file."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("a,b,c\nd,e,f\ng,h,i")

        result = DsvHelper.parse_file(test_file, delimiter=",")
        expected = [["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]]
        assert result == expected

    def test_parse_file_tsv(self, tmp_path: Path) -> None:
        """Test parsing TSV file."""
        test_file = tmp_path / "test.tsv"
        test_file.write_text("a\tb\tc\nd\te\tf")

        result = DsvHelper.parse_file(test_file, delimiter="\t")
        expected = [["a", "b", "c"], ["d", "e", "f"]]
        assert result == expected

    def test_parse_file_with_quoted_values(self, tmp_path: Path) -> None:
        """Test parsing file with quoted values."""
        test_file = tmp_path / "test.csv"
        test_file.write_text('"a","b","c"\n"d","e","f"')

        result = DsvHelper.parse_file(test_file, delimiter=",", bookend='"')
        expected = [["a", "b", "c"], ["d", "e", "f"]]
        assert result == expected

    def test_parse_file_with_skip_header(self, tmp_path: Path) -> None:
        """Test parsing file with header skip."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("header1,header2,header3\na,b,c\nd,e,f")

        result = DsvHelper.parse_file(test_file, delimiter=",", skip_header_rows=1)
        expected = [["a", "b", "c"], ["d", "e", "f"]]
        assert result == expected

    def test_parse_file_with_skip_footer(self, tmp_path: Path) -> None:
        """Test parsing file with footer skip."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("a,b,c\nd,e,f\nfooter1,footer2,footer3")

        result = DsvHelper.parse_file(test_file, delimiter=",", skip_footer_rows=1)
        expected = [["a", "b", "c"], ["d", "e", "f"]]
        assert result == expected

    def test_parse_file_with_skip_header_and_footer(self, tmp_path: Path) -> None:
        """Test parsing file with both header and footer skip."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("header1,header2,header3\na,b,c\nd,e,f\nfooter1,footer2,footer3")

        result = DsvHelper.parse_file(test_file, delimiter=",", skip_header_rows=1, skip_footer_rows=1)
        expected = [["a", "b", "c"], ["d", "e", "f"]]
        assert result == expected

    def test_parse_file_without_strip(self, tmp_path: Path) -> None:
        """Test parsing file without stripping."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("a , b , c\nd , e , f")

        result = DsvHelper.parse_file(test_file, delimiter=",", strip=False)
        expected = [["a ", " b ", " c"], ["d ", " e ", " f"]]
        assert result == expected

    def test_parse_file_with_different_encoding(self, tmp_path: Path) -> None:
        """Test parsing file with different encoding."""
        test_file = tmp_path / "test.csv"
        content = "a,b,c\nd,e,f"
        test_file.write_text(content, encoding="utf-16")

        result = DsvHelper.parse_file(test_file, delimiter=",", encoding="utf-16")
        expected = [["a", "b", "c"], ["d", "e", "f"]]
        assert result == expected

    def test_parse_file_empty(self, tmp_path: Path) -> None:
        """Test parsing empty file."""
        test_file = tmp_path / "empty.csv"
        test_file.write_text("")

        result = DsvHelper.parse_file(test_file, delimiter=",")
        assert result == []

    def test_parse_file_single_line(self, tmp_path: Path) -> None:
        """Test parsing single line file."""
        test_file = tmp_path / "single.csv"
        test_file.write_text("a,b,c")

        result = DsvHelper.parse_file(test_file, delimiter=",")
        expected = [["a", "b", "c"]]
        assert result == expected

    def test_parse_file_nonexistent_raises_error(self, tmp_path: Path) -> None:
        """Test that parsing non-existent file raises error."""
        test_file = tmp_path / "nonexistent.csv"

        with pytest.raises(SplurgeFileNotFoundError):
            DsvHelper.parse_file(test_file, delimiter=",")

    def test_parse_file_with_empty_delimiter_raises_error(self, tmp_path: Path) -> None:
        """Test that parsing with empty delimiter raises error."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("a,b,c")

        with pytest.raises(SplurgeParameterError, match="delimiter cannot be empty or None"):
            DsvHelper.parse_file(test_file, delimiter="")


class TestFileStreamingIntegration:
    """Test file streaming with actual files."""

    def test_parse_stream_empty_file(self, tmp_path: Path) -> None:
        """Test streaming empty file."""
        test_file = tmp_path / "empty.csv"
        test_file.write_text("")

        result = list(DsvHelper.parse_stream(test_file, delimiter=","))
        assert result == []

    def test_parse_stream_basic_csv(self, tmp_path: Path) -> None:
        """Test streaming basic CSV file."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("a,b,c\nd,e,f\ng,h,i")

        result = list(DsvHelper.parse_stream(test_file, delimiter=","))
        expected = [[["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]]]
        assert result == expected

    def test_parse_stream_with_quoted_values(self, tmp_path: Path) -> None:
        """Test streaming file with quoted values."""
        test_file = tmp_path / "test.csv"
        test_file.write_text('"a","b","c"\n"d","e","f"')

        result = list(DsvHelper.parse_stream(test_file, delimiter=",", bookend='"'))
        expected = [[["a", "b", "c"], ["d", "e", "f"]]]
        assert result == expected

    def test_parse_stream_with_skip_header(self, tmp_path: Path) -> None:
        """Test streaming file with header skip."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("header1,header2,header3\na,b,c\nd,e,f")

        result = list(DsvHelper.parse_stream(test_file, delimiter=",", skip_header_rows=1))
        expected = [[["a", "b", "c"], ["d", "e", "f"]]]
        assert result == expected

    def test_parse_stream_nonexistent_file_raises_error(self, tmp_path: Path) -> None:
        """Test that streaming non-existent file raises error."""
        test_file = tmp_path / "nonexistent.csv"

        with pytest.raises(SplurgeFileNotFoundError):
            list(DsvHelper.parse_stream(test_file, delimiter=","))


class TestFileEncodingIntegration:
    """Test file encoding handling with actual files."""

    def test_parse_file_with_unicode_content(self, tmp_path: Path) -> None:
        """Test parsing file with unicode content."""
        test_file = tmp_path / "unicode.csv"
        content = "a,b,c\nd,é,f\ng,h,ñ"
        test_file.write_text(content, encoding="utf-8")

        result = DsvHelper.parse_file(test_file, delimiter=",", encoding="utf-8")
        expected = [["a", "b", "c"], ["d", "é", "f"], ["g", "h", "ñ"]]
        assert result == expected

    def test_parse_file_with_mixed_line_endings(self, tmp_path: Path) -> None:
        """Test parsing file with mixed line endings."""
        test_file = tmp_path / "mixed_endings.csv"
        content = "a,b,c\r\nd,e,f\ng,h,i"
        test_file.write_text(content, newline="")

        result = DsvHelper.parse_file(test_file, delimiter=",")
        expected = [["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]]
        assert result == expected

    def test_parse_file_with_trailing_newlines(self, tmp_path: Path) -> None:
        """Test parsing file with trailing newlines."""
        test_file = tmp_path / "trailing_newlines.csv"
        content = "a,b,c\nd,e,f\n\n"
        test_file.write_text(content)

        result = DsvHelper.parse_file(test_file, delimiter=",")
        expected = [["a", "b", "c"], ["d", "e", "f"], []]
        assert result == expected

    def test_parse_file_with_only_newlines(self, tmp_path: Path) -> None:
        """Test parsing file with only newlines."""
        test_file = tmp_path / "only_newlines.csv"
        content = "\n\n\n"
        test_file.write_text(content)

        result = DsvHelper.parse_file(test_file, delimiter=",")
        expected = [[], [], []]
        assert result == expected

    def test_parse_file_with_encoding_error(self, tmp_path: Path) -> None:
        """Test parsing file with encoding error."""
        test_file = tmp_path / "encoding_error.csv"
        # Write binary data that's not valid UTF-8
        test_file.write_bytes(b"a,b,c\nd,e,\xff\nf,g,h")

        with pytest.raises(SplurgeFileEncodingError):
            DsvHelper.parse_file(test_file, delimiter=",")

    def test_parse_file_with_permission_error(self, tmp_path: Path) -> None:
        """Test parsing file with permission error."""
        # Skip this test on Windows as chmod(0o000) doesn't make files unreadable
        if platform.system() == "Windows":
            pytest.skip("File permission test not reliable on Windows")

        test_file = tmp_path / "permission_test.csv"
        test_file.write_text("a,b,c")

        # Make file unreadable
        os.chmod(test_file, 0o000)

        try:
            with pytest.raises(SplurgeFilePermissionError):
                DsvHelper.parse_file(test_file, delimiter=",")
        finally:
            # Restore permissions
            os.chmod(test_file, 0o644)


class TestLargeFileIntegration:
    """Test large file handling."""

    def test_parse_stream_large_file(self, tmp_path: Path) -> None:
        """Test streaming large file."""
        test_file = tmp_path / "large.csv"
        
        # Create a large file with 1000 rows
        lines = []
        for i in range(1000):
            lines.append(f"row{i},value{i},data{i}")
        
        test_file.write_text("\n".join(lines))

        # Stream the file
        result = list(DsvHelper.parse_stream(test_file, delimiter=","))
        
        # The result is a list of chunks, each chunk contains multiple rows
        # With default chunk size, we might get multiple chunks
        total_rows = sum(len(chunk) for chunk in result)
        assert total_rows == 1000  # Total rows should be 1000
        
        # Check first and last rows
        first_row = result[0][0]
        last_row = result[-1][-1]
        assert first_row == ["row0", "value0", "data0"]
        assert last_row == ["row999", "value999", "data999"]
