"""
Tests for the DSV helper module.

Tests the core DSV parsing functionality for string-based operations,
including single string parsing (parse method), multiple string parsing
(parses method), and edge cases with Unicode content and special characters.
File parsing and streaming operations are tested in integration tests.
"""

# Third-party imports
import pytest

# Local imports
from splurge_dsv.dsv_helper import DsvHelper
from splurge_dsv.exceptions import SplurgeDsvColumnMismatchError, SplurgeDsvParameterError


class TestDsvHelperParse:
    """Test the parse method."""

    def test_parse_basic_csv(self) -> None:
        """Test basic CSV parsing."""
        result = DsvHelper.parse("a,b,c", delimiter=",")
        assert result == ["a", "b", "c"]

    def test_parse_tsv(self) -> None:
        """Test TSV parsing."""
        result = DsvHelper.parse("a\tb\tc", delimiter="\t")
        assert result == ["a", "b", "c"]

    def test_parse_pipe_separated(self) -> None:
        """Test pipe-separated values."""
        result = DsvHelper.parse("a|b|c", delimiter="|")
        assert result == ["a", "b", "c"]

    def test_parse_semicolon_separated(self) -> None:
        """Test semicolon-separated values."""
        result = DsvHelper.parse("a;b;c", delimiter=";")
        assert result == ["a", "b", "c"]

    def test_parse_with_spaces(self) -> None:
        """Test parsing with spaces around delimiter."""
        result = DsvHelper.parse("a , b , c", delimiter=",")
        assert result == ["a", "b", "c"]

    def test_parse_without_strip(self) -> None:
        """Test parsing without stripping whitespace."""
        result = DsvHelper.parse("a , b , c", delimiter=",", strip=False)
        assert result == ["a ", " b ", " c"]

    def test_parse_with_empty_tokens(self) -> None:
        """Test parsing with empty tokens."""
        result = DsvHelper.parse("a,,c", delimiter=",")
        assert result == ["a", "", "c"]

    def test_parse_with_quoted_values(self) -> None:
        """Test parsing with quoted values."""
        result = DsvHelper.parse('"a","b","c"', delimiter=",", bookend='"')
        assert result == ["a", "b", "c"]

    def test_parse_with_quoted_values_no_strip(self) -> None:
        """Test parsing with quoted values without stripping."""
        result = DsvHelper.parse('"a","b","c"', delimiter=",", bookend='"', bookend_strip=False)
        assert result == ["a", "b", "c"]

    def test_parse_with_mixed_quoted_values(self) -> None:
        """Test parsing with mixed quoted and unquoted values."""
        result = DsvHelper.parse('a,"b",c', delimiter=",", bookend='"')
        assert result == ["a", "b", "c"]

    def test_parse_with_single_quotes(self) -> None:
        """Test parsing with single quotes."""
        result = DsvHelper.parse("'a','b','c'", delimiter=",", bookend="'")
        assert result == ["a", "b", "c"]

    def test_parse_with_brackets(self) -> None:
        """Test parsing with bracket bookends."""
        result = DsvHelper.parse("[a],[b],[c]", delimiter=",", bookend="[")
        assert result == ["[a]", "[b]", "[c]"]

        # Test with matching bracket bookends
        result = DsvHelper.parse("[a[,[b[,[c[", delimiter=",", bookend="[")
        assert result == ["a", "b", "c"]

    def test_parse_empty_string(self) -> None:
        """Test parsing empty string."""
        result = DsvHelper.parse("", delimiter=",")
        assert result == [""]

    def test_parse_empty_string_stripped(self) -> None:
        """Test parsing empty string with strip."""
        result = DsvHelper.parse("   ", delimiter=",", strip=True)
        assert result == [""]

    def test_parse_single_token(self) -> None:
        """Test parsing single token."""
        result = DsvHelper.parse("single", delimiter=",")
        assert result == ["single"]

    def test_parse_with_empty_delimiter_raises_error(self) -> None:
        """Test that empty delimiter raises error."""
        with pytest.raises(SplurgeDsvParameterError, match="delimiter cannot be empty or None"):
            DsvHelper.parse("a,b,c", delimiter="")

    def test_parse_with_none_delimiter_raises_error(self) -> None:
        """Test that None delimiter raises error."""
        with pytest.raises(SplurgeDsvParameterError, match="delimiter cannot be empty or None"):
            DsvHelper.parse("a,b,c", delimiter=None)


