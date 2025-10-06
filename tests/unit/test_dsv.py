"""
Unit tests for the Dsv and DsvConfig classes.

This module provides comprehensive unit tests for the new DSV parsing API
that uses configuration dataclasses for better type safety and reusability.

Copyright (c) 2025 Jim Schilling

This module is licensed under the MIT License.
"""

# Standard library imports
import tempfile
from pathlib import Path

# Third-party imports
import pytest

# Local imports
from splurge_dsv.dsv import Dsv, DsvConfig
from splurge_dsv.dsv_helper import DsvHelper
from splurge_dsv.exceptions import SplurgeDsvParameterError


class TestDsvConfig:
    """Test cases for DsvConfig dataclass."""

    def test_dsv_config_creation_basic(self):
        """Test basic DsvConfig creation with minimal parameters."""
        config = DsvConfig(delimiter=",")
        assert config.delimiter == ","
        assert config.strip is True
        assert config.bookend is None
        assert config.bookend_strip is True
        assert config.encoding == "utf-8"
        assert config.skip_header_rows == 0
        assert config.skip_footer_rows == 0
        assert config.chunk_size == 500

    def test_dsv_config_creation_full(self):
        """Test DsvConfig creation with all parameters specified."""
        config = DsvConfig(
            delimiter=";",
            strip=False,
            bookend='"',
            bookend_strip=False,
            encoding="latin-1",
            skip_header_rows=1,
            skip_footer_rows=2,
            chunk_size=1000,
        )
        assert config.delimiter == ";"
        assert config.strip is False
        assert config.bookend == '"'
        assert config.bookend_strip is False
        assert config.encoding == "latin-1"
        assert config.skip_header_rows == 1
        assert config.skip_footer_rows == 2
        assert config.chunk_size == 1000

    def test_dsv_config_frozen(self):
        """Test that DsvConfig is frozen and cannot be modified."""
        config = DsvConfig(delimiter=",")
        with pytest.raises(AttributeError, match="cannot assign to field"):
            config.delimiter = ";"  # type: ignore

    def test_dsv_config_validation_empty_delimiter(self):
        """Test that empty delimiter raises ParameterError."""
        with pytest.raises(SplurgeDsvParameterError, match="delimiter cannot be empty"):
            DsvConfig(delimiter="")

    def test_dsv_config_validation_chunk_size_too_small(self):
        """Test that chunk_size below minimum raises ParameterError."""
        with pytest.raises(SplurgeDsvParameterError, match="chunk_size must be at least 100"):
            DsvConfig(delimiter=",", chunk_size=50)

    def test_dsv_config_validation_negative_skip_header(self):
        """Test that negative skip_header_rows raises ParameterError."""
        with pytest.raises(SplurgeDsvParameterError, match="skip_header_rows cannot be negative"):
            DsvConfig(delimiter=",", skip_header_rows=-1)

    def test_dsv_config_validation_negative_skip_footer(self):
        """Test that negative skip_footer_rows raises ParameterError."""
        with pytest.raises(SplurgeDsvParameterError, match="skip_footer_rows cannot be negative"):
            DsvConfig(delimiter=",", skip_footer_rows=-1)

    def test_dsv_config_csv_factory(self):
        """Test DsvConfig.csv() factory method."""
        config = DsvConfig.csv()
        assert config.delimiter == ","
        assert config.strip is True  # default

    def test_dsv_config_csv_factory_with_overrides(self):
        """Test DsvConfig.csv() factory method with parameter overrides."""
        config = DsvConfig.csv(skip_header_rows=1, encoding="utf-16")
        assert config.delimiter == ","
        assert config.skip_header_rows == 1
        assert config.encoding == "utf-16"

    def test_dsv_config_tsv_factory(self):
        """Test DsvConfig.tsv() factory method."""
        config = DsvConfig.tsv()
        assert config.delimiter == "\t"
        assert config.strip is True  # default

    def test_dsv_config_tsv_factory_with_overrides(self):
        """Test DsvConfig.tsv() factory method with parameter overrides."""
        config = DsvConfig.tsv(bookend='"', chunk_size=1000)
        assert config.delimiter == "\t"
        assert config.bookend == '"'
        assert config.chunk_size == 1000

    def test_dsv_config_from_params_basic(self):
        """Test DsvConfig.from_params() with basic parameters."""
        config = DsvConfig.from_params(delimiter=";", encoding="utf-16")
        assert config.delimiter == ";"
        assert config.encoding == "utf-16"
        # Other fields should have defaults
        assert config.strip is True

    def test_dsv_config_from_params_filters_invalid(self):
        """Test DsvConfig.from_params() filters out invalid parameters."""
        config = DsvConfig.from_params(
            delimiter=",",
            invalid_param="ignored",
            another_invalid=123,
            encoding="utf-8",  # valid
        )
        assert config.delimiter == ","
        assert config.encoding == "utf-8"
        # Should not have the invalid attributes
        assert not hasattr(config, "invalid_param")
        assert not hasattr(config, "another_invalid")

    def test_dsv_config_from_params_empty_kwargs(self):
        """Test DsvConfig.from_params() with no parameters raises error."""
        with pytest.raises(TypeError):
            # delimiter is required, so this should fail
            DsvConfig.from_params()


