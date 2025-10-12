"""Tests that `splurge_dsv.__init__` handles missing current working directory.

These tests reload the package under monkeypatched `pathlib.Path.cwd` and
`os.chdir` to exercise import-time defensive logic that switches the cwd to
the package directory when the original working directory is missing.
"""

import os
import pathlib


def test_init_switches_to_package_dir_when_cwd_missing(monkeypatch, reload_pkg_under):
    # Make Path.cwd().exists() return False so the import code will call os.chdir
    # Return a real Path object that does not exist so pathlib.Path
    # checks continue to succeed (pytest expects Path instances).
    monkeypatch.setattr(
        pathlib.Path,
        "cwd",
        classmethod(lambda cls: pathlib.Path("this_path_should_not_exist_12345")),
    )

    called = {}

    def fake_chdir(path):
        called["path"] = path

    monkeypatch.setattr(os, "chdir", fake_chdir)

    mod = reload_pkg_under()

    # Import should have called os.chdir to switch to the package directory
    assert "path" in called
    # And module should be imported with version metadata present
    assert hasattr(mod, "__version__")


def test_init_handles_path_cwd_raises_file_not_found(monkeypatch, reload_pkg_under):
    # Make Path.cwd() raise FileNotFoundError to hit the except branch
    def raise_file_not_found(cls):
        raise FileNotFoundError()

    monkeypatch.setattr(pathlib.Path, "cwd", classmethod(raise_file_not_found))

    called = {}

    def fake_chdir(path):
        called["path"] = path

    monkeypatch.setattr(os, "chdir", fake_chdir)

    mod = reload_pkg_under()

    assert "path" in called
    assert hasattr(mod, "__version__")
