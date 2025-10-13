import argparse
import importlib
import string
import sys
from collections.abc import Callable
from pathlib import Path

import pytest
from hypothesis import strategies as st

from splurge_dsv.dsv import DsvConfig


@pytest.fixture
def cli_args() -> Callable[[str], argparse.Namespace]:
    """Return a small factory that builds a fully-populated argparse.Namespace
    like the tests previously constructed inline. Tests can call this
    fixture as a function: args = cli_args(path)
    """

    def _build(file_path: str) -> argparse.Namespace:
        return argparse.Namespace(
            file_path=str(file_path),
            delimiter=",",
            bookend=None,
            no_strip=False,
            no_bookend_strip=False,
            encoding="utf-8",
            skip_header=0,
            skip_footer=0,
            stream=False,
            chunk_size=500,
            output_format="table",
            detect_columns=False,
            raise_on_missing_columns=False,
            raise_on_extra_columns=False,
            max_detect_chunks=None,
        )

    return _build


@pytest.fixture
def reload_pkg_under() -> Callable[[], object]:
    """Return a callable that reloads the splurge_dsv package while
    ensuring any existing import is restored. Tests that need to reload
    the package under modified environment (monkeypatching Path.cwd, os.chdir,
    etc.) can call this function to safely import the package.
    """

    def _reload():
        orig = sys.modules.pop("splurge_dsv", None)
        try:
            return importlib.import_module("splurge_dsv")
        finally:
            if orig is not None:
                sys.modules["splurge_dsv"] = orig

    return _reload


"""Shared test configuration and Hypothesis strategies for splurge-dsv testing.

This module provides common test fixtures, Hypothesis strategies, and
configuration used across all test modules.
"""


@st.composite
def delimiter_strategy(draw) -> str:
    """Generate valid delimiter characters for DSV parsing."""
    # Common delimiters plus some edge cases
    common_delimiters = [",", "\t", "|", ";", ":", "@", "#", "$", "%", "^", "&", "*"]
    # Single character delimiters (excluding control characters and common text)
    single_chars = [
        c for c in string.printable if c not in string.whitespace + string.digits + string.ascii_letters + "\",'"
    ]

    all_delimiters = list(set(common_delimiters + single_chars))
    return draw(st.sampled_from(all_delimiters))


@st.composite
def quote_strategy(draw) -> str:
    """Generate valid quote characters for DSV parsing."""
    # Common quote characters
    quotes = ['"', "'", "`", "´", "¨", "ˆ"]
    return draw(st.sampled_from(quotes))


@st.composite
def escape_strategy(draw) -> str:
    """Generate valid escape characters for DSV parsing."""
    # Common escape characters
    escapes = ["\\", "^", "~", "`"]
    return draw(st.sampled_from(escapes))


@st.composite
def text_content_strategy(draw, min_length: int = 0, max_length: int = 100) -> str:
    """Generate various text content for testing."""
    return draw(
        st.text(
            alphabet=st.characters(
                categories=["L", "N", "P", "S", "Zs"],  # Letters, numbers, punctuation, symbols, spaces
                exclude_categories=["Cc", "Cf"],  # Exclude control and format characters
            ),
            min_size=min_length,
            max_size=max_length,
        )
    )


@st.composite
def csv_field_strategy(draw) -> str:
    """Generate valid CSV field content."""
    # Mix of simple fields and quoted fields with special characters
    strategies = [
        # Simple fields without special characters
        st.text(alphabet=st.characters(categories=["L", "N"]), min_size=0, max_size=20),
        # Fields with spaces
        st.text(alphabet=st.characters(categories=["L", "N", "Zs"]), min_size=1, max_size=20),
        # Quoted fields with commas and quotes
        st.builds(
            lambda content: f'"{content}"',
            st.text(alphabet=st.characters(categories=["L", "N", "P", "Zs"]), min_size=0, max_size=15),
        ),
        # Empty fields
        st.just(""),
    ]

    return draw(st.one_of(*strategies))


@st.composite
def csv_row_strategy(draw, min_fields: int = 1, max_fields: int = 10) -> list[str]:
    """Generate valid CSV row data."""
    num_fields = draw(st.integers(min_value=min_fields, max_value=max_fields))
    fields = []
    for _ in range(num_fields):
        fields.append(draw(csv_field_strategy()))
    return fields


@st.composite
def csv_content_strategy(draw, min_rows: int = 1, max_rows: int = 50) -> str:
    """Generate valid CSV content."""
    delimiter = draw(delimiter_strategy())
    rows = []

    for _ in range(draw(st.integers(min_value=min_rows, max_value=max_rows))):
        row = draw(csv_row_strategy())
        # Join fields with delimiter, handling quoted fields properly
        csv_row = delimiter.join(f'"{field}"' if delimiter in field or '"' in field else field for field in row)
        rows.append(csv_row)

    return "\n".join(rows)


@st.composite
def file_path_strategy(draw, allow_relative: bool = True, allow_absolute: bool = True) -> str:
    """Generate file path strings for testing."""
    strategies = []

    if allow_relative:
        # Relative paths
        strategies.extend(
            [
                st.just("file.csv"),
                st.just("data/file.csv"),
                st.just("./file.csv"),
                st.just("../file.csv"),
                st.just("subdir/file.csv"),
            ]
        )

    if allow_absolute:
        # Absolute paths (simplified for cross-platform)
        strategies.extend(
            [
                st.just("/tmp/file.csv"),
                st.just("/home/user/file.csv"),
                st.just("C:/temp/file.csv"),
                st.just("C:\\temp\\file.csv"),
            ]
        )

    # Dynamic path generation
    path_parts = draw(
        st.lists(
            st.text(alphabet=st.characters(categories=["L", "N"]), min_size=1, max_size=10), min_size=1, max_size=3
        )
    )

    if path_parts:
        dynamic_path = "/".join(path_parts) + ".csv"
        strategies.append(st.just(dynamic_path))

    return draw(st.one_of(*strategies))


@st.composite
def dsv_config_strategy(draw) -> DsvConfig:
    """Generate valid DsvConfig instances for testing."""
    return DsvConfig(
        delimiter=draw(delimiter_strategy()),
        strip=draw(st.booleans()),
        bookend=draw(st.one_of(quote_strategy(), st.none())),
        bookend_strip=draw(st.booleans()),
        encoding=draw(st.sampled_from(["utf-8", "utf-16", "latin-1", "ascii"])),
        skip_header_rows=draw(st.integers(min_value=0, max_value=5)),
        skip_footer_rows=draw(st.integers(min_value=0, max_value=5)),
        chunk_size=draw(st.integers(min_value=1, max_value=10000)),
    )


# Pytest Fixtures
# ===============


@pytest.fixture
def temp_csv_file(tmp_path):
    """Create a temporary CSV file for testing."""

    def _create_csv(content: str, filename: str = "test.csv") -> Path:
        file_path = tmp_path / filename
        file_path.write_text(content, encoding="utf-8")
        return file_path

    return _create_csv


@pytest.fixture
def sample_csv_content():
    """Provide sample CSV content for testing."""
    return """name,age,city
John,30,"New York, NY"
Jane,25,London
Bob,35,"Los Angeles, CA"
Alice,28,Boston"""


@pytest.fixture
def sample_tsv_content():
    """Provide sample TSV content for testing."""
    return """name\tage\tcity
John\t30\tNew York
Jane\t25\tLondon
Bob\t35\tLos Angeles
Alice\t28\tBoston"""


# Hypothesis Profiles
# ===================

# Register hypothesis profiles for different testing modes
st.register_type_strategy(Path, file_path_strategy())