class TestDsv:
    """Test cases for Dsv class."""

    def test_dsv_creation(self):
        """Test Dsv class instantiation."""
        config = DsvConfig(delimiter=",")
        parser = Dsv(config)
        assert parser.config is config

    def test_dsv_parse_basic(self):
        """Test Dsv.parse() method."""
        config = DsvConfig(delimiter=",")
        parser = Dsv(config)
        result = parser.parse("a,b,c")
        assert result == ["a", "b", "c"]

    def test_dsv_parse_with_config(self):
        """Test Dsv.parse() respects configuration."""
        config = DsvConfig(delimiter=";", strip=False, bookend='"')
        parser = Dsv(config)
        result = parser.parse('"a";"b";"c"')
        assert result == ["a", "b", "c"]  # bookends are always removed when specified

    def test_dsv_parse_matches_dsv_helper(self):
        """Test that Dsv.parse() produces same results as DsvHelper.parse()."""
        config = DsvConfig(delimiter=",", strip=True, bookend='"')
        parser = Dsv(config)

        test_string = '"hello","world","test"'
        dsv_result = parser.parse(test_string)
        helper_result = DsvHelper.parse(
            test_string,
            delimiter=",",
            strip=True,
            bookend='"',
            bookend_strip=True,
        )

        assert dsv_result == helper_result

    def test_dsv_parses_basic(self):
        """Test Dsv.parses() method."""
        config = DsvConfig(delimiter=",")
        parser = Dsv(config)
        result = parser.parses(["a,b", "c,d"])
        assert result == [["a", "b"], ["c", "d"]]

    def test_dsv_parses_matches_dsv_helper(self):
        """Test that Dsv.parses() produces same results as DsvHelper.parses()."""
        config = DsvConfig(delimiter="\t", strip=False)
        parser = Dsv(config)

        test_lines = ["a\tb\tc", "d\te\tf"]
        dsv_result = parser.parses(test_lines)
        helper_result = DsvHelper.parses(
            test_lines,
            delimiter="\t",
            strip=False,
            bookend=None,
            bookend_strip=True,
        )

        assert dsv_result == helper_result

    def test_dsv_parse_file_basic(self):
        """Test Dsv.parse_file() method with a temporary file."""
        config = DsvConfig(delimiter=",")
        parser = Dsv(config)

        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("name,age,city\n")
            f.write("Alice,25,New York\n")
            f.write("Bob,30,London\n")
            temp_path = f.name

        try:
            result = parser.parse_file(temp_path)
            expected = [
                ["name", "age", "city"],
                ["Alice", "25", "New York"],
                ["Bob", "30", "London"],
            ]
            assert result == expected
        finally:
            Path(temp_path).unlink()

    def test_dsv_parse_file_with_skip_header(self):
        """Test Dsv.parse_file() with skip_header_rows configuration."""
        config = DsvConfig(delimiter=",", skip_header_rows=1)
        parser = Dsv(config)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("name,age,city\n")  # header to skip
            f.write("Alice,25,New York\n")
            f.write("Bob,30,London\n")
            temp_path = f.name

        try:
            result = parser.parse_file(temp_path)
            expected = [
                ["Alice", "25", "New York"],
                ["Bob", "30", "London"],
            ]
            assert result == expected
        finally:
            Path(temp_path).unlink()

    def test_dsv_parse_file_matches_dsv_helper(self):
        """Test that Dsv.parse_file() produces same results as DsvHelper.parse_file()."""
        config = DsvConfig(delimiter="|", encoding="utf-8", skip_header_rows=1)
        parser = Dsv(config)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write("header1|header2|header3\n")
            f.write("value1|value2|value3\n")
            f.write("data1|data2|data3\n")
            temp_path = f.name

        try:
            dsv_result = parser.parse_file(temp_path)
            helper_result = DsvHelper.parse_file(
                temp_path,
                delimiter="|",
                encoding="utf-8",
                skip_header_rows=1,
                skip_footer_rows=0,
                strip=True,
                bookend=None,
                bookend_strip=True,
            )
            assert dsv_result == helper_result
        finally:
            Path(temp_path).unlink()

    def test_dsv_parse_stream_basic(self):
        """Test Dsv.parse_stream() method."""
        config = DsvConfig(delimiter=",", chunk_size=200)
        parser = Dsv(config)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            for i in range(5):
                f.write(f"row{i},data{i}\n")
            temp_path = f.name

        try:
            chunks = list(parser.parse_stream(temp_path))
            # Should have at least one chunk
            assert len(chunks) >= 1
            # All chunks should be non-empty
            assert all(len(chunk) > 0 for chunk in chunks)
            # Total rows should be 5
            total_rows = sum(len(chunk) for chunk in chunks)
            assert total_rows == 5
        finally:
            Path(temp_path).unlink()

    def test_dsv_parse_stream_matches_dsv_helper(self):
        """Test that Dsv.parse_stream() produces same results as DsvHelper.parse_stream()."""
        config = DsvConfig(delimiter="\t", chunk_size=150, skip_header_rows=1)
        parser = Dsv(config)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".tsv", delete=False) as f:
            f.write("header1\theader2\n")  # will be skipped
            for i in range(7):
                f.write(f"value{i}\tdata{i}\n")
            temp_path = f.name

        try:
            dsv_chunks = list(parser.parse_stream(temp_path))
            helper_chunks = list(
                DsvHelper.parse_stream(
                    temp_path,
                    delimiter="\t",
                    chunk_size=3,
                    skip_header_rows=1,
                    skip_footer_rows=0,
                    strip=True,
                    bookend=None,
                    bookend_strip=True,
                    encoding="utf-8",
                )
            )
            assert dsv_chunks == helper_chunks
        finally:
            Path(temp_path).unlink()


