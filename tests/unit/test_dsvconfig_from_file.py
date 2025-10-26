import textwrap
from pathlib import Path

import pytest

from splurge_dsv.dsv import DsvConfig
from splurge_dsv.exceptions import SplurgeDsvOSError, SplurgeDsvTypeError, SplurgeDsvValueError


def test_from_file_valid_yaml(tmp_path: Path):
    pytest.importorskip("yaml")

    content = textwrap.dedent(
        """
        delimiter: ","
        strip: true
        bookend: '"'
        encoding: utf-8
        skip_header_rows: 1
        detect_columns: true
        """
    )

    p = tmp_path / "cfg.yaml"
    p.write_text(content, encoding="utf-8")

    cfg = DsvConfig.from_file(p)
    assert isinstance(cfg, DsvConfig)
    assert cfg.delimiter == ","
    assert cfg.strip is True
    assert cfg.bookend == '"'


def test_from_file_missing_file_raises(tmp_path: Path):
    with pytest.raises(SplurgeDsvOSError):
        DsvConfig.from_file(tmp_path / "does-not-exist.yaml")


def test_from_file_invalid_yaml_raises(tmp_path: Path):
    pytest.importorskip("yaml")

    p = tmp_path / "bad.yaml"
    # invalid YAML
    p.write_text("::not_yaml::", encoding="utf-8")

    with pytest.raises(SplurgeDsvValueError):
        DsvConfig.from_file(p)


def test_from_file_non_dict_top_level_raises(tmp_path: Path):
    pytest.importorskip("yaml")

    p = tmp_path / "list.yaml"
    p.write_text("- a\n- b\n", encoding="utf-8")

    with pytest.raises(SplurgeDsvTypeError):
        DsvConfig.from_file(p)
