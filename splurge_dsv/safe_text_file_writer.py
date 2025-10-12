"""Compatibility shim for safe text file writer using splurge_safe_io.

Delegates to ``splurge_safe_io.safe_text_file_writer`` and maps
exception classes to `splurge_dsv.exceptions` equivalents.
"""

from __future__ import annotations

import io
import warnings
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from pathlib import Path

import splurge_safe_io.safe_text_file_writer as safe_io_text_file_writer
from splurge_safe_io import exceptions as safe_io_exceptions

from splurge_dsv.exceptions import (
    SplurgeDsvError,
    SplurgeDsvFileEncodingError,
    SplurgeDsvFileExistsError,
    SplurgeDsvFileOperationError,
    SplurgeDsvFilePermissionError,
    SplurgeDsvPathValidationError,
)


class SafeTextFileWriter:
    """Compatibility wrapper around splurge_safe_io.SafeTextFileWriter.

    Args:
        file_path: Path or str to the target file.
        encoding: Text encoding to use (default 'utf-8').
        newline: Newline handling mode (default None).
        mode: File open mode, one of 'w', 'a', or 'x' (default 'w').

    Raises:
        SplurgeDsvPathValidationError: If the file path is invalid.
        SplurgeDsvFileEncodingError: If the encoding is unsupported.
        SplurgeDsvFileNotFoundError: If the file does not exist (for '
    """

    def __init__(
        self,
        file_path: Path | str,
        *,
        encoding: str = safe_io_text_file_writer.DEFAULT_ENCODING,
        newline: str | None = safe_io_text_file_writer.CANONICAL_NEWLINE,
    ) -> None:
        self._file_path = Path(file_path)
        self._encoding = encoding
        self._newline = newline
        self._file: io.TextIOBase | None = None
        self._mode = "w"
        self._impl: safe_io_text_file_writer.SafeTextFileWriter | None = None

    def open(self, mode: str = "w") -> io.TextIOBase:
        """Initializes and opens the file for writing.

        Returns:
            The underlying text IO object for writing.

        Args:
            mode: File open mode, one of 'w', 'a', or 'x' (default 'w').

        Raises:
            SplurgeDsvPathValidationError: If the file path is invalid.
            SplurgeDsvFileEncodingError: If the encoding is unsupported.
            SplurgeDsvFileExistsError: If the file already exists (for 'x' mode).
            SplurgeDsvFilePermissionError: If there are permission issues.
            SplurgeDsvFileOperationError: For other file operation errors.
            SplurgeDsvError: For unexpected errors.

        Note: The external SafeTextFileWriter does not expose an open()
        method, so this simply returns the internal implementation which
        provides the necessary methods for writing.

        **Deprecated:** This method is deprecated and will be removed in a future release.
        """
        # Emit a DeprecationWarning to signal removal in a future release
        warnings.warn(
            "SafeTextFileWriter.open is deprecated and will be removed in a future release. Consider using splurge-safe-io directly.",
            DeprecationWarning,
            stacklevel=2,
        )
        from splurge_safe_io.safe_text_file_writer import TextFileWriteMode

        if mode in ["w", "wt"]:
            file_write_mode = TextFileWriteMode.CREATE_OR_TRUNCATE
        elif mode in ["a", "at"]:
            file_write_mode = TextFileWriteMode.CREATE_OR_APPEND
        elif mode in ["x", "xt"]:
            file_write_mode = TextFileWriteMode.CREATE_NEW
        else:
            # Default behavior
            file_write_mode = TextFileWriteMode.CREATE_OR_TRUNCATE

        try:
            # Construct the external implementation and rely on it.
            self._impl = safe_io_text_file_writer.SafeTextFileWriter(
                self._file_path,
                encoding=self._encoding,
                canonical_newline=self._newline,
                file_write_mode=file_write_mode,
            )
            self._file = self._impl._file_obj  # type: ignore[attr-defined]
            # mypy: ensure we don't return Optional
            assert self._file is not None
            return self._file

        except safe_io_exceptions.SplurgeSafeIoPathValidationError as e:
            raise SplurgeDsvPathValidationError(str(e)) from e
        except safe_io_exceptions.SplurgeSafeIoFileEncodingError as e:
            raise SplurgeDsvFileEncodingError(str(e)) from e
        except safe_io_exceptions.SplurgeSafeIoFileAlreadyExistsError as e:
            raise SplurgeDsvFileExistsError(str(e)) from e
        except safe_io_exceptions.SplurgeSafeIoFilePermissionError as e:
            raise SplurgeDsvFilePermissionError(str(e)) from e
        except safe_io_exceptions.SplurgeSafeIoOsError as e:
            raise SplurgeDsvFileOperationError(str(e)) from e
        except Exception as e:
            raise SplurgeDsvError(str(e)) from e

    def write(self, text: str) -> int:
        """Writes a string to the file.

        Args:
            text: The string to write.

        Returns:
            The number of characters written.

        Raises:
            SplurgeDsvError: If file is not opened and for unexpected errors.
            SplurgeDsvFileEncodingError: For encoding-related errors.
            SplurgeDsvFileOperationError: For file operation errors.

        **Deprecated:** This method is deprecated and will be removed in a future release. Consider using splurge-safe-io directly.
        """
        # Emit a DeprecationWarning to signal removal in a future release
        warnings.warn(
            "SafeTextFileWriter.write is deprecated and will be removed in a future release. Consider using splurge-safe-io directly.",
            DeprecationWarning,
            stacklevel=2,
        )

        if not self._impl:
            raise SplurgeDsvError("SafeTextFileWriter is not open. Call open() before writing.")

        try:
            return self._impl.write(text)

        except safe_io_exceptions.SplurgeSafeIoFileEncodingError as e:
            raise SplurgeDsvFileEncodingError(str(e)) from e
        except safe_io_exceptions.SplurgeSafeIoOsError as e:
            raise SplurgeDsvFileOperationError(str(e)) from e
        except Exception as e:
            raise SplurgeDsvError(str(e)) from e

    def writelines(self, lines: Iterable[str]) -> None:
        """Writes an iterable of strings to the file.

        Args:
            lines: An iterable of strings to write.

        Raises:
            SplurgeDsvError: If file is not opened and for unexpected errors.
            SplurgeDsvFileEncodingError: For encoding-related errors.
            SplurgeDsvFileOperationError: For file operation errors.

        **Deprecated:** This method is deprecated and will be removed in a future release. Consider using splurge-safe-io directly.
        """
        # Emit a DeprecationWarning to signal removal in a future release
        warnings.warn(
            "SafeTextFileWriter.writelines is deprecated and will be removed in a future release. Consider using splurge-safe-io directly.",
            DeprecationWarning,
            stacklevel=2,
        )

        if not self._impl:
            raise SplurgeDsvError("SafeTextFileWriter is not open. Call open() before writing.")

        try:
            return self._impl.writelines(lines)

        except safe_io_exceptions.SplurgeSafeIoFileEncodingError as e:
            raise SplurgeDsvFileEncodingError(str(e)) from e
        except safe_io_exceptions.SplurgeSafeIoOsError as e:
            raise SplurgeDsvFileOperationError(str(e)) from e
        except Exception as e:
            raise SplurgeDsvError(str(e)) from e

    def flush(self) -> None:
        """Flushes any buffered content to disk.

        Raises:
            SplurgeDsvError: If file is not opened and for unexpected errors.
            SplurgeDsvFileOperationError: For file operation errors.

        **Deprecated:** This method is deprecated and will be removed in a future release. Consider using splurge-safe-io directly.
        """
        # Emit a DeprecationWarning to signal removal in a future release
        warnings.warn(
            "SafeTextFileWriter.flush is deprecated and will be removed in a future release. Consider using splurge-safe-io directly.",
            DeprecationWarning,
            stacklevel=2,
        )

        if not self._impl:
            raise SplurgeDsvError("SafeTextFileWriter is not open. Call open() before writing.")

        try:
            self._impl.flush()

        except safe_io_exceptions.SplurgeSafeIoOsError as e:
            raise SplurgeDsvFileOperationError(str(e)) from e
        except Exception as e:
            raise SplurgeDsvError(str(e)) from e

    def close(self) -> None:
        """Closes the writer, flushing any buffered content to disk.

        Raises:
            SplurgeDsvError: For unexpected errors.

        **Deprecated:** This method is deprecated and will be removed in a future release. Consider using splurge-safe-io directly.
        """
        # Emit a DeprecationWarning to signal removal in a future release
        warnings.warn(
            "SafeTextFileWriter.close is deprecated and will be removed in a future release. Consider using splurge-safe-io directly.",
            DeprecationWarning,
            stacklevel=2,
        )

        try:
            if self._impl:
                self._impl.close()

        except Exception as e:
            raise SplurgeDsvError(str(e)) from e

        finally:
            self._impl = None
            self._file = None


@contextmanager
def open_text_writer(file_path: Path | str, *, encoding: str = "utf-8", mode: str = "w") -> Iterator[io.StringIO]:
    """Context manager yielding an in-memory StringIO to accumulate text.

    On successful exit, the buffered content is normalized and written to
    disk using :class:`SafeTextFileWriter`. If an exception occurs inside
    the context, nothing is written and the exception is propagated.

    Args:
        file_path: Destination path to write to on successful exit.
        encoding: Encoding to use when writing.
        mode: File open mode passed to writer (default: 'w').

    Yields:
        io.StringIO: Buffer to write textual content into.

    **Deprecated:** This function is deprecated and will be removed in a future release. Consider using splurge-safe-io directly.
    """
    # Emit a DeprecationWarning to signal removal in a future release
    warnings.warn(
        "open_text_writer is deprecated and will be removed in a future release. Consider using splurge-safe-io directly.",
        DeprecationWarning,
        stacklevel=2,
    )
    path = Path(file_path)
    buffer = io.StringIO()
    try:
        yield buffer
    except Exception:
        # Do not write on exceptions; re-raise
        raise
    else:
        content = buffer.getvalue()
        writer = SafeTextFileWriter(path, encoding=encoding)
        try:
            writer.open(mode=mode)
            writer.write(content)
            writer.flush()
        finally:
            writer.close()
