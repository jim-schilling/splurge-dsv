"""
Tests for the exceptions module.

Tests all custom exception classes and their functionality.
"""

# Local imports
from splurge_dsv.exceptions import (
    SplurgeDsvColumnMismatchError,
    SplurgeDsvConfigurationError,
    SplurgeDsvDataProcessingError,
    SplurgeDsvError,
    SplurgeDsvFileEncodingError,
    SplurgeDsvFileNotFoundError,
    SplurgeDsvFileOperationError,
    SplurgeDsvFilePermissionError,
    SplurgeDsvFormatError,
    SplurgeDsvParameterError,
    SplurgeDsvParsingError,
    SplurgeDsvPathValidationError,
    SplurgeDsvPerformanceWarning,
    SplurgeDsvRangeError,
    SplurgeDsvResourceAcquisitionError,
    SplurgeDsvResourceError,
    SplurgeDsvResourceReleaseError,
    SplurgeDsvStreamingError,
    SplurgeDsvTypeConversionError,
    SplurgeDsvValidationError,
)


class TestSplurgeDsvError:
    """Test the base exception class."""

    def test_init_with_message_only(self) -> None:
        """Test initialization with only a message."""
        error = SplurgeDsvError("Test error message")
        assert error.message == "Test error message"
        assert error.details is None
        assert str(error) == "Test error message"

    def test_init_with_message_and_details(self) -> None:
        """Test initialization with message and details."""
        error = SplurgeDsvError("Test error", details="Additional details")
        assert error.message == "Test error"
        assert error.details == "Additional details"
        assert str(error) == "Test error"

    def test_inheritance(self) -> None:
        """Test that SplurgeDsvError inherits from Exception."""
        error = SplurgeDsvError("Test")
        assert isinstance(error, Exception)


class TestSplurgeValidationError:
    """Test validation error exceptions."""

    def test_parameter_error(self) -> None:
        """Test SplurgeDsv ParameterError."""
        error = SplurgeDsvParameterError("Invalid parameter", details="Parameter 'x' must be positive")
        assert isinstance(error, SplurgeDsvValidationError)
        assert isinstance(error, SplurgeDsvError)
        assert error.message == "Invalid parameter"
        assert error.details == "Parameter 'x' must be positive"

    def test_range_error(self) -> None:
        """Test SplurgeDsvRangeError."""
        error = SplurgeDsvRangeError("Value out of range", details="Value 100 exceeds maximum of 50")
        assert isinstance(error, SplurgeDsvValidationError)
        assert isinstance(error, SplurgeDsvError)
        assert error.message == "Value out of range"
        assert error.details == "Value 100 exceeds maximum of 50"

    def test_format_error(self) -> None:
        """Test SplurgeDsvFormatError."""
        error = SplurgeDsvFormatError("Invalid format", details="Expected CSV format, got TSV")
        assert isinstance(error, SplurgeDsvValidationError)
        assert isinstance(error, SplurgeDsvError)
        assert error.message == "Invalid format"
        assert error.details == "Expected CSV format, got TSV"


class TestSplurgeFileOperationError:
    """Test file operation error exceptions."""

    def test_file_not_found_error(self) -> None:
        """Test SplurgeDsvFileNotFoundError."""
        error = SplurgeDsvFileNotFoundError("File not found", details="File '/path/to/file.txt' does not exist")
        assert isinstance(error, SplurgeDsvFileOperationError)
        assert isinstance(error, SplurgeDsvError)
        assert error.message == "File not found"
        assert error.details == "File '/path/to/file.txt' does not exist"

    def test_file_permission_error(self) -> None:
        """Test SplurgeDsvFilePermissionError."""
        error = SplurgeDsvFilePermissionError("Permission denied", details="Cannot read '/path/to/file.txt'")
        assert isinstance(error, SplurgeDsvFileOperationError)
        assert isinstance(error, SplurgeDsvError)
        assert error.message == "Permission denied"
        assert error.details == "Cannot read '/path/to/file.txt'"

    def test_file_encoding_error(self) -> None:
        """Test SplurgeDsvFileEncodingError."""
        error = SplurgeDsvFileEncodingError("Encoding error", details="Cannot decode file with UTF-8 encoding")
        assert isinstance(error, SplurgeDsvFileOperationError)
        assert isinstance(error, SplurgeDsvError)
        assert error.message == "Encoding error"
        assert error.details == "Cannot decode file with UTF-8 encoding"

    def test_path_validation_error(self) -> None:
        """Test SplurgeDsvPathValidationError."""
        error = SplurgeDsvPathValidationError("Invalid path", details="Path contains dangerous characters")
        assert isinstance(error, SplurgeDsvFileOperationError)
        assert isinstance(error, SplurgeDsvError)
        assert error.message == "Invalid path"
        assert error.details == "Path contains dangerous characters"


class TestSplurgeDataProcessingError:
    """Test data processing error exceptions."""

    def test_column_mismatch_error(self) -> None:
        """Test SplurgeDsvColumnMismatchError."""
        error = SplurgeDsvColumnMismatchError("Column mismatch", details="Expected 3 columns, got 2")
        assert isinstance(error, SplurgeDsvDataProcessingError)
        assert isinstance(error, SplurgeDsvError)
        assert error.message == "Column mismatch"
        assert error.details == "Expected 3 columns, got 2"

    def test_type_conversion_error(self) -> None:
        """Test SplurgeDsvTypeConversionError."""
        error = SplurgeDsvTypeConversionError("Conversion failed", details="Cannot convert 'abc' to integer")
        assert isinstance(error, SplurgeDsvDataProcessingError)
        assert isinstance(error, SplurgeDsvError)
        assert error.message == "Conversion failed"
        assert error.details == "Cannot convert 'abc' to integer"

    def test_streaming_error(self) -> None:
        """Test SplurgeDsvStreamingError."""
        error = SplurgeDsvStreamingError("Stream failed", details="Connection lost during streaming")
        assert isinstance(error, SplurgeDsvDataProcessingError)
        assert isinstance(error, SplurgeDsvError)
        assert error.message == "Stream failed"
        assert error.details == "Connection lost during streaming"


