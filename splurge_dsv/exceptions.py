"""
Custom exceptions for the splurge-dsv package.

This module provides a hierarchy of custom exceptions for better error handling
and more specific error messages throughout the package.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""


class SplurgeDsvError(Exception):
    """Base exception for all splurge-dsv errors."""

    def __init__(self, message: str, *, details: str | None = None) -> None:
        """
        Initialize SplurgeDsvError.

        Args:
            message: Primary error message
            details: Additional error details
        """
        self.message = message
        self.details = details
        super().__init__(self.message)


# New-style exception names. Use a SplurgeDsv* prefix to avoid colliding with
# Python builtins. We keep the Splurge* aliases for backward compatibility.


class SplurgeDsvValidationError(SplurgeDsvError):
    """Raised when data validation fails."""


class SplurgeDsvFileOperationError(SplurgeDsvError):
    """Base exception for file operation errors."""


class SplurgeDsvFileNotFoundError(SplurgeDsvFileOperationError):
    """Raised when a file is not found."""


class SplurgeDsvFilePermissionError(SplurgeDsvFileOperationError):
    """Raised when there are permission issues with file operations."""


class SplurgeDsvFileEncodingError(SplurgeDsvFileOperationError):
    """Raised when there are encoding issues with file operations."""


class SplurgeDsvPathValidationError(SplurgeDsvFileOperationError):
    """Raised when file path validation fails."""


class SplurgeDsvDataProcessingError(SplurgeDsvError):
    """Base exception for data processing errors."""


class SplurgeDsvParsingError(SplurgeDsvDataProcessingError):
    """Raised when data parsing fails."""


class SplurgeDsvTypeConversionError(SplurgeDsvDataProcessingError):
    """Raised when type conversion fails."""


class SplurgeDsvStreamingError(SplurgeDsvDataProcessingError):
    """Raised when streaming operations fail."""


class SplurgeDsvConfigurationError(SplurgeDsvError):
    """Raised when configuration is invalid."""


class SplurgeDsvResourceError(SplurgeDsvError):
    """Base exception for resource management errors."""


class SplurgeDsvResourceAcquisitionError(SplurgeDsvResourceError):
    """Raised when resource acquisition fails."""


class SplurgeDsvResourceReleaseError(SplurgeDsvResourceError):
    """Raised when resource release fails."""


class SplurgeDsvPerformanceWarning(SplurgeDsvError):
    """Warning for performance-related issues."""


class SplurgeDsvParameterError(SplurgeDsvValidationError):
    """Raised when function parameters are invalid."""


class SplurgeDsvRangeError(SplurgeDsvValidationError):
    """Raised when values are outside expected ranges."""


class SplurgeDsvFormatError(SplurgeDsvValidationError):
    """Raised when data format is invalid."""
