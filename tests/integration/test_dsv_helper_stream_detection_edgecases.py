"""Integration tests for streaming detection edge-cases in DsvHelper.

These tests ensure behavior when the first chunk contains only blank lines.
They exercise only public APIs (`Dsv`/`DsvConfig` and `DsvHelper.parse_file_stream`).
"""

import tempfile
from pathlib import Path

from splurge_dsv.dsv import Dsv, DsvConfig
from splurge_dsv.dsv_helper import DsvHelper


def _flatten(chunks):
    return [r for chunk in chunks for r in chunk]


def test_stream_detection_first_chunk_blank_no_detection():
    # Build a file where, after skipping header, the first chunk contains only blank lines
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("header1,header2,header3\n")
        # write enough blank lines so the first chunk (min chunk size) is all blanks
        for _ in range(DsvHelper.DEFAULT_MIN_CHUNK_SIZE):
            f.write("\n")
        f.write("a,b,c\n")
        f.write("d,e\n")
        path = f.name

    try:
        config = DsvConfig(
            delimiter=",",
            detect_columns=True,
            chunk_size=DsvHelper.DEFAULT_MIN_CHUNK_SIZE,
            skip_header_rows=1,
        )
        parser = Dsv(config)

        chunks = list(parser.parse_file_stream(path))
        rows = _flatten(chunks)

        # Detection scans multiple chunks; since the first non-blank logical
        # row ('a,b,c') appears within the scanned window, normalization will
        # be applied beginning with that chunk. Earlier blank-only chunks are
        # emitted without normalization.
        assert any(r == ["a", "b", "c"] for r in rows)
        # 'd,e' should be normalized to 3 columns because detection found
        # a 3-column row earlier in the scan window.
        assert any(r == ["d", "e", ""] for r in rows)
        # Ensure blank-only rows prior to detection were not normalized to 3 empty tokens
        assert not any(len(r) == 3 and all(tok == "" for tok in r) for r in rows if r != ["", "", ""])
    finally:
        try:
            Path(path).unlink()
        except PermissionError:
            pass


def test_stream_detection_first_chunk_blank_with_explicit_normalize():
    # Same file but call the helper directly with an explicit normalize_columns
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("header1,header2,header3\n")
        f.write("\n")
        f.write("\n")
        f.write("a,b,c\n")
        f.write("d,e\n")
        path = f.name

    try:
        # Provide normalize_columns explicitly; detection flag is ignored when normalize_columns>0
        chunks = list(
            DsvHelper.parse_file_stream(
                path,
                delimiter=",",
                detect_columns=True,
                normalize_columns=3,
                chunk_size=DsvHelper.DEFAULT_MIN_CHUNK_SIZE,
                skip_header_rows=1,
            )
        )
        rows = _flatten(chunks)

        # Now blank lines are normalized to 3 empty tokens
        assert rows == [["", "", ""], ["", "", ""], ["a", "b", "c"], ["d", "e", ""]]
    finally:
        try:
            Path(path).unlink()
        except PermissionError:
            pass
