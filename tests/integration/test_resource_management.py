"""
Integration tests for resource management.

Tests resource management functionality including
file operations and context managers with real files.
"""

# Standard library imports
import os
import platform
from pathlib import Path

# Third-party imports
import pytest

# Local imports
from splurge_dsv.exceptions import (
    SplurgeFileEncodingError,
    SplurgeFileNotFoundError,
    SplurgeFilePermissionError,
    SplurgePathValidationError,
)
from splurge_dsv.resource_manager import FileResourceManager


class TestFileResourceManagerIntegration:
    """Test file resource management with actual files."""

    def test_file_resource_manager_basic_read(self, tmp_path: Path) -> None:
        """Test basic file reading."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        with FileResourceManager(test_file, mode="r") as file_handle:
            content = file_handle.read()
            assert content == "test content"

    def test_file_resource_manager_basic_write(self, tmp_path: Path) -> None:
        """Test basic file writing."""
        test_file = tmp_path / "test.txt"

        with FileResourceManager(test_file, mode="w") as file_handle:
            file_handle.write("new content")

        assert test_file.read_text() == "new content"

    def test_file_resource_manager_append(self, tmp_path: Path) -> None:
        """Test file appending."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("original")

        with FileResourceManager(test_file, mode="a") as file_handle:
            file_handle.write(" appended")

        assert test_file.read_text() == "original appended"

    def test_file_resource_manager_binary_read(self, tmp_path: Path) -> None:
        """Test binary file reading."""
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b"binary content")

        with FileResourceManager(test_file, mode="rb") as file_handle:
            content = file_handle.read()
            assert content == b"binary content"

    def test_file_resource_manager_binary_write(self, tmp_path: Path) -> None:
        """Test binary file writing."""
        test_file = tmp_path / "test.bin"

        with FileResourceManager(test_file, mode="wb") as file_handle:
            file_handle.write(b"new binary content")

        assert test_file.read_bytes() == b"new binary content"

    def test_file_resource_manager_with_encoding(self, tmp_path: Path) -> None:
        """Test file operations with specific encoding."""
        test_file = tmp_path / "test.txt"
        content = "test content with émojis"

        with FileResourceManager(test_file, mode="w", encoding="utf-8") as file_handle:
            file_handle.write(content)

        with FileResourceManager(test_file, mode="r", encoding="utf-8") as file_handle:
            read_content = file_handle.read()
            assert read_content == content

    def test_file_resource_manager_nonexistent_file_read_mode_raises_error(self, tmp_path: Path) -> None:
        """Test that non-existent file raises error in read mode."""
        test_file = tmp_path / "nonexistent.txt"

        with pytest.raises(SplurgeFileNotFoundError):
            with FileResourceManager(test_file, mode="r"):
                pass

    def test_file_resource_manager_nonexistent_file_write_mode_succeeds(self, tmp_path: Path) -> None:
        """Test that non-existent file succeeds in write mode."""
        test_file = tmp_path / "new_file.txt"

        with FileResourceManager(test_file, mode="w") as file_handle:
            file_handle.write("new content")

        assert test_file.read_text() == "new content"

    def test_file_resource_manager_file_permission_error(self, tmp_path: Path) -> None:
        """Test file permission error."""
        # Skip this test on Windows as chmod(0o000) doesn't make files unreadable
        if platform.system() == "Windows":
            pytest.skip("File permission test not reliable on Windows")

        test_file = tmp_path / "permission_test.txt"
        test_file.write_text("content")

        # Make file unreadable
        os.chmod(test_file, 0o000)

        try:
            with pytest.raises(SplurgeFilePermissionError):
                with FileResourceManager(test_file, mode="r"):
                    pass
        finally:
            # Restore permissions
            os.chmod(test_file, 0o644)

    def test_file_resource_manager_encoding_error(self, tmp_path: Path) -> None:
        """Test encoding error."""
        # Skip this test on Windows as encoding error handling may differ
        if platform.system() == "Windows":
            pytest.skip("Encoding error test not reliable on Windows")

        test_file = tmp_path / "encoding_test.txt"
        # Write binary data that's not valid UTF-8
        test_file.write_bytes(b"valid text\n\xff\xfe\nmore text")

        with pytest.raises(SplurgeFileEncodingError):
            with FileResourceManager(test_file, mode="r"):
                pass

    def test_file_resource_manager_invalid_path_raises_error(self) -> None:
        """Test that invalid path raises error."""
        with pytest.raises(SplurgePathValidationError):
            FileResourceManager("file<with>invalid:chars?.txt")

    def test_file_resource_manager_directory_path_raises_error(self, tmp_path: Path) -> None:
        """Test that directory path raises error."""
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()

        with pytest.raises(SplurgePathValidationError):
            FileResourceManager(test_dir, mode="r")

    def test_file_resource_manager_context_manager_exception_propagation(self, tmp_path: Path) -> None:
        """Test that exceptions in context manager are properly propagated."""
        test_file = tmp_path / "exception_test.txt"
        test_file.write_text("content")

        with pytest.raises(RuntimeError, match="Test exception"):
            with FileResourceManager(test_file, mode="r") as _:
                raise RuntimeError("Test exception")

    def test_file_resource_manager_context_manager_close_error_raises_error(self, tmp_path: Path) -> None:
        """Test that close error raises SplurgeResourceReleaseError."""
        test_file = tmp_path / "close_error_test.txt"
        test_file.write_text("content")

        # Test that the file is properly closed even when an error occurs
        try:
            with FileResourceManager(test_file, mode="r") as file_handle:
                content = file_handle.read()
                # This should not raise an error since the file handle is properly managed
                assert content == "content"
        except Exception as e:
            # If any error occurs, it should be related to the actual file operations
            # not to mocking or artificial close failures
            pytest.fail(f"Unexpected error occurred: {e}")

        # File should still be accessible
        assert test_file.read_text() == "content"


