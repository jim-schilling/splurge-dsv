from pathlib import Path

from splurge_dsv.text_file_helper import TextFileHelper


def test_line_count_and_read(tmp_path: Path) -> None:
    p = tmp_path / "f.txt"
    p.write_text("a\nb\nc\n")

    cnt = TextFileHelper.line_count(p)
    assert cnt == 3

    lines = TextFileHelper.read(p)
    assert lines == ["a", "b", "c"]


def test_preview_and_read_as_stream(tmp_path: Path) -> None:
    p = tmp_path / "f2.txt"
    p.write_text("1\n2\n3\n4\n5\n")

    prev = TextFileHelper.preview(p, max_lines=2)
    assert prev == ["1", "2"]

    chunks = list(TextFileHelper.read_as_stream(p, chunk_size=2))
    assert sum(len(c) for c in chunks) == 5
