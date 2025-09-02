"""
Tests for the resource_manager module.

Tests all public classes and context managers including
file operations, temporary files, and stream management.
"""

import os
import platform
from pathlib import Path

import pytest

from splurge_dsv.exceptions import (
    SplurgeFileEncodingError,
    SplurgeFileNotFoundError,
    SplurgeFilePermissionError,
    SplurgePathValidationError,
    SplurgeResourceAcquisitionError,
    SplurgeResourceReleaseError,
)
from splurge_dsv.resource_manager import (
    FileResourceManager,
    ResourceManager,
    StreamResourceManager,
    safe_file_operation,
    safe_stream_operation,
)


class TestResourceManager:
    """Test the base ResourceManager class."""

    def test_init(self) -> None:
        """Test ResourceManager initialization."""
        manager = ResourceManager()
        assert not manager.is_acquired()

    def test_acquire_not_implemented(self) -> None:
        """Test that acquire raises NotImplementedError when _create_resource is not implemented."""
        manager = ResourceManager()

        with pytest.raises(NotImplementedError):
            manager.acquire()

    def test_release_not_acquired(self) -> None:
        """Test releasing when not acquired."""
        manager = ResourceManager()
        # Should not raise an error
        manager.release()

    def test_is_acquired_initial_state(self) -> None:
        """Test initial acquired state."""
        manager = ResourceManager()
        assert not manager.is_acquired()

    def test_acquire_twice_raises_error(self) -> None:
        """Test that acquiring twice raises error."""

        class TestResourceManager(ResourceManager):
            def _create_resource(self):
                return "test_resource"

        manager = TestResourceManager()
        resource = manager.acquire()
        assert resource == "test_resource"
        assert manager.is_acquired()

        with pytest.raises(SplurgeResourceAcquisitionError, match="Resource is already acquired"):
            manager.acquire()

    def test_acquire_release_cycle(self) -> None:
        """Test complete acquire/release cycle."""

        class TestResourceManager(ResourceManager):
            def _create_resource(self):
                return "test_resource"

            def _cleanup_resource(self):
                # Simulate cleanup
                pass

        manager = TestResourceManager()

        # Initial state
        assert not manager.is_acquired()

        # Acquire
        resource = manager.acquire()
        assert resource == "test_resource"
        assert manager.is_acquired()

        # Release
        manager.release()
        assert not manager.is_acquired()

        # Can acquire again after release
        resource2 = manager.acquire()
        assert resource2 == "test_resource"
        assert manager.is_acquired()

    def test_release_with_cleanup_error_raises_error(self) -> None:
        """Test that cleanup error during release raises SplurgeResourceReleaseError."""

        class TestResourceManager(ResourceManager):
            def _create_resource(self):
                return "test_resource"

            def _cleanup_resource(self):
                raise RuntimeError("Cleanup failed")

        manager = TestResourceManager()
        manager.acquire()

        with pytest.raises(SplurgeResourceReleaseError, match="Failed to release resource"):
            manager.release()


