"""Custom exceptions used across the splurge-dsv package.

This module defines a clear exception hierarchy so callers can catch
specific error categories (file, validation, parsing, streaming, etc.)
instead of dealing with generic builtins. Each exception stores a
human-readable ``message`` and optional ``details`` for diagnostic output.

Module contents are intentionally lightweight: exceptions are primarily
containers for structured error information.

Example:
    raise SplurgeDsvOSError(f"File not found", details={"file_path":"/data/foo.csv"})

License: MIT

Copyright (c) 2025 Jim Schilling
"""

from splurge_exceptions import SplurgeFrameworkError


class SplurgeDsvError(SplurgeFrameworkError):
    """Base exception for all splurge-dsv errors."""

    _domain = "splurge-dsv"


class SplurgeDsvTypeError(SplurgeDsvError):
    """Raised when an operation or function is applied to an object of inappropriate type.

    This exception indicates that the type of a provided value does not
    match the expected type for the operation.
    """

    _domain = "splurge-dsv.type"


class SplurgeDsvValueError(SplurgeDsvError):
    """Raised when an operation receives a value with the right type but inappropriate content.

    This exception indicates that the value of a provided argument is
    invalid, even though its type is correct.
    """

    _domain = "splurge-dsv.value"


class SplurgeDsvLookupError(SplurgeDsvError):
    """Raised when a requested key or index is not found in a collection.

    This exception indicates that a lookup operation failed because the
    specified key, index, or identifier does not exist.
    """

    _domain = "splurge-dsv.lookup"


class SplurgeDsvOSError(SplurgeDsvError):
    """Raised for operating system-related errors.

    This exception indicates failures related to OS operations such as
    file handling, permissions, or environment issues.
    """

    _domain = "splurge-dsv.os"


class SplurgeDsvRuntimeError(SplurgeDsvError):
    """Raised for errors that occur during runtime execution.

    This exception indicates conditions that arise during program
    execution that are not covered by more specific exception types.
    """

    _domain = "splurge-dsv.runtime"


class SplurgeDsvPathValidationError(SplurgeDsvError):
    """Raised when a provided filesystem path fails validation checks.

    Use this exception for path traversal, dangerous characters, or other
    validation failures detected by the path validation utilities.
    """

    _domain = "splurge-dsv.path-validation"


class SplurgeDsvDataProcessingError(SplurgeDsvError):
    """Base exception for errors that occur during data processing (parsing, conversion).

    This groups parsing, type conversion, and streaming errors that occur
    while transforming file content into structured data.
    """

    _domain = "splurge-dsv.data-processing"


class SplurgeDsvColumnMismatchError(SplurgeDsvDataProcessingError):
    """Raised when a row has a different number of columns than expected."""

    _domain = "splurge-dsv.data-processing"
