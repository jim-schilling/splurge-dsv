"""DSV parsing primitives and configuration objects.

This module exposes the :class:`DsvConfig` dataclass and the :class:`Dsv`
parser. ``DsvConfig`` encapsulates parsing options such as delimiter,
encoding and header/footer skipping. ``Dsv`` is a thin, stateful wrapper
around :mod:`splurge_dsv.dsv_helper` that binds a configuration to
parsing operations and provides convenience methods for parsing strings,
files, and streaming large inputs.

Public API:
    - DsvConfig: Configuration dataclass for parsing behavior.
    - Dsv: Parser instance that performs parse/parse_file/parse_stream.

License: MIT

Copyright (c) 2025 Jim Schilling
"""

# Standard library imports
from collections.abc import Iterator
from dataclasses import dataclass, fields
from os import PathLike

# Local imports
from splurge_dsv.dsv_helper import DsvHelper
from splurge_dsv.exceptions import SplurgeDsvParameterError


@dataclass(frozen=True)
class DsvConfig:
    """Configuration for DSV parsing operations.

    This frozen dataclass stores parsing options and performs basic
    validation in :meth:`__post_init__`.

    Args:
        delimiter: The delimiter character used to separate values.
        strip: Whether to strip whitespace from parsed values.
        bookend: Optional character that wraps text fields (e.g., quotes).
        bookend_strip: Whether to strip whitespace from bookend characters.
        encoding: Text encoding for file operations.
        skip_header_rows: Number of header rows to skip when reading files.
        skip_footer_rows: Number of footer rows to skip when reading files.
        chunk_size: Size of chunks for streaming operations.

    Raises:
        SplurgeDsvParameterError: If delimiter is empty, chunk_size is too
            small, or skip counts are negative.
    """

    delimiter: str
    strip: bool = True
    bookend: str | None = None
    bookend_strip: bool = True
    encoding: str = "utf-8"
    skip_header_rows: int = 0
    skip_footer_rows: int = 0
    chunk_size: int = 500

    def __post_init__(self) -> None:
        """Validate configuration after initialization.

        Ensures required fields are present and numeric ranges are valid.
        """
        if not self.delimiter:
            raise SplurgeDsvParameterError("delimiter cannot be empty or None")

        if self.chunk_size < DsvHelper.DEFAULT_MIN_CHUNK_SIZE:
            raise SplurgeDsvParameterError(
                f"chunk_size must be at least {DsvHelper.DEFAULT_MIN_CHUNK_SIZE}, got {self.chunk_size}"
            )

        if self.skip_header_rows < 0:
            raise SplurgeDsvParameterError(f"skip_header_rows cannot be negative, got {self.skip_header_rows}")

        if self.skip_footer_rows < 0:
            raise SplurgeDsvParameterError(f"skip_footer_rows cannot be negative, got {self.skip_footer_rows}")

    @classmethod
    def csv(cls, **overrides) -> "DsvConfig":
        """
        Create a CSV configuration with sensible defaults.

        Args:
            **overrides: Any configuration values to override

        Returns:
            DsvConfig: CSV configuration object

        Example:
            >>> config = DsvConfig.csv(skip_header_rows=1)
            >>> config.delimiter
            ','
        """
        return cls(delimiter=",", **overrides)

    @classmethod
    def tsv(cls, **overrides) -> "DsvConfig":
        """
        Create a TSV configuration with sensible defaults.

        Args:
            **overrides: Any configuration values to override

        Returns:
            DsvConfig: TSV configuration object

        Example:
            >>> config = DsvConfig.tsv(encoding="utf-16")
            >>> config.delimiter
            '\t'
        """
        return cls(delimiter="\t", **overrides)

    @classmethod
    def from_params(cls, **kwargs) -> "DsvConfig":
        """
        Create a DsvConfig from arbitrary keyword arguments.

        This method filters out any invalid parameters that don't correspond
        to DsvConfig fields, making it safe to pass through arbitrary parameter
        dictionaries (useful for migration from existing APIs).

        Args:
            **kwargs: Configuration parameters (invalid ones are ignored)

        Returns:
            DsvConfig: Configuration object with valid parameters

        Example:
            >>> config = DsvConfig.from_params(delimiter=",", invalid_param="ignored")
            >>> config.delimiter
            ','
        """
        valid_fields = {f.name for f in fields(cls)}
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_fields}
        return cls(**filtered_kwargs)


