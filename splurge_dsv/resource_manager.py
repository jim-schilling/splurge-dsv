"""
Resource management utilities with context managers.

This module provides context managers and resource management utilities
for safe handling of file operations, streams, and other resources.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Any, IO

from splurge_dsv.exceptions import (
    SplurgeResourceAcquisitionError,
    SplurgeResourceReleaseError,
    SplurgeFileNotFoundError,
    SplurgeFilePermissionError,
    SplurgeFileEncodingError
)
from splurge_dsv.path_validator import PathValidator
 


# Module-level constants for resource management
DEFAULT_BUFFERING = -1  # Default buffering for file operations
DEFAULT_ENCODING = "utf-8"  # Default text encoding
DEFAULT_MODE = "r"  # Default file mode for reading


class ResourceManager:
    """
    Generic resource manager that implements the ResourceManagerProtocol.
    
    This class provides a base implementation for resource management
    with acquire/release semantics.
    """
    
    def __init__(self) -> None:
        """Initialize the resource manager."""
        self._resource: Any | None = None
        self._is_acquired_flag: bool = False
    
    def acquire(self) -> Any:
        """
        Acquire the managed resource.
        
        Returns:
            The acquired resource
            
        Raises:
            SplurgeResourceAcquisitionError: If resource cannot be acquired
        """
        if self._is_acquired_flag:
            raise SplurgeResourceAcquisitionError(
                "Resource is already acquired",
                details="Cannot acquire resource that is already in use"
            )
        
        try:
            self._resource = self._create_resource()
            self._is_acquired_flag = True
            return self._resource
        except Exception as e:
            raise SplurgeResourceAcquisitionError(
                "Failed to acquire resource",
                details=str(e)
            )
    
    def release(self) -> None:
        """
        Release the managed resource.
        
        Raises:
            SplurgeResourceReleaseError: If resource cannot be released
        """
        if not self._is_acquired_flag:
            return  # Nothing to release
        
        try:
            self._cleanup_resource()
            self._resource = None
            self._is_acquired_flag = False
        except Exception as e:
            raise SplurgeResourceReleaseError(
                "Failed to release resource",
                details=str(e)
            )
    
    def is_acquired(self) -> bool:
        """
        Check if the resource is currently acquired.
        
        Returns:
            True if resource is acquired, False otherwise
        """
        return self._is_acquired_flag
    
    def _create_resource(self) -> Any:
        """
        Create the resource to be managed.
        
        This method should be overridden by subclasses to provide
        specific resource creation logic.
        
        Returns:
            The created resource
            
        Raises:
            NotImplementedError: If not overridden by subclass
        """
        raise NotImplementedError("Subclasses must implement _create_resource")
    
    def _cleanup_resource(self) -> None:
        """
        Clean up the managed resource.
        
        This method should be overridden by subclasses to provide
        specific resource cleanup logic.
        """
        if self._resource is not None and hasattr(self._resource, 'close'):
            self._resource.close()


class FileResourceManager:
    """
    Context manager for safe file operations with automatic cleanup.
    
    This class provides context managers for reading and writing files
    with proper error handling and resource cleanup.
    """
    
    def __init__(
        self,
        file_path: str | Path,
        *,
        mode: str = DEFAULT_MODE,
        encoding: str | None = DEFAULT_ENCODING,
        errors: str | None = None,
        newline: str | None = None,
        buffering: int = DEFAULT_BUFFERING
    ) -> None:
        """
        Initialize FileResourceManager.
        
        Args:
            file_path: Path to the file
            mode: File open mode ('r', 'w', 'a', etc.)
            encoding: Text encoding (for text mode)
            errors: Error handling for encoding
            newline: Newline handling
            buffering: Buffer size
            
        Raises:
            SplurgePathValidationError: If file path is invalid
            SplurgeResourceAcquisitionError: If file cannot be opened
        """
        self._file_path = PathValidator.validate_path(
            file_path,
            must_exist=(mode in ['r', 'rb']),
            must_be_file=True,
            must_be_readable=(mode in ['r', 'rb'])
        )
        self.mode = mode
        self.encoding = encoding
        self.errors = errors
        self.newline = newline
        self.buffering = buffering
        self._file_handle: IO[Any] | None = None
    
    def __enter__(self) -> IO[Any]:
        """
        Open the file and return the file handle.
        
        Returns:
            File handle
            
        Raises:
            SplurgeResourceAcquisitionError: If file cannot be opened
        """
        try:
            if 'b' in self.mode:
                # Binary mode
                self._file_handle = open(
                    self.file_path,
                    mode=self.mode,
                    buffering=self.buffering
                )
            else:
                # Text mode
                self._file_handle = open(
                    self.file_path,
                    mode=self.mode,
                    encoding=self.encoding,
                    errors=self.errors,
                    newline=self.newline,
                    buffering=self.buffering
                )
            return self._file_handle
        except FileNotFoundError as e:
            raise SplurgeFileNotFoundError(
                f"File not found: {self.file_path}",
                details=str(e)
            )
        except PermissionError as e:
            raise SplurgeFilePermissionError(
                f"Permission denied: {self.file_path}",
                details=str(e)
            )
        except UnicodeDecodeError as e:
            raise SplurgeFileEncodingError(
                f"Encoding error reading file: {self.file_path}",
                details=str(e)
            )
        except OSError as e:
            raise SplurgeResourceAcquisitionError(
                f"Failed to open file: {self.file_path}",
                details=str(e)
            )
    
    def __exit__(
        self,
        exc_type: type | None,
        exc_val: Exception | None,
        exc_tb: Any | None
    ) -> None:
        """
        Close the file handle and cleanup resources.
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        if self._file_handle is not None:
            try:
                self._file_handle.close()
            except OSError as e:
                raise SplurgeResourceReleaseError(
                    f"Failed to close file: {self.file_path}",
                    details=str(e)
                )
            finally:
                self._file_handle = None
    
    @property
    def file_path(self) -> Path | None:
        """Get the path of the temporary file."""
        return self._file_path


