"""
string_tokenizer.py

A utility module for string tokenization operations.
Provides methods to split strings into tokens and manipulate string boundaries.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

# Local imports
from splurge_dsv.exceptions import SplurgeDsvValueError


class StringTokenizer:
    """
    Utility class for string tokenization operations.

    This class provides methods to:
    - Split strings into tokens based on delimiters
    - Process multiple strings into token lists
    - Remove matching characters from string boundaries
    """

    DEFAULT_STRIP = True

    @staticmethod
    def parse(content: str | None, *, delimiter: str, strip: bool = DEFAULT_STRIP) -> list[str]:
        """Tokenize a single string using ``delimiter``.

        The function preserves empty tokens (e.g. ``"a,,c"`` with
        delimiter ``","`` yields ``['a', '', 'c']``). If ``content`` is
        None an empty list is returned.

        Args:
            content: The input string to tokenize, or ``None``.
            delimiter: The delimiter string to split on.
            strip: If True, strip leading/trailing whitespace from each token.

        Returns:
            A list of tokens. Empty tokens are preserved.

        Raises:
            SplurgeDsvValueError: If ``delimiter`` is empty or ``None``.

        Examples:
            >>> StringTokenizer.parse("a,b,c", delimiter=",")
            ['a', 'b', 'c']
            >>> StringTokenizer.parse("a,,c", delimiter=",")
            ['a', '', 'c']
        """
        if content is None:
            return []

        if delimiter is None or delimiter == "":
            raise SplurgeDsvValueError("delimiter cannot be empty or None")

        # If stripping is enabled and the input is only whitespace (or
        # empty), treat it as a single empty token rather than returning an
        # empty list. Returning [] causes downstream code that expects the
        # same number of columns as the header to raise IndexError. The
        # external safe reader yields empty strings for blank lines, so we
        # preserve that semantic here.
        if strip and not content.strip():
            return [""]

        result: list[str] = content.split(delimiter)
        if strip:
            result = [token.strip() for token in result]
        return result

    @classmethod
    def parses(cls, content: list[str], *, delimiter: str, strip: bool = DEFAULT_STRIP) -> list[list[str]]:
        """Tokenize multiple strings.

        Args:
            content: A list of strings to tokenize.
            delimiter: The delimiter to use for splitting.
            strip: If True, strip whitespace from tokens.

        Returns:
            A list where each element is the token list for the corresponding
            input string.

        Raises:
            SplurgeDsvValueError: If ``delimiter`` is empty or ``None``.

        Example:
            >>> StringTokenizer.parses(["a,b", "c,d"], delimiter=",")
            [['a', 'b'], ['c', 'd']]
        """
        if delimiter is None or delimiter == "":
            raise SplurgeDsvValueError("delimiter cannot be empty or None")

        return [cls.parse(text, delimiter=delimiter, strip=strip) for text in content]

    @staticmethod
    def remove_bookends(content: str, *, bookend: str, strip: bool = DEFAULT_STRIP) -> str:
        """Remove matching bookend characters from both endpoints of ``content``.

        The function optionally strips surrounding whitespace before checking
        for matching bookend characters. If both ends match the provided
        ``bookend`` and the remaining content is long enough, the bookends are
        removed; otherwise the possibly-stripped input is returned unchanged.

        Args:
            content: The input string to process.
            bookend: The bookend string to remove from both ends (e.g. '"').
            strip: If True, strip whitespace prior to bookend removal.

        Returns:
            The input string with matching bookend characters removed when
            applicable.

        Raises:
            SplurgeDsvValueError: If ``bookend`` is empty or ``None``.

        Example:
            >>> StringTokenizer.remove_bookends("'hello'", bookend="'")
            'hello'
        """
        if bookend is None or bookend == "":
            raise SplurgeDsvValueError("bookend cannot be empty or None")

        value: str = content.strip() if strip else content
        if value.startswith(bookend) and value.endswith(bookend) and len(value) > 2 * len(bookend) - 1:
            return value[len(bookend) : -len(bookend)]
        return value
