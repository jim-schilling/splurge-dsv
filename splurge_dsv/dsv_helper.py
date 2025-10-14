"""
A utility module for working with DSV (Delimited String Values) files.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

# Standard library imports
from collections.abc import Iterator
from os import PathLike
from pathlib import Path

import splurge_safe_io.constants as safe_io_constants
import splurge_safe_io.path_validator as safe_io_path_validator
import splurge_safe_io.safe_text_file_reader as safe_io_text_file_reader

# Local imports
from splurge_dsv.exceptions import (
    SplurgeDsvColumnMismatchError,
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
    # When detecting normalize_columns across a stream, how many chunks to scan
    # before giving up. Scanning more chunks increases work but helps if the
    # first logical row starts later than the first chunk (e.g., many blank lines
    # or very small chunks). Keep small by default to avoid buffering too much.
    MAX_DETECT_CHUNKS = 10
    DEFAULT_ENCODING = "utf-8"
    DEFAULT_SKIP_HEADER_ROWS = 0
    DEFAULT_SKIP_FOOTER_ROWS = 0
    DEFAULT_MIN_CHUNK_SIZE = safe_io_constants.MIN_CHUNK_SIZE
    DEFAULT_STRIP = True
    DEFAULT_BOOKEND_STRIP = True

    @classmethod
    def parse(
        cls,
        content: str,
        *,
        delimiter: str,
        strip: bool = DEFAULT_STRIP,
        bookend: str | None = None,
        bookend_strip: bool = DEFAULT_BOOKEND_STRIP,
        normalize_columns: int = 0,
        raise_on_missing_columns: bool = False,
        raise_on_extra_columns: bool = False,
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
            normalize_columns: If > 0, ensure the returned list has exactly this many columns,
                padding with empty strings or truncating as needed.
            raise_on_missing_columns: If True, raise an error if the line has fewer columns than ``normalize_columns``.
            raise_on_extra_columns: If True, raise an error if the line has more columns than

        Returns:
            A list of parsed token strings.

        Raises:
            SplurgeDsvParameterError: If ``delimiter`` is empty or None.
            SplurgeDsvParameterError: If ``normalize_columns`` is negative.
            SplurgeDsvColumnMismatchError: If column validation fails.

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

        # If requested, validate columns (raises) and/or normalize the row length
        if normalize_columns and normalize_columns > 0:
            # Validation is only performed if the caller asked for raises
            if raise_on_missing_columns or raise_on_extra_columns:
                cls._validate_columns(
                    len(tokens),
                    expected_columns=normalize_columns,
                    raise_on_missing_columns=raise_on_missing_columns,
                    raise_on_extra_columns=raise_on_extra_columns,
                )

            tokens = cls._normalize_columns(tokens, expected_columns=normalize_columns)

        return tokens

    @classmethod
    def _normalize_columns(cls, row: list[str], *, expected_columns: int) -> list[str]:
        """Normalize a token list to the expected number of columns.

        If the row has fewer columns than expected, append empty strings to reach
        the expected length. If the row has more columns than expected, truncate
        the excess columns.

        Args:
            row: The list of tokens to normalize.
            expected_columns: Desired number of columns.

        Returns:
            A new list of tokens with length == expected_columns.

        Raises:
            SplurgeDsvParameterError: If ``expected_columns`` is negative.
        """
        if expected_columns < 0:
            raise SplurgeDsvParameterError("expected_columns must be non-negative")

        current = len(row)
        if current == expected_columns:
            return row
        if current < expected_columns:
            # append empty strings
            return row + [""] * (expected_columns - current)
        # current > expected -> truncate
        return row[:expected_columns]

    @classmethod
    def _validate_columns(
        cls, actual_columns: int, *, expected_columns: int, raise_on_missing_columns: bool, raise_on_extra_columns: bool
    ) -> None:
        """Validate column count against expected_columns.

        Raises a SplurgeDsvError (or a more specific subclass) when the
        validation fails according to the provided flags.

        Args:
            actual_columns: The actual number of columns in the row.
            expected_columns: The expected number of columns.
            raise_on_missing_columns: If True, raise an error if actual_columns < expected_columns.
            raise_on_extra_columns: If True, raise an error if actual_columns > expected_columns.

        Raises:
            SplurgeDsvColumnMismatchError: If column validation fails.
            SplurgeDsvParameterError: If ``expected_columns`` is negative.
        """
        if expected_columns < 0:
            raise SplurgeDsvParameterError("expected_columns must be non-negative")

        if raise_on_missing_columns and actual_columns < expected_columns:
            raise SplurgeDsvColumnMismatchError(f"Row is missing columns: ({actual_columns} < {expected_columns})")

        if raise_on_extra_columns and actual_columns > expected_columns:
            raise SplurgeDsvColumnMismatchError(f"Row has extra columns: ({actual_columns} > {expected_columns})")

    @classmethod
    def parses(
        cls,
        content: list[str],
        *,
        delimiter: str,
        strip: bool = DEFAULT_STRIP,
        bookend: str | None = None,
        bookend_strip: bool = DEFAULT_BOOKEND_STRIP,
        normalize_columns: int = 0,
        raise_on_missing_columns: bool = False,
        raise_on_extra_columns: bool = False,
        detect_columns: bool = False,
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
            normalize_columns: If > 0, ensure each returned list has exactly this many columns,
                padding with empty strings or truncating as needed.
            raise_on_missing_columns: If True, raise an error if a line has fewer columns than ``normalize_columns``.
            raise_on_extra_columns: If True, raise an error if a line has more columns than ``normalize_columns``.
            detect_columns: If True and ``normalize_columns`` is not set or <= 0, detect the number of columns from the content.

        Returns:
            A list of token lists, one per input line.

        Raises:
            SplurgeDsvParameterError: If ``content`` is not a list of strings, or
                if ``delimiter`` is empty or None, or if ``normalize_columns`` is negative.
            SplurgeDsvColumnMismatchError: If column validation fails.

        Example:
            >>> DsvHelper.parses(["a,b,c", "d,e,f"], delimiter=",")
            [['a', 'b', 'c'], ['d', 'e', 'f']]
        """
        if not isinstance(content, list):
            raise SplurgeDsvParameterError("content must be a list")

        if not all(isinstance(item, str) for item in content):
            raise SplurgeDsvParameterError("content must be a list of strings")

        # If requested, detect expected columns from the first logical row
        if detect_columns and (not normalize_columns or normalize_columns <= 0):
            if not content:
                return []
            # Find the first non-blank logical row in the provided content
            first_non_blank = None
            for ln in content:
                if isinstance(ln, str) and ln.strip() != "":
                    first_non_blank = ln
                    break
            if first_non_blank is None:
                return []

            detected = cls.parse(
                first_non_blank,
                delimiter=delimiter,
                strip=strip,
                bookend=bookend,
                bookend_strip=bookend_strip,
                normalize_columns=0,
                raise_on_missing_columns=False,
                raise_on_extra_columns=False,
            )
            normalize_columns = len(detected)

        return [
            cls.parse(
                item,
                delimiter=delimiter,
                strip=strip,
                bookend=bookend,
                bookend_strip=bookend_strip,
                normalize_columns=normalize_columns,
                raise_on_missing_columns=raise_on_missing_columns,
                raise_on_extra_columns=raise_on_extra_columns,
            )
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
        skip_empty_lines: bool = False,
        normalize_columns: int = 0,
        raise_on_missing_columns: bool = False,
        raise_on_extra_columns: bool = False,
        detect_columns: bool = False,
    ) -> list[list[str]]:
        """Read and parse an entire DSV file.

        This convenience reads all lines from ``file_path`` using
        :class:`splurge_safe_io.safe_text_file_reader.SafeTextFileReader` and then parses each
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
            normalize_columns: Number of columns to normalize.
            raise_on_missing_columns: Raise an error if a line has fewer columns than ``normalize_columns``.
            raise_on_extra_columns: Raise an error if a line has more columns than ``normalize_columns``.

        Returns:
            A list of token lists (one list per non-skipped line).

        Raises:
            SplurgeDsvParameterError: If ``delimiter`` is empty or None, or if ``normalize_columns`` is negative.
            SplurgeDsvFileNotFoundError: If the file at ``file_path`` does not exist.
            SplurgeDsvFilePermissionError: If the file cannot be accessed due to permission restrictions.
            SplurgeDsvFileDecodingError: If the file cannot be decoded using the provided ``encoding``.
            SplurgeDsvPathValidationError: If the file path is invalid.
            SplurgeDsvColumnMismatchError: If column validation fails.
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
                skip_empty_lines=skip_empty_lines,
            )
            lines: list[str] = reader.read()

        except safe_io_text_file_reader.SplurgeSafeIoFileDecodingError as ex:
            raise SplurgeDsvFileDecodingError(f"File decoding error: {effective_file_path}") from ex
        except safe_io_text_file_reader.SplurgeSafeIoFilePermissionError as ex:
            raise SplurgeDsvFilePermissionError(f"File permission error: {effective_file_path}") from ex
        except safe_io_text_file_reader.SplurgeSafeIoOsError as ex:
            raise SplurgeDsvFilePermissionError(f"File access error: {effective_file_path}") from ex
        except Exception as ex:
            # If the exception is already a SplurgeDsvError (or subclass),
            # re-raise it unchanged so callers can handle specific errors
            # (for example, SplurgeDsvColumnMismatchError from validation).
            if isinstance(ex, SplurgeDsvError):
                raise

            raise SplurgeDsvError(f"Unexpected error reading file: {effective_file_path}") from ex

        return cls.parses(
            lines,
            delimiter=delimiter,
            strip=strip,
            bookend=bookend,
            bookend_strip=bookend_strip,
            normalize_columns=normalize_columns,
            raise_on_missing_columns=raise_on_missing_columns,
            raise_on_extra_columns=raise_on_extra_columns,
            detect_columns=detect_columns,
        )

    @classmethod
    def _process_stream_chunk(
        cls,
        chunk: list[str],
        *,
        delimiter: str,
        strip: bool = DEFAULT_STRIP,
        bookend: str | None = None,
        bookend_strip: bool = DEFAULT_BOOKEND_STRIP,
        normalize_columns: int = 0,
        raise_on_missing_columns: bool = False,
        raise_on_extra_columns: bool = False,
    ) -> list[list[str]]:
        """Parse a chunk of lines into tokenized rows.

        Designed to be used by :meth:`parse_file_stream` as a helper for converting a
        batch of raw lines into parsed rows.

        Args:
            chunk: A list of raw input lines.
            delimiter: Delimiter used to split each line.
            strip: If True, strip whitespace from tokens.
            bookend: Optional bookend character to remove from tokens.
            bookend_strip: If True, strip whitespace after removing bookends.
            normalize_columns: If > 0, ensure each returned list has exactly this many columns,
                padding with empty strings or truncating as needed.
            raise_on_missing_columns: If True, raise an error if a line has fewer columns than ``normalize_columns``.
            raise_on_extra_columns: If True, raise an error if a line has more columns than ``normalize_columns``.

        Raises:
            SplurgeDsvParameterError: If ``delimiter`` is empty or None,
                or if ``normalize_columns`` is negative,
                or if ``chunk`` is not a list of strings, or if any element in ``chunk`` is not a string.
            SplurgeDsvColumnMismatchError: If column validation fails.

        Returns:
            A list where each element is the token list for a corresponding
            input line from ``chunk``.
        """
        return cls.parses(
            chunk,
            delimiter=delimiter,
            strip=strip,
            bookend=bookend,
            bookend_strip=bookend_strip,
            normalize_columns=normalize_columns,
            raise_on_missing_columns=raise_on_missing_columns,
            raise_on_extra_columns=raise_on_extra_columns,
        )

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
        skip_empty_lines: bool = False,
        normalize_columns: int = 0,
        raise_on_missing_columns: bool = False,
        raise_on_extra_columns: bool = False,
        detect_columns: bool = False,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        # How many chunks to scan when attempting to detect normalize_columns
        # from the beginning of a stream. Only used when
        # `detect_columns is True` and `normalize_columns` is falsy.
        max_detect_chunks: int = MAX_DETECT_CHUNKS,
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
            normalize_columns (int): If > 0, ensure each returned list has exactly this many columns,
                padding with empty strings or truncating as needed.
            raise_on_missing_columns (bool): If True, raise an error if a line has fewer columns than ``normalize_columns``.
            raise_on_extra_columns (bool): If True, raise an error if a line has more columns than ``normalize_columns``.
            detect_columns (bool): If True and ``normalize_columns`` is not set or <= 0,
                detect the expected number of columns from the first non-blank logical row.
            chunk_size (int): Number of lines per chunk (default: 100).
            max_detect_chunks (int): When detecting columns, how many chunks to scan
                from the start of the stream before giving up (default: 10).

        Yields:
            list[list[str]]: Parsed rows for each chunk.

        Raises:
            SplurgeDsvParameterError: If delimiter is empty or None, or if ``normalize_columns`` is negative,
                or if ``chunk`` is not a list of strings, or if any element in ``chunk`` is not a string.
            SplurgeDsvFileNotFoundError: If the file does not exist.
            SplurgeDsvFilePermissionError: If the file cannot be accessed.
            SplurgeDsvFileDecodingError: If the file cannot be decoded with the specified encoding.
            SplurgeDsvPathValidationError: If the file path is invalid.
            SplurgeDsvError: For other unexpected errors.
            SplurgeDsvColumnMismatchError: If column validation fails.
        """

        effective_file_path = cls._validate_file_path(Path(file_path))

        chunk_size = max(chunk_size, cls.DEFAULT_MIN_CHUNK_SIZE)
        skip_header_rows = max(skip_header_rows, cls.DEFAULT_SKIP_HEADER_ROWS)
        skip_footer_rows = max(skip_footer_rows, cls.DEFAULT_SKIP_FOOTER_ROWS)
        # Allow callers to pass None to use the module default. Ensure we have
        # a positive integer to drive the detection loop.
        if max_detect_chunks is None:
            max_detect_chunks = cls.MAX_DETECT_CHUNKS
        else:
            max_detect_chunks = max(int(max_detect_chunks), 1)

        try:
            reader = safe_io_text_file_reader.SafeTextFileReader(
                effective_file_path,
                encoding=encoding,
                skip_header_lines=skip_header_rows,
                skip_footer_lines=skip_footer_rows,
                strip=strip,
                skip_empty_lines=skip_empty_lines,
                chunk_size=chunk_size,
            )
            stream_iter = reader.read_as_stream()

            if detect_columns and (not normalize_columns or normalize_columns <= 0):
                # Buffer up to `max_detect_chunks` from the stream while
                # searching for the first non-blank logical row. This allows us
                # to detect the expected column count even if the first logical
                # row doesn't appear in the very first chunk (for example,
                # when the file begins with many blank lines or very small
                # chunks).
                buffered_chunks: list[list[str]] = []
                max_scan = max_detect_chunks if max_detect_chunks is not None else cls.MAX_DETECT_CHUNKS
                chunks_scanned = 0

                while chunks_scanned < max_scan:
                    try:
                        chunk = next(stream_iter)
                    except StopIteration:
                        break
                    buffered_chunks.append(chunk)

                    # Inspect this chunk for the first non-blank logical row
                    first_line = None
                    for ln in chunk:
                        if isinstance(ln, str) and ln.strip() != "":
                            first_line = ln
                            break

                    if first_line is not None:
                        detected = cls.parse(
                            first_line,
                            delimiter=delimiter,
                            strip=strip,
                            bookend=bookend,
                            bookend_strip=bookend_strip,
                            normalize_columns=0,
                            raise_on_missing_columns=False,
                            raise_on_extra_columns=False,
                        )
                        normalize_columns = len(detected)
                        # remember which buffered chunk contained the first
                        # logical row so we can start applying normalization
                        # beginning with that chunk only
                        detected_index = len(buffered_chunks) - 1
                        break

                    chunks_scanned += 1

                # Replay any buffered chunks (in order) so callers receive the
                # full content starting at the beginning of the file. If we
                # detected the first logical row in one of the buffered chunks
                # then only apply normalization beginning with that chunk;
                # earlier buffered chunks must be emitted without
                # normalization so we don't convert blank-only lines into
                # padded empty-token rows.
                if "detected_index" in locals():
                    for idx, b in enumerate(buffered_chunks):
                        use_norm = normalize_columns if idx == detected_index else 0
                        yield cls._process_stream_chunk(
                            b,
                            delimiter=delimiter,
                            strip=strip,
                            bookend=bookend,
                            bookend_strip=bookend_strip,
                            normalize_columns=use_norm,
                            raise_on_missing_columns=raise_on_missing_columns,
                            raise_on_extra_columns=raise_on_extra_columns,
                        )
                else:
                    for b in buffered_chunks:
                        yield cls._process_stream_chunk(
                            b,
                            delimiter=delimiter,
                            strip=strip,
                            bookend=bookend,
                            bookend_strip=bookend_strip,
                            normalize_columns=0,
                            raise_on_missing_columns=raise_on_missing_columns,
                            raise_on_extra_columns=raise_on_extra_columns,
                        )

            # Continue streaming the rest of the file
            for chunk in stream_iter:
                yield cls._process_stream_chunk(
                    chunk,
                    delimiter=delimiter,
                    strip=strip,
                    bookend=bookend,
                    bookend_strip=bookend_strip,
                    normalize_columns=normalize_columns,
                    raise_on_missing_columns=raise_on_missing_columns,
                    raise_on_extra_columns=raise_on_extra_columns,
                )
        except safe_io_text_file_reader.SplurgeSafeIoFileDecodingError as ex:
            raise SplurgeDsvFileDecodingError(f"File decoding error: {effective_file_path}") from ex
        except safe_io_text_file_reader.SplurgeSafeIoFilePermissionError as ex:
            raise SplurgeDsvFilePermissionError(f"File permission error: {effective_file_path}") from ex
        except safe_io_text_file_reader.SplurgeSafeIoOsError as ex:
            raise SplurgeDsvFilePermissionError(f"File access error: {effective_file_path}") from ex
        except Exception as ex:
            # Preserve and re-raise known SplurgeDsvError subclasses so
            # callers can handle specific errors (e.g. column mismatch) as
            # intended. Only wrap unknown exceptions in a generic
            # SplurgeDsvError.
            if isinstance(ex, SplurgeDsvError):
                raise

            raise SplurgeDsvError(f"Unexpected error reading file: {effective_file_path}") from ex
