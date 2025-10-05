"""
DSV (Delimited String Values) parsing with configuration objects.

This module provides a modern, object-oriented API for DSV parsing using
configuration dataclasses for better type safety and reusability.

Copyright (c) 2025 Jim Schilling

This module is licensed under the MIT License.

Please preserve this header and all related material when sharing!
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
    """
    Configuration for DSV parsing operations.

    This frozen dataclass encapsulates all configuration parameters for DSV parsing,
    providing type safety, validation, and convenient factory methods.

    Attributes:
        delimiter: The delimiter character used to separate values
        strip: Whether to strip whitespace from parsed values
        bookend: Optional character that wraps text fields (e.g., quotes)
        bookend_strip: Whether to strip whitespace from bookend characters
        encoding: Text encoding for file operations
        skip_header_rows: Number of header rows to skip when reading files
        skip_footer_rows: Number of footer rows to skip when reading files
        chunk_size: Size of chunks for streaming operations
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
        """Validate configuration after initialization."""
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
    """
    DSV parser with encapsulated configuration.

    This class provides an object-oriented interface for DSV parsing operations,
    encapsulating configuration to enable reuse across multiple parsing operations.

    Attributes:
        config: The DsvConfig object containing parsing configuration
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
        """
        Parse a string into a list of strings.

        Args:
            content: The string to parse

        Returns:
            List of parsed strings

        Example:
            >>> parser = Dsv(DsvConfig(delimiter=","))
            >>> parser.parse("a,b,c")
            ['a', 'b', 'c']
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
        """
        Parse a file into a list of lists of strings.

        Args:
            file_path: Path to the file to parse

        Returns:
            List of lists of parsed strings

        Example:
            >>> parser = Dsv(DsvConfig.csv())
            >>> rows = parser.parse_file("data.csv")
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
        """
        Stream-parse a file in chunks.

        Args:
            file_path: Path to the file to parse

        Yields:
            Chunks of parsed rows

        Example:
            >>> parser = Dsv(DsvConfig.csv())
            >>> for chunk in parser.parse_stream("large.csv"):
            ...     process_chunk(chunk)
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