class TestDsvHelperParses:
    """Test the parses method."""

    def test_parses_multiple_lines(self) -> None:
        """Test parsing multiple lines."""
        content = ["a,b,c", "d,e,f", "g,h,i"]
        result = DsvHelper.parses(content, delimiter=",")
        expected = [["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]]
        assert result == expected

    def test_parses_with_spaces(self) -> None:
        """Test parsing multiple lines with spaces."""
        content = ["a , b , c", "d , e , f"]
        result = DsvHelper.parses(content, delimiter=",")
        expected = [["a", "b", "c"], ["d", "e", "f"]]
        assert result == expected

    def test_parses_without_strip(self) -> None:
        """Test parsing multiple lines without stripping."""
        content = ["a , b , c", "d , e , f"]
        result = DsvHelper.parses(content, delimiter=",", strip=False)
        expected = [["a ", " b ", " c"], ["d ", " e ", " f"]]
        assert result == expected

    def test_parses_with_quoted_values(self) -> None:
        """Test parsing multiple lines with quoted values."""
        content = ['"a","b","c"', '"d","e","f"']
        result = DsvHelper.parses(content, delimiter=",", bookend='"')
        expected = [["a", "b", "c"], ["d", "e", "f"]]
        assert result == expected

    def test_parses_empty_list(self) -> None:
        """Test parsing empty list."""
        result = DsvHelper.parses([], delimiter=",")
        assert result == []

    def test_parses_list_with_empty_strings(self) -> None:
        """Test parsing list with empty strings."""
        content = ["", "a,b", ""]
        result = DsvHelper.parses(content, delimiter=",")
        expected = [[""], ["a", "b"], [""]]
        assert result == expected

    def test_parses_with_different_delimiters(self) -> None:
        """Test parsing with different delimiters."""
        content = ["a|b|c", "d;e;f", "g\th\ti"]
        result_pipe = DsvHelper.parses(content, delimiter="|")
        result_semicolon = DsvHelper.parses(content, delimiter=";")
        result_tab = DsvHelper.parses(content, delimiter="\t")

        assert result_pipe == [["a", "b", "c"], ["d;e;f"], ["g\th\ti"]]
        assert result_semicolon == [["a|b|c"], ["d", "e", "f"], ["g\th\ti"]]
        assert result_tab == [["a|b|c"], ["d;e;f"], ["g", "h", "i"]]

    def test_parses_with_empty_delimiter_raises_error(self) -> None:
        """Test that empty delimiter raises error."""
        with pytest.raises(SplurgeDsvParameterError, match="delimiter cannot be empty or None"):
            DsvHelper.parses(["a,b,c"], delimiter="")

    def test_parses_with_none_delimiter_raises_error(self) -> None:
        """Test that None delimiter raises error."""
        with pytest.raises(SplurgeDsvParameterError, match="delimiter cannot be empty or None"):
            DsvHelper.parses(["a,b,c"], delimiter=None)

    def test_parses_with_non_string_content_raises_error(self) -> None:
        """Test that non-string content raises error."""
        with pytest.raises(SplurgeDsvParameterError, match="content must be a list of strings"):
            DsvHelper.parses(["a,b,c", 123], delimiter=",")

    def test_parses_with_non_list_content_raises_error(self) -> None:
        """Test that non-list content raises error."""
        with pytest.raises(SplurgeDsvParameterError, match="content must be a list"):
            DsvHelper.parses("a,b,c", delimiter=",")


# File parsing and streaming tests moved to integration tests


class TestDsvHelperEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_parse_with_unicode_content(self) -> None:
        """Test parsing with Unicode content."""
        result = DsvHelper.parse("α,β,γ", delimiter=",")
        assert result == ["α", "β", "γ"]

    def test_parse_with_unicode_delimiter(self) -> None:
        """Test parsing with Unicode delimiter."""
        result = DsvHelper.parse("a→b→c", delimiter="→")
        assert result == ["a", "b", "c"]

    def test_parse_with_newlines_in_content(self) -> None:
        """Test parsing with newlines in content."""
        result = DsvHelper.parse("a\n,b\n,c", delimiter=",", strip=False)
        assert result == ["a\n", "b\n", "c"]

    def test_parse_with_tabs_in_content(self) -> None:
        """Test parsing with tabs in content."""
        result = DsvHelper.parse("a\t,b\t,c", delimiter=",", strip=False)
        assert result == ["a\t", "b\t", "c"]

    def test_parse_normalize_padding_and_truncate(self) -> None:
        """Test normalize_columns pads and truncates correctly."""
        padded = DsvHelper.parse("a,b", delimiter=",", normalize_columns=3)
        assert padded == ["a", "b", ""]

        truncated = DsvHelper.parse("a,b,c,d", delimiter=",", normalize_columns=3)
        assert truncated == ["a", "b", "c"]

    def test_parse_validate_raises(self) -> None:
        """Test that validation flags raise parsing errors appropriately."""
        with pytest.raises(SplurgeDsvColumnMismatchError):
            DsvHelper.parse("a,b", delimiter=",", normalize_columns=3, raise_on_missing_columns=True)

        with pytest.raises(SplurgeDsvColumnMismatchError):
            DsvHelper.parse("a,b,c,d", delimiter=",", normalize_columns=3, raise_on_extra_columns=True)

    def test_parses_detect_columns_in_memory(self) -> None:
        """Test detects expected columns from first non-blank line in memory."""

    content = ["", "a,b,c", "d,e"]
    result = DsvHelper.parses(content, delimiter=",", detect_columns=True)
    # Leading blank line is preserved as [''] then subsequent rows are normalized
    assert result == [["", "", ""], ["a", "b", "c"], ["d", "e", ""]]

    # File system tests moved to integration tests
