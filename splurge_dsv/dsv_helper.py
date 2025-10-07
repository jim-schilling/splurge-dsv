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

# Local imports
from splurge_dsv.exceptions import SplurgeDsvParameterError
from splurge_dsv.string_tokenizer import StringTokenizer
from splurge_dsv.text_file_helper import TextFileHelper


class DsvHelper:
    """
    Utility class for working with DSV (Delimited String Values) files.

    Provides methods to parse DSV content from strings, lists of strings, and files.
    Supports configurable delimiters, text bookends, and whitespace handling options.
    """

    DEFAULT_CHUNK_SIZE = 500  # Default chunk size for streaming operations
    DEFAULT_ENCODING = "utf-8"  # Default text encoding for file operations
    DEFAULT_SKIP_HEADER_ROWS = 0  # Default number of header rows to skip
    DEFAULT_SKIP_FOOTER_ROWS = 0  # Default number of footer rows to skip
    DEFAULT_MIN_CHUNK_SIZE = 100
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

    @classmethod
    def parse_file(
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
            SplurgeDsvFilePermissionError: If the file cannot be accessed due to
                permission restrictions.
            SplurgeDsvFileEncodingError: If the file cannot be decoded using
                the provided ``encoding``.
        """
        lines: list[str] = TextFileHelper.read(
            file_path, encoding=encoding, skip_header_rows=skip_header_rows, skip_footer_rows=skip_footer_rows
        )

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
            SplurgeParameterError: If delimiter is empty or None.
            SplurgeFileNotFoundError: If the file does not exist.
            SplurgeFilePermissionError: If the file cannot be accessed.
            SplurgeFileEncodingError: If the file cannot be decoded with the specified encoding.
        """
        if delimiter is None or delimiter == "":
            raise SplurgeDsvParameterError("delimiter cannot be empty or None")

        chunk_size = max(chunk_size, cls.DEFAULT_MIN_CHUNK_SIZE)
        skip_header_rows = max(skip_header_rows, cls.DEFAULT_SKIP_HEADER_ROWS)
        skip_footer_rows = max(skip_footer_rows, cls.DEFAULT_SKIP_FOOTER_ROWS)

        # Use TextFileHelper.read_as_stream for consistent error handling
        yield from (
            cls._process_stream_chunk(
                chunk, delimiter=delimiter, strip=strip, bookend=bookend, bookend_strip=bookend_strip
            )
            for chunk in TextFileHelper.read_as_stream(
                file_path,
                encoding=encoding,
                skip_header_rows=skip_header_rows,
                skip_footer_rows=skip_footer_rows,
                chunk_size=chunk_size,
            )
        )

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