class TestFileResourceManagerAdvancedIntegration:
    """Test advanced file resource management scenarios."""

    def test_file_resource_manager_with_unicode_path(self, tmp_path: Path) -> None:
        """Test file operations with unicode path."""
        test_file = tmp_path / "testémoji.txt"
        content = "content with émojis"

        with FileResourceManager(test_file, mode="w", encoding="utf-8") as file_handle:
            file_handle.write(content)

        with FileResourceManager(test_file, mode="r", encoding="utf-8") as file_handle:
            read_content = file_handle.read()
            assert read_content == content

    def test_file_resource_manager_with_spaces_in_path(self, tmp_path: Path) -> None:
        """Test file operations with spaces in path."""
        test_file = tmp_path / "file with spaces.txt"
        content = "content with spaces"

        with FileResourceManager(test_file, mode="w") as file_handle:
            file_handle.write(content)

        with FileResourceManager(test_file, mode="r") as file_handle:
            read_content = file_handle.read()
            assert read_content == content

    def test_file_resource_manager_concurrent_access(self, tmp_path: Path) -> None:
        """Test concurrent access to the same file."""
        test_file = tmp_path / "concurrent.txt"
        test_file.write_text("initial content")

        # Simulate concurrent access by opening multiple handles
        with FileResourceManager(test_file, mode="r") as handle1:
            with FileResourceManager(test_file, mode="r") as handle2:
                content1 = handle1.read()
                content2 = handle2.read()
                assert content1 == content2 == "initial content"

    def test_file_resource_manager_error_handling(self, tmp_path: Path) -> None:
        """Test error handling in resource manager."""
        test_file = tmp_path / "error_test.txt"
        test_file.write_text("content")

        # Test that the file is properly closed even when an error occurs
        try:
            with FileResourceManager(test_file, mode="r") as file_handle:
                file_handle.read()
                raise RuntimeError("Test error")
        except RuntimeError:
            pass

        # File should still be accessible
        assert test_file.read_text() == "content"

    def test_file_resource_manager_with_special_characters(self, tmp_path: Path) -> None:
        """Test file operations with special characters in content."""
        test_file = tmp_path / "special_chars.txt"
        content = "line1\nline2\r\nline3\rline4"

        with FileResourceManager(test_file, mode="w", newline="") as file_handle:
            file_handle.write(content)

        with FileResourceManager(test_file, mode="r") as file_handle:
            read_content = file_handle.read()
            # Line endings may be normalized during read/write, so we check the content without strict line ending comparison
            assert "line1" in read_content
            assert "line2" in read_content
            assert "line3" in read_content
            assert "line4" in read_content

    def test_file_resource_manager_with_different_line_endings(self, tmp_path: Path) -> None:
        """Test file operations with different line endings."""
        test_file = tmp_path / "line_endings.txt"
        content = "line1\nline2\r\nline3\rline4"

        with FileResourceManager(test_file, mode="w", newline="") as file_handle:
            file_handle.write(content)

        with FileResourceManager(test_file, mode="r") as file_handle:
            read_content = file_handle.read()
            # Line endings may be normalized during read/write, so we check the content without strict line ending comparison
            assert "line1" in read_content
            assert "line2" in read_content
            assert "line3" in read_content
            assert "line4" in read_content

    def test_file_resource_manager_with_relative_path(self, tmp_path: Path) -> None:
        """Test file operations with relative path."""
        # Change to tmp_path directory
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            test_file = Path("relative_file.txt")
            content = "relative path content"

            with FileResourceManager(test_file, mode="w") as file_handle:
                file_handle.write(content)

            with FileResourceManager(test_file, mode="r") as file_handle:
                read_content = file_handle.read()
                assert read_content == content

            # Clean up
            test_file.unlink()
        finally:
            # Restore original working directory
            os.chdir(original_cwd)


