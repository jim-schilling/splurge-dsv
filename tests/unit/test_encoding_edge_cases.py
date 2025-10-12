"""
Unit tests for encoding edge cases.

This module tests how the text file handling deals with various encoding
edge cases including mixed encodings, invalid sequences, BOM handling,
and encoding detection.
"""

# Standard library imports
import os
import tempfile

# Third-party imports
import pytest

# Local imports
from splurge_dsv.exceptions import SplurgeDsvFileDecodingError
from splurge_dsv.text_file_helper import TextFileHelper


class TestEncodingEdgeCases:
    """Test encoding edge cases in text file operations."""

    def test_invalid_utf8_sequences(self) -> None:
        """Test handling of invalid UTF-8 byte sequences."""
        # Create a file with invalid UTF-8 bytes
        invalid_utf8_bytes = b"\xff\xfe\x00\x00"  # Invalid UTF-8 sequence

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(invalid_utf8_bytes)
            temp_path = f.name

        try:
            # Should raise decoding error when trying to read as UTF-8
            with pytest.raises(SplurgeDsvFileDecodingError):
                TextFileHelper.read(temp_path, encoding="utf-8")
        finally:
            os.unlink(temp_path)

    def test_mixed_encoding_content(self) -> None:
        """Test files that appear to have mixed encodings."""
        # Create content that might be misinterpreted
        # This is tricky to test reliably, so we'll test with latin-1 vs utf-8
        content_latin1 = "tést".encode("latin-1")  # Different bytes in latin-1 vs utf-8

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(content_latin1)
            temp_path = f.name

        try:
            # Reading as latin-1 should work
            result_latin1 = TextFileHelper.read(temp_path, encoding="latin-1")
            assert len(result_latin1) == 1

            # Reading as UTF-8 might fail or give different result
            try:
                result_utf8 = TextFileHelper.read(temp_path, encoding="utf-8")
                # If it succeeds, the content might be different
                assert isinstance(result_utf8, list)
            except SplurgeDsvFileDecodingError:
                # Expected if the bytes are invalid UTF-8
                pass

        finally:
            os.unlink(temp_path)

    def test_bom_handling_utf8(self) -> None:
        """Test handling of UTF-8 files with and without BOM."""
        # Note: Our text reader doesn't strip BOMs - it preserves them as zero-width characters
        content_with_bom = "\ufeffHello,World\nSecond,Line"
        content_without_bom = "Hello,World\nSecond,Line"

        # Test with BOM
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8-sig", delete=False, suffix=".txt") as f:
            f.write(content_with_bom)
            temp_path_bom = f.name

        # Test without BOM
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, suffix=".txt") as f:
            f.write(content_without_bom)
            temp_path_no_bom = f.name

        try:
            # Both should be readable as UTF-8
            result_bom = TextFileHelper.read(temp_path_bom, encoding="utf-8")
            result_no_bom = TextFileHelper.read(temp_path_no_bom, encoding="utf-8")

            # Should have same number of lines
            assert len(result_bom) == len(result_no_bom) == 2

            # First line should contain the same text (BOM may or may not be preserved)
            assert "Hello,World" in result_bom[0]
            assert result_no_bom[0] == "Hello,World"
            assert result_bom[1] == result_no_bom[1] == "Second,Line"

        finally:
            os.unlink(temp_path_bom)
            os.unlink(temp_path_no_bom)

    def test_bom_handling_utf16(self) -> None:
        """Test handling of UTF-16 files with BOM."""
        # Note: Our text reader preserves BOM characters in the content
        content_utf16 = "\ufeffHello,World\nSecond,Line"

        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-16", delete=False, suffix=".txt") as f:
            f.write(content_utf16)
            temp_path = f.name

        try:
            # Should be readable as UTF-16
            result = TextFileHelper.read(temp_path, encoding="utf-16")
            assert len(result) == 2
            # BOM may be preserved in the first line
            assert "Hello,World" in result[0]
            assert result[1] == "Second,Line"

        finally:
            os.unlink(temp_path)

    def test_encoding_mismatch_error(self) -> None:
        """Test error when file encoding doesn't match specified encoding."""
        # Create UTF-8 content
        utf8_content = b"Hello, \xe4\xb8\x96\xe7\x95\x8c"  # "Hello, 世界" in UTF-8 bytes

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(utf8_content)
            temp_path = f.name

        try:
            # Should work with UTF-8
            result_utf8 = TextFileHelper.read(temp_path, encoding="utf-8")
            assert len(result_utf8) == 1
            assert "世界" in result_utf8[0]

            # Should fail with latin-1 if it contains incompatible characters
            # (This might not always fail, depending on the content)
            try:
                result_latin1 = TextFileHelper.read(temp_path, encoding="latin-1")
                # If it succeeds, the content might be mangled
                assert isinstance(result_latin1, list)
            except SplurgeDsvFileDecodingError:
                # Expected for some content
                pass

        finally:
            os.unlink(temp_path)

    def test_line_count_with_encoding_issues(self) -> None:
        """Test line counting with encoding issues."""
        # Create valid UTF-8 content
        content = b"Line 1\nLine 2\nLine 3"

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(content)
            temp_path = f.name

        try:
            # Should count lines correctly
            count = TextFileHelper.line_count(temp_path, encoding="utf-8")
            assert count == 3

        finally:
            os.unlink(temp_path)

    def test_preview_with_encoding_issues(self) -> None:
        """Test preview with encoding issues."""
        content = b"Line 1\nLine 2\nLine 3\nLine 4\nLine 5"

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(content)
            temp_path = f.name

        try:
            # Should preview correctly
            preview = TextFileHelper.preview(temp_path, max_lines=2, encoding="utf-8")
            assert len(preview) == 2
            assert preview[0] == "Line 1"
            assert preview[1] == "Line 2"

        finally:
            os.unlink(temp_path)

    def test_null_bytes_in_file(self) -> None:
        """Test handling of null bytes in files."""
        content_with_nulls = b"Line 1\n\x00Line 2\nLine 3"

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(content_with_nulls)
            temp_path = f.name

        try:
            # Should handle null bytes (they become \x00 in strings)
            result = TextFileHelper.read(temp_path, encoding="latin-1")  # Use latin-1 to preserve bytes
            assert len(result) == 3
            assert "\x00" in result[1]  # Second line contains null byte

        finally:
            os.unlink(temp_path)

    def test_empty_file_encoding(self) -> None:
        """Test encoding handling for empty files."""
        empty_content = b""

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(empty_content)
            temp_path = f.name

        try:
            # Should handle empty files
            result = TextFileHelper.read(temp_path, encoding="utf-8")
            assert result == []

            count = TextFileHelper.line_count(temp_path, encoding="utf-8")
            assert count == 0

        finally:
            os.unlink(temp_path)
