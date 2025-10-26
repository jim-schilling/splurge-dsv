"""Unit tests targeting error branches in splurge_dsv.dsv_helper using public APIs.

These tests monkeypatch the underlying safe reader to simulate decoding and
permission errors and validate that the helper maps them to the public
exceptions defined in splurge_dsv.exceptions.
"""

import pytest

from splurge_dsv.dsv_helper import DsvHelper
from splurge_dsv.exceptions import (
    SplurgeDsvLookupError,
    SplurgeDsvOSError,
)


def test_parse_file_nonexistent_raises(tmp_path) -> None:
    missing = tmp_path / "nope.csv"
    assert not missing.exists()

    with pytest.raises(SplurgeDsvOSError):
        DsvHelper.parse_file(missing, delimiter=",")


def test_parse_file_decoding_error_monkeypatched(monkeypatch, tmp_path) -> None:
    # Create a real file path to satisfy path validation
    p = tmp_path / "some.csv"
    p.write_text("a,b\n1,2\n")

    from splurge_safe_io.exceptions import SplurgeSafeIoLookupError

    class FakeReader:
        def __init__(self, *args, **kwargs):
            pass

        def readlines(self):
            raise SplurgeSafeIoLookupError(message="Decoding error", error_code="decode-error")

    import splurge_dsv.dsv_helper as dh

    monkeypatch.setattr(dh.safe_io_text_file_reader, "SafeTextFileReader", FakeReader)

    with pytest.raises(SplurgeDsvLookupError):
        DsvHelper.parse_file(p, delimiter=",")


def test_parse_file_stream_decoding_error_monkeypatched(monkeypatch, tmp_path) -> None:
    p = tmp_path / "stream.csv"
    p.write_text("a,b\n1,2\n")

    from splurge_safe_io.exceptions import SplurgeSafeIoLookupError

    class FakeReader2:
        def __init__(self, *args, **kwargs):
            pass

        def readlines_as_stream(self):
            raise SplurgeSafeIoLookupError(message="Decoding error in stream", error_code="decode-error")

    import splurge_dsv.dsv_helper as dh

    monkeypatch.setattr(dh.safe_io_text_file_reader, "SafeTextFileReader", FakeReader2)

    with pytest.raises(SplurgeDsvLookupError):
        list(DsvHelper.parse_file_stream(p, delimiter=","))


def test_parse_file_permission_error_monkeypatched(monkeypatch, tmp_path) -> None:
    p = tmp_path / "perm.csv"
    p.write_text("a,b\n1,2\n")

    from splurge_safe_io.exceptions import SplurgeSafeIoOSError

    class FakeReader3:
        def __init__(self, *args, **kwargs):
            pass

        def readlines(self):
            raise SplurgeSafeIoOSError(message="Permission denied", error_code="permission-error")

    import splurge_dsv.dsv_helper as dh

    monkeypatch.setattr(dh.safe_io_text_file_reader, "SafeTextFileReader", FakeReader3)

    with pytest.raises(SplurgeDsvOSError):
        DsvHelper.parse_file(p, delimiter=",")
