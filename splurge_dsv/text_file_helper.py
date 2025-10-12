"""
Text file utility functions for common file operations.

This module provides helper methods for working with text files, including
line counting, file previewing, and file loading capabilities. The TextFileHelper
class implements static methods for efficient file operations without requiring
class instantiation.

Key features:
- Line counting for text files
- File previewing with configurable line limits
- Complete file loading with header/footer skipping
- Streaming file loading with configurable chunk sizes
- Configurable whitespace handling and encoding
- Secure file path validation
- Resource management with context managers

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

# Standard library imports
import warnings
from collections.abc import Iterator
from os import PathLike
from pathlib import Path

# Import external reader module to honor its configured limits
import splurge_safe_io.path_validator as safe_io_path_validator
import splurge_safe_io.safe_text_file_reader as safe_io_text_file_reader

# Local imports
from splurge_dsv.exceptions import (
    SplurgeDsvError,
    SplurgeDsvFileDecodingError,
    SplurgeDsvFileNotFoundError,
    SplurgeDsvFilePermissionError,
    SplurgeDsvParameterError,
    SplurgeDsvPathValidationError,
)


class TextFileHelper:
    """Utility helpers for working with text files.

    All methods are provided as classmethods and are designed to be memory
    efficient. This module enforces a deterministic newline policy: CRLF
    ("\r\n"), CR ("\r"), and LF ("\n") are normalized to a single ``\n``
    newline. Methods return logical, normalized lines which makes behavior
    consistent across platforms and simplifies testing.
    """

    DEFAULT_ENCODING = "utf-8"
    DEFAULT_MAX_LINES = 25
    DEFAULT_CHUNK_SIZE = 500
    DEFAULT_MIN_CHUNK_SIZE = 100
    DEFAULT_SKIP_HEADER_ROWS = 0
    DEFAULT_SKIP_FOOTER_ROWS = 0
    DEFAULT_STRIP = True
    DEFAULT_MODE = "r"

    @staticmethod
    def _validate_path(
        path: Path | str, *, must_exist: bool = True, must_be_file: bool = True, must_be_readable: bool = True
    ) -> Path:
        """Validate the provided file path.

        Args:
            path: The file path to validate.

        Returns:
            A validated Path object.

        Raises:
            SplurgeDsvPathValidationError: If the file path is invalid.
            SplurgeDsvFileNotFoundError: If the file does not exist.
            SplurgeDsvFilePermissionError: If the file cannot be accessed due to permission restrictions
            SplurgeDsvError: For other unexpected errors.
        """
        try:
            effective_path = safe_io_path_validator.PathValidator.validate_path(
                Path(path), must_exist=must_exist, must_be_file=must_be_file, must_be_readable=must_be_readable
            )
        except safe_io_path_validator.SplurgeSafeIoPathValidationError as ex:
            raise SplurgeDsvPathValidationError(f"Invalid file path: {path}") from ex
        except safe_io_path_validator.SplurgeSafeIoFileNotFoundError as ex:
            raise SplurgeDsvFileNotFoundError(f"File not found: {path}") from ex
        except safe_io_path_validator.SplurgeSafeIoFilePermissionError as ex:
            raise SplurgeDsvFilePermissionError(f"File permission error: {path}") from ex
        except Exception as ex:
            raise SplurgeDsvError(f"Unexpected error validating file path: {path}") from ex

        return effective_path

    @classmethod
    def line_count(cls, file_path: PathLike[str] | str, *, encoding: str = DEFAULT_ENCODING) -> int:
        """Return the number of logical lines in ``file_path``.

        The file is iterated efficiently without reading the entire contents
        into memory. Newlines are normalized according to the package newline
        policy before counting.

        Args:
            file_path: Path to the text file to inspect.
            encoding: Text encoding to use when reading the file.

        Returns:
            The number of logical lines in the file.

        Raises:
            SplurgeDsvFileNotFoundError: If ``file_path`` does not exist.
            SplurgeDsvFilePermissionError: If the file cannot be read due to
                permissions.
            SplurgeDsvFileEncodingError: If the file cannot be decoded using the
                provided ``encoding``.
            SplurgeDsvPathValidationError: If path validation fails.

        **Deprecated:** This method is deprecated and will be removed in a future release.
        """
        # Emit a DeprecationWarning to signal removal in a future release
        warnings.warn(
            "TextFileHelper.line_count() is deprecated and will be removed in a future release. Consider using splurge-safe-io directly.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Validate file path
        effective_file_path = cls._validate_path(
            Path(file_path), must_exist=True, must_be_file=True, must_be_readable=True
        )

        # Delegate to the external SafeTextFileReader implementation which
        # centralizes newline normalization and streaming behavior.
        try:
            # strip is a per-instance option on the external reader; the
            # read() method takes no parameters.
            reader = safe_io_text_file_reader.SafeTextFileReader(effective_file_path, encoding=encoding)
            return reader.line_count()

        except safe_io_text_file_reader.SplurgeSafeIoFileDecodingError as ex:
            raise SplurgeDsvFileDecodingError(f"File decoding error: {effective_file_path}") from ex
        except safe_io_text_file_reader.SplurgeSafeIoFilePermissionError as ex:
            raise SplurgeDsvFilePermissionError(f"File permission error: {effective_file_path}") from ex
        except safe_io_text_file_reader.SplurgeSafeIoOsError as ex:
            raise SplurgeDsvFilePermissionError(f"File access error: {effective_file_path}") from ex
        except Exception as ex:
            raise SplurgeDsvError(f"Unexpected error reading file: {effective_file_path}") from ex

    @classmethod
    def preview(
        cls,
        file_path: PathLike[str] | str,
        *,
        max_lines: int = DEFAULT_MAX_LINES,
        strip: bool = DEFAULT_STRIP,
        encoding: str = DEFAULT_ENCODING,
        skip_header_rows: int = DEFAULT_SKIP_HEADER_ROWS,
    ) -> list[str]:
        """Return the first ``max_lines`` logical lines from ``file_path``.

        The preview respects header skipping and optional whitespace
        stripping. Lines returned are normalized according to the package
        newline policy.

        Args:
            file_path: Path to the text file.
            max_lines: Maximum number of lines to return (must be >= 1).
            strip: If True, strip leading/trailing whitespace from each line.
            encoding: File encoding to use when reading the file.
            skip_header_rows: Number of leading lines to ignore before previewing.

        Returns:
            A list of logical lines (strings), up to ``max_lines`` in length.

        Raises:
            SplurgeDsvParameterError: If ``max_lines`` is less than 1.
            SplurgeDsvFileNotFoundError: If ``file_path`` does not exist.
            SplurgeDsvFilePermissionError: If the file cannot be read due to
                permissions.
            SplurgeDsvFileEncodingError: If the file cannot be decoded using the
                provided ``encoding``.
            SplurgeDsvPathValidationError: If path validation fails.

        **Deprecated:** This method is deprecated and will be removed in a future release.
        """
        # Emit a DeprecationWarning to signal removal in a future release
        warnings.warn(
            "TextFileHelper.preview() is deprecated and will be removed in a future release. Consider using splurge-safe-io directly.",
            DeprecationWarning,
            stacklevel=2,
        )

        if max_lines < 1:
            raise SplurgeDsvParameterError(
                "TextFileHelper.preview: max_lines is less than 1", details="max_lines must be at least 1"
            )

        # Validate file path
        effective_file_path = cls._validate_path(
            Path(file_path), must_exist=True, must_be_file=True, must_be_readable=True
        )

        skip_header_rows = max(skip_header_rows, cls.DEFAULT_SKIP_HEADER_ROWS)

        try:
            # preview's behavior is controlled by the reader instance options.
            reader = safe_io_text_file_reader.SafeTextFileReader(
                effective_file_path, encoding=encoding, strip=strip, skip_header_lines=skip_header_rows
            )
            return reader.preview(max_lines=max_lines)

        except safe_io_text_file_reader.SplurgeSafeIoFileDecodingError as ex:
            raise SplurgeDsvFileDecodingError(f"File decoding error: {effective_file_path}") from ex
        except safe_io_text_file_reader.SplurgeSafeIoFilePermissionError as ex:
            raise SplurgeDsvFilePermissionError(f"File permission error: {effective_file_path}") from ex
        except safe_io_text_file_reader.SplurgeSafeIoOsError as ex:
            raise SplurgeDsvFilePermissionError(f"File access error: {effective_file_path}") from ex
        except Exception as ex:
            raise SplurgeDsvError(f"Unexpected error reading file: {effective_file_path}") from ex

    @classmethod
    def read_as_stream(
        cls,
        file_path: PathLike[str] | str,
        *,
        strip: bool = DEFAULT_STRIP,
        encoding: str = DEFAULT_ENCODING,
        skip_header_rows: int = DEFAULT_SKIP_HEADER_ROWS,
        skip_footer_rows: int = DEFAULT_SKIP_FOOTER_ROWS,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> Iterator[list[str]]:
        """Yield the file contents as successive chunks of logical lines.

        Each yielded value is a list of lines (strings), where each chunk
        contains up to ``chunk_size`` lines. Footer skipping is implemented
        using a sliding-window technique so the file is not fully loaded into
        memory.

        Args:
            file_path: Path to the text file to stream.
            strip: If True, strip leading/trailing whitespace from each line.
            encoding: Text encoding used to read the file.
            skip_header_rows: Number of leading lines to skip before yielding.
            skip_footer_rows: Number of trailing lines to skip (handled via
                an internal buffer; does not require reading the whole file).
            chunk_size: Target number of lines per yielded chunk.

        Yields:
            Lists of logical lines (each a list[str]) for each chunk.

        Raises:
            SplurgeDsvFileNotFoundError: If ``file_path`` does not exist.
            SplurgeDsvFilePermissionError: If the file cannot be read due to
                permissions.
            SplurgeDsvFileEncodingError: If the file cannot be decoded using the
                provided ``encoding``.
            SplurgeDsvPathValidationError: If path validation fails.
            SplurgeDsvError: For other unexpected errors.

        **Deprecated:** This method is deprecated and will be removed in a future release. Consider using splurge-safe-io directly.
        """
        # Emit a DeprecationWarning to signal removal in a future release
        warnings.warn(
            "TextFileHelper.read_as_stream() is deprecated and will be removed in a future release. Consider using splurge-safe-io directly.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Enforce the external library's minimum chunk size. We always delegate
        # chunking behavior to the underlying implementation; the external
        # library defines a MIN_CHUNK_SIZE (default 10) and DEFAULT_CHUNK_SIZE
        # (default 500).
        min_chunk = safe_io_text_file_reader.MIN_CHUNK_SIZE
        chunk_size = max(chunk_size, min_chunk)
        skip_header_rows = max(skip_header_rows, cls.DEFAULT_SKIP_HEADER_ROWS)
        skip_footer_rows = max(skip_footer_rows, cls.DEFAULT_SKIP_FOOTER_ROWS)

        # Validate file path
        effective_file_path = cls._validate_path(
            Path(file_path), must_exist=True, must_be_file=True, must_be_readable=True
        )

        # Use SafeTextFileReader to centralize newline normalization and streaming behavior.
        # Pass chunk_size through so the underlying implementation can honor it.
        try:
            # All per-call options are passed to the constructor; the
            # iterator returned by read_as_stream() accepts no parameters.
            reader = safe_io_text_file_reader.SafeTextFileReader(
                effective_file_path,
                encoding=encoding,
                strip=strip,
                skip_header_lines=skip_header_rows,
                skip_footer_lines=skip_footer_rows,
                chunk_size=chunk_size,
            )
            yield from reader.read_as_stream()

        except safe_io_text_file_reader.SplurgeSafeIoFileDecodingError as ex:
            raise SplurgeDsvFileDecodingError(f"File decoding error: {effective_file_path}") from ex
        except safe_io_text_file_reader.SplurgeSafeIoFilePermissionError as ex:
            raise SplurgeDsvFilePermissionError(f"File permission error: {effective_file_path}") from ex
        except safe_io_text_file_reader.SplurgeSafeIoOsError as ex:
            raise SplurgeDsvFilePermissionError(f"File access error: {effective_file_path}") from ex
        except Exception as ex:
            raise SplurgeDsvError(f"Unexpected error reading file: {effective_file_path}") from ex

    @classmethod
    def read(
        cls,
        file_path: PathLike[str] | str,
        *,
        strip: bool = DEFAULT_STRIP,
        encoding: str = DEFAULT_ENCODING,
        skip_header_rows: int = DEFAULT_SKIP_HEADER_ROWS,
        skip_footer_rows: int = DEFAULT_SKIP_FOOTER_ROWS,
    ) -> list[str]:
        """Read all logical lines from ``file_path`` into memory.

        This convenience method returns the entire file as a list of
        normalized lines. Header and footer rows may be skipped with the
        corresponding parameters.

        Args:
            file_path: Path to the text file to read.
            strip: If True, strip leading/trailing whitespace from each line.
            encoding: Text encoding used to read the file.
            skip_header_rows: Number of leading lines to ignore.
            skip_footer_rows: Number of trailing lines to ignore.

        Returns:
            A list containing every logical line from the file except skipped
            header/footer lines.

        Raises:
            SplurgeDsvFileNotFoundError: If ``file_path`` does not exist.
            SplurgeDsvFilePermissionError: If the file cannot be read due to
                permissions.
            SplurgeDsvFileEncodingError: If the file cannot be decoded using the
                provided ``encoding``.
            SplurgeDsvPathValidationError: If path validation fails.
            SplurgeDsvError: For other unexpected errors.

        **Deprecated:** This method is deprecated and will be removed in a future release. Consider using splurge-safe-io directly.
        """
        # Emit a DeprecationWarning to signal removal in a future release
        warnings.warn(
            "TextFileHelper.read() is deprecated and will be removed in a future release. Consider using splurge-safe-io directly.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Validate file path
        effective_file_path = cls._validate_path(
            Path(file_path), must_exist=True, must_be_file=True, must_be_readable=True
        )

        skip_header_rows = max(skip_header_rows, cls.DEFAULT_SKIP_HEADER_ROWS)
        skip_footer_rows = max(skip_footer_rows, cls.DEFAULT_SKIP_FOOTER_ROWS)

        try:
            reader = safe_io_text_file_reader.SafeTextFileReader(
                effective_file_path,
                encoding=encoding,
                strip=strip,
                skip_header_lines=skip_header_rows,
                skip_footer_lines=skip_footer_rows,
            )
            return reader.read()

        except safe_io_text_file_reader.SplurgeSafeIoFileDecodingError as ex:
            raise SplurgeDsvFileDecodingError(f"File decoding error: {effective_file_path}") from ex
        except safe_io_text_file_reader.SplurgeSafeIoFilePermissionError as ex:
            raise SplurgeDsvFilePermissionError(f"File permission error: {effective_file_path}") from ex
        except safe_io_text_file_reader.SplurgeSafeIoOsError as ex:
            raise SplurgeDsvFilePermissionError(f"File access error: {effective_file_path}") from ex
        except Exception as ex:
            raise SplurgeDsvError(f"Unexpected error reading file: {effective_file_path}") from ex
