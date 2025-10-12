from pathlib import Path

from splurge_dsv import (
    Dsv,
    DsvConfig,
    DsvHelper,
    SplurgeDsvError,
    StringTokenizer,
)


def test_package_exports_exist() -> None:
    # Smoke test that key exports are present and importable
    assert Dsv is not None
    assert DsvConfig is not None
    assert DsvHelper is not None
    assert StringTokenizer is not None
    assert SplurgeDsvError is not None


def test_parse_file_stream_public_api(tmp_path: Path) -> None:
    p = tmp_path / "data.csv"
    p.write_text("a,b,c\n1,2,3\n")

    chunks = list(DsvHelper.parse_file_stream(p, delimiter=",", chunk_size=1))
    # Flatten
    rows = [row for chunk in chunks for row in chunk]
    assert rows == [["a", "b", "c"], ["1", "2", "3"]]
