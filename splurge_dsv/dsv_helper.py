"""
A utility module for working with DSV (Delimited String Values) files.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

# Standard library imports
import warnings
from collections.abc import Iterator
from os import PathLike
from pathlib import Path

import splurge_safe_io.constants as safe_io_constants
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
from splurge_dsv.string_tokenizer import StringTokenizer


class DsvHelper:
    """
    Utility class for working with DSV (Delimited String Values) files.

    Provides methods to parse DSV content from strings, lists of strings, and files.
    Supports configurable delimiters, text bookends, and whitespace handling options.
    """

    DEFAULT_CHUNK_SIZE = safe_io_constants.DEFAULT_CHUNK_SIZE
    DEFAULT_ENCODING = "utf-8"
    DEFAULT_SKIP_HEADER_ROWS = 0
    DEFAULT_SKIP_FOOTER_ROWS = 0
    DEFAULT_MIN_CHUNK_SIZE = safe_io_constants.MIN_CHUNK_SIZE
    DEFAULT_STRIP = True
    DEFAULT_BOOKEND_STRIP = True

    @staticmethod
    def parse(
        content: str,
        *,
        delimiter: str,
        strip: bool = DEFAULT_STRIP,
        bookend: str | None = None,
        bookend_strip: bool = DEFAULT_BOOKEND_STRIP,
    ) -> list[str]:
        """Parse a single DSV line into tokens.

        This method tokenizes a single line of DSV text using the provided
        ``delimiter``. It optionally strips surrounding whitespace from each
        token and may remove configured bookend characters (for example,
        double-quotes used around fields).

        Args:
            content: The input line to tokenize.
            delimiter: A single-character delimiter string (e.g. "," or "\t").
            strip: If True, strip leading/trailing whitespace from each token.
            bookend: Optional bookend character to remove from token ends.
            bookend_strip: If True, strip whitespace after removing bookends.

        Returns:
            A list of parsed token strings.

        Raises:
            SplurgeDsvParameterError: If ``delimiter`` is empty or None.

        Examples:
            >>> DsvHelper.parse("a,b,c", delimiter=",")
            ['a', 'b', 'c']
            >>> DsvHelper.parse('"a","b","c"', delimiter=",", bookend='"')
            ['a', 'b', 'c']
        """
        if delimiter is None or delimiter == "":
            raise SplurgeDsvParameterError("delimiter cannot be empty or None")

        tokens: list[str] = StringTokenizer.parse(content, delimiter=delimiter, strip=strip)

        if bookend:
            tokens = [StringTokenizer.remove_bookends(token, bookend=bookend, strip=bookend_strip) for token in tokens]

        return tokens

    @classmethod
    def parses(
        cls,
        content: list[str],
        *,
        delimiter: str,
        strip: bool = DEFAULT_STRIP,
        bookend: str | None = None,
        bookend_strip: bool = DEFAULT_BOOKEND_STRIP,
    ) -> list[list[str]]:
        """Parse multiple DSV lines.

        Given a list of lines (for example, the result of reading a file),
        return a list where each element is the list of tokens for that line.

        Args:
            content: A list of input lines to parse.
            delimiter: Delimiter used to split each line.
            strip: If True, strip whitespace from tokens.
            bookend: Optional bookend character to remove from tokens.
            bookend_strip: If True, strip whitespace after removing bookends.

        Returns:
            A list of token lists, one per input line.

        Raises:
            SplurgeDsvParameterError: If ``content`` is not a list of strings or
                if ``delimiter`` is empty or None.

        Example:
            >>> DsvHelper.parses(["a,b,c", "d,e,f"], delimiter=",")
            [['a', 'b', 'c'], ['d', 'e', 'f']]
        """
        if not isinstance(content, list):
            raise SplurgeDsvParameterError("content must be a list")

        if not all(isinstance(item, str) for item in content):
            raise SplurgeDsvParameterError("content must be a list of strings")

        return [
            cls.parse(item, delimiter=delimiter, strip=strip, bookend=bookend, bookend_strip=bookend_strip)
            for item in content
        ]

    @staticmethod
    def _validate_file_path(
        file_path: Path | str, *, must_exist: bool = True, must_be_file: bool = True, must_be_readable: bool = True
    ) -> Path:
        """Validate the provided file path.

        Args:
            file_path: The file path to validate.

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
                Path(file_path), must_exist=must_exist, must_be_file=must_be_file, must_be_readable=must_be_readable
            )
        except safe_io_path_validator.SplurgeSafeIoPathValidationError as ex:
            raise SplurgeDsvPathValidationError(f"Invalid file path: {file_path}") from ex
        except safe_io_path_validator.SplurgeSafeIoFileNotFoundError as ex:
            raise SplurgeDsvFileNotFoundError(f"File not found: {file_path}") from ex
        except safe_io_path_validator.SplurgeSafeIoFilePermissionError as ex:
            raise SplurgeDsvFilePermissionError(f"File permission error: {file_path}") from ex
        except Exception as ex:
            raise SplurgeDsvError(f"Unexpected error validating file path: {file_path}") from ex

        return effective_path

    @classmethod
    def parse_file(
        cls,
        file_path: PathLike[str] | Path | str,
        *,
        delimiter: str,
        strip: bool = DEFAULT_STRIP,
        bookend: str | None = None,
        bookend_strip: bool = DEFAULT_BOOKEND_STRIP,
        encoding: str = DEFAULT_ENCODING,
        skip_header_rows: int = DEFAULT_SKIP_HEADER_ROWS,
        skip_footer_rows: int = DEFAULT_SKIP_FOOTER_ROWS,
    ) -> list[list[str]]:
        """Read and parse an entire DSV file.

        This convenience reads all lines from ``file_path`` using
        :class:`splurge_dsv.text_file_helper.TextFileHelper` and then parses each
        line into tokens. Header and footer rows may be skipped via the
        ``skip_header_rows`` and ``skip_footer_rows`` parameters.

        Args:
            file_path: Path to the file to read.
            delimiter: Delimiter to split fields on.
            strip: If True, strip whitespace from tokens.
            bookend: Optional bookend character to remove from tokens.
            bookend_strip: If True, strip whitespace after removing bookends.
            encoding: Text encoding to use when reading the file.
            skip_header_rows: Number of leading lines to ignore.
            skip_footer_rows: Number of trailing lines to ignore.

        Returns:
            A list of token lists (one list per non-skipped line).

        Raises:
            SplurgeDsvParameterError: If ``delimiter`` is empty or None.
            SplurgeDsvFileNotFoundError: If the file at ``file_path`` does not exist.
            SplurgeDsvFilePermissionError: If the file cannot be accessed due to permission restrictions.
            SplurgeDsvFileDecodingError: If the file cannot be decoded using the provided ``encoding``.
            SplurgeDsvError: For other unexpected errors.
        """
        effective_file_path = cls._validate_file_path(Path(file_path))

        skip_header_rows = max(skip_header_rows, cls.DEFAULT_SKIP_HEADER_ROWS)
        skip_footer_rows = max(skip_footer_rows, cls.DEFAULT_SKIP_FOOTER_ROWS)

        try:
            reader = safe_io_text_file_reader.SafeTextFileReader(
                effective_file_path,
                encoding=encoding,
                skip_header_lines=skip_header_rows,
                skip_footer_lines=skip_footer_rows,
                strip=strip,
            )
            lines: list[str] = reader.read()

        except safe_io_text_file_reader.SplurgeSafeIoFileDecodingError as ex:
            raise SplurgeDsvFileDecodingError(f"File decoding error: {effective_file_path}") from ex
        except safe_io_text_file_reader.SplurgeSafeIoFilePermissionError as ex:
            raise SplurgeDsvFilePermissionError(f"File permission error: {effective_file_path}") from ex
        except safe_io_text_file_reader.SplurgeSafeIoOsError as ex:
            raise SplurgeDsvFilePermissionError(f"File access error: {effective_file_path}") from ex
        except Exception as ex:
            raise SplurgeDsvError(f"Unexpected error reading file: {effective_file_path}") from ex

        return cls.parses(lines, delimiter=delimiter, strip=strip, bookend=bookend, bookend_strip=bookend_strip)

    @classmethod
    def _process_stream_chunk(
        cls,
        chunk: list[str],
        *,
        delimiter: str,
        strip: bool = DEFAULT_STRIP,
        bookend: str | None = None,
        bookend_strip: bool = DEFAULT_BOOKEND_STRIP,
    ) -> list[list[str]]:
        """Parse a chunk of lines into tokenized rows.

        Designed to be used by :meth:`parse_stream` as a helper for converting a
        batch of raw lines into parsed rows.

        Args:
            chunk: A list of raw input lines.
            delimiter: Delimiter used to split each line.
            strip: If True, strip whitespace from tokens.
            bookend: Optional bookend character to remove from tokens.
            bookend_strip: If True, strip whitespace after removing bookends.

        Returns:
            A list where each element is the token list for a corresponding
            input line from ``chunk``.
        """
        return cls.parses(chunk, delimiter=delimiter, strip=strip, bookend=bookend, bookend_strip=bookend_strip)

    @classmethod
    def parse_file_stream(
        cls,
        file_path: PathLike[str] | str,
        *,
        delimiter: str,
        strip: bool = DEFAULT_STRIP,
        bookend: str | None = None,
        bookend_strip: bool = DEFAULT_BOOKEND_STRIP,
        encoding: str = DEFAULT_ENCODING,
        skip_header_rows: int = DEFAULT_SKIP_HEADER_ROWS,
        skip_footer_rows: int = DEFAULT_SKIP_FOOTER_ROWS,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> Iterator[list[list[str]]]:
        """
        Stream-parse a DSV file into chunks of lines.

        Args:
            file_path (PathLike[str] | str): The path to the file to parse.
            delimiter (str): The delimiter to use.
            strip (bool): Whether to strip whitespace from the strings.
            bookend (str | None): The bookend to use for text fields.
            bookend_strip (bool): Whether to strip whitespace from the bookend.
            encoding (str): The file encoding.
            skip_header_rows (int): Number of header rows to skip.
            skip_footer_rows (int): Number of footer rows to skip.
            chunk_size (int): Number of lines per chunk (default: 100).

        Yields:
            list[list[str]]: Parsed rows for each chunk.

        Raises:
            SplurgeDsvParameterError: If delimiter is empty or None.
            SplurgeDsvFileNotFoundError: If the file does not exist.
            SplurgeDsvFilePermissionError: If the file cannot be accessed.
            SplurgeDsvFileDecodingError: If the file cannot be decoded with the specified encoding.
            SplurgeDsvPathValidationError: If the file path is invalid.
            SplurgeDsvError: For other unexpected errors.
        """

        effective_file_path = cls._validate_file_path(Path(file_path))

        chunk_size = max(chunk_size, cls.DEFAULT_MIN_CHUNK_SIZE)
        skip_header_rows = max(skip_header_rows, cls.DEFAULT_SKIP_HEADER_ROWS)
        skip_footer_rows = max(skip_footer_rows, cls.DEFAULT_SKIP_FOOTER_ROWS)

        try:
            reader = safe_io_text_file_reader.SafeTextFileReader(
                effective_file_path,
                encoding=encoding,
                skip_header_lines=skip_header_rows,
                skip_footer_lines=skip_footer_rows,
                strip=strip,
                chunk_size=chunk_size,
            )
            yield from (
                cls._process_stream_chunk(
                    chunk, delimiter=delimiter, strip=strip, bookend=bookend, bookend_strip=bookend_strip
                )
                for chunk in reader.read_as_stream()
            )
        except safe_io_text_file_reader.SplurgeSafeIoFileDecodingError as ex:
            raise SplurgeDsvFileDecodingError(f"File decoding error: {effective_file_path}") from ex
        except safe_io_text_file_reader.SplurgeSafeIoFilePermissionError as ex:
            raise SplurgeDsvFilePermissionError(f"File permission error: {effective_file_path}") from ex
        except safe_io_text_file_reader.SplurgeSafeIoOsError as ex:
            raise SplurgeDsvFilePermissionError(f"File access error: {effective_file_path}") from ex
        except Exception as ex:
            raise SplurgeDsvError(f"Unexpected error reading file: {effective_file_path}") from ex

    @classmethod
    def parse_stream(
        cls,
        file_path: PathLike[str] | str,
        *,
        delimiter: str,
        strip: bool = DEFAULT_STRIP,
        bookend: str | None = None,
        bookend_strip: bool = DEFAULT_BOOKEND_STRIP,
        encoding: str = DEFAULT_ENCODING,
        skip_header_rows: int = DEFAULT_SKIP_HEADER_ROWS,
        skip_footer_rows: int = DEFAULT_SKIP_FOOTER_ROWS,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> Iterator[list[list[str]]]:
        """
        Stream-parse a DSV file, yielding chunks of parsed rows.

        The method yields lists of parsed rows (each row itself is a list of
        strings). Chunk sizing is controlled by the bound configuration's
        ``chunk_size`` value.

        Args:
            file_path: Path to the file to parse.

        Yields:
            Lists of parsed rows, each list containing up to ``chunk_size`` rows.

        Deprecated: Use `parse_file_stream` instead. This method will be removed in a future release.
        """
        # Emit a DeprecationWarning to signal removal in a future release
        warnings.warn(
            "DsvHelper.parse_stream() is deprecated and will be removed in a future release; use DsvHelper.parse_file_stream() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        return cls.parse_file_stream(
            file_path,
            delimiter=delimiter,
            strip=strip,
            bookend=bookend,
            bookend_strip=bookend_strip,
            encoding=encoding,
            skip_header_rows=skip_header_rows,
            skip_footer_rows=skip_footer_rows,
            chunk_size=chunk_size,
        )
