"""Unit tests targeting error branches in splurge_dsv.dsv_helper using public APIs.

These tests monkeypatch the underlying safe reader to simulate decoding and
permission errors and validate that the helper maps them to the public
exceptions defined in splurge_dsv.exceptions.
"""

import pytest

from splurge_dsv.dsv_helper import DsvHelper
from splurge_dsv.exceptions import (
    SplurgeDsvFileDecodingError,
    SplurgeDsvFileNotFoundError,
    SplurgeDsvFilePermissionError,
)


def test_parse_file_nonexistent_raises(tmp_path) -> None:
    missing = tmp_path / "nope.csv"
    assert not missing.exists()

    with pytest.raises(SplurgeDsvFileNotFoundError):
        DsvHelper.parse_file(missing, delimiter=",")


def test_parse_file_decoding_error_monkeypatched(monkeypatch, tmp_path) -> None:
    # Create a real file path to satisfy path validation
    p = tmp_path / "some.csv"
    p.write_text("a,b\n1,2\n")

    class FakeDecodeError(Exception):
        pass

    class FakeReader:
        def __init__(self, *args, **kwargs):
            pass

        def readlines(self):
            raise FakeDecodeError("boom")

    import splurge_dsv.dsv_helper as dh

    monkeypatch.setattr(dh.safe_io_text_file_reader, "SafeTextFileReader", FakeReader)
    monkeypatch.setattr(dh.safe_io_text_file_reader, "SplurgeSafeIoFileDecodingError", FakeDecodeError)

    with pytest.raises(SplurgeDsvFileDecodingError):
        DsvHelper.parse_file(p, delimiter=",")


def test_parse_file_stream_decoding_error_monkeypatched(monkeypatch, tmp_path) -> None:
    p = tmp_path / "stream.csv"
    p.write_text("a,b\n1,2\n")

    class FakeDecodeError(Exception):
        pass

    class FakeReader2:
        def __init__(self, *args, **kwargs):
            pass

        def readlines_as_stream(self):
            raise FakeDecodeError("boom stream")

    import splurge_dsv.dsv_helper as dh

    monkeypatch.setattr(dh.safe_io_text_file_reader, "SafeTextFileReader", FakeReader2)
    monkeypatch.setattr(dh.safe_io_text_file_reader, "SplurgeSafeIoFileDecodingError", FakeDecodeError)

    with pytest.raises(SplurgeDsvFileDecodingError):
        list(DsvHelper.parse_file_stream(p, delimiter=","))


def test_parse_file_permission_error_monkeypatched(monkeypatch, tmp_path) -> None:
    p = tmp_path / "perm.csv"
    p.write_text("a,b\n1,2\n")

    class FakePermError(Exception):
        pass

    class FakeReader3:
        def __init__(self, *args, **kwargs):
            pass

        def readlines(self):
            raise FakePermError("no access")

    import splurge_dsv.dsv_helper as dh

    monkeypatch.setattr(dh.safe_io_text_file_reader, "SafeTextFileReader", FakeReader3)
    monkeypatch.setattr(dh.safe_io_text_file_reader, "SplurgeSafeIoFilePermissionError", FakePermError)

    with pytest.raises(SplurgeDsvFilePermissionError):
        DsvHelper.parse_file(p, delimiter=",")
