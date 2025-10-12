from pathlib import Path

from splurge_dsv.safe_text_file_writer import open_text_writer


def test_open_text_writer_smoke(tmp_path: Path) -> None:
    p = tmp_path / "out.txt"
    content = "line1\nline2\n"
    with open_text_writer(p, encoding="utf-8", mode="w") as fh:
        fh.write(content)

    assert p.exists()
    assert p.read_text(encoding="utf-8") == content


def test_safe_text_file_writer_normalizes_newlines(tmp_path: Path) -> None:
    p = tmp_path / "out.txt"
    # mixed input newlines
    content = "line1\r\nline2\nline3\r"
    with open_text_writer(p, encoding="utf-8", mode="w") as fh:
        fh.write(content)

    # Read raw bytes to verify the writer wrote LF-only newlines
    raw = p.read_bytes()
    assert b"\r" not in raw
    assert raw == b"line1\nline2\nline3\n"
