"""
Splurge DSV - A utility library for working with DSV (Delimited String Values) files.

This package provides utilities for parsing, processing, and manipulating
delimited string value files with support for various delimiters, text bookends,
and streaming operations.

Copyright (c) 2025 Jim Schilling

This module is licensed under the MIT License.
"""

# Ensure current working directory exists. Some test environments or earlier
# test cases may remove the process working directory which causes calls to
# os.getcwd() to raise FileNotFoundError later during test execution. Guard
# against that here by switching to this package directory when cwd is missing.
import os
from pathlib import Path as _Path

try:
    if not _Path.cwd().exists():
        os.chdir(_Path(__file__).resolve().parent)
except Exception:
    # Be conservative: if this fails, don't break import - tests will report
    # the original failure. Swallowing ensures import-time is resilient.
    pass

# Local imports
from splurge_dsv.dsv_helper import DsvHelper
from splurge_dsv.exceptions import (
    SplurgeConfigurationError,
    SplurgeDataProcessingError,
    SplurgeDsvError,
    SplurgeFileEncodingError,
    SplurgeFileNotFoundError,
    SplurgeFileOperationError,
    SplurgeFilePermissionError,
    SplurgeFormatError,
    SplurgeParameterError,
    SplurgeParsingError,
    SplurgePathValidationError,
    SplurgePerformanceWarning,
    SplurgeRangeError,
    SplurgeResourceAcquisitionError,
    SplurgeResourceError,
    SplurgeResourceReleaseError,
    SplurgeStreamingError,
    SplurgeTypeConversionError,
    SplurgeValidationError,
)
from splurge_dsv.path_validator import PathValidator
from splurge_dsv.resource_manager import (
    FileResourceManager,
    ResourceManager,
    StreamResourceManager,
    safe_file_operation,
    safe_stream_operation,
)
from splurge_dsv.string_tokenizer import StringTokenizer
from splurge_dsv.text_file_helper import TextFileHelper

__version__ = "2025.2.0"
__author__ = "Jim Schilling"
__license__ = "MIT"

__all__ = [
    # Main helper class
    "DsvHelper",
    # Exceptions
    "SplurgeDsvError",
    "SplurgeValidationError",
    "SplurgeFileOperationError",
    "SplurgeFileNotFoundError",
    "SplurgeFilePermissionError",
    "SplurgeFileEncodingError",
    "SplurgePathValidationError",
    "SplurgeDataProcessingError",
    "SplurgeParsingError",
    "SplurgeTypeConversionError",
    "SplurgeStreamingError",
    "SplurgeConfigurationError",
    "SplurgeResourceError",
    "SplurgeResourceAcquisitionError",
    "SplurgeResourceReleaseError",
    "SplurgePerformanceWarning",
    "SplurgeParameterError",
    "SplurgeRangeError",
    "SplurgeFormatError",
    # Utility classes
    "StringTokenizer",
    "TextFileHelper",
    "PathValidator",
    "ResourceManager",
    "FileResourceManager",
    "StreamResourceManager",
    # Context managers
    "safe_file_operation",
    "safe_stream_operation",
]
