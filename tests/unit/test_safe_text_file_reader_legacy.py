from pathlib import Path

from splurge_dsv.safe_text_file_reader import SafeTextFileReader, open_text


def test_reader_read_and_preview(tmp_path: Path) -> None:
    p = tmp_path / "data.txt"
    p.write_text("line1\nline2\nline3\n")

    r = SafeTextFileReader(p)
    lines = r.read()
    assert lines == ["line1", "line2", "line3"]

    prev = r.preview(2)
    assert prev == ["line1", "line2"]


def test_reader_read_as_stream(tmp_path: Path) -> None:
    p = tmp_path / "data2.txt"
    p.write_text("a\nb\nc\nd\n")

    r = SafeTextFileReader(p, chunk_size=2)
    chunks = list(r.read_as_stream())
    # chunks should be lists of strings
    assert all(isinstance(c, list) for c in chunks)
    assert sum(len(c) for c in chunks) == 4


def test_open_text_context_manager(tmp_path: Path) -> None:
    p = tmp_path / "data3.txt"
    p.write_text("x\n")

    with open_text(p) as sio:
        assert sio.read().strip() == "x"
