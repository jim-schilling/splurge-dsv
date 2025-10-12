"""Minimal shim tests for `splurge_dsv.path_validator`.

These tests purposefully avoid re-testing the extensive behavior of
`splurge_safe_io`. The external library is already well-tested. Here we
only assert that the thin shim delegates to the external package and
returns/raises the expected high-level outcomes.
"""

from pathlib import Path

import pytest

from splurge_dsv.exceptions import (
    SplurgeDsvFileNotFoundError,
)
from splurge_dsv.path_validator import PathValidator


def test_validate_existing_file_smoke(tmp_path: Path) -> None:
    test_file = tmp_path / "test.txt"
    test_file.write_text("x")

    result = PathValidator.validate_path(test_file, must_exist=True)
    assert isinstance(result, Path)


def test_validate_missing_file_raises(tmp_path: Path) -> None:
    test_file = tmp_path / "nope.txt"
    with pytest.raises(SplurgeDsvFileNotFoundError):
        PathValidator.validate_path(test_file, must_exist=True)


def test_sanitize_filename_smoke() -> None:
    result = PathValidator.sanitize_filename("file<name.txt")
    assert isinstance(result, str) and len(result) > 0


def test_is_safe_path_returns_bool(tmp_path: Path) -> None:
    test_file = tmp_path / "test.txt"
    assert isinstance(PathValidator.is_safe_path(test_file), bool)
