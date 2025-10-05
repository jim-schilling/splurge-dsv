"""Deterministic text-only writer utilities.

Provides SafeTextFileWriter which ensures consistent newline handling across
platforms by normalizing newlines to LF before writing. Also exposes
``open_text_writer`` context manager which yields a file-like object for
writing text safely (with explicit encoding and newline normalization).

This mirrors the read-only semantics in ``safe_text_file_reader.py`` but for
writing.

Copyright 2025 Jim Schilling
Please preserve this header and all related material when sharing!
This module is licensed under the MIT License.
"""

from __future__ import annotations

import io
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import cast

from .exceptions import SplurgeDsvFileEncodingError


class SafeTextFileWriter:
    """A small helper for deterministic text writes.

    Behavior contract:
    - Always writes text using the provided encoding (default UTF-8).
    - Always normalizes any incoming newline characters to LF ("\n").
    - Exposes a minimal file-like API: write(), writelines(), flush(), close().

    This class intentionally does not support binary modes.
    """

    def __init__(self, file_path: Path, *, encoding: str = "utf-8", newline: str | None = "\n") -> None:
        self._path = Path(file_path)
        self._encoding = encoding
        # newline is the canonical newline we will write; default to LF
        self._newline = "\n" if newline is None else newline
        self._file: io.TextIOBase | None = None

    def open(self, mode: str = "w") -> io.TextIOBase:
        """Open the underlying file for text writing.

        Raises SplurgeFileEncodingError if the file cannot be opened with the
        requested encoding.
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
        """Normalize newlines and write text to the file.

        Returns number of characters written.
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
    """Context manager that yields an in-memory StringIO writer which will be
    flushed to disk on successful exit.

    This allows callers to build up content safely in memory and write the
    fully-normalized result to disk atomically (best-effort) when the context
    exits.
    """
    path = Path(file_path)
    buffer = io.StringIO()
    try:
        yield buffer
    except Exception:
        # Do not write on exceptions; re-raise
        raise
    else:
        # Normalize final content and write to disk using SafeTextFileWriter
        content = buffer.getvalue()
        writer = SafeTextFileWriter(path, encoding=encoding)
        try:
            writer.open(mode=mode)
            writer.write(content)
            writer.flush()
        finally:
            writer.close()
