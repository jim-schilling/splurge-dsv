"""
Unit tests for file system edge cases.

This module tests how the file handling deals with various file system
edge cases including permission changes, file truncation, concurrent access,
and network paths.
"""

# Standard library imports
import os
import tempfile
import threading
import time

# Third-party imports
import pytest

# Local imports
from splurge_dsv.exceptions import (
    SplurgeDsvFileNotFoundError,
    SplurgeDsvFilePermissionError,
    SplurgeDsvPathValidationError,
)
from splurge_dsv.text_file_helper import TextFileHelper


class TestFilesystemEdgeCases:
    """Test file system edge cases in file operations."""

    def test_file_disappears_during_operation(self) -> None:
        """Test handling when file disappears during reading."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("Line 1\nLine 2\nLine 3")
            temp_path = f.name

        try:
            # File exists initially
            assert os.path.exists(temp_path)

            # Start reading in a separate thread
            def delayed_delete():
                time.sleep(0.1)  # Small delay
                os.unlink(temp_path)

            delete_thread = threading.Thread(target=delayed_delete)
            delete_thread.start()

            # Try to read - this might succeed or fail depending on timing
            try:
                result = TextFileHelper.read(temp_path)
                # If it succeeds, we should get the content
                assert isinstance(result, list)
            except (SplurgeDsvFileNotFoundError, SplurgeDsvFilePermissionError, OSError):
                # Expected if file disappears during read
                pass

            delete_thread.join()

        finally:
            # Clean up if file still exists
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_permission_denied_during_read(self) -> None:
        """Test handling of permission denied errors."""
        # Skip this test on Windows where chmod doesn't work reliably
        if os.name == "nt":
            pytest.skip("Permission testing not reliable on Windows")

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("Test content")
            temp_path = f.name

        try:
            # Remove read permission
            os.chmod(temp_path, 0o000)  # No permissions

            # Should raise permission error
            with pytest.raises((SplurgeDsvFilePermissionError, OSError)):
                TextFileHelper.read(temp_path)

        finally:
            # Try to restore permissions for cleanup (may fail)
            try:
                os.chmod(temp_path, 0o644)
            except OSError:
                pass  # Expected if permissions were changed
            # Clean up (may fail if no permissions)
            try:
                os.unlink(temp_path)
            except OSError:
                pass  # May not be able to delete if no permissions

    def test_file_modified_during_streaming(self) -> None:
        """Test behavior when file is modified during streaming read."""
        # Note: Our current implementation reads the entire file into memory first,
        # so file modifications during streaming won't affect the results.
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")
            temp_path = f.name

        try:
            # Read first chunk
            stream = TextFileHelper.read_as_stream(temp_path, chunk_size=2)
            first_chunk = next(stream)
            assert len(first_chunk) == 2
            assert first_chunk[0] == "Line 1"

            # Modify file after first chunk is read
            # (but since we read everything into memory first, this won't matter)
            with open(temp_path, "w") as f:
                f.write("Modified\nContent")

            # Read remaining chunks - should still get original content
            remaining_chunks = list(stream)
            total_remaining_lines = sum(len(chunk) for chunk in remaining_chunks)
            assert total_remaining_lines == 3  # Lines 3, 4, 5

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_empty_file_operations(self) -> None:
        """Test operations on empty files."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            # Create empty file
            temp_path = f.name

        try:
            # Should handle empty files gracefully
            result = TextFileHelper.read(temp_path)
            assert result == []

            count = TextFileHelper.line_count(temp_path)
            assert count == 0

            preview = TextFileHelper.preview(temp_path, max_lines=10)
            assert preview == []

        finally:
            os.unlink(temp_path)

    def test_large_file_line_count(self) -> None:
        """Test line counting on larger files."""
        # Create a file with many lines
        lines = [f"Line {i}" for i in range(1000)]
        content = "\n".join(lines)

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write(content)
            temp_path = f.name

        try:
            count = TextFileHelper.line_count(temp_path)
            assert count == 1000

        finally:
            os.unlink(temp_path)

    def test_directory_as_file(self) -> None:
        """Test attempting to read a directory as a file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to read directory as file
            with pytest.raises(SplurgeDsvPathValidationError):
                TextFileHelper.read(temp_dir)

    def test_nonexistent_file_operations(self) -> None:
        """Test operations on non-existent files."""
        nonexistent_path = "/tmp/nonexistent_file_12345.txt"

        with pytest.raises(SplurgeDsvFileNotFoundError):
            TextFileHelper.read(nonexistent_path)

        with pytest.raises(SplurgeDsvFileNotFoundError):
            TextFileHelper.line_count(nonexistent_path)

        with pytest.raises(SplurgeDsvFileNotFoundError):
            TextFileHelper.preview(nonexistent_path)

    def test_file_with_special_characters_in_path(self) -> None:
        """Test files with special characters in path."""
        # Create a file with special characters in name (if supported)
        try:
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt", prefix="test_file_特殊字符_") as f:
                f.write("Test content")
                temp_path = f.name

            # Should be able to read it
            result = TextFileHelper.read(temp_path)
            assert len(result) == 1

        except (OSError, UnicodeEncodeError):
            # Some systems may not support special characters in filenames
            pytest.skip("Special characters in filenames not supported on this system")
        finally:
            if "temp_path" in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_concurrent_reads(self) -> None:
        """Test concurrent read operations on the same file."""
        content = "\n".join([f"Line {i}" for i in range(100)])

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write(content)
            temp_path = f.name

        try:
            results = []

            def read_file():
                result = TextFileHelper.read(temp_path)
                results.append(result)

            # Start multiple threads reading the same file
            threads = []
            for _ in range(5):
                thread = threading.Thread(target=read_file)
                threads.append(thread)
                thread.start()

            # Wait for all threads
            for thread in threads:
                thread.join()

            # All should have read the same content
            assert len(results) == 5
            for result in results:
                assert len(result) == 100
                assert result[0] == "Line 0"
                assert result[-1] == "Line 99"

        finally:
            os.unlink(temp_path)

    def test_network_path_simulation(self) -> None:
        """Test handling of network-style paths (simulated)."""
        # Test UNC-style paths (on systems that support them)
        if os.name == "nt":  # Windows
            # Try a UNC-style path that doesn't exist - may be blocked by path validation
            unc_path = r"\\nonexistent\share\file.txt"
            with pytest.raises((SplurgeDsvFileNotFoundError, SplurgeDsvPathValidationError)):
                TextFileHelper.read(unc_path)
        else:
            # On Unix-like systems, test paths that look like UNC
            unc_like_path = "//nonexistent/share/file.txt"
            with pytest.raises((SplurgeDsvFileNotFoundError, SplurgeDsvPathValidationError)):
                TextFileHelper.read(unc_like_path)
