"""Safe text file reader utilities.

This module provides SafeTextFileReader which reads text files only and
normalizes newline sequences (CRLF, CR, LF) to a predictable contract.

Copyright 2025 Jim Schilling
Please preserve this header and all related material when sharing!
This module is licensed under the MIT License.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from io import StringIO
from pathlib import Path

from splurge_dsv.exceptions import SplurgeDsvFileEncodingError


class SafeTextFileReader:
    """Read text files with deterministic newline normalization.

    Usage: SafeTextFileReader(path, encoding="utf-8").read(...)
    """

    def __init__(self, file_path: Path | str, *, encoding: str = "utf-8") -> None:
        self.path = Path(file_path)
        self.encoding = encoding

    def _read_text(self) -> str:
        try:
            # Read raw bytes and decode explicitly to avoid the platform's
            # text-mode newline translations (which can double-translate
            # mixed endings when files are written with different conventions).
            with self.path.open("rb") as fh:
                raw = fh.read()
            # Decode using the requested encoding; let decoding errors surface
            # as SplurgeDsvFileEncodingError
            return raw.decode(self.encoding)
        except Exception as e:
            raise SplurgeDsvFileEncodingError(f"Encoding error reading file: {self.path}", details=str(e)) from e

    def read(self, *, strip: bool = True, skip_header_rows: int = 0, skip_footer_rows: int = 0) -> list[str]:
        """Read entire file and return list of lines with normalization."""
        text = self._read_text()
        # Normalize newlines to LF
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = normalized.splitlines()

        if skip_header_rows:
            lines = lines[skip_header_rows:]
        if skip_footer_rows:
            if skip_footer_rows >= len(lines):
                return []
            lines = lines[:-skip_footer_rows]

        if strip:
            return [ln.strip() for ln in lines]
        return list(lines)

    def preview(self, max_lines: int = 100, *, strip: bool = True, skip_header_rows: int = 0) -> list[str]:
        text = self._read_text()
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = normalized.splitlines()
        if skip_header_rows:
            lines = lines[skip_header_rows:]
        if max_lines < 1:
            return []
        result = lines[:max_lines]
        return [ln.strip() for ln in result] if strip else list(result)

    def read_as_stream(
        self, *, strip: bool = True, skip_header_rows: int = 0, skip_footer_rows: int = 0, chunk_size: int = 500
    ) -> Iterator[list[str]]:
        """Yield chunks of lines. This implementation reads the whole file into memory
        (tests are small); for large files this could be optimized later."""
        lines = self.read(strip=strip, skip_header_rows=skip_header_rows, skip_footer_rows=skip_footer_rows)
        chunk: list[str] = []
        for ln in lines:
            chunk.append(ln)
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk


@contextmanager
def open_text(file_path: Path | str, *, encoding: str = "utf-8"):
    """Context manager that yields an in-memory text stream with normalized newlines.

    This helper is convenient for code paths that expect a file-like object
    (for example, legacy callers using the resource manager). The returned
    object is an io.StringIO containing the normalized file text.
    """
    reader = SafeTextFileReader(file_path, encoding=encoding)
    text_lines = reader.read(strip=False)
    text = "\n".join(text_lines)
    sio = StringIO(text)
    try:
        yield sio
    finally:
        sio.close()
