"""Top-level package for Splurge DSV.

This package provides utilities for parsing, processing and manipulating
delimited string value (DSV) files. It exposes the high-level API objects
such as :class:`~splurge_dsv.dsv.Dsv` and :class:`~splurge_dsv.dsv.DsvConfig`,
convenience helpers, and the package's exception types.

License: MIT
Copyright (c) 2025 Jim Schilling
"""

# Ensure current working directory exists. Some test environments or earlier
# test cases may remove the process working directory which causes calls to
# os.getcwd() to raise FileNotFoundError later during test execution. Guard
# against that here by switching to this package directory when cwd is missing.
# Ensure the required external implementation is available on import so the
# rest of the package can rely on its APIs. Fail fast with a helpful message
# instructing the user to install the package if it's missing.

import os
from pathlib import Path as _Path

try:
    try:
        # os.getcwd() can raise FileNotFoundError in CI/runner environments
        # if the original working directory was removed. Check existence via
        # Path.cwd(); if it doesn't exist, switch to the package directory.
        if not _Path.cwd().exists():
            os.chdir(_Path(__file__).resolve().parent)
    except FileNotFoundError:
        # Fall back to package directory when cwd is gone
        os.chdir(_Path(__file__).resolve().parent)
except Exception:
    # Be conservative: if this fails, don't break import - tests will report
    # the original failure. Swallowing ensures import-time is resilient.
    pass

# Local imports
from .dsv import Dsv, DsvConfig
from .dsv_helper import DsvHelper
from .exceptions import (
    SplurgeDsvColumnMismatchError,
    SplurgeDsvDataProcessingError,
    SplurgeDsvError,
    SplurgeDsvLookupError,
    SplurgeDsvOSError,
    SplurgeDsvPathValidationError,
    SplurgeDsvRuntimeError,
    SplurgeDsvTypeError,
    SplurgeDsvValueError,
)
from .string_tokenizer import StringTokenizer

__version__ = "2025.5.0"
__author__ = "Jim Schilling"
__license__ = "MIT"

__all__ = [
    "__version__",
    # Main classes
    "Dsv",
    "DsvConfig",
    "DsvHelper",
    # Exceptions
    "SplurgeDsvColumnMismatchError",
    "SplurgeDsvDataProcessingError",
    "SplurgeDsvError",
    "SplurgeDsvPathValidationError",
    "SplurgeDsvValueError",
    "SplurgeDsvTypeError",
    "SplurgeDsvOSError",
    "SplurgeDsvLookupError",
    "SplurgeDsvRuntimeError",
    # Utility classes
    "StringTokenizer",
]
