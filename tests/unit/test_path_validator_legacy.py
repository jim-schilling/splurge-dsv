from pathlib import Path

import pytest

from splurge_dsv import path_validator as pv
from splurge_dsv.exceptions import SplurgeDsvFileNotFoundError


def test_validate_path_existing_file(tmp_path: Path) -> None:
    p = tmp_path / "f.txt"
    p.write_text("abc")

    # Classmethod
    res = pv.PathValidator.validate_path(p, must_exist=True, must_be_file=True)
    assert isinstance(res, Path)

    # Module-level helper
    res2 = pv.validate_path(str(p), must_exist=True, must_be_file=True)
    assert isinstance(res2, Path)


def test_validate_path_nonexistent_raises(tmp_path: Path) -> None:
    p = tmp_path / "does-not-exist.txt"
    with pytest.raises(SplurgeDsvFileNotFoundError):
        pv.PathValidator.validate_path(p, must_exist=True, must_be_file=True)


def test_is_safe_path_and_sanitize() -> None:
    assert pv.is_safe_path("normal.txt") is True
    s = pv.PathValidator.sanitize_filename("../weird/name.txt")
    assert isinstance(s, str)
    # Ensure sanitize_filename removed any parent-directory segments; exact
    # output may vary by external implementation, so be permissive about
    # path separators but strict about '..' which would indicate traversal.
    assert ".." not in s