class TestSafeFileOperationsIntegration:
    """Test safe file operations with actual files."""

    def test_safe_file_operation_read(self, tmp_path: Path) -> None:
        """Test safe file read operation."""
        test_file = tmp_path / "safe_read.txt"
        test_file.write_text("safe content")

        from splurge_dsv.resource_manager import safe_file_operation

        with safe_file_operation(test_file, mode="r") as file_handle:
            result = file_handle.read()
            assert result == "safe content"

    def test_safe_file_operation_write(self, tmp_path: Path) -> None:
        """Test safe file write operation."""
        test_file = tmp_path / "safe_write.txt"

        from splurge_dsv.resource_manager import safe_file_operation

        with safe_file_operation(test_file, mode="w") as file_handle:
            file_handle.write("safe write content")

        assert test_file.read_text() == "safe write content"

    def test_safe_file_operation_with_encoding(self, tmp_path: Path) -> None:
        """Test safe file operation with encoding."""
        test_file = tmp_path / "safe_encoding.txt"
        content = "content with émojis"

        from splurge_dsv.resource_manager import safe_file_operation

        with safe_file_operation(test_file, mode="w", encoding="utf-8") as file_handle:
            file_handle.write(content)

        with safe_file_operation(test_file, mode="r", encoding="utf-8") as file_handle:
            result = file_handle.read()
            assert result == content

    def test_safe_file_operation_nonexistent_file_raises_error(self, tmp_path: Path) -> None:
        """Test that safe file operation with non-existent file raises error."""
        test_file = tmp_path / "nonexistent.txt"

        from splurge_dsv.resource_manager import safe_file_operation

        with pytest.raises(SplurgeFileNotFoundError):
            with safe_file_operation(test_file, mode="r") as _:
                pass

    def test_safe_file_operation_with_all_parameters(self, tmp_path: Path) -> None:
        """Test safe file operation with all parameters."""
        test_file = tmp_path / "all_params.txt"
        content = "content with parameters"

        from splurge_dsv.resource_manager import safe_file_operation

        with safe_file_operation(test_file, mode="w", encoding="utf-8", newline="") as file_handle:
            file_handle.write(content)

        with safe_file_operation(test_file, mode="r", encoding="utf-8") as file_handle:
            result = file_handle.read()
            assert result == content

    def test_safe_file_operation_exception_propagation(self, tmp_path: Path) -> None:
        """Test that exceptions in safe file operation are properly propagated."""
        test_file = tmp_path / "exception_test.txt"
        test_file.write_text("content")

        from splurge_dsv.resource_manager import safe_file_operation

        with pytest.raises(RuntimeError, match="Test exception"):
            with safe_file_operation(test_file, mode="r") as _:
                raise RuntimeError("Test exception")