class Dsv:
    """Parser class that binds a :class:`DsvConfig` to parsing operations.

    The class delegates actual parsing to :mod:`splurge_dsv.dsv_helper` while
    providing a convenient instance API for repeated parsing tasks with the
    same configuration.

    Attributes:
        config (DsvConfig): Configuration instance used for parsing calls.
    """

    def __init__(self, config: DsvConfig) -> None:
        """
        Initialize DSV parser with configuration.

        Args:
            config: DsvConfig object containing parsing parameters

        Example:
            >>> config = DsvConfig(delimiter=",")
            >>> parser = Dsv(config)
        """
        self.config = config

    def parse(self, content: str) -> list[str]:
        """Parse a single DSV record (string) into a list of tokens.

        Args:
            content: Input string representing a single DSV record.

        Returns:
            List of parsed tokens as strings.

        Raises:
            SplurgeDsvParameterError: If the configured delimiter is invalid.
        """
        return DsvHelper.parse(
            content,
            delimiter=self.config.delimiter,
            strip=self.config.strip,
            bookend=self.config.bookend,
            bookend_strip=self.config.bookend_strip,
        )

    def parses(self, content: list[str]) -> list[list[str]]:
        """
        Parse a list of strings into a list of lists of strings.

        Args:
            content: List of strings to parse

        Returns:
            List of lists of parsed strings

        Example:
            >>> parser = Dsv(DsvConfig(delimiter=","))
            >>> parser.parses(["a,b", "c,d"])
            [['a', 'b'], ['c', 'd']]
        """
        return DsvHelper.parses(
            content,
            delimiter=self.config.delimiter,
            strip=self.config.strip,
            bookend=self.config.bookend,
            bookend_strip=self.config.bookend_strip,
        )

    def parse_file(self, file_path: PathLike[str] | str) -> list[list[str]]:
        """Parse a DSV file and return all rows as lists of strings.

        Args:
            file_path: Path to the file to parse.

        Returns:
            A list of rows, where each row is a list of string tokens.

        Raises:
            SplurgeDsvFileNotFoundError: If the file cannot be found.
            SplurgeDsvFilePermissionError: If the file cannot be read.
            SplurgeDsvFileEncodingError: If the file cannot be decoded with
                the configured encoding.
        """
        return DsvHelper.parse_file(
            file_path,
            delimiter=self.config.delimiter,
            strip=self.config.strip,
            bookend=self.config.bookend,
            bookend_strip=self.config.bookend_strip,
            encoding=self.config.encoding,
            skip_header_rows=self.config.skip_header_rows,
            skip_footer_rows=self.config.skip_footer_rows,
        )

    def parse_stream(self, file_path: PathLike[str] | str) -> Iterator[list[list[str]]]:
        """Stream-parse a DSV file, yielding chunks of parsed rows.

        The method yields lists of parsed rows (each row itself is a list of
        strings). Chunk sizing is controlled by the bound configuration's
        ``chunk_size`` value.

        Args:
            file_path: Path to the file to parse.

        Yields:
            Lists of parsed rows, each list containing up to ``chunk_size`` rows.
        """
        return DsvHelper.parse_stream(
            file_path,
            delimiter=self.config.delimiter,
            strip=self.config.strip,
            bookend=self.config.bookend,
            bookend_strip=self.config.bookend_strip,
            encoding=self.config.encoding,
            skip_header_rows=self.config.skip_header_rows,
            skip_footer_rows=self.config.skip_footer_rows,
            chunk_size=self.config.chunk_size,
        )
