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
    """
    Utility class for text file operations.
    All methods are static and memory efficient.

    Newline policy: this library canonicalizes newline sequences. CRLF ("\r\n"), CR ("\r"),
    and LF ("\n") are normalized to Python's universal newline behavior (returns "\n"),
    and methods return logical lines. This is not configurable; it provides a
    deterministic, cross-platform contract for callers and tests.
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
        """
        Count the number of lines in a text file.

        This method efficiently counts lines by iterating through the file
        without loading it entirely into memory.

        Args:
            file_path: Path to the text file
            encoding: File encoding to use (default: 'utf-8')

        Returns:
            int: Number of lines in the file

        Raises:
            SplurgeDsvFileNotFoundError: If the specified file doesn't exist
            SplurgeDsvFilePermissionError: If there are permission issues
            SplurgeDsvFileEncodingError: If the file cannot be decoded with the specified encoding
            SplurgeDsvPathValidationError: If file path validation fails
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
        """
        Preview the first N lines of a text file.

        This method reads up to max_lines from the beginning of the file,
        optionally stripping whitespace from each line and skipping header rows.

        Args:
            file_path: Path to the text file
            max_lines: Maximum number of lines to read (default: 100)
            strip: Whether to strip whitespace from lines (default: True)
            encoding: File encoding to use (default: 'utf-8')
            skip_header_rows: Number of rows to skip from the start (default: 0)

        Returns:
            list[str]: List of lines from the file

        Raises:
            SplurgeDsvParameterError: If max_lines < 1
            SplurgeDsvFileNotFoundError: If the specified file doesn't exist
            SplurgeDsvFilePermissionError: If there are permission issues
            SplurgeDsvFileEncodingError: If the file cannot be decoded with the specified encoding
            SplurgeDsvPathValidationError: If file path validation fails
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
        """
        Read a text file as a stream of line chunks.

        This method yields chunks of lines from the file, allowing for
        memory-efficient processing of large files. Each chunk contains
        up to chunk_size lines. Uses a sliding window approach to handle
        footer row skipping without loading the entire file into memory.

        Args:
            file_path: Path to the text file
            strip: Whether to strip whitespace from lines (default: True)
            encoding: File encoding to use (default: 'utf-8')
            skip_header_rows: Number of rows to skip from the start (default: 0)
            skip_footer_rows: Number of rows to skip from the end (default: 0)
            chunk_size: Number of lines per chunk (default: 500)

        Yields:
            List[str]: Chunks of lines from the file

        Raises:
            SplurgeFileNotFoundError: If the specified file doesn't exist
            SplurgeFilePermissionError: If there are permission issues
            SplurgeFileEncodingError: If the file cannot be decoded with the specified encoding
            SplurgePathValidationError: If file path validation fails
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
        """
        Read the entire contents of a text file into a list of strings.

        This method reads the complete file into memory, with options to
        strip whitespace from each line and skip header/footer rows.

        Args:
            file_path: Path to the text file
            strip: Whether to strip whitespace from lines (default: True)
            encoding: File encoding to use (default: 'utf-8')
            skip_header_rows: Number of rows to skip from the start (default: 0)
            skip_footer_rows: Number of rows to skip from the end (default: 0)

        Returns:
            List[str]: List of all lines from the file, excluding skipped rows

        Raises:
            SplurgeFileNotFoundError: If the specified file doesn't exist
            SplurgeFilePermissionError: If there are permission issues
            SplurgeFileEncodingError: If the file cannot be decoded with the specified encoding
            SplurgePathValidationError: If file path validation fails
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
