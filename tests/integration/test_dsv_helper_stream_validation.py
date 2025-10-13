import tempfile
from pathlib import Path

import pytest

from splurge_dsv.dsv import Dsv, DsvConfig
from splurge_dsv.exceptions import SplurgeDsvColumnMismatchError


def test_stream_raise_on_column_mismatch():
    config = DsvConfig(delimiter=",", chunk_size=10)
    parser = Dsv(config)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("h1,h2,h3\n")
        f.write("a,b,c\n")
        f.write("d,e\n")
        temp_path = f.name

    try:
        # Request detection and raise if fewer columns found
        cfg = DsvConfig(
            delimiter=",", detect_columns=True, raise_on_missing_columns=True, chunk_size=10, skip_header_rows=1
        )
        parser = Dsv(cfg)

        with pytest.raises(SplurgeDsvColumnMismatchError):
            # Iterate to trigger processing
            list(parser.parse_file_stream(temp_path))
    finally:
        try:
            Path(temp_path).unlink()
        except PermissionError:
            # On Windows the file may still be held open briefly by the reader;
            # ignore the permission error for test cleanup.
            pass
