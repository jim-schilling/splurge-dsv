"""Safe text file reader utilities.

This module implements :class:`SafeTextFileReader`, a small helper that reads
text files in binary mode and performs deterministic newline normalization.
It intentionally decodes bytes explicitly to avoid platform newline
translation side-effects and centralizes encoding error handling into a
package-specific exception type.

Public API summary:
        - SafeTextFileReader: Read, preview, and stream text files with normalized
            newlines and optional header/footer skipping.
        - open_text: Context manager returning an in-memory text stream for
            callers that expect a file-like object.

Example:
        reader = SafeTextFileReader("data.csv", encoding="utf-8")
        lines = reader.read()

License: MIT

Copyright (c) 2025 Jim Schilling
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from io import StringIO
from pathlib import Path

from splurge_dsv.exceptions import SplurgeDsvFileEncodingError


class SafeTextFileReader:
    """Read text files with deterministic newline normalization.

    The class reads raw bytes from disk and decodes using the provided
    encoding. Newline sequences are normalized to ``\n`` (LF). Public
    methods provide convenience wrappers for full reads, previews and
    chunked streaming.

    Args:
        file_path (Path | str): Path to the file to read.
        encoding (str): Encoding to use when decoding bytes (default: utf-8).

    Example:
        reader = SafeTextFileReader("/tmp/data.csv", encoding="utf-8")
        rows = reader.read(skip_header_rows=1)
    """

    def __init__(self, file_path: Path | str, *, encoding: str = "utf-8") -> None:
        self.path = Path(file_path)
        self.encoding = encoding

    def _read_text(self) -> str:
        """Read the file bytes and return decoded text with no newline normalization applied.

        Returns:
            Decoded text (str).

        Raises:
            SplurgeDsvFileEncodingError: If decoding fails or the file cannot
                be read.
        """
        try:
            # Read raw bytes and decode explicitly to avoid the platform's
            # text-mode newline translations which can alter mixed line endings.
            with self.path.open("rb") as fh:
                raw = fh.read()
            return raw.decode(self.encoding)
        except Exception as e:
            raise SplurgeDsvFileEncodingError(f"Encoding error reading file: {self.path}", details=str(e)) from e

    def read(self, *, strip: bool = True, skip_header_rows: int = 0, skip_footer_rows: int = 0) -> list[str]:
        """Read the entire file and return a list of normalized lines.

        Newlines are normalized to ``\n`` and optional header/footer rows
        can be skipped. If ``strip`` is True, whitespace surrounding each
        line is removed.

        Args:
            strip (bool): Strip whitespace from each line (default: True).
            skip_header_rows (int): Number of rows to skip at the start.
            skip_footer_rows (int): Number of rows to skip at the end.

        Returns:
            List of lines as strings.
        """
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
        """Return the first ``max_lines`` lines of the file after normalization.

        Args:
            max_lines (int): Maximum number of lines to return.
            strip (bool): Strip whitespace from each returned line.
            skip_header_rows (int): Number of header rows to skip before previewing.

        Returns:
            A list of preview lines.
        """
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
        """Yield chunks of lines from the file.

        This convenience method currently reads the decoded file into memory
        and yields chunks of ``chunk_size`` lines. For very large files this
        could be optimized to stream from disk without full materialization.

        Args:
            strip (bool): Whether to strip whitespace from each line.
            skip_header_rows (int): Number of header rows to skip.
            skip_footer_rows (int): Number of footer rows to skip.
            chunk_size (int): Number of lines per yielded chunk.

        Yields:
            Lists of lines (each list length <= chunk_size).
        """
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
    """Context manager returning a text stream (io.StringIO) with normalized newlines.

    Useful when an API expects a file-like object. The returned StringIO
    contains the normalized text (LF newlines) and is closed automatically
    when the context exits.

    Args:
        file_path: Path to the file to open.
        encoding: Encoding to decode the file with.

    Yields:
        io.StringIO: In-memory text buffer with normalized newlines.
    """
    reader = SafeTextFileReader(file_path, encoding=encoding)
    text_lines = reader.read(strip=False)
    text = "\n".join(text_lines)
    sio = StringIO(text)
    try:
        yield sio
    finally:
        sio.close()
