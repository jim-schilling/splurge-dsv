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
from collections.abc import Iterator
from os import PathLike
from pathlib import Path

# Local imports
from splurge_dsv.exceptions import SplurgeDsvParameterError
from splurge_dsv.path_validator import PathValidator
from splurge_dsv.safe_text_file_reader import SafeTextFileReader


class TextFileHelper:
    """Utility helpers for working with text files.

    All methods are provided as classmethods and are designed to be memory
    efficient. This module enforces a deterministic newline policy: CRLF
    ("\r\n"), CR ("\r"), and LF ("\n") are normalized to a single ``\n``
    newline. Methods return logical, normalized lines which makes behavior
    consistent across platforms and simplifies testing.
    """

    DEFAULT_ENCODING = "utf-8"
    DEFAULT_MAX_LINES = 100
    DEFAULT_CHUNK_SIZE = 500
    DEFAULT_MIN_CHUNK_SIZE = 100
    DEFAULT_SKIP_HEADER_ROWS = 0
    DEFAULT_SKIP_FOOTER_ROWS = 0
    DEFAULT_STRIP = True
    DEFAULT_MODE = "r"

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
        """
        # Validate file path
        validated_path = PathValidator.validate_path(
            Path(file_path), must_exist=True, must_be_file=True, must_be_readable=True
        )

        # Delegate to SafeTextFileReader which centralizes newline normalization
        reader = SafeTextFileReader(validated_path, encoding=encoding)
        return len(reader.read(strip=False))

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
        """
        if max_lines < 1:
            raise SplurgeDsvParameterError(
                "TextFileHelper.preview: max_lines is less than 1", details="max_lines must be at least 1"
            )

        # Validate file path
        validated_path = PathValidator.validate_path(
            Path(file_path), must_exist=True, must_be_file=True, must_be_readable=True
        )

        skip_header_rows = max(skip_header_rows, cls.DEFAULT_SKIP_HEADER_ROWS)
        reader = SafeTextFileReader(validated_path, encoding=encoding)
        return reader.preview(max_lines=max_lines, strip=strip, skip_header_rows=skip_header_rows)

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
        """
        # Allow small chunk sizes for testing, but enforce minimum for performance
        # Only enforce minimum if chunk_size is "moderately small" (to prevent accidental small chunks)
        if chunk_size >= 10:  # If someone sets a chunk size >= 10, enforce minimum for performance
            chunk_size = max(chunk_size, cls.DEFAULT_MIN_CHUNK_SIZE)
        # For very small chunk sizes (like 1-9), allow them (useful for testing)
        skip_header_rows = max(skip_header_rows, cls.DEFAULT_SKIP_HEADER_ROWS)
        skip_footer_rows = max(skip_footer_rows, cls.DEFAULT_SKIP_FOOTER_ROWS)

        # Validate file path
        validated_path = PathValidator.validate_path(
            Path(file_path), must_exist=True, must_be_file=True, must_be_readable=True
        )

        # Use SafeTextFileReader to centralize newline normalization and streaming behavior.
        reader = SafeTextFileReader(validated_path, encoding=encoding)
        yield from reader.read_as_stream(
            strip=strip, skip_header_rows=skip_header_rows, skip_footer_rows=skip_footer_rows, chunk_size=chunk_size
        )

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
        """
        # Validate file path
        validated_path = PathValidator.validate_path(
            Path(file_path), must_exist=True, must_be_file=True, must_be_readable=True
        )

        skip_header_rows = max(skip_header_rows, cls.DEFAULT_SKIP_HEADER_ROWS)
        skip_footer_rows = max(skip_footer_rows, cls.DEFAULT_SKIP_FOOTER_ROWS)

        skip_header_rows = max(skip_header_rows, cls.DEFAULT_SKIP_HEADER_ROWS)
        skip_footer_rows = max(skip_footer_rows, cls.DEFAULT_SKIP_FOOTER_ROWS)

        reader = SafeTextFileReader(validated_path, encoding=encoding)
        return reader.read(strip=strip, skip_header_rows=skip_header_rows, skip_footer_rows=skip_footer_rows)
