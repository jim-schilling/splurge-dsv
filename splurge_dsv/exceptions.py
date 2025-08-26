"""
Custom exceptions for the splurge-dsv package.

This module provides a hierarchy of custom exceptions for better error handling
and more specific error messages throughout the package.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

# No typing imports needed


class SplurgeDsvError(Exception):
    """Base exception for all splurge-dsv errors."""
    
    def __init__(
        self,
        message: str,
        *,
        details: str | None = None
    ) -> None:
        """
        Initialize SplurgeDsvError.
        
        Args:
            message: Primary error message
            details: Additional error details
        """
        self.message = message
        self.details = details
        super().__init__(self.message)


class SplurgeValidationError(SplurgeDsvError):
    """Raised when data validation fails."""
    pass


class SplurgeFileOperationError(SplurgeDsvError):
    """Base exception for file operation errors."""
    pass


class SplurgeFileNotFoundError(SplurgeFileOperationError):
    """Raised when a file is not found."""
    pass


class SplurgeFilePermissionError(SplurgeFileOperationError):
    """Raised when there are permission issues with file operations."""
    pass


class SplurgeFileEncodingError(SplurgeFileOperationError):
    """Raised when there are encoding issues with file operations."""
    pass


class SplurgePathValidationError(SplurgeFileOperationError):
    """Raised when file path validation fails."""
    pass


class SplurgeDataProcessingError(SplurgeDsvError):
    """Base exception for data processing errors."""
    pass


class SplurgeParsingError(SplurgeDataProcessingError):
    """Raised when data parsing fails."""
    pass


class SplurgeTypeConversionError(SplurgeDataProcessingError):
    """Raised when type conversion fails."""
    pass


class SplurgeStreamingError(SplurgeDataProcessingError):
    """Raised when streaming operations fail."""
    pass


class SplurgeConfigurationError(SplurgeDsvError):
    """Raised when configuration is invalid."""
    pass


class SplurgeResourceError(SplurgeDsvError):
    """Base exception for resource management errors."""
    pass


class SplurgeResourceAcquisitionError(SplurgeResourceError):
    """Raised when resource acquisition fails."""
    pass


class SplurgeResourceReleaseError(SplurgeResourceError):
    """Raised when resource release fails."""
    pass


class SplurgePerformanceWarning(SplurgeDsvError):
    """Warning for performance-related issues."""
    pass


class SplurgeParameterError(SplurgeValidationError):
    """Raised when function parameters are invalid."""
    pass


class SplurgeRangeError(SplurgeValidationError):
    """Raised when values are outside expected ranges."""
    pass


class SplurgeFormatError(SplurgeValidationError):
    """Raised when data format is invalid."""
    pass