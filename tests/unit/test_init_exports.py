"""Tests for splurge_dsv package __init__ exports to improve coverage."""

import importlib
import inspect


def test_package_metadata_and_exports():
    pkg = importlib.import_module("splurge_dsv")

    # Basic metadata
    assert hasattr(pkg, "__version__")
    assert isinstance(pkg.__version__, str)
    assert hasattr(pkg, "__author__")
    assert isinstance(pkg.__author__, str)
    assert hasattr(pkg, "__license__")
    assert isinstance(pkg.__license__, str)

    # __all__ should list exported names and they should be attributes on the package
    assert hasattr(pkg, "__all__")
    for name in pkg.__all__:
        assert hasattr(pkg, name), f"Expected {name} to be exported in package"

    # Check a few specific exports are classes or callables where expected
    assert inspect.isclass(pkg.Dsv)
    assert inspect.isclass(pkg.DsvConfig)
    assert inspect.isclass(pkg.DsvHelper)
    assert inspect.isclass(pkg.StringTokenizer)

    # Exceptions should be present and subclass Exception
    ex = pkg.SplurgeDsvError
    assert inspect.isclass(ex)
    assert issubclass(ex, Exception)

    col_mismatch = pkg.SplurgeDsvColumnMismatchError
    assert inspect.isclass(col_mismatch)
    assert issubclass(col_mismatch, Exception)
