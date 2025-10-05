"""
Custom exceptions for the splurge-dsv package.

This module provides a hierarchy of custom exceptions for better error handling
and more specific error messages throughout the package.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

import warnings


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


class SplurgeValidationError(SplurgeDsvValidationError):
    """Deprecated alias for :class:`SplurgeDsvValidationError`.

    Use :class:`SplurgeDsvValidationError` instead.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "SplurgeValidationError is deprecated; use SplurgeDsvValidationError",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class SplurgeFileOperationError(SplurgeDsvFileOperationError):
    """Deprecated alias for :class:`SplurgeDsvFileOperationError`.

    Use :class:`SplurgeDsvFileOperationError` instead.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "SplurgeFileOperationError is deprecated; use SplurgeDsvFileOperationError",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class SplurgeFileNotFoundError(SplurgeDsvFileNotFoundError):
    """Deprecated alias for :class:`SplurgeDsvFileNotFoundError`.

    Use :class:`SplurgeDsvFileNotFoundError` instead.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "SplurgeFileNotFoundError is deprecated; use SplurgeDsvFileNotFoundError",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class SplurgeFilePermissionError(SplurgeDsvFilePermissionError):
    """Deprecated alias for :class:`SplurgeDsvFilePermissionError`.

    Use :class:`SplurgeDsvFilePermissionError` instead.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "SplurgeFilePermissionError is deprecated; use SplurgeDsvFilePermissionError",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class SplurgeFileEncodingError(SplurgeDsvFileEncodingError):
    """Deprecated alias for :class:`SplurgeDsvFileEncodingError`.

    Use :class:`SplurgeDsvFileEncodingError` instead.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "SplurgeFileEncodingError is deprecated; use SplurgeDsvFileEncodingError",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class SplurgePathValidationError(SplurgeDsvPathValidationError):
    """Deprecated alias for :class:`SplurgeDsvPathValidationError`.

    Use :class:`SplurgeDsvPathValidationError` instead.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "SplurgePathValidationError is deprecated; use SplurgeDsvPathValidationError",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class SplurgeDataProcessingError(SplurgeDsvDataProcessingError):
    """Deprecated alias for :class:`SplurgeDsvDataProcessingError`.

    Use :class:`SplurgeDsvDataProcessingError` instead.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "SplurgeDataProcessingError is deprecated; use SplurgeDsvDataProcessingError",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class SplurgeParsingError(SplurgeDsvParsingError):
    """Deprecated alias for :class:`SplurgeDsvParsingError`.

    Use :class:`SplurgeDsvParsingError` instead.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "SplurgeParsingError is deprecated; use SplurgeDsvParsingError",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class SplurgeTypeConversionError(SplurgeDsvTypeConversionError):
    """Deprecated alias for :class:`SplurgeDsvTypeConversionError`.

    Use :class:`SplurgeDsvTypeConversionError` instead.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "SplurgeTypeConversionError is deprecated; use SplurgeDsvTypeConversionError",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class SplurgeStreamingError(SplurgeDsvStreamingError):
    """Deprecated alias for :class:`SplurgeDsvStreamingError`.

    Use :class:`SplurgeDsvStreamingError` instead.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "SplurgeStreamingError is deprecated; use SplurgeDsvStreamingError",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class SplurgeConfigurationError(SplurgeDsvConfigurationError):
    """Deprecated alias for :class:`SplurgeDsvConfigurationError`.

    Use :class:`SplurgeDsvConfigurationError` instead.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "SplurgeConfigurationError is deprecated; use SplurgeDsvConfigurationError",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class SplurgeResourceError(SplurgeDsvResourceError):
    """Deprecated alias for :class:`SplurgeDsvResourceError`.

    Use :class:`SplurgeDsvResourceError` instead.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "SplurgeResourceError is deprecated; use SplurgeDsvResourceError",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class SplurgeResourceAcquisitionError(SplurgeDsvResourceAcquisitionError):
    """Deprecated alias for :class:`SplurgeDsvResourceAcquisitionError`.

    Use :class:`SplurgeDsvResourceAcquisitionError` instead.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "SplurgeResourceAcquisitionError is deprecated; use SplurgeDsvResourceAcquisitionError",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class SplurgeResourceReleaseError(SplurgeDsvResourceReleaseError):
    """Deprecated alias for :class:`SplurgeDsvResourceReleaseError`.

    Use :class:`SplurgeDsvResourceReleaseError` instead.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "SplurgeResourceReleaseError is deprecated; use SplurgeDsvResourceReleaseError",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class SplurgePerformanceWarning(SplurgeDsvPerformanceWarning):
    """Deprecated alias for :class:`SplurgeDsvPerformanceWarning`.

    Use :class:`SplurgeDsvPerformanceWarning` instead.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "SplurgePerformanceWarning is deprecated; use SplurgeDsvPerformanceWarning",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class SplurgeParameterError(SplurgeDsvParameterError):
    """Deprecated alias for :class:`SplurgeDsvParameterError`.

    Use :class:`SplurgeDsvParameterError` instead.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "SplurgeParameterError is deprecated; use SplurgeDsvParameterError",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class SplurgeRangeError(SplurgeDsvRangeError):
    """Deprecated alias for :class:`SplurgeDsvRangeError`.

    Use :class:`SplurgeDsvRangeError` instead.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "SplurgeRangeError is deprecated; use SplurgeDsvRangeError",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class SplurgeFormatError(SplurgeDsvFormatError):
    """Deprecated alias for :class:`SplurgeDsvFormatError`.

    Use :class:`SplurgeDsvFormatError` instead.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "SplurgeFormatError is deprecated; use SplurgeDsvFormatError",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
