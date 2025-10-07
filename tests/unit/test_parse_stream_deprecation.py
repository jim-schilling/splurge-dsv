import pytest

from splurge_dsv.dsv import Dsv, DsvConfig
from splurge_dsv.dsv_helper import DsvHelper


def _stub_parse_file_stream(*args, **kwargs):
    # Return a simple iterator to avoid touching the filesystem during the test
    yield ["a", "b", "c"]


def test_dsvhelper_parse_stream_emits_deprecation(monkeypatch):
    monkeypatch.setattr(DsvHelper, "parse_file_stream", _stub_parse_file_stream)

    with pytest.warns(DeprecationWarning):
        chunks = list(DsvHelper.parse_stream("dummy.csv", delimiter=","))

    assert chunks == [["a", "b", "c"]]


def test_dsv_parse_stream_emits_deprecation(monkeypatch):
    monkeypatch.setattr(DsvHelper, "parse_file_stream", _stub_parse_file_stream)

    cfg = DsvConfig.csv()
    parser = Dsv(cfg)

    with pytest.warns(DeprecationWarning):
        chunks = list(parser.parse_stream("dummy.csv"))

    assert chunks == [["a", "b", "c"]]
