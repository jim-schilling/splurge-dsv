"""Compatibility shim for safe text file reader using splurge_safe_io.

This module preserves the public API of the original
`splurge_dsv.safe_text_file_reader` while delegating implementation to
`splurge_safe_io.safe_text_file_reader`. It maps the external package's
exception types to the package's `splurge_dsv.exceptions` equivalents so
existing callers continue to observe the same exception types.
"""

from __future__ import annotations

import warnings
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import splurge_safe_io.safe_text_file_reader as safe_io_text_file_reader
from splurge_safe_io import exceptions as safe_io_exceptions

from splurge_dsv.exceptions import (
    SplurgeDsvError,
    SplurgeDsvFileDecodingError,
    SplurgeDsvFileNotFoundError,
    SplurgeDsvFileOperationError,
    SplurgeDsvFilePermissionError,
    SplurgeDsvPathValidationError,
)

# Re-export primary names for callers that import from splurge_dsv


class SafeTextFileReader:
    """Minimal compatibility wrapper that delegates to
    ``splurge_safe_io.safe_text_file_reader.SafeTextFileReader``.

    This shim is intentionally thin: it preserves the same constructor
    parameters but forwards operations to the underlying implementation
    unchanged. It enforces the external library's minimum chunk size so
    callers cannot request a chunk size below ``MIN_CHUNK_SIZE``.

    **Deprecated:** SafeTextFileReader is deprecated and will be removed in a future release. Consider using
    splurge-safe-io directly.
    """

    def __init__(
        self,
        file_path: Path | str,
        *,
        encoding: str = safe_io_text_file_reader.DEFAULT_ENCODING,
        strip: bool = False,
        skip_header_lines: int = 0,
        skip_footer_lines: int = 0,
        chunk_size: int | None = None,
        buffer_size: int | None = None,
    ) -> None:
        # Emit a DeprecationWarning to signal removal in a future release
        warnings.warn(
            "SafeTextFileReader is deprecated and will be removed in a future release. Consider using splurge-safe-io directly.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Use the external defaults when caller does not provide a value.
        if chunk_size is None:
            chunk_size = getattr(safe_io_text_file_reader, "DEFAULT_CHUNK_SIZE", 500)

        # Enforce the external minimum chunk size
        min_chunk = getattr(safe_io_text_file_reader, "MIN_CHUNK_SIZE", 10)
        if chunk_size < min_chunk:
            chunk_size = min_chunk

        if buffer_size is None:
            buffer_size = getattr(safe_io_text_file_reader, "DEFAULT_BUFFER_SIZE", 16384)

        try:
            # Construct the external implementation and delegate to it.
            self._impl = safe_io_text_file_reader.SafeTextFileReader(
                file_path,
                encoding=encoding,
                strip=strip,
                skip_header_lines=skip_header_lines,
                skip_footer_lines=skip_footer_lines,
                chunk_size=chunk_size,
                buffer_size=buffer_size,
            )

        except safe_io_exceptions.SplurgeSafeIoPathValidationError as e:
            raise SplurgeDsvPathValidationError(str(e)) from e
        except safe_io_exceptions.SplurgeSafeIoFileNotFoundError as e:
            raise SplurgeDsvFileNotFoundError(str(e)) from e
        except safe_io_exceptions.SplurgeSafeIoFilePermissionError as e:
            raise SplurgeDsvFilePermissionError(str(e)) from e
        except Exception as e:
            raise SplurgeDsvError(str(e)) from e

    def read(
        self,
        *,
        strip: bool | None = None,
        skip_header_rows: int | None = None,
        skip_footer_rows: int | None = None,
        chunk_size: int | None = None,
    ) -> list[str]:
        """Read and return all logical lines, preserving optional per-call overrides.

        Accepts legacy per-call parameters (strip, skip_header_rows,
        skip_footer_rows, chunk_size) and creates a temporary external
        implementation when any of them differ from the instance's
        configuration.

        Args:
            strip: If True, strips leading and trailing whitespace from each line.
            skip_header_rows: Number of header lines to skip.
            skip_footer_rows: Number of footer lines to skip.
            chunk_size: Number of lines to read per chunk when reading in streaming mode.

        Returns: A list of logical lines read from the file.

        Raises:
            SplurgeDsvPathValidationError: If the file path is invalid.
            SplurgeDsvFileEncodingError: If a decoding error occurs using the
                provided ``encoding``.
            SplurgeDsvFileNotFoundError: If the file does not exist.
            SplurgeDsvFilePermissionError: If there are insufficient permissions to read the file.
            SplurgeDsvError: For other unexpected errors.

        **Deprecated:** This method is deprecated and will be removed in a future release. Consider using splurge-safe-io directly.
        """
        # Emit a DeprecationWarning to signal removal in a future release
        warnings.warn(
            "SafeTextFileReader.read is deprecated and will be removed in a future release. Consider using splurge-safe-io directly.",
            DeprecationWarning,
            stacklevel=2,
        )

        try:
            # Determine effective values
            effective_strip = self._impl.strip if strip is None else strip
            effective_skip_header = self._impl.skip_header_lines if skip_header_rows is None else skip_header_rows
            effective_skip_footer = self._impl.skip_footer_lines if skip_footer_rows is None else skip_footer_rows
            effective_chunk = (
                getattr(self._impl, "chunk_size", getattr(safe_io_text_file_reader, "DEFAULT_CHUNK_SIZE", 500))
                if chunk_size is None
                else chunk_size
            )

            # Enforce external minimum chunk size
            min_chunk = getattr(safe_io_text_file_reader, "MIN_CHUNK_SIZE", 10)
            if effective_chunk < min_chunk:
                effective_chunk = min_chunk

            # If the call-time args match the stored impl, use it directly
            if (
                effective_strip == self._impl.strip
                and effective_skip_header == self._impl.skip_header_lines
                and effective_skip_footer == self._impl.skip_footer_lines
                and effective_chunk == getattr(self._impl, "chunk_size", None)
            ):
                impl = self._impl
            else:
                impl = safe_io_text_file_reader.SafeTextFileReader(
                    getattr(self._impl, "file_path", None) or None,
                    encoding=self._impl.encoding,
                    strip=effective_strip,
                    skip_header_lines=effective_skip_header,
                    skip_footer_lines=effective_skip_footer,
                    chunk_size=effective_chunk,
                    buffer_size=getattr(self._impl, "buffer_size", None),
                )
            return impl.read()

        except safe_io_exceptions.SplurgeSafeIoPathValidationError as e:
            raise SplurgeDsvPathValidationError(str(e)) from e
        except safe_io_exceptions.SplurgeSafeIoFileDecodingError as e:
            raise SplurgeDsvFileDecodingError(str(e)) from e
        except safe_io_exceptions.SplurgeSafeIoFileNotFoundError as e:
            raise SplurgeDsvFileNotFoundError(str(e)) from e
        except safe_io_exceptions.SplurgeSafeIoFilePermissionError as e:
            raise SplurgeDsvFilePermissionError(str(e)) from e
        except safe_io_exceptions.SplurgeSafeIoOsError as e:
            raise SplurgeDsvFileOperationError(str(e)) from e
        except Exception as e:
            raise SplurgeDsvError(str(e)) from e

    def preview(
        self, max_lines: int = 100, *, strip: bool | None = None, skip_header_rows: int | None = None
    ) -> list[str]:
        """Read and return up to max_lines logical lines from the start of the file.
        Args:
            max_lines: Maximum number of lines to read.
            strip: If True, strips leading and trailing whitespace from each line.
            skip_header_rows: Number of header lines to skip.

        Returns: A list of logical lines read from the start of the file, up to max_lines.

        Raises:
            SplurgeDsvPathValidationError: If the file path is invalid.
            SplurgeDsvFileDecodingError: If a decoding error occurs using the
                provided ``encoding``.
            SplurgeDsvFileNotFoundError: If the file does not exist.
            SplurgeDsvFilePermissionError: If there are insufficient permissions to read the file.
            SplurgeDsvError: For other unexpected errors.

        **Deprecated:** This method is deprecated and will be removed in a future release. Consider using splurge-safe-io directly.
        """
        # Emit a DeprecationWarning to signal removal in a future release
        warnings.warn(
            "SafeTextFileReader.preview is deprecated and will be removed in a future release. Consider using splurge-safe-io directly.",
            DeprecationWarning,
            stacklevel=2,
        )

        try:
            effective_strip = self._impl.strip if strip is None else strip
            effective_skip_header = self._impl.skip_header_lines if skip_header_rows is None else skip_header_rows

            if effective_strip == self._impl.strip and effective_skip_header == self._impl.skip_header_lines:
                impl = self._impl
            else:
                impl = safe_io_text_file_reader.SafeTextFileReader(
                    getattr(self._impl, "file_path", None) or None,
                    encoding=self._impl.encoding,
                    strip=effective_strip,
                    skip_header_lines=effective_skip_header,
                    skip_footer_lines=self._impl.skip_footer_lines,
                    chunk_size=getattr(
                        self._impl, "chunk_size", getattr(safe_io_text_file_reader, "DEFAULT_CHUNK_SIZE", 500)
                    ),
                    buffer_size=getattr(self._impl, "buffer_size", None),
                )
            return impl.preview(max_lines=max_lines)

        except safe_io_exceptions.SplurgeSafeIoPathValidationError as e:
            raise SplurgeDsvPathValidationError(str(e)) from e
        except safe_io_exceptions.SplurgeSafeIoFileDecodingError as e:
            raise SplurgeDsvFileDecodingError(str(e)) from e
        except safe_io_exceptions.SplurgeSafeIoFileNotFoundError as e:
            raise SplurgeDsvFileNotFoundError(str(e)) from e
        except safe_io_exceptions.SplurgeSafeIoFilePermissionError as e:
            raise SplurgeDsvFilePermissionError(str(e)) from e
        except safe_io_exceptions.SplurgeSafeIoOsError as e:
            raise SplurgeDsvFileOperationError(str(e)) from e
        except Exception as e:
            raise SplurgeDsvError(str(e)) from e

    def read_as_stream(
        self,
        *,
        strip: bool | None = None,
        skip_header_rows: int | None = None,
        skip_footer_rows: int | None = None,
        chunk_size: int | None = None,
    ) -> Iterator[list[str]]:
        """Read and yield logical lines in chunks, preserving optional per-call overrides.

        Args:
            strip: If True, strips leading and trailing whitespace from each line.
            skip_header_rows: Number of header lines to skip.
            skip_footer_rows: Number of footer lines to skip.
            chunk_size: Number of lines to read per chunk when reading in streaming mode.

        Yields: Lists of logical lines read from the file in chunks.

        Raises:
            SplurgeDsvFileDecodingError: If a decoding error occurs using the
                provided ``encoding``.
            SplurgeDsvFileNotFoundError: If the file does not exist.
            SplurgeDsvFilePermissionError: If there are insufficient permissions to read the file.
            SplurgeDsvError: For other unexpected errors.

        **Deprecated:** This method is deprecated and will be removed in a future release. Consider using splurge-safe-io directly.
        """
        # Emit a DeprecationWarning to signal removal in a future release
        warnings.warn(
            "SafeTextFileReader.read_as_stream is deprecated and will be removed in a future release. Consider using splurge-safe-io directly.",
            DeprecationWarning,
            stacklevel=2,
        )

        try:
            effective_strip = self._impl.strip if strip is None else strip
            effective_skip_header = self._impl.skip_header_lines if skip_header_rows is None else skip_header_rows
            effective_skip_footer = self._impl.skip_footer_lines if skip_footer_rows is None else skip_footer_rows
            effective_chunk = (
                getattr(self._impl, "chunk_size", getattr(safe_io_text_file_reader, "DEFAULT_CHUNK_SIZE", 500))
                if chunk_size is None
                else chunk_size
            )

            min_chunk = getattr(safe_io_text_file_reader, "MIN_CHUNK_SIZE", 10)
            if effective_chunk < min_chunk:
                effective_chunk = min_chunk

            if (
                effective_strip == self._impl.strip
                and effective_skip_header == self._impl.skip_header_lines
                and effective_skip_footer == self._impl.skip_footer_lines
                and effective_chunk == getattr(self._impl, "chunk_size", None)
            ):
                impl = self._impl
            else:
                impl = safe_io_text_file_reader.SafeTextFileReader(
                    getattr(self._impl, "file_path", None) or None,
                    encoding=self._impl.encoding,
                    strip=effective_strip,
                    skip_header_lines=effective_skip_header,
                    skip_footer_lines=effective_skip_footer,
                    chunk_size=effective_chunk,
                    buffer_size=getattr(self._impl, "buffer_size", None),
                )

            # Wrap the external iterator so we can ensure any underlying
            # resources are cleaned up when the consumer stops iterating.
            iterator = impl.read_as_stream()
            try:
                yield from iterator
            finally:
                # Attempt to close the implementation if it provides a close
                # method. This is defensive: the external implementation may
                # hold file handles open until explicitly closed.
                for candidate in (impl, getattr(self, "_impl", None)):
                    try:
                        if candidate is None:
                            continue
                        close_fn = getattr(candidate, "close", None)
                        if callable(close_fn):
                            close_fn()
                    except Exception:
                        # Best-effort cleanup; don't surface cleanup errors
                        # to callers of the streaming iterator.
                        pass

        except safe_io_exceptions.SplurgeSafeIoPathValidationError as e:
            raise SplurgeDsvPathValidationError(str(e)) from e
        except safe_io_exceptions.SplurgeSafeIoFileDecodingError as e:
            raise SplurgeDsvFileDecodingError(str(e)) from e
        except safe_io_exceptions.SplurgeSafeIoFileNotFoundError as e:
            raise SplurgeDsvFileNotFoundError(str(e)) from e
        except safe_io_exceptions.SplurgeSafeIoFilePermissionError as e:
            raise SplurgeDsvFilePermissionError(str(e)) from e
        except safe_io_exceptions.SplurgeSafeIoOsError as e:
            raise SplurgeDsvFileOperationError(str(e)) from e
        except Exception as e:
            raise SplurgeDsvError(str(e)) from e


@contextmanager
def open_text(file_path: Path | str, *, encoding: str = safe_io_text_file_reader.DEFAULT_ENCODING):
    """Context manager that yields a StringIO with normalized text.

    Delegates to ``open_safe_text_reader`` when available and maps
    exceptions to splurge_dsv types.
    """
    try:
        # We require the external helper to be present; use its signature
        # defaults for the additional keyword arguments so our API matches
        # the external implementation exactly.
        import inspect as _inspect

        sig = _inspect.signature(safe_io_text_file_reader.open_safe_text_reader)
        strip_param = sig.parameters.get("strip")
        skip_header_param = sig.parameters.get("skip_header_lines")
        skip_footer_param = sig.parameters.get("skip_footer_lines")

        strip_default = (
            strip_param.default
            if strip_param is not None and strip_param.default is not _inspect._empty
            else getattr(safe_io_text_file_reader, "DEFAULT_STRIP", False)
        )
        skip_header_default = (
            skip_header_param.default
            if skip_header_param is not None and skip_header_param.default is not _inspect._empty
            else getattr(safe_io_text_file_reader, "DEFAULT_SKIP_HEADER_LINES", 0)
        )
        skip_footer_default = (
            skip_footer_param.default
            if skip_footer_param is not None and skip_footer_param.default is not _inspect._empty
            else getattr(safe_io_text_file_reader, "DEFAULT_SKIP_FOOTER_LINES", 0)
        )

        # Respect the external defaults unless caller overrides via kwargs
        # (exposed as explicit parameters to this function).
        with safe_io_text_file_reader.open_safe_text_reader(
            file_path,
            encoding=encoding,
            strip=strip_default,
            skip_header_lines=skip_header_default,
            skip_footer_lines=skip_footer_default,
        ) as sio:
            yield sio

    except safe_io_exceptions.SplurgeSafeIoPathValidationError as e:
        raise SplurgeDsvPathValidationError(str(e)) from e
    except safe_io_exceptions.SplurgeSafeIoFileDecodingError as e:
        raise SplurgeDsvFileDecodingError(str(e)) from e
    except safe_io_exceptions.SplurgeSafeIoFileNotFoundError as e:
        raise SplurgeDsvFileNotFoundError(str(e)) from e
    except safe_io_exceptions.SplurgeSafeIoFilePermissionError as e:
        raise SplurgeDsvFilePermissionError(str(e)) from e
    except safe_io_exceptions.SplurgeSafeIoOsError as e:
        raise SplurgeDsvFileOperationError(str(e)) from e
    except Exception as e:
        raise SplurgeDsvError(str(e)) from e
