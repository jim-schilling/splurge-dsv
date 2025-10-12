"""CLI-level tests for --max-detect-chunks wiring.

These tests monkeypatch `parse_arguments` to simulate CLI input and then
monkeypatch `Dsv.parse_file_stream` / `Dsv.parse_file` to assert the
`Dsv` instance has `config.max_detect_chunks` set to the provided value.
"""

from splurge_dsv.cli import run_cli
from splurge_dsv.dsv import Dsv, DsvConfig
from splurge_dsv.dsv_helper import DsvHelper


def test_cli_passes_max_detect_chunks_to_streaming(monkeypatch, tmp_path, cli_args):
    f = tmp_path / "stream.csv"
    f.write_text("h1,h2\n1,2\n")
    args = cli_args(f)
    args.stream = True
    args.chunk_size = DsvHelper.DEFAULT_MIN_CHUNK_SIZE
    args.max_detect_chunks = 5

    monkeypatch.setattr("splurge_dsv.cli.parse_arguments", lambda: args)

    # Intercept Dsv.parse_file_stream to assert config value is propagated
    def fake_parse_file_stream(self, file_path):
        assert isinstance(self.config, DsvConfig)
        assert self.config.max_detect_chunks == 5
        # yield an empty chunk so CLI continues normally
        yield []

    monkeypatch.setattr(Dsv, "parse_file_stream", fake_parse_file_stream, raising=False)

    rc = run_cli()
    assert rc == 0


def test_cli_passes_max_detect_chunks_to_non_stream(monkeypatch, tmp_path, cli_args):
    f = tmp_path / "data.csv"
    f.write_text("a,b\n1,2\n")

    args = cli_args(f)
    args.stream = False
    args.max_detect_chunks = 7

    monkeypatch.setattr("splurge_dsv.cli.parse_arguments", lambda: args)

    def fake_parse_file(self, file_path):
        assert isinstance(self.config, DsvConfig)
        assert self.config.max_detect_chunks == 7
        return [["a", "b"], ["1", "2"]]

    monkeypatch.setattr(Dsv, "parse_file", fake_parse_file, raising=False)

    rc = run_cli()
    assert rc == 0