class TestDsvIntegration:
    """Integration tests for Dsv class with real-world scenarios."""

    def test_csv_parsing_workflow(self):
        """Test complete CSV parsing workflow."""
        # Create parser with CSV config
        parser = Dsv(DsvConfig.csv(skip_header_rows=1))

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("id,name,email\n")  # header
            f.write("1,John Doe,john@example.com\n")
            f.write("2,Jane Smith,jane@example.com\n")
            temp_path = f.name

        try:
            result = parser.parse_file(temp_path)
            expected = [
                ["1", "John Doe", "john@example.com"],
                ["2", "Jane Smith", "jane@example.com"],
            ]
            assert result == expected
        finally:
            Path(temp_path).unlink()

    def test_tsv_parsing_workflow(self):
        """Test complete TSV parsing workflow."""
        parser = Dsv(DsvConfig.tsv(bookend='"'))

        with tempfile.NamedTemporaryFile(mode="w", suffix=".tsv", delete=False) as f:
            f.write('"Product"\t"Price"\t"Category"\n')
            f.write('"Widget"\t"19.99"\t"Gadgets"\n')
            f.write('"Gadget"\t"29.99"\t"Gadgets"\n')
            temp_path = f.name

        try:
            result = parser.parse_file(temp_path)
            expected = [
                ["Product", "Price", "Category"],
                ["Widget", "19.99", "Gadgets"],
                ["Gadget", "29.99", "Gadgets"],
            ]
            assert result == expected
        finally:
            Path(temp_path).unlink()

    def test_configuration_reuse(self):
        """Test that configuration can be reused across multiple operations."""
        config = DsvConfig(delimiter=";", skip_header_rows=1, encoding="utf-8")
        parser = Dsv(config)

        # Create two similar files
        files_data = [
            ("file1.txt", ["header;a;b", "1;x;y", "2;p;q"]),
            ("file2.txt", ["header;a;b", "3;m;n", "4;r;s"]),
        ]

        temp_paths = []
        try:
            for _filename, lines in files_data:
                with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
                    for line in lines:
                        f.write(line + "\n")
                    temp_paths.append(f.name)

            # Parse both files with same config
            result1 = parser.parse_file(temp_paths[0])
            result2 = parser.parse_file(temp_paths[1])

            expected1 = [["1", "x", "y"], ["2", "p", "q"]]
            expected2 = [["3", "m", "n"], ["4", "r", "s"]]

            assert result1 == expected1
            assert result2 == expected2

        finally:
            for path in temp_paths:
                Path(path).unlink()
