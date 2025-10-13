"""Custom exceptions used across the splurge-dsv package.

This module defines a clear exception hierarchy so callers can catch
specific error categories (file, validation, parsing, streaming, etc.)
instead of dealing with generic builtins. Each exception stores a
human-readable ``message`` and optional ``details`` for diagnostic output.

Module contents are intentionally lightweight: exceptions are primarily
containers for structured error information.

Example:
    raise SplurgeDsvFileNotFoundError("File not found", details="/data/foo.csv")

License: MIT

Copyright (c) 2025 Jim Schilling
"""


class SplurgeDsvError(Exception):
    """Base exception carrying a message and optional details.

    Args:
        message: Primary error message to display to the user.
        details: Optional machine-readable details useful for debugging.

    Attributes:
        message: User-facing error message.
        details: Optional additional diagnostic information.
    """

    def __init__(self, message: str, *, details: str | None = None) -> None:
        self.message = message
        self.details = details
        super().__init__(self.message)


# New-style exception names. Use a SplurgeDsv* prefix to avoid colliding with
# Python builtins. We keep the Splurge* aliases for backward compatibility.


class SplurgeDsvValidationError(SplurgeDsvError):
    """Raised when data validation fails.

    This exception indicates input or configuration values do not meet
    expected constraints (for example: invalid delimiter, out-of-range
    parameters, or malformed metadata).
    """


class SplurgeDsvFileOperationError(SplurgeDsvError):
    """Base exception for file operation errors.

    Used as a parent for file-related conditions such as not found,
    permission denied, or encoding issues.
    """


class SplurgeDsvFileNotFoundError(SplurgeDsvFileOperationError):
    """Raised when an expected file cannot be located.

    This typically maps to ``FileNotFoundError`` semantics but uses the
    package-specific exception hierarchy so callers can distinguish
    file errors from other error types.
    """


class SplurgeDsvFileExistsError(SplurgeDsvFileOperationError):
    """Raised when attempting to create a file that already exists.

    This typically maps to ``FileExistsError`` semantics but uses the
    package-specific exception hierarchy so callers can distinguish
    file errors from other error types.
    """


class SplurgeDsvFilePermissionError(SplurgeDsvFileOperationError):
    """Raised for permission or access-related file errors.

    For example, attempting to open a file without read permission will
    raise this exception.
    """


class SplurgeDsvFileDecodingError(SplurgeDsvFileOperationError):
    """Raised when decoding or encoding a text file fails.

    The exception typically wraps the underlying decoding error and
    provides a descriptive message and optional details for diagnostics.
    """


class SplurgeDsvFileEncodingError(SplurgeDsvFileOperationError):
    """Raised when encoding a text file fails.

    The exception typically wraps the underlying encoding error and
    provides a descriptive message and optional details for diagnostics.
    """


class SplurgeDsvPathValidationError(SplurgeDsvFileOperationError):
    """Raised when a provided filesystem path fails validation checks.

    Use this exception for path traversal, dangerous characters, or other
    validation failures detected by the path validation utilities.
    """


class SplurgeDsvDataProcessingError(SplurgeDsvError):
    """Base exception for errors that occur during data processing (parsing, conversion).

    This groups parsing, type conversion, and streaming errors that occur
    while transforming file content into structured data.
    """


class SplurgeDsvParsingError(SplurgeDsvDataProcessingError):
    """Raised when parsing fails due to malformed or unexpected content."""


class SplurgeDsvColumnMismatchError(SplurgeDsvDataProcessingError):
    """Raised when a row has a different number of columns than expected."""


class SplurgeDsvTypeConversionError(SplurgeDsvDataProcessingError):
    """Raised when a value cannot be converted to the requested type."""


class SplurgeDsvStreamingError(SplurgeDsvDataProcessingError):
    """Raised for errors during streaming (e.g., partial reads, IO interruptions)."""


class SplurgeDsvConfigurationError(SplurgeDsvError):
    """Raised when an invalid configuration is provided to an API.

    Examples include invalid chunk sizes, missing delimiters, or mutually
    exclusive options supplied together.
    """


class SplurgeDsvResourceError(SplurgeDsvError):
    """Base exception for resource acquisition and release errors."""


class SplurgeDsvResourceAcquisitionError(SplurgeDsvResourceError):
    """Raised when acquiring external resources (files, streams) fails."""


class SplurgeDsvResourceReleaseError(SplurgeDsvResourceError):
    """Raised when releasing resources (closing files or handles) fails."""


class SplurgeDsvPerformanceWarning(SplurgeDsvError):
    """Raised to indicate performance-related concerns that may need attention.

    This is not a fatal error but can be used to signal suboptimal usage
    patterns (for example, very small streaming chunk sizes) to callers.
    """


class SplurgeDsvParameterError(SplurgeDsvValidationError):
    """Raised when a function or method receives invalid parameters.

    Use this for invalid types, missing required values, or arguments that
    violate expected constraints.
    """


class SplurgeDsvRangeError(SplurgeDsvValidationError):
    """Raised when a value falls outside an expected numeric or length range."""


class SplurgeDsvFormatError(SplurgeDsvValidationError):
    """Raised when the data format is invalid or cannot be parsed as expected."""
