"""Integration tests for multi-chunk detection and column validation.

These tests exercise the streaming detection window behaviour and the
raise_on_missing_columns / raise_on_extra_columns validation flags.
"""

import tempfile
from pathlib import Path

import pytest

from splurge_dsv.dsv import Dsv, DsvConfig
from splurge_dsv.dsv_helper import DsvHelper
from splurge_dsv.exceptions import SplurgeDsvColumnMismatchError


def _flatten(chunks):
    return [r for chunk in chunks for r in chunk]


def test_detect_across_multiple_chunks():
    # Create a file where the first non-blank logical row appears in the
    # third chunk. We set max_detect_chunks to 3 so detection should succeed.
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        # header skipped by config
        f.write("header1,header2\n")
        # two full chunks of blank lines
        for _ in range(DsvHelper.DEFAULT_MIN_CHUNK_SIZE * 2):
            f.write("\n")
        # third chunk contains our first non-blank logical row
        f.write("a,b,c\n")
        f.write("d,e\n")
        path = f.name

    try:
        cfg = DsvConfig(
            delimiter=",",
            detect_columns=True,
            chunk_size=DsvHelper.DEFAULT_MIN_CHUNK_SIZE,
            max_detect_chunks=3,
            skip_header_rows=1,
        )
        parser = Dsv(cfg)

        chunks = list(parser.parse_file_stream(path))
        rows = _flatten(chunks)

        # detection should find 3 columns and normalize subsequent rows
        assert any(r == ["a", "b", "c"] for r in rows)
        assert any(r == ["d", "e", ""] for r in rows)
    finally:
        try:
            Path(path).unlink()
        except PermissionError:
            pass


def test_no_detection_within_max_window():
    # Create a file where no non-blank logical line exists within max_detect_chunks
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("header1,header2\n")
        # write blank lines longer than max window
        for _ in range(DsvHelper.DEFAULT_MIN_CHUNK_SIZE * 5):
            f.write("\n")
        f.write("a,b,c\n")
        path = f.name

    try:
        cfg = DsvConfig(
            delimiter=",",
            detect_columns=True,
            chunk_size=DsvHelper.DEFAULT_MIN_CHUNK_SIZE,
            max_detect_chunks=2,
            skip_header_rows=1,
        )
        parser = Dsv(cfg)

        chunks = list(parser.parse_file_stream(path))
        rows = _flatten(chunks)

        # Since detection did not occur within the window, we should see the
        # data rows as-is (no normalization). 'a,b,c' will be a 3-col row
        # and 'd,e' (if present) would remain 2-col; here we only check that
        # the 3-col row is present and preserved.
        assert any(r == ["a", "b", "c"] for r in rows)
        # Ensure we did not normalize blank-only lines into 3 empty tokens
        assert not any(len(r) == 3 and all(tok == "" for tok in r) for r in rows)
    finally:
        try:
            Path(path).unlink()
        except PermissionError:
            pass


def test_raise_on_missing_columns_triggers():
    # Create a file where detection will find 3 columns and we include a short row
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("h1,h2,h3\n")
        f.write("a,b,c\n")
        f.write("x,y\n")
        path = f.name

    try:
        cfg = DsvConfig(
            delimiter=",", detect_columns=True, chunk_size=10, skip_header_rows=1, raise_on_missing_columns=True
        )
        parser = Dsv(cfg)

        # Expect a SplurgeDsvColumnMismatchError when iterating the stream
        with pytest.raises(SplurgeDsvColumnMismatchError):
            list(parser.parse_file_stream(path))
    finally:
        try:
            Path(path).unlink()
        except PermissionError:
            pass


def test_raise_columns_greater_triggers():
    # Create a file where detection will find 2 columns and we include a long row
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("h1,h2\n")
        f.write("a,b\n")
        f.write("x,y,z\n")
        path = f.name

    try:
        cfg = DsvConfig(
            delimiter=",", detect_columns=True, chunk_size=10, skip_header_rows=1, raise_on_extra_columns=True
        )
        parser = Dsv(cfg)

        # Expect an exception when raise_on_extra_columns is True
        with pytest.raises(SplurgeDsvColumnMismatchError):
            list(parser.parse_file_stream(path))
    finally:
        try:
            Path(path).unlink()
        except PermissionError:
            pass
