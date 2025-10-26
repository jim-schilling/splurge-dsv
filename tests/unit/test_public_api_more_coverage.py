import json

import pytest

from splurge_dsv.cli import run_cli
from splurge_dsv.dsv_helper import DsvHelper
from splurge_dsv.exceptions import SplurgeDsvLookupError


def test_run_cli_file_not_found(monkeypatch, tmp_path, capsys, cli_args):
    missing = tmp_path / "does_not_exist.csv"
    monkeypatch.setattr("sys.argv", ["splurge-dsv", str(missing), "--delimiter", ","])

    rc = run_cli()
    captured = capsys.readouterr()
    assert rc == 1
    assert "not found" in captured.err.lower()


@pytest.mark.parametrize("output_format", ["table", "json", "ndjson"])
def test_run_cli_parse_file_outputs(output_format, monkeypatch, tmp_path, capsys, cli_args):
    f = tmp_path / "data.csv"
    f.write_text("a,b\n1,2\n3,4\n")
    # Run the CLI end-to-end by setting argv
    argv = ["splurge-dsv", str(f), "--delimiter", ","]
    if output_format != "table":
        argv += ["--output-format", output_format]
    monkeypatch.setattr("sys.argv", argv)

    rc = run_cli()
    captured = capsys.readouterr()
    assert rc == 0

    if output_format == "table":
        # Dsv.parse_file includes the header row by default
        assert "Parsed 3 rows" in captured.out
        assert "|" in captured.out
    elif output_format == "json":
        # Should be a JSON array
        data = json.loads(captured.out)
        assert isinstance(data, list)
        assert len(data) == 3
    else:  # ndjson
        lines = [ln for ln in captured.out.splitlines() if ln.strip()]
        # Header + two rows -> three JSON lines
        assert len(lines) == 3
        for ln in lines:
            obj = json.loads(ln)
            assert isinstance(obj, list)


@pytest.mark.parametrize("output_format", ["table", "json", "ndjson"])
def test_run_cli_streaming_outputs(output_format, monkeypatch, tmp_path, capsys, cli_args):
    # Create a file with several rows to force streaming chunking
    f = tmp_path / "stream.csv"
    rows = ["h1,h2"] + [f"v{i},w{i}" for i in range(1, 5)]
    f.write_text("\n".join(rows) + "\n")

    argv = [
        "splurge-dsv",
        str(f),
        "--delimiter",
        ",",
        "--stream",
        "--chunk-size",
        str(DsvHelper.DEFAULT_MIN_CHUNK_SIZE),
    ]
    if output_format != "table":
        argv += ["--output-format", output_format]
    monkeypatch.setattr("sys.argv", argv)

    rc = run_cli()
    captured = capsys.readouterr()
    assert rc == 0

    if output_format == "table":
        assert "Chunk 1" in captured.out
        assert "Total:" in captured.out
    elif output_format == "json":
        # Each chunk prints a JSON list
        # ensure we can parse at least one JSON chunk
        assert "[" in captured.out
        json.loads([ln for ln in captured.out.splitlines() if ln.strip()][0])
    else:
        # ndjson prints JSON per row (arrays), but CLI may print a header line before
        lines = list(captured.out.splitlines())
        parsed = []
        for ln in lines:
            text = ln.strip()
            if not text:
                continue
            try:
                obj = json.loads(text)
            except Exception:
                # skip non-JSON headers or logging lines
                continue
            parsed.append(obj)

        # header + 4 data rows -> total rows written
        assert len(parsed) == len(rows)
        for obj in parsed:
            assert isinstance(obj, list)


def test_parse_file_raises_decoding_error_monkeypatched(monkeypatch, tmp_path):
    # Create a real file path but monkeypatch the SafeTextFileReader to raise
    p = tmp_path / "some.csv"
    p.write_text("a,b\n1,2\n")

    from splurge_safe_io.exceptions import SplurgeSafeIoLookupError

    class FakeReader:
        def __init__(self, *args, **kwargs):
            pass

        def readlines(self):
            raise SplurgeSafeIoLookupError(message="Decoding error", error_code="decode-error")

    # Patch the reader and the exception name on the module
    import splurge_dsv.dsv_helper as dh

    monkeypatch.setattr(dh.safe_io_text_file_reader, "SafeTextFileReader", FakeReader)

    with pytest.raises(SplurgeDsvLookupError):
        DsvHelper.parse_file(p, delimiter=",")


def test_parse_file_stream_raises_decoding_error_monkeypatched(monkeypatch, tmp_path):
    p = tmp_path / "some2.csv"
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
        # iterate to trigger the reader
        list(DsvHelper.parse_file_stream(p, delimiter=","))


def test_stream_chunk_materialization_and_mismatch(monkeypatch, tmp_path, capsys, cli_args):
    """Ensure that parse_file_stream handles generator chunks and mismatched row lengths."""
    p = tmp_path / "mismatch.csv"
    p.write_text("h1,h2\n1,2\n3,4\n")

    # Create a generator chunk (no __len__) and a subsequent list chunk with a mismatch
    def gen_chunk():
        yield from (["h1", "h2"], ["1", "2"])

    def fake_parse_file_stream(self, file_path):
        yield gen_chunk()
        yield [["a", "b"], ["c", "d", "e"]]

    import splurge_dsv.dsv as dmod

    # Monkeypatch Dsv.parse_file_stream so CLI receives raw chunks and performs materialization
    monkeypatch.setattr(dmod.Dsv, "parse_file_stream", fake_parse_file_stream, raising=False)
    # Run through the CLI path to ensure mismatch inspection branch is exercised
    argv = [
        "splurge-dsv",
        str(p),
        "--delimiter",
        ",",
        "--stream",
        "--chunk-size",
        str(DsvHelper.DEFAULT_MIN_CHUNK_SIZE),
    ]
    monkeypatch.setattr("sys.argv", argv)

    rc = run_cli()
    captured = capsys.readouterr()
    # The CLI will raise an error printing mismatched rows in table mode; ensure we observe a streaming error
    assert rc != 0
    assert "Error during streaming" in captured.err
