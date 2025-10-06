from pathlib import Path

from splurge_dsv.safe_text_file_writer import open_text_writer


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
