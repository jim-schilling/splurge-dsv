from pathlib import Path

from splurge_dsv.safe_text_file_reader import SafeTextFileReader, open_text


def test_safe_text_file_reader_read_smoke(tmp_path: Path) -> None:
    p = tmp_path / "in.txt"
    p.write_text("a\nb\nc\n")

    reader = SafeTextFileReader(p)
    lines = reader.read()
    assert isinstance(lines, list)
    assert lines and all(isinstance(line, str) for line in lines)


def test_open_text_context_manager_smoke(tmp_path: Path) -> None:
    p = tmp_path / "in2.txt"
    p.write_text("x\n")

    with open_text(p, encoding="utf-8") as sio:
        content = sio.read()
    assert isinstance(content, str)
