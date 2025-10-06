"""
Integration tests for text file operations.

Tests text file operations including reading,
writing, and processing with real files.
"""

# Standard library imports
import os
import platform
from pathlib import Path

# Third-party imports
import pytest

# Local imports
from splurge_dsv.exceptions import (
    SplurgeDsvFileEncodingError,
    SplurgeDsvFileNotFoundError,
    SplurgeDsvFilePermissionError,
)
from splurge_dsv.text_file_helper import TextFileHelper


class TestTextFileHelperLineCountIntegration:
    """Test line counting with actual files."""

    def test_line_count_empty_file(self, tmp_path: Path) -> None:
        """Test counting lines in an empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")

        count = TextFileHelper.line_count(test_file)
        assert count == 0

    def test_line_count_single_line(self, tmp_path: Path) -> None:
        """Test counting lines in a single line file."""
        test_file = tmp_path / "single.txt"
        test_file.write_text("single line")

        count = TextFileHelper.line_count(test_file)
        assert count == 1

    def test_line_count_multiple_lines(self, tmp_path: Path) -> None:
        """Test counting lines in a multi-line file."""
        test_file = tmp_path / "multiple.txt"
        test_file.write_text("line 1\nline 2\nline 3")

        count = TextFileHelper.line_count(test_file)
        assert count == 3

    def test_line_count_with_empty_lines(self, tmp_path: Path) -> None:
        """Test counting lines with empty lines."""
        test_file = tmp_path / "empty_lines.txt"
        test_file.write_text("line 1\n\nline 3\n\n")

        count = TextFileHelper.line_count(test_file)
        assert count == 4

    def test_line_count_with_trailing_newline(self, tmp_path: Path) -> None:
        """Test counting lines with trailing newline."""
        test_file = tmp_path / "trailing.txt"
        test_file.write_text("line 1\nline 2\n")

        count = TextFileHelper.line_count(test_file)
        assert count == 2

    def test_line_count_without_trailing_newline(self, tmp_path: Path) -> None:
        """Test counting lines without trailing newline."""
        test_file = tmp_path / "no_trailing.txt"
        test_file.write_text("line 1\nline 2")

        count = TextFileHelper.line_count(test_file)
        assert count == 2

    def test_line_count_nonexistent_file_raises_error(self, tmp_path: Path) -> None:
        """Test that counting lines in non-existent file raises error."""
        test_file = tmp_path / "nonexistent.txt"

        with pytest.raises(SplurgeDsvFileNotFoundError):
            TextFileHelper.line_count(test_file)

    def test_line_count_with_different_encoding(self, tmp_path: Path) -> None:
        """Test counting lines with different encoding."""
        test_file = tmp_path / "utf16.txt"
        content = "line 1\nline 2\nline 3"
        test_file.write_text(content, encoding="utf-16")

        count = TextFileHelper.line_count(test_file, encoding="utf-16")
        assert count == 3


class TestTextFileHelperPreviewIntegration:
    """Test file previewing with actual files."""

    def test_preview_empty_file(self, tmp_path: Path) -> None:
        """Test previewing an empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")

        lines = TextFileHelper.preview(test_file)
        assert lines == []

    def test_preview_single_line(self, tmp_path: Path) -> None:
        """Test previewing a single line file."""
        test_file = tmp_path / "single.txt"
        test_file.write_text("single line")

        lines = TextFileHelper.preview(test_file)
        assert lines == ["single line"]

    def test_preview_multiple_lines(self, tmp_path: Path) -> None:
        """Test previewing multiple lines."""
        test_file = tmp_path / "multiple.txt"
        test_file.write_text("line 1\nline 2\nline 3\nline 4\nline 5")

        lines = TextFileHelper.preview(test_file, max_lines=3)
        assert lines == ["line 1", "line 2", "line 3"]

    def test_preview_without_strip(self, tmp_path: Path) -> None:
        """Test previewing without stripping whitespace."""
        test_file = tmp_path / "whitespace.txt"
        test_file.write_text("  line 1  \n  line 2  \n  line 3  ")

        lines = TextFileHelper.preview(test_file, strip=False)
        assert lines == ["  line 1  ", "  line 2  ", "  line 3  "]

    def test_preview_with_skip_header(self, tmp_path: Path) -> None:
        """Test previewing with header skip."""
        test_file = tmp_path / "with_header.txt"
        test_file.write_text("header1\nheader2\ndata1\ndata2\ndata3")

        lines = TextFileHelper.preview(test_file, max_lines=3, skip_header_rows=2)
        assert lines == ["data1", "data2", "data3"]

    def test_preview_max_lines_exceeds_file_size(self, tmp_path: Path) -> None:
        """Test previewing when max_lines exceeds file size."""
        test_file = tmp_path / "small.txt"
        test_file.write_text("line 1\nline 2")

        lines = TextFileHelper.preview(test_file, max_lines=10)
        assert lines == ["line 1", "line 2"]

    def test_preview_skip_header_exceeds_file_size(self, tmp_path: Path) -> None:
        """Test previewing when skip_header exceeds file size."""
        test_file = tmp_path / "small.txt"
        test_file.write_text("line 1\nline 2")

        lines = TextFileHelper.preview(test_file, skip_header_rows=5)
        assert lines == []

    def test_preview_nonexistent_file_raises_error(self, tmp_path: Path) -> None:
        """Test that previewing non-existent file raises error."""
        test_file = tmp_path / "nonexistent.txt"

        with pytest.raises(SplurgeDsvFileNotFoundError):
            TextFileHelper.preview(test_file)


