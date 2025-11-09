"""DSV parsing primitives and configuration objects.

This module exposes the :class:`DsvConfig` dataclass and the :class:`Dsv`
parser. ``DsvConfig`` encapsulates parsing options such as delimiter,
encoding and header/footer skipping. ``Dsv`` is a thin, stateful wrapper
around :mod:`splurge_dsv.dsv_helper` that binds a configuration to
parsing operations and provides convenience methods for parsing strings,
files, and streaming large inputs.

Public API:
    - DsvConfig: Configuration dataclass for parsing behavior.
    - Dsv: Parser instance that performs parse/parse_file/parse_file_stream.

License: MIT

Copyright (c) 2025 Jim Schilling
"""

# Standard library imports
from collections.abc import Iterator
from os import PathLike
from pathlib import Path
from uuid import uuid4

from ._vendor.splurge_pub_sub.pubsub_solo import PubSubSolo

# Local imports
from .dsv_config import DsvConfig
from .dsv_helper import DsvHelper
from .exceptions import SplurgeDsvError


class Dsv:
    """Parser class that binds a :class:`DsvConfig` to parsing operations.

    The class delegates actual parsing to :mod:`splurge_dsv.dsv_helper` while
    providing a convenient instance API for repeated parsing tasks with the
    same configuration. Each instance maintains a unique correlation_id and
    publishes events throughout the parsing lifecycle for monitoring and tracing.

    Attributes:
        config (DsvConfig): Configuration instance used for parsing calls.
        correlation_id (str): Unique identifier for tracing this instance's operations.
    """

    @property
    def correlation_id(self) -> str:
        """Get the correlation id for this instance."""
        return self._correlation_id

    def __init__(self, config: DsvConfig, correlation_id: str | None = None) -> None:
        """
        Initialize DSV parser with configuration.

        Creates a new parser instance with a unique correlation_id for tracing
        operations. Publishes an initialization event to registered subscribers.

        Args:
            config: DsvConfig object containing parsing parameters

        Example:
            >>> config = DsvConfig(delimiter=",")
            >>> parser = Dsv(config)
        """
        self._correlation_id = correlation_id or str(uuid4())
        self._config = config
        PubSubSolo.publish(topic="dsv.init", correlation_id=self._correlation_id, scope="splurge-dsv")

    @property
    def config(self) -> DsvConfig:
        """Get the configuration for the parser."""
        return self._config

    def parse(self, content: str) -> list[str]:
        """Parse a single DSV record (string) into a list of tokens.

        Publishes lifecycle events (begin, end, error) to registered subscribers
        using the instance's correlation_id for tracing.

        Args:
            content: Input string representing a single DSV record.

        Returns:
            List of parsed tokens as strings.

        Raises:
            SplurgeDsvValueError: If the configured delimiter is invalid.
            SplurgeDsvColumnMismatchError: If column validation fails.
        """
        PubSubSolo.publish(topic="dsv.parse.begin", correlation_id=self.correlation_id, scope="splurge-dsv")

        try:
            result = DsvHelper.parse(
                content,
                delimiter=self.config.delimiter,
                strip=self.config.strip,
                bookend=self.config.bookend,
                bookend_strip=self.config.bookend_strip,
                normalize_columns=0,
                raise_on_missing_columns=self.config.raise_on_missing_columns,
                raise_on_extra_columns=self.config.raise_on_extra_columns,
                correlation_id=self.correlation_id,
            )
        except SplurgeDsvError as e:
            PubSubSolo.publish(
                topic="dsv.parse.error", data={"error": e}, correlation_id=self.correlation_id, scope="splurge-dsv"
            )
            raise
        finally:
            PubSubSolo.publish(topic="dsv.parse.end", correlation_id=self.correlation_id, scope="splurge-dsv")

        return result

    def parses(self, content: list[str]) -> list[list[str]]:
        """
        Parse a list of strings into a list of lists of strings.

        Publishes lifecycle events (begin, end, error) to registered subscribers
        using the instance's correlation_id for tracing.

        Args:
            content: List of strings to parse

        Returns:
            List of lists of parsed strings

        Raises:
            SplurgeDsvValueError: If the configured delimiter is invalid.
            SplurgeDsvTypeError: If the input is not a list of strings.
            SplurgeDsvColumnMismatchError: If column validation fails.

        Example:
            >>> parser = Dsv(DsvConfig(delimiter=","))
            >>> parser.parses(["a,b", "c,d"])
            [['a', 'b'], ['c', 'd']]
        """
        PubSubSolo.publish(topic="dsv.parses.begin", correlation_id=self.correlation_id, scope="splurge-dsv")

        try:
            result = DsvHelper.parses(
                content,
                delimiter=self.config.delimiter,
                strip=self.config.strip,
                bookend=self.config.bookend,
                bookend_strip=self.config.bookend_strip,
                normalize_columns=0,
                raise_on_missing_columns=self.config.raise_on_missing_columns,
                raise_on_extra_columns=self.config.raise_on_extra_columns,
                detect_columns=self.config.detect_columns,
                correlation_id=self.correlation_id,
            )
        except SplurgeDsvError as e:
            PubSubSolo.publish(
                topic="dsv.parses.error", data={"error": e}, correlation_id=self.correlation_id, scope="splurge-dsv"
            )
            raise
        finally:
            PubSubSolo.publish(topic="dsv.parses.end", correlation_id=self.correlation_id, scope="splurge-dsv")

        return result

    def parse_file(self, file_path: PathLike[str] | Path | str) -> list[list[str]]:
        """Parse a DSV file and return all rows as lists of strings.

        Publishes lifecycle events (begin, end, error) to registered subscribers
        using the instance's correlation_id for tracing.

        Args:
            file_path: Path to the file to parse.

        Returns:
            A list of rows, where each row is a list of string tokens.

        Raises:
            SplurgeDsvPathValidationError: If the file path is invalid.
            SplurgeDsvOSError: If the file cannot be found.
            SplurgeDsvOSError: If the file cannot be read.
            SplurgeDsvLookupError: If the codecs initialization fails or codecs cannot be found.
            SplurgeDsvUnicodeError: If the file cannot be decoded with the configured encoding.
            SplurgeDsvColumnMismatchError: If column validation fails.
            SplurgeDsvValueError: If the configured delimiter is invalid.
            SplurgeDsvTypeError: If the input is not a list of strings.
            SplurgeDsvRuntimeError: For other runtime errors.
        """
        PubSubSolo.publish(
            topic="dsv.parse.file.begin",
            data={"file_path": str(file_path)},
            correlation_id=self.correlation_id,
            scope="splurge-dsv",
        )

        try:
            result = DsvHelper.parse_file(
                file_path,
                delimiter=self.config.delimiter,
                strip=self.config.strip,
                bookend=self.config.bookend,
                bookend_strip=self.config.bookend_strip,
                encoding=self.config.encoding,
                skip_header_rows=self.config.skip_header_rows,
                skip_empty_lines=self.config.skip_empty_lines,
                skip_footer_rows=self.config.skip_footer_rows,
                detect_columns=self.config.detect_columns,
                raise_on_missing_columns=self.config.raise_on_missing_columns,
                raise_on_extra_columns=self.config.raise_on_extra_columns,
                correlation_id=self.correlation_id,
            )
        except SplurgeDsvError as e:
            PubSubSolo.publish(
                topic="dsv.parse.file.error", data={"error": e}, correlation_id=self.correlation_id, scope="splurge-dsv"
            )
            raise
        finally:
            PubSubSolo.publish(topic="dsv.parse.file.end", correlation_id=self.correlation_id, scope="splurge-dsv")

        return result

    def parse_file_stream(self, file_path: PathLike[str] | Path | str) -> Iterator[list[list[str]]]:
        """Stream-parse a DSV file, yielding chunks of parsed rows.

        The method yields lists of parsed rows (each row itself is a list of
        strings). Chunk sizing is controlled by the bound configuration's
        ``chunk_size`` value. Publishes lifecycle events (begin, end, error) to
        registered subscribers using the instance's correlation_id for tracing.

        Args:
            file_path: Path to the file to parse.

        Yields:
            Lists of parsed rows, each list containing up to ``chunk_size`` rows.

        Raises:
            SplurgeDsvPathValidationError: If the file path is invalid.
            SplurgeDsvOSError: If the file cannot be found.
            SplurgeDsvOSError: If the file cannot be read.
            SplurgeDsvLookupError: If the codecs initialization fails or codecs cannot be found.
            SplurgeDsvUnicodeError: If the file cannot be decoded with the configured encoding.
            SplurgeDsvColumnMismatchError: If column validation fails.
            SplurgeDsvValueError: If the configured delimiter is invalid.
            SplurgeDsvTypeError: If the input is not a list of strings.
            SplurgeDsvRuntimeError: For other unexpected errors.
        """
        PubSubSolo.publish(
            topic="dsv.parse.file.stream.begin",
            data={"file_path": str(file_path)},
            correlation_id=self.correlation_id,
            scope="splurge-dsv",
        )

        try:
            result = DsvHelper.parse_file_stream(
                file_path,
                delimiter=self.config.delimiter,
                strip=self.config.strip,
                bookend=self.config.bookend,
                bookend_strip=self.config.bookend_strip,
                encoding=self.config.encoding,
                skip_header_rows=self.config.skip_header_rows,
                skip_empty_lines=self.config.skip_empty_lines,
                skip_footer_rows=self.config.skip_footer_rows,
                detect_columns=self.config.detect_columns,
                raise_on_missing_columns=self.config.raise_on_missing_columns,
                raise_on_extra_columns=self.config.raise_on_extra_columns,
                chunk_size=self.config.chunk_size,
                max_detect_chunks=self.config.max_detect_chunks,
                correlation_id=self.correlation_id,
            )
        except SplurgeDsvError as e:
            PubSubSolo.publish(
                topic="dsv.parse.file.stream.error",
                data={"error": e},
                correlation_id=self.correlation_id,
                scope="splurge-dsv",
            )
            raise
        finally:
            PubSubSolo.publish(
                topic="dsv.parse.file.stream.end", correlation_id=self.correlation_id, scope="splurge-dsv"
            )
        return result
