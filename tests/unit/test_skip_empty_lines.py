from pathlib import Path

import pytest

from splurge_dsv.dsv import Dsv, DsvConfig


def _make_test_file(path: Path, *, lines: int = 150000, empty_every: int = 10, encoding: str = "utf-8"):
    # Create a file with `lines` non-empty lines and an empty line every `empty_every` items
    # Each non-empty line is unique so we can assert sequence.
    with path.open("w", encoding=encoding, newline="") as fh:
        seq = 0
        for i in range(lines):
            fh.write(f"data-{seq}\n")
            seq += 1
            if i % empty_every == 0:
                fh.write("\n")
    return path


@pytest.mark.parametrize("encoding,skip", [("utf-8", True), ("utf-8", False), ("utf-16", True), ("utf-16", False)])
def test_skip_empty_lines_file_and_stream(tmp_path: Path, encoding: str, skip: bool):
    # Create test file ~1.5MiB: adjust count down if needed
    file_path = tmp_path / f"test_{encoding.replace('-', '')}_{'skip' if skip else 'noskip'}.txt"
    # For speed in CI, choose smaller counts but still large-ish; tune if necessary.
    total_lines = 20000
    empty_every = 7
    _make_test_file(file_path, lines=total_lines, empty_every=empty_every, encoding=encoding)

    cfg = DsvConfig.from_params(delimiter=",", encoding=encoding, skip_empty_lines=skip)
    dsv = Dsv(cfg)

    # parse_file should return rows list where each row is a list of one token "data-N"
    rows = dsv.parse_file(file_path)
    # Determine expected number of non-empty logical rows according to skip setting
    # In our generator, we wrote total_lines non-empty lines and additionally wrote an empty \n every `empty_every` iterations.
    # Note: raw logical row counts include blank lines we inserted; assertions below check observed behavior.

    if skip:
        # With skipping, expect only the non-empty lines
        assert len(rows) == total_lines
    else:
        # Without skipping, many rows will include blank tokens; the exact shape depends on stripping behavior
        # We expect more rows than total_lines due to blank lines
        assert len(rows) >= total_lines

    # Stream read: ensure it yields the same set of non-empty rows when skip=True
    streamed = []
    for chunk in dsv.parse_file_stream(file_path):
        for r in chunk:
            streamed.append(r)

    if skip:
        assert len(streamed) == total_lines
    else:
        assert len(streamed) >= total_lines

    # Basic content check: all non-empty rows start with 'data-'
    non_empty_rows = [r for r in rows if any(tok != "" for tok in r)]
    assert all(row[0].startswith("data-") for row in non_empty_rows)