class TestSplurgeResourceError:
    """Test resource error exceptions."""

    def test_resource_acquisition_error(self) -> None:
        """Test SplurgeDsvResourceAcquisitionError."""
        error = SplurgeDsvResourceAcquisitionError("Acquisition failed", details="Database connection timeout")
        assert isinstance(error, SplurgeDsvResourceError)
        assert isinstance(error, SplurgeDsvError)
        assert error.message == "Acquisition failed"
        assert error.details == "Database connection timeout"

    def test_resource_release_error(self) -> None:
        """Test SplurgeDsvResourceReleaseError."""
        error = SplurgeDsvResourceReleaseError("Release failed", details="Cannot close file handle")
        assert isinstance(error, SplurgeDsvResourceError)
        assert isinstance(error, SplurgeDsvError)
        assert error.message == "Release failed"
        assert error.details == "Cannot close file handle"


class TestSplurgeConfigurationError:
    """Test configuration error exceptions."""

    def test_configuration_error(self) -> None:
        """Test SplurgeDsvConfigurationError."""
        error = SplurgeDsvConfigurationError("Invalid config", details="Missing required setting 'delimiter'")
        assert isinstance(error, SplurgeDsvError)
        assert error.message == "Invalid config"
        assert error.details == "Missing required setting 'delimiter'"


class TestSplurgePerformanceWarning:
    """Test performance warning exceptions."""

    def test_performance_warning(self) -> None:
        """Test SplurgeDsvPerformanceWarning."""
        warning = SplurgeDsvPerformanceWarning("Performance issue", details="Large file may cause memory issues")
        assert isinstance(warning, SplurgeDsvError)
        assert warning.message == "Performance issue"
        assert warning.details == "Large file may cause memory issues"


class TestExceptionHierarchy:
    """Test the exception hierarchy and inheritance."""

    def test_exception_hierarchy(self) -> None:
        """Test that all exceptions properly inherit from the base class."""
        exceptions = [
            SplurgeDsvValidationError("test"),
            SplurgeDsvFileOperationError("test"),
            SplurgeDsvDataProcessingError("test"),
            SplurgeDsvConfigurationError("test"),
            SplurgeDsvResourceError("test"),
            SplurgeDsvPerformanceWarning("test"),
            SplurgeDsvParameterError("test"),
            SplurgeDsvRangeError("test"),
            SplurgeDsvFormatError("test"),
            SplurgeDsvFileNotFoundError("test"),
            SplurgeDsvFilePermissionError("test"),
            SplurgeDsvFileEncodingError("test"),
            SplurgeDsvPathValidationError("test"),
            SplurgeDsvParsingError("test"),
            SplurgeDsvColumnMismatchError("test"),
            SplurgeDsvTypeConversionError("test"),
            SplurgeDsvStreamingError("test"),
            SplurgeDsvResourceAcquisitionError("test"),
            SplurgeDsvResourceReleaseError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, SplurgeDsvError)
            assert isinstance(exc, Exception)

    def test_specific_inheritance(self) -> None:
        """Test specific inheritance relationships."""
        # Test validation errors
        param_error = SplurgeDsvParameterError("test")
        range_error = SplurgeDsvRangeError("test")
        format_error = SplurgeDsvFormatError("test")

        assert isinstance(param_error, SplurgeDsvValidationError)
        assert isinstance(range_error, SplurgeDsvValidationError)
        assert isinstance(format_error, SplurgeDsvValidationError)

        # Test file operation errors
        file_not_found = SplurgeDsvFileNotFoundError("test")
        file_permission = SplurgeDsvFilePermissionError("test")
        file_encoding = SplurgeDsvFileEncodingError("test")
        path_validation = SplurgeDsvPathValidationError("test")

        assert isinstance(file_not_found, SplurgeDsvFileOperationError)
        assert isinstance(file_permission, SplurgeDsvFileOperationError)
        assert isinstance(file_encoding, SplurgeDsvFileOperationError)
        assert isinstance(path_validation, SplurgeDsvFileOperationError)

        # Test data processing errors
        parsing_error = SplurgeDsvParsingError("test")
        column_mismatch_error = SplurgeDsvColumnMismatchError("test")
        type_error = SplurgeDsvTypeConversionError("test")
        streaming_error = SplurgeDsvStreamingError("test")

        assert isinstance(parsing_error, SplurgeDsvDataProcessingError)
        assert isinstance(column_mismatch_error, SplurgeDsvDataProcessingError)
        assert isinstance(type_error, SplurgeDsvDataProcessingError)
        assert isinstance(streaming_error, SplurgeDsvDataProcessingError)

        # Test resource errors
        acquisition_error = SplurgeDsvResourceAcquisitionError("test")
        release_error = SplurgeDsvResourceReleaseError("test")

        assert isinstance(acquisition_error, SplurgeDsvResourceError)
        assert isinstance(release_error, SplurgeDsvResourceError)