class TestFileResourceManager:
    """Test the FileResourceManager class."""

    def test_init_with_string_path(self, tmp_path: Path) -> None:
        """Test initialization with string path."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        manager = FileResourceManager(str(test_file))
        assert manager.file_path == test_file
        assert manager.mode == "r"
        assert manager.encoding == "utf-8"

    def test_init_with_path_object(self, tmp_path: Path) -> None:
        """Test initialization with Path object."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        manager = FileResourceManager(test_file)
        assert manager.file_path == test_file

    def test_init_with_custom_parameters(self, tmp_path: Path) -> None:
        """Test initialization with custom parameters."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        manager = FileResourceManager(
            test_file, mode="w", encoding="utf-16", errors="ignore", newline="\r\n", buffering=1024
        )
        assert manager.mode == "w"
        assert manager.encoding == "utf-16"
        assert manager.errors == "ignore"
        assert manager.newline == "\r\n"
        assert manager.buffering == 1024

    def test_context_manager_text_mode(self, tmp_path: Path) -> None:
        """Test context manager with text mode."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        with FileResourceManager(test_file, mode="r") as file_handle:
            content = file_handle.read()
            assert content == "test content"

    def test_context_manager_binary_mode(self, tmp_path: Path) -> None:
        """Test context manager with binary mode."""
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b"binary content")

        with FileResourceManager(test_file, mode="rb") as file_handle:
            content = file_handle.read()
            assert content == b"binary content"

    def test_context_manager_write_mode(self, tmp_path: Path) -> None:
        """Test context manager with write mode."""
        test_file = tmp_path / "write_test.txt"

        with FileResourceManager(test_file, mode="w") as file_handle:
            file_handle.write("written content")

        assert test_file.read_text() == "written content"

    def test_context_manager_append_mode(self, tmp_path: Path) -> None:
        """Test context manager with append mode."""
        test_file = tmp_path / "append_test.txt"
        test_file.write_text("original content")

        with FileResourceManager(test_file, mode="a") as file_handle:
            file_handle.write(" appended content")

        assert test_file.read_text() == "original content appended content"

    def test_context_manager_read_write_mode(self, tmp_path: Path) -> None:
        """Test context manager with read-write mode."""
        test_file = tmp_path / "rw_test.txt"
        test_file.write_text("original content")

        with FileResourceManager(test_file, mode="r+") as file_handle:
            content = file_handle.read()
            assert content == "original content"

            file_handle.seek(0)
            file_handle.truncate()  # Clear the file
            file_handle.write("new content")

        assert test_file.read_text() == "new content"

    def test_context_manager_binary_write_mode(self, tmp_path: Path) -> None:
        """Test context manager with binary write mode."""
        test_file = tmp_path / "binary_write.bin"

        with FileResourceManager(test_file, mode="wb") as file_handle:
            file_handle.write(b"binary content")

        assert test_file.read_bytes() == b"binary content"

    def test_context_manager_binary_append_mode(self, tmp_path: Path) -> None:
        """Test context manager with binary append mode."""
        test_file = tmp_path / "binary_append.bin"
        test_file.write_bytes(b"original")

        with FileResourceManager(test_file, mode="ab") as file_handle:
            file_handle.write(b" appended")

        assert test_file.read_bytes() == b"original appended"

    def test_nonexistent_file_read_mode_raises_error(self, tmp_path: Path) -> None:
        """Test that non-existent file raises error in read mode."""
        test_file = tmp_path / "nonexistent.txt"

        with pytest.raises(SplurgeFileNotFoundError):
            with FileResourceManager(test_file, mode="r"):
                pass

    def test_nonexistent_file_write_mode_succeeds(self, tmp_path: Path) -> None:
        """Test that non-existent file succeeds in write mode."""
        test_file = tmp_path / "new_file.txt"

        with FileResourceManager(test_file, mode="w") as file_handle:
            file_handle.write("new content")

        assert test_file.read_text() == "new content"

    def test_file_permission_error(self, tmp_path: Path) -> None:
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

    def test_encoding_error(self, tmp_path: Path) -> None:
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

    def test_invalid_path_raises_error(self) -> None:
        """Test that invalid path raises error."""
        with pytest.raises(SplurgePathValidationError):
            FileResourceManager("file<with>invalid:chars?.txt")

    def test_directory_path_raises_error(self, tmp_path: Path) -> None:
        """Test that directory path raises error."""
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()

        with pytest.raises(SplurgePathValidationError):
            FileResourceManager(test_dir, mode="r")

    def test_context_manager_exception_propagation(self, tmp_path: Path) -> None:
        """Test that exceptions in context manager are properly propagated."""
        test_file = tmp_path / "exception_test.txt"
        test_file.write_text("content")

        with pytest.raises(RuntimeError, match="Test exception"):
            with FileResourceManager(test_file, mode="r") as _:
                raise RuntimeError("Test exception")

    def test_context_manager_close_error_raises_error(self, tmp_path: Path) -> None:
        """Test that close error raises SplurgeResourceReleaseError."""
        test_file = tmp_path / "close_error_test.txt"
        test_file.write_text("content")

        # Create a file handle that will fail to close
        class FailingFileHandle:
            def __init__(self, file_path):
                self.file_path = file_path
                self.closed = False

            def read(self):
                return "content"

            def close(self):
                raise OSError("Failed to close")

        # Mock the file opening to return our failing handle
        original_open = open
        try:

            def mock_open(*args, **kwargs):
                return FailingFileHandle(test_file)

            # Replace open function temporarily
            import builtins

            builtins.open = mock_open

            with pytest.raises(SplurgeResourceReleaseError, match="Failed to close file"):
                with FileResourceManager(test_file, mode="r") as file_handle:
                    content = file_handle.read()
                    assert content == "content"
        finally:
            # Restore original open function
            builtins.open = original_open

    def test_context_manager_multiple_operations(self, tmp_path: Path) -> None:
        """Test multiple operations within context manager."""
        test_file = tmp_path / "multi_op_test.txt"
        test_file.write_text("line1\nline2\nline3")

        with FileResourceManager(test_file, mode="r") as file_handle:
            # Multiple read operations
            line1 = file_handle.readline()
            line2 = file_handle.readline()
            line3 = file_handle.readline()

            assert line1 == "line1\n"
            assert line2 == "line2\n"
            assert line3 == "line3"

    def test_context_manager_with_encoding_parameters(self, tmp_path: Path) -> None:
        """Test context manager with various encoding parameters."""
        test_file = tmp_path / "encoding_params_test.txt"
        content = "test content with special chars: éñü"
        test_file.write_text(content, encoding="utf-8")

        with FileResourceManager(
            test_file, mode="r", encoding="utf-8", errors="strict", newline=None, buffering=1024
        ) as file_handle:
            read_content = file_handle.read()
            assert read_content == content


