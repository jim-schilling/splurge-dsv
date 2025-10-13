from pathlib import Path

import pytest

from splurge_dsv.cli import run_cli


def write_sample_dsv(p: Path) -> None:
    p.write_text("a,b\n1,2\n", encoding="utf-8")


def test_cli_config_overrides_yaml(tmp_path: Path, capsys, monkeypatch):
    pytest.importorskip("yaml")

    data_file = tmp_path / "data.csv"
    write_sample_dsv(data_file)

    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(
        """
delimiter: ","
strip: true
bookend: '"'
encoding: utf-8
skip_header_rows: 0
""",
        encoding="utf-8",
    )

    # Provide a CLI delimiter that should override the YAML delimiter
    argv = [str(data_file), "--config", str(cfg), "--delimiter", "|"]

    # Patch sys.argv and invoke run_cli()
    monkeypatch.setattr("sys.argv", ["splurge-dsv"] + argv)
    rc = run_cli()

    # Should succeed
    assert rc == 0


def test_cli_uses_yaml_when_missing_args(tmp_path: Path, monkeypatch):
    pytest.importorskip("yaml")

    data_file = tmp_path / "data.csv"
    write_sample_dsv(data_file)

    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(
        """
delimiter: ","
strip: true
encoding: utf-8
skip_header_rows: 0
""",
        encoding="utf-8",
    )

    argv = [str(data_file), "--config", str(cfg)]
    monkeypatch.setattr("sys.argv", ["splurge-dsv"] + argv)

    rc = run_cli()

    assert rc == 0
