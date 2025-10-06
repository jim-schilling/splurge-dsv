"""Deterministic text-only writer utilities.

This module implements :class:`SafeTextFileWriter` and a convenience
``open_text_writer`` context manager. Writes always use the configured
encoding and normalize newline characters to a canonical form (LF) to
ensure consistent files across platforms.

Example:
    with open_text_writer("out.txt") as buf:
        buf.write("line1\nline2\n")

Copyright (c) 2025 Jim Schilling
Please preserve this header and all related material when sharing!

License: MIT
"""

from __future__ import annotations

import io
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import cast

from .exceptions import SplurgeDsvFileEncodingError


class SafeTextFileWriter:
    """Helper for deterministic text writes with newline normalization.

    Args:
        file_path: Destination file path.
        encoding: Text encoding to use (default: 'utf-8').
        newline: Canonical newline sequence to write (default: '\n').

    The class exposes a minimal file-like API and will raise
    :class:`SplurgeDsvFileEncodingError` when the underlying file cannot be
    opened with the requested encoding.
    """

    def __init__(self, file_path: Path, *, encoding: str = "utf-8", newline: str | None = "\n") -> None:
        self._path = Path(file_path)
        self._encoding = encoding
        # newline is the canonical newline we will write; default to LF
        self._newline = "\n" if newline is None else newline
        self._file: io.TextIOBase | None = None

    def open(self, mode: str = "w") -> io.TextIOBase:
        """Open the underlying file for text writing.

        Args:
            mode: File open mode (default: 'w').

        Returns:
            The opened text file object.

        Raises:
            SplurgeDsvFileEncodingError: If the file cannot be opened with the
                requested encoding or underlying OS error occurs.
        """
        try:
            # open with newline="" to allow us to manage newline normalization
            fp = open(self._path, mode, encoding=self._encoding, newline="")
            # cast to TextIOBase for precise typing
            self._file = cast(io.TextIOBase, fp)
            return self._file
        except (LookupError, OSError) as exc:
            raise SplurgeDsvFileEncodingError(str(exc)) from exc

    def write(self, text: str) -> int:
        """Normalize newlines and write ``text`` to the opened file.

        Args:
            text: Text to write (newlines will be normalized).

        Returns:
            Number of characters written.
        """
        if self._file is None:
            raise ValueError("file not opened")
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        return self._file.write(normalized)

    def writelines(self, lines: Iterable[str]) -> None:
        if self._file is None:
            raise ValueError("file not opened")
        for line in lines:
            self.write(line)

    def flush(self) -> None:
        if self._file is None:
            return
        self._file.flush()

    def close(self) -> None:
        if self._file is None:
            return
        try:
            self._file.close()
        finally:
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
    """
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