class TestStreamResourceManager:
    """Test the StreamResourceManager class."""

    def test_init_default_parameters(self) -> None:
        """Test initialization with default parameters."""
        stream = iter([1, 2, 3])
        manager = StreamResourceManager(stream)
        assert manager.stream == stream
        assert manager.auto_close is True
        assert not manager.is_closed

    def test_init_custom_parameters(self) -> None:
        """Test initialization with custom parameters."""
        stream = iter([1, 2, 3])
        manager = StreamResourceManager(stream, auto_close=False)
        assert manager.stream == stream
        assert manager.auto_close is False

    def test_context_manager_basic(self) -> None:
        """Test basic context manager functionality."""
        stream = iter([1, 2, 3])
        with StreamResourceManager(stream) as managed_stream:
            items = list(managed_stream)
            assert items == [1, 2, 3]

    def test_context_manager_with_closeable_stream(self) -> None:
        """Test context manager with closeable stream."""

        class CloseableStream:
            def __init__(self):
                self.closed = False

            def __iter__(self):
                return iter([1, 2, 3])

            def close(self):
                self.closed = True

        stream = CloseableStream()
        with StreamResourceManager(stream) as managed_stream:
            items = list(managed_stream)
            assert items == [1, 2, 3]

        assert stream.closed

    def test_context_manager_without_auto_close(self) -> None:
        """Test context manager without auto close."""

        class CloseableStream:
            def __init__(self):
                self.closed = False

            def __iter__(self):
                return iter([1, 2, 3])

            def close(self):
                self.closed = True

        stream = CloseableStream()
        with StreamResourceManager(stream, auto_close=False) as managed_stream:
            items = list(managed_stream)
            assert items == [1, 2, 3]

        assert not stream.closed

    def test_context_manager_with_non_closeable_stream(self) -> None:
        """Test context manager with non-closeable stream."""
        stream = iter([1, 2, 3])
        manager = StreamResourceManager(stream)
        assert not manager.is_closed

        with manager as managed_stream:
            items = list(managed_stream)
            assert items == [1, 2, 3]

        # Should be marked as closed after context manager exits
        assert manager.is_closed

    def test_context_manager_with_close_error_raises_error(self) -> None:
        """Test that close error raises SplurgeResourceReleaseError."""

        class FailingCloseStream:
            def __init__(self):
                self.closed = False

            def __iter__(self):
                return iter([1, 2, 3])

            def close(self):
                raise RuntimeError("Close failed")

        stream = FailingCloseStream()
        with pytest.raises(SplurgeResourceReleaseError, match="Failed to close stream"):
            with StreamResourceManager(stream) as managed_stream:
                items = list(managed_stream)
                assert items == [1, 2, 3]

    def test_context_manager_exception_propagation(self) -> None:
        """Test that exceptions in context manager are properly propagated."""
        stream = iter([1, 2, 3])

        with pytest.raises(RuntimeError, match="Test exception"):
            with StreamResourceManager(stream) as _:
                raise RuntimeError("Test exception")

    def test_context_manager_multiple_iterations(self) -> None:
        """Test multiple iterations within context manager."""
        stream = iter([1, 2, 3])

        with StreamResourceManager(stream) as managed_stream:
            # First iteration
            items1 = list(managed_stream)
            assert items1 == [1, 2, 3]

            # Second iteration (should be empty since stream is exhausted)
            items2 = list(managed_stream)
            assert items2 == []

    def test_context_manager_with_generator(self) -> None:
        """Test context manager with generator function."""

        def number_generator():
            for i in range(1, 4):
                yield i

        with StreamResourceManager(number_generator()) as managed_stream:
            items = list(managed_stream)
            assert items == [1, 2, 3]