class TestTextFileHelperReadIntegration:
    """Test file reading with actual files."""

    def test_read_empty_file(self, tmp_path: Path) -> None:
        """Test reading an empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")

        lines = TextFileHelper.read(test_file)
        assert lines == []

    def test_read_single_line(self, tmp_path: Path) -> None:
        """Test reading a single line file."""
        test_file = tmp_path / "single.txt"
        test_file.write_text("single line")

        lines = TextFileHelper.read(test_file)
        assert lines == ["single line"]

    def test_read_multiple_lines(self, tmp_path: Path) -> None:
        """Test reading multiple lines."""
        test_file = tmp_path / "multiple.txt"
        test_file.write_text("line 1\nline 2\nline 3\nline 4\nline 5")

        lines = TextFileHelper.read(test_file)
        assert lines == ["line 1", "line 2", "line 3", "line 4", "line 5"]

    def test_read_without_strip(self, tmp_path: Path) -> None:
        """Test reading without stripping whitespace."""
        test_file = tmp_path / "whitespace.txt"
        test_file.write_text("  line 1  \n  line 2  \n  line 3  ")

        lines = TextFileHelper.read(test_file, strip=False)
        assert lines == ["  line 1  ", "  line 2  ", "  line 3  "]

    def test_read_with_skip_header(self, tmp_path: Path) -> None:
        """Test reading with header skip."""
        test_file = tmp_path / "with_header.txt"
        test_file.write_text("header1\nheader2\ndata1\ndata2\ndata3")

        lines = TextFileHelper.read(test_file, skip_header_rows=2)
        assert lines == ["data1", "data2", "data3"]

    def test_read_with_skip_footer(self, tmp_path: Path) -> None:
        """Test reading with footer skip."""
        test_file = tmp_path / "with_footer.txt"
        test_file.write_text("data1\ndata2\ndata3\nfooter1\nfooter2")

        lines = TextFileHelper.read(test_file, skip_footer_rows=2)
        assert lines == ["data1", "data2", "data3"]

    def test_read_with_skip_header_and_footer(self, tmp_path: Path) -> None:
        """Test reading with both header and footer skip."""
        test_file = tmp_path / "with_header_footer.txt"
        test_file.write_text("header1\nheader2\ndata1\ndata2\ndata3\nfooter1\nfooter2")

        lines = TextFileHelper.read(test_file, skip_header_rows=2, skip_footer_rows=2)
        assert lines == ["data1", "data2", "data3"]

    def test_read_skip_header_exceeds_file_size(self, tmp_path: Path) -> None:
        """Test reading when skip_header exceeds file size."""
        test_file = tmp_path / "small.txt"
        test_file.write_text("line 1\nline 2")

        lines = TextFileHelper.read(test_file, skip_header_rows=5)
        assert lines == []

    def test_read_skip_footer_exceeds_file_size(self, tmp_path: Path) -> None:
        """Test reading when skip_footer exceeds file size."""
        test_file = tmp_path / "small.txt"
        test_file.write_text("line 1\nline 2")

        lines = TextFileHelper.read(test_file, skip_footer_rows=5)
        assert lines == []

    def test_read_nonexistent_file_raises_error(self, tmp_path: Path) -> None:
        """Test that reading non-existent file raises error."""
        test_file = tmp_path / "nonexistent.txt"

        with pytest.raises(SplurgeDsvFileNotFoundError):
            TextFileHelper.read(test_file)

    def test_read_with_different_encoding(self, tmp_path: Path) -> None:
        """Test reading with different encoding."""
        test_file = tmp_path / "utf16.txt"
        content = "line 1\nline 2\nline 3"
        test_file.write_text(content, encoding="utf-16")

        lines = TextFileHelper.read(test_file, encoding="utf-16")
        assert lines == ["line 1", "line 2", "line 3"]

    def test_read_skip_header_and_footer_equals_file_size(self, tmp_path: Path) -> None:
        """Test reading when skip_header + skip_footer equals file size."""
        test_file = tmp_path / "exact.txt"
        test_file.write_text("header1\nheader2\ndata1\ndata2\nfooter1\nfooter2")

        lines = TextFileHelper.read(test_file, skip_header_rows=2, skip_footer_rows=2)
        assert lines == ["data1", "data2"]

    def test_read_skip_header_and_footer_greater_than_file_size(self, tmp_path: Path) -> None:
        """Test reading when skip_header + skip_footer exceeds file size."""
        test_file = tmp_path / "small.txt"
        test_file.write_text("line 1\nline 2")

        lines = TextFileHelper.read(test_file, skip_header_rows=1, skip_footer_rows=2)
        assert lines == []


class TestTextFileHelperStreamIntegration:
    """Test file streaming with actual files."""

    def test_read_as_stream_empty_file(self, tmp_path: Path) -> None:
        """Test streaming an empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")

        lines = list(TextFileHelper.read_as_stream(test_file))
        assert lines == []

    def test_read_as_stream_single_line(self, tmp_path: Path) -> None:
        """Test streaming a single line file."""
        test_file = tmp_path / "single.txt"
        test_file.write_text("single line")

        lines = list(TextFileHelper.read_as_stream(test_file))
        assert lines == [["single line"]]

    def test_read_as_stream_multiple_lines(self, tmp_path: Path) -> None:
        """Test streaming multiple lines."""
        test_file = tmp_path / "multiple.txt"
        test_file.write_text("line 1\nline 2\nline 3\nline 4\nline 5")

        lines = list(TextFileHelper.read_as_stream(test_file))
        assert lines == [["line 1", "line 2", "line 3", "line 4", "line 5"]]

    def test_read_as_stream_without_strip(self, tmp_path: Path) -> None:
        """Test streaming without stripping whitespace."""
        test_file = tmp_path / "whitespace.txt"
        test_file.write_text("  line 1  \n  line 2  \n  line 3  ")

        lines = list(TextFileHelper.read_as_stream(test_file, strip=False))
        assert lines == [["  line 1  ", "  line 2  ", "  line 3  "]]

    def test_read_as_stream_with_skip_header(self, tmp_path: Path) -> None:
        """Test streaming with header skip."""
        test_file = tmp_path / "with_header.txt"
        test_file.write_text("header1\nheader2\ndata1\ndata2\ndata3")

        lines = list(TextFileHelper.read_as_stream(test_file, skip_header_rows=2))
        assert lines == [["data1", "data2", "data3"]]

    def test_read_as_stream_with_skip_footer(self, tmp_path: Path) -> None:
        """Test streaming with footer skip."""
        test_file = tmp_path / "with_footer.txt"
        test_file.write_text("data1\ndata2\ndata3\nfooter1\nfooter2")

        lines = list(TextFileHelper.read_as_stream(test_file, skip_footer_rows=2))
        assert lines == [["data1", "data2", "data3"]]

    def test_read_as_stream_with_skip_header_and_footer(self, tmp_path: Path) -> None:
        """Test streaming with both header and footer skip."""
        test_file = tmp_path / "with_header_footer.txt"
        test_file.write_text("header1\nheader2\ndata1\ndata2\ndata3\nfooter1\nfooter2")

        lines = list(TextFileHelper.read_as_stream(test_file, skip_header_rows=2, skip_footer_rows=2))
        assert lines == [["data1", "data2", "data3"]]

    def test_read_as_stream_nonexistent_file_raises_error(self, tmp_path: Path) -> None:
        """Test that streaming non-existent file raises error."""
        test_file = tmp_path / "nonexistent.txt"

        with pytest.raises(SplurgeDsvFileNotFoundError):
            list(TextFileHelper.read_as_stream(test_file))

    def test_read_as_stream_with_different_encoding(self, tmp_path: Path) -> None:
        """Test streaming with different encoding."""
        test_file = tmp_path / "utf16.txt"
        content = "line 1\nline 2\nline 3"
        test_file.write_text(content, encoding="utf-16")

        lines = list(TextFileHelper.read_as_stream(test_file, encoding="utf-16"))
        assert lines == [["line 1", "line 2", "line 3"]]

    def test_read_as_stream_skip_header_exceeds_file_size(self, tmp_path: Path) -> None:
        """Test streaming when skip_header exceeds file size."""
        test_file = tmp_path / "small.txt"
        test_file.write_text("line 1\nline 2")

        lines = list(TextFileHelper.read_as_stream(test_file, skip_header_rows=5))
        assert lines == []

    def test_read_as_stream_skip_footer_exceeds_file_size(self, tmp_path: Path) -> None:
        """Test streaming when skip_footer exceeds file size."""
        test_file = tmp_path / "small.txt"
        test_file.write_text("line 1\nline 2")

        lines = list(TextFileHelper.read_as_stream(test_file, skip_footer_rows=5))
        assert lines == []

    def test_read_as_stream_skip_header_and_footer_exceed_file_size(self, tmp_path: Path) -> None:
        """Test streaming when skip_header + skip_footer exceeds file size."""
        test_file = tmp_path / "small.txt"
        test_file.write_text("line 1\nline 2")

        lines = list(TextFileHelper.read_as_stream(test_file, skip_header_rows=1, skip_footer_rows=2))
        assert lines == []