class StreamResourceManager:
    """
    Context manager for stream operations.
    
    This class provides context managers for managing data streams
    with proper cleanup and error handling.
    """
    
    def __init__(
        self,
        stream: Iterator[Any],
        *,
        auto_close: bool = True
    ) -> None:
        """
        Initialize StreamResourceManager.
        
        Args:
            stream: Iterator to manage
            auto_close: Whether to automatically close the stream
        """
        self.stream = stream
        self.auto_close = auto_close
        self._is_closed = False
    
    def __enter__(self) -> Iterator[Any]:
        """
        Return the stream.
        
        Returns:
            Stream iterator
        """
        return self.stream
    
    def __exit__(
        self,
        exc_type: type | None,
        exc_val: Exception | None,
        exc_tb: Any | None
    ) -> None:
        """
        Clean up the stream.
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        if self.auto_close and hasattr(self.stream, 'close'):
            try:
                self.stream.close()
                self._is_closed = True
            except Exception as e:
                raise SplurgeResourceReleaseError(
                    "Failed to close stream",
                    details=str(e)
                )
    
    @property
    def is_closed(self) -> bool:
        """Check if the stream is closed."""
        return self._is_closed


@contextmanager
def safe_file_operation(
    file_path: str | Path,
    *,
    mode: str = DEFAULT_MODE,
    encoding: str | None = DEFAULT_ENCODING,
    errors: str | None = None,
    newline: str | None = None,
    buffering: int = DEFAULT_BUFFERING
) -> Iterator[IO[Any]]:
    """
    Context manager for safe file operations.
    
    Args:
        file_path: Path to the file
        mode: File open mode
        encoding: Text encoding (for text mode)
        errors: Error handling for encoding
        newline: Newline handling
        buffering: Buffer size
        
    Yields:
        File handle
        
    Raises:
        SplurgePathValidationError: If file path is invalid
        SplurgeResourceAcquisitionError: If file cannot be opened
        SplurgeResourceReleaseError: If file cannot be closed
    """
    manager = FileResourceManager(
        file_path,
        mode=mode,
        encoding=encoding,
        errors=errors,
        newline=newline,
        buffering=buffering
    )
    with manager as file_handle:
        yield file_handle





@contextmanager
def safe_stream_operation(
    stream: Iterator[Any],
    *,
    auto_close: bool = True
) -> Iterator[Iterator[Any]]:
    """
    Context manager for safe stream operations.
    
    Args:
        stream: Iterator to manage
        auto_close: Whether to automatically close the stream
        
    Yields:
        Stream iterator
        
    Raises:
        SplurgeResourceReleaseError: If stream cannot be closed
    """
    manager = StreamResourceManager(stream, auto_close=auto_close)
    with manager as stream_handle:
        yield stream_handle


def _handle_file_error(
    error: Exception,
    file_path: Path,
    operation: str
) -> None:
    """
    Handle file operation errors with consistent error mapping.
    
    Args:
        error: The original exception
        file_path: Path to the file that caused the error
        operation: Description of the operation that failed
        
    Raises:
        SplurgeFileNotFoundError: If file not found
        SplurgeFilePermissionError: If permission denied
        SplurgeFileEncodingError: If encoding error
        SplurgeResourceAcquisitionError: For other file errors
    """
    if isinstance(error, FileNotFoundError):
        raise SplurgeFileNotFoundError(
            f"File not found during {operation}: {file_path}",
            details=str(error)
        )
    elif isinstance(error, PermissionError):
        raise SplurgeFilePermissionError(
            f"Permission denied during {operation}: {file_path}",
            details=str(error)
        )
    elif isinstance(error, UnicodeDecodeError):
        raise SplurgeFileEncodingError(
            f"Encoding error during {operation}: {file_path}",
            details=str(error)
        )
    else:
        raise SplurgeResourceAcquisitionError(
            f"Failed to {operation} file: {file_path}",
            details=str(error)
        )


def _handle_resource_cleanup_error(
    error: Exception,
    resource_name: str,
    operation: str
) -> None:
    """
    Handle resource cleanup errors with consistent error mapping.
    
    Args:
        error: The original exception
        resource_name: Name or path of the resource
        operation: Description of the cleanup operation that failed
        
    Raises:
        SplurgeResourceReleaseError: For resource cleanup errors
    """
    raise SplurgeResourceReleaseError(
        f"Failed to {operation} {resource_name}",
        details=str(error)
    )