class TestSafeFileOperation:
    """Test the safe_file_operation context manager."""

    def test_safe_file_operation_read(self, tmp_path: Path) -> None:
        """Test safe file operation for reading."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        with safe_file_operation(test_file, mode="r") as file_handle:
            content = file_handle.read()
            assert content == "test content"

    def test_safe_file_operation_write(self, tmp_path: Path) -> None:
        """Test safe file operation for writing."""
        test_file = tmp_path / "write_test.txt"

        with safe_file_operation(test_file, mode="w") as file_handle:
            file_handle.write("written content")

        assert test_file.read_text() == "written content"

    def test_safe_file_operation_with_encoding(self, tmp_path: Path) -> None:
        """Test safe file operation with custom encoding."""
        test_file = tmp_path / "utf16_test.txt"
        content = "test content"
        test_file.write_text(content, encoding="utf-16")

        with safe_file_operation(test_file, mode="r", encoding="utf-16") as file_handle:
            read_content = file_handle.read()
            assert read_content == content

    def test_safe_file_operation_nonexistent_file_raises_error(self, tmp_path: Path) -> None:
        """Test that non-existent file raises error."""
        test_file = tmp_path / "nonexistent.txt"

        with pytest.raises(SplurgeFileNotFoundError):
            with safe_file_operation(test_file, mode="r"):
                pass

    def test_safe_file_operation_with_all_parameters(self, tmp_path: Path) -> None:
        """Test safe file operation with all parameters."""
        test_file = tmp_path / "all_params_test.txt"
        content = "test content"
        test_file.write_text(content)

        with safe_file_operation(
            test_file, mode="r", encoding="utf-8", errors="strict", newline=None, buffering=1024
        ) as file_handle:
            read_content = file_handle.read()
            assert read_content == content

    def test_safe_file_operation_exception_propagation(self, tmp_path: Path) -> None:
        """Test that exceptions in safe file operation are properly propagated."""
        test_file = tmp_path / "exception_test.txt"
        test_file.write_text("content")

        with pytest.raises(RuntimeError, match="Test exception"):
            with safe_file_operation(test_file, mode="r") as _:
                raise RuntimeError("Test exception")


class TestSafeStreamOperation:
    """Test the safe_stream_operation context manager."""

    def test_safe_stream_operation_basic(self) -> None:
        """Test basic safe stream operation."""
        stream = iter([1, 2, 3])
        with safe_stream_operation(stream) as managed_stream:
            items = list(managed_stream)
            assert items == [1, 2, 3]

    def test_safe_stream_operation_with_closeable_stream(self) -> None:
        """Test safe stream operation with closeable stream."""

        class CloseableStream:
            def __init__(self):
                self.closed = False

            def __iter__(self):
                return iter([1, 2, 3])

            def close(self):
                self.closed = True

        stream = CloseableStream()
        with safe_stream_operation(stream) as managed_stream:
            items = list(managed_stream)
            assert items == [1, 2, 3]

        assert stream.closed

    def test_safe_stream_operation_without_auto_close(self) -> None:
        """Test safe stream operation without auto close."""

        class CloseableStream:
            def __init__(self):
                self.closed = False

            def __iter__(self):
                return iter([1, 2, 3])

            def close(self):
                self.closed = True

        stream = CloseableStream()
        with safe_stream_operation(stream, auto_close=False) as managed_stream:
            items = list(managed_stream)
            assert items == [1, 2, 3]

        assert not stream.closed

    def test_safe_stream_operation_exception_propagation(self) -> None:
        """Test that exceptions in safe stream operation are properly propagated."""
        stream = iter([1, 2, 3])

        with pytest.raises(RuntimeError, match="Test exception"):
            with safe_stream_operation(stream) as _:
                raise RuntimeError("Test exception")

    def test_safe_stream_operation_with_generator(self) -> None:
        """Test safe stream operation with generator function."""

        def number_generator():
            for i in range(1, 4):
                yield i

        with safe_stream_operation(number_generator()) as managed_stream:
            items = list(managed_stream)
            assert items == [1, 2, 3]


class TestResourceManagerEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_file_resource_manager_with_unicode_path(self, tmp_path: Path) -> None:
        """Test file resource manager with Unicode path."""
        unicode_file = tmp_path / "αβγ.txt"
        unicode_file.write_text("unicode content")

        with FileResourceManager(unicode_file) as file_handle:
            content = file_handle.read()
            assert content == "unicode content"

    def test_file_resource_manager_with_spaces_in_path(self, tmp_path: Path) -> None:
        """Test file resource manager with spaces in path."""
        spaced_file = tmp_path / "file with spaces.txt"
        spaced_file.write_text("content with spaces")

        with FileResourceManager(spaced_file) as file_handle:
            content = file_handle.read()
            assert content == "content with spaces"

    def test_stream_resource_manager_with_empty_stream(self) -> None:
        """Test stream resource manager with empty stream."""
        stream = iter([])
        with StreamResourceManager(stream) as managed_stream:
            items = list(managed_stream)
            assert items == []

    def test_stream_resource_manager_with_large_stream(self) -> None:
        """Test stream resource manager with large stream."""
        stream = iter(range(1000))
        with StreamResourceManager(stream) as managed_stream:
            items = list(managed_stream)
            assert len(items) == 1000
            assert items[0] == 0
            assert items[-1] == 999

    def test_file_resource_manager_concurrent_access(self, tmp_path: Path) -> None:
        """Test file resource manager with concurrent access."""
        test_file = tmp_path / "concurrent.txt"
        test_file.write_text("original content")

        # This should work without issues
        with FileResourceManager(test_file, mode="r") as file1:
            with FileResourceManager(test_file, mode="r") as file2:
                content1 = file1.read()
                content2 = file2.read()
                assert content1 == content2 == "original content"

    def test_file_resource_manager_error_handling(self, tmp_path: Path) -> None:
        """Test file resource manager error handling."""
        # Skip this test on Windows as chmod(0o000) doesn't make files unreadable
        if platform.system() == "Windows":
            pytest.skip("File permission test not reliable on Windows")

        test_file = tmp_path / "error_test.txt"
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

    def test_file_resource_manager_with_special_characters(self, tmp_path: Path) -> None:
        """Test file resource manager with special characters in content."""
        test_file = tmp_path / "special_chars.txt"
        content = "Special chars: éñüß©®™\nNew line\r\nCarriage return"
        test_file.write_text(content, encoding="utf-8", newline="")

        with FileResourceManager(test_file, mode="r", encoding="utf-8", newline="") as file_handle:
            read_content = file_handle.read()
            assert read_content == content

    def test_stream_resource_manager_with_none_values(self) -> None:
        """Test stream resource manager with None values in stream."""
        stream = iter([1, None, 3, None, 5])
        with StreamResourceManager(stream) as managed_stream:
            items = list(managed_stream)
            assert items == [1, None, 3, None, 5]

    def test_file_resource_manager_with_different_line_endings(self, tmp_path: Path) -> None:
        """Test file resource manager with different line endings."""
        test_file = tmp_path / "line_endings.txt"
        content = "line1\nline2\r\nline3\rline4"
        test_file.write_text(content, encoding="utf-8", newline="")

        with FileResourceManager(test_file, mode="r", newline="") as file_handle:
            lines = file_handle.readlines()
            assert len(lines) == 4
            assert lines[0] == "line1\n"
            assert lines[1] == "line2\r\n"
            assert lines[2] == "line3\r"
            assert lines[3] == "line4"

    def test_resource_manager_with_custom_resource(self) -> None:
        """Test ResourceManager with custom resource implementation."""

        class CustomResource:
            def __init__(self, value):
                self.value = value
                self.closed = False

            def close(self):
                self.closed = True

        class CustomResourceManager(ResourceManager):
            def __init__(self, value):
                super().__init__()
                self.value = value

            def _create_resource(self):
                return CustomResource(self.value)

            def _cleanup_resource(self):
                if self._resource:
                    self._resource.close()

        manager = CustomResourceManager("test_value")

        # Test acquire/release cycle
        resource = manager.acquire()
        assert resource.value == "test_value"
        assert not resource.closed
        assert manager.is_acquired()

        manager.release()
        assert resource.closed
        assert not manager.is_acquired()

    def test_file_resource_manager_with_relative_path(self, tmp_path: Path) -> None:
        """Test file resource manager with relative path."""
        # Change to tmp_path directory
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            test_file = Path("relative_test.txt")
            test_file.write_text("relative content")

            with FileResourceManager(test_file, mode="r") as file_handle:
                content = file_handle.read()
                assert content == "relative content"
        finally:
            # Restore original working directory
            os.chdir(original_cwd)

    def test_stream_resource_manager_with_iterator_protocol(self) -> None:
        """Test stream resource manager with custom iterator protocol."""

        class CustomIterator:
            def __init__(self, data):
                self.data = data
                self.index = 0
                self.closed = False

            def __iter__(self):
                return self

            def __next__(self):
                if self.index >= len(self.data):
                    raise StopIteration
                result = self.data[self.index]
                self.index += 1
                return result

            def close(self):
                self.closed = True

        custom_iter = CustomIterator([1, 2, 3, 4, 5])

        with StreamResourceManager(custom_iter) as managed_stream:
            items = list(managed_stream)
            assert items == [1, 2, 3, 4, 5]

        assert custom_iter.closed