class TestTextFileHelperEncodingIntegration:
    """Test file encoding handling with actual files."""

    def test_read_file_with_unicode_content(self, tmp_path: Path) -> None:
        """Test reading file with unicode content."""
        test_file = tmp_path / "unicode.txt"
        content = "line 1\nline with émojis\nline with ñ characters"
        test_file.write_text(content, encoding="utf-8")

        lines = TextFileHelper.read(test_file, encoding="utf-8")
        assert lines == ["line 1", "line with émojis", "line with ñ characters"]

    def test_read_file_with_mixed_line_endings(self, tmp_path: Path) -> None:
        """Test reading file with mixed line endings."""
        test_file = tmp_path / "mixed_endings.txt"
        content = "line 1\r\nline 2\nline 3\rline 4"
        test_file.write_text(content, newline="")

        lines = TextFileHelper.read(test_file)
        assert lines == ["line 1", "line 2", "line 3", "line 4"]

    def test_read_file_with_trailing_newlines(self, tmp_path: Path) -> None:
        """Test reading file with trailing newlines."""
        test_file = tmp_path / "trailing_newlines.txt"
        content = "line 1\nline 2\n\n"
        test_file.write_text(content)

        lines = TextFileHelper.read(test_file)
        assert lines == ["line 1", "line 2", ""]

    def test_read_file_with_only_newlines(self, tmp_path: Path) -> None:
        """Test reading file with only newlines."""
        test_file = tmp_path / "only_newlines.txt"
        content = "\n\n\n"
        test_file.write_text(content)

        lines = TextFileHelper.read(test_file)
        assert lines == ["", "", ""]

    def test_stream_large_file(self, tmp_path: Path) -> None:
        """Test streaming large file."""
        test_file = tmp_path / "large.txt"

        # Create a large file with 1000 lines
        lines = []
        for i in range(1000):
            lines.append(f"line {i} with some content")

        test_file.write_text("\n".join(lines))

        # Stream the file
        result = list(TextFileHelper.read_as_stream(test_file))

        # The result is a list of chunks, each chunk contains multiple lines
        total_lines = sum(len(chunk) for chunk in result)
        assert total_lines == 1000  # Total lines should be 1000

        # Check first and last lines
        first_line = result[0][0]
        last_line = result[-1][-1]
        assert first_line == "line 0 with some content"
        assert last_line == "line 999 with some content"

    def test_read_file_with_encoding_error(self, tmp_path: Path) -> None:
        """Test reading file with encoding error."""
        test_file = tmp_path / "encoding_error.txt"
        # Write binary data that's not valid UTF-8
        test_file.write_bytes(b"valid text\n\xff\xfe\nmore text")

        with pytest.raises(SplurgeDsvFileEncodingError):
            TextFileHelper.read(test_file)

    def test_read_file_with_permission_error(self, tmp_path: Path) -> None:
        """Test reading file with permission error."""
        # Skip this test on Windows as chmod(0o000) doesn't make files unreadable
        if platform.system() == "Windows":
            pytest.skip("File permission test not reliable on Windows")

        test_file = tmp_path / "permission_test.txt"
        test_file.write_text("content")

        # Make file unreadable
        os.chmod(test_file, 0o000)

        try:
            with pytest.raises(SplurgeDsvFilePermissionError):
                TextFileHelper.read(test_file)
        finally:
            # Restore permissions
            os.chmod(test_file, 0o644)
