from pathlib import Path

from splurge_dsv.safe_text_file_writer import SafeTextFileWriter, open_text_writer


def test_writer_open_write_close(tmp_path: Path) -> None:
    p = tmp_path / "out.txt"
    writer = SafeTextFileWriter(p)
    f = writer.open(mode="w")
    assert hasattr(f, "write")
    writer.write("hello\n")
    writer.flush()
    writer.close()

    assert p.read_text() == "hello\n"


def test_writelines_and_context_manager(tmp_path: Path) -> None:
    p = tmp_path / "out2.txt"
    with open_text_writer(p, encoding="utf-8", mode="w") as buf:
        buf.write("one\n")
        buf.writelines(["two\n", "three\n"])

    # File should be written after context manager
    content = p.read_text().splitlines()
    assert content == ["one", "two", "three"]
