"""Cross-platform compatibility tests for splurge-dsv.

This module tests cross-platform compatibility features including:
- Path separator normalization
- Line ending normalization
- Encoding consistency across platforms
"""

import tempfile
from pathlib import Path

from splurge_safe_io.safe_text_file_reader import SafeTextFileReader

from splurge_dsv import Dsv, DsvConfig


class TestCrossPlatformCompatibility:
    """Test cross-platform compatibility features."""

    def test_path_separator_normalization(self, tmp_path):
        """Test that path separators are handled consistently across platforms."""
        # Create test data with different path formats
        test_data = "name,value\nJohn,100\nJane,200"

        # Test with forward slashes (Unix-style)
        unix_path = tmp_path / "unix" / "style" / "test.csv"
        unix_path.parent.mkdir(parents=True, exist_ok=True)
        unix_path.write_text(test_data, encoding="utf-8")

        # Test with backslashes (Windows-style) - simulate on any platform
        win_path = tmp_path / "windows" / "style" / "test.csv"
        win_path.parent.mkdir(parents=True, exist_ok=True)
        win_path.write_text(test_data, encoding="utf-8")

        # Both should parse identically regardless of path format
        config = DsvConfig(delimiter=",", skip_header_rows=1)

        unix_result = Dsv(config).parse_file(str(unix_path))
        win_result = Dsv(config).parse_file(str(win_path))

        assert unix_result == win_result
        assert len(unix_result) == 2
        assert unix_result[0] == ["John", "100"]
        assert unix_result[1] == ["Jane", "200"]

    def test_line_ending_normalization_crlf(self, tmp_path):
        """Test CRLF line ending normalization."""
        # Create test data with CRLF line endings (Windows-style)
        crlf_data = "name,value\r\nJohn,100\r\nJane,200\r\n"

        crlf_file = tmp_path / "crlf_test.csv"
        crlf_file.write_bytes(crlf_data.encode("utf-8"))

        config = DsvConfig(delimiter=",", skip_header_rows=1)
        result = Dsv(config).parse_file(str(crlf_file))

        assert len(result) == 2
        assert result[0] == ["John", "100"]
        assert result[1] == ["Jane", "200"]

    def test_line_ending_normalization_lf(self, tmp_path):
        """Test LF line ending normalization."""
        # Create test data with LF line endings (Unix-style)
        lf_data = "name,value\nJohn,100\nJane,200\n"

        lf_file = tmp_path / "lf_test.csv"
        lf_file.write_text(lf_data, encoding="utf-8")

        config = DsvConfig(delimiter=",", skip_header_rows=1)
        result = Dsv(config).parse_file(str(lf_file))

        assert len(result) == 2
        assert result[0] == ["John", "100"]
        assert result[1] == ["Jane", "200"]

    def test_line_ending_normalization_mixed(self, tmp_path):
        """Test mixed line ending normalization."""
        # Create test data with mixed line endings
        mixed_data = "name,value\r\nJohn,100\nJane,200\r\n"

        mixed_file = tmp_path / "mixed_test.csv"
        mixed_file.write_bytes(mixed_data.encode("utf-8"))

        config = DsvConfig(delimiter=",", skip_header_rows=1)
        result = Dsv(config).parse_file(str(mixed_file))

        assert len(result) == 2
        assert result[0] == ["John", "100"]
        assert result[1] == ["Jane", "200"]

    def test_encoding_consistency_utf8(self, tmp_path):
        """Test UTF-8 encoding consistency across platforms."""
        # Test data with Unicode characters
        unicode_data = "name,value\nJosé,100\nBjörk,200\n"

        utf8_file = tmp_path / "utf8_test.csv"
        utf8_file.write_text(unicode_data, encoding="utf-8")

        config = DsvConfig(delimiter=",", skip_header_rows=1, encoding="utf-8")
        result = Dsv(config).parse_file(str(utf8_file))

        assert len(result) == 2
        assert result[0] == ["José", "100"]
        assert result[1] == ["Björk", "200"]

    def test_encoding_consistency_utf16(self, tmp_path):
        """Test UTF-16 encoding consistency."""
        # Test data with Unicode characters
        unicode_data = "name,value\nJosé,100\nBjörk,200\n"

        utf16_file = tmp_path / "utf16_test.csv"
        utf16_file.write_text(unicode_data, encoding="utf-16")

        config = DsvConfig(delimiter=",", skip_header_rows=1, encoding="utf-16")
        result = Dsv(config).parse_file(str(utf16_file))

        assert len(result) == 2
        assert result[0] == ["José", "100"]
        assert result[1] == ["Björk", "200"]

    def test_encoding_consistency_latin1(self, tmp_path):
        """Test Latin-1 encoding consistency."""
        # Test data with Latin-1 characters
        latin1_data = "name,value\nJosé,100\n"

        latin1_file = tmp_path / "latin1_test.csv"
        latin1_file.write_text(latin1_data, encoding="latin-1")

        config = DsvConfig(delimiter=",", skip_header_rows=1, encoding="latin-1")
        result = Dsv(config).parse_file(str(latin1_file))

        assert len(result) == 1
        assert result[0] == ["José", "100"]

    def test_path_handling_with_spaces(self, tmp_path):
        """Test path handling with spaces in directory/file names."""
        # Create directory and file with spaces
        spaced_dir = tmp_path / "test directory"
        spaced_dir.mkdir()

        spaced_file = spaced_dir / "test file.csv"
        test_data = "name,value\nJohn,100\nJane,200"
        spaced_file.write_text(test_data, encoding="utf-8")

        config = DsvConfig(delimiter=",", skip_header_rows=1)
        result = Dsv(config).parse_file(str(spaced_file))

        assert len(result) == 2
        assert result[0] == ["John", "100"]
        assert result[1] == ["Jane", "200"]

    def test_path_handling_with_unicode_names(self, tmp_path):
        """Test path handling with Unicode characters in names."""
        # Create directory and file with Unicode names
        unicode_dir = tmp_path / "tëst_dïr"
        unicode_dir.mkdir()

        unicode_file = unicode_dir / "tëst_fïlé.csv"
        test_data = "name,value\nJohn,100\nJane,200"
        unicode_file.write_text(test_data, encoding="utf-8")

        config = DsvConfig(delimiter=",", skip_header_rows=1)
        result = Dsv(config).parse_file(str(unicode_file))

        assert len(result) == 2
        assert result[0] == ["John", "100"]
        assert result[1] == ["Jane", "200"]

    def test_streaming_with_different_line_endings(self, tmp_path):
        """Test streaming functionality with different line endings."""
        # Test CRLF
        crlf_data = "line1\r\nline2\r\nline3\r\n"
        crlf_file = tmp_path / "crlf_stream.csv"
        crlf_file.write_bytes(crlf_data.encode("utf-8"))

        reader = SafeTextFileReader(Path(crlf_file))
        crlf_lines = list(reader.readlines_as_stream())
        # Flatten chunks to get individual lines
        crlf_lines_flat = [line for chunk in crlf_lines for line in chunk]
        assert len(crlf_lines_flat) == 3
        assert crlf_lines_flat == ["line1", "line2", "line3"]

        # Test LF
        lf_data = "line1\nline2\nline3\n"
        lf_file = tmp_path / "lf_stream.csv"
        lf_file.write_text(lf_data, encoding="utf-8")
        reader = SafeTextFileReader(Path(lf_file))
        lf_lines = list(reader.readlines_as_stream())
        # Flatten chunks to get individual lines
        lf_lines_flat = [line for chunk in lf_lines for line in chunk]
        assert len(lf_lines_flat) == 3
        assert lf_lines_flat == ["line1", "line2", "line3"]

    def test_temporary_file_handling(self, tmp_path):
        """Test handling of temporary files created by different systems."""
        test_data = "name,value\nTest,123"

        # Create file with system temp file handling
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, dir=tmp_path) as f:
            f.write(test_data)
            temp_path = f.name

        try:
            config = DsvConfig(delimiter=",", skip_header_rows=1)
            result = Dsv(config).parse_file(temp_path)

            assert len(result) == 1
            assert result[0] == ["Test", "123"]
        finally:
            # Clean up
            Path(temp_path).unlink(missing_ok=True)
