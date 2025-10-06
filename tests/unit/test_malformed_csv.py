"""
Unit tests for malformed CSV structure edge cases.

This module tests how the DSV parsing handles various malformed CSV structures
including unclosed quotes, mixed quote types, nested quotes, and other edge cases.
"""

# Local imports
from splurge_dsv.dsv_helper import DsvHelper


class TestMalformedCsvStructures:
    """Test malformed CSV structure edge cases."""

    def test_unclosed_quotes_basic(self) -> None:
        """Test parsing with unclosed quotes."""
        # Basic unclosed quote - should still parse but incorrectly
        content = '"field1,"field2,field3'
        result = DsvHelper.parse(content, delimiter=",", bookend='"')

        # This will split on comma inside the quote, which is incorrect CSV behavior
        # But our current implementation doesn't handle quoted delimiters specially
        assert len(result) == 3  # "field1,  "field2  ,  field3

    def test_unclosed_quotes_at_end(self) -> None:
        """Test parsing with unclosed quote at end of string."""
        content = 'field1,field2,"field3'
        result = DsvHelper.parse(content, delimiter=",", bookend='"')

        # Should parse as 3 fields, with the last one not having its quote removed
        assert len(result) == 3
        assert result[2] == '"field3'  # Quote not removed due to unclosed

    def test_mixed_quote_types(self) -> None:
        """Test parsing with mixed quote types."""
        content = "'field1',\"field2\",field3"
        result = DsvHelper.parse(content, delimiter=",", bookend='"')

        # With " as bookend, only the double quotes should be removed
        assert len(result) == 3
        assert result[0] == "'field1'"  # Single quotes not removed
        assert result[1] == "field2"  # Double quotes removed
        assert result[2] == "field3"  # No quotes

    def test_nested_quotes(self) -> None:
        """Test parsing with nested quotes inside fields."""
        content = '"field with "nested" quotes",field2,field3'
        result = DsvHelper.parse(content, delimiter=",", bookend='"')

        # This will incorrectly split on the comma inside the nested quotes
        # Our parser doesn't handle escaped quotes or nested quotes
        assert len(result) >= 3  # Will be more than 3 due to incorrect splitting

    def test_escaped_quotes_backslash(self) -> None:
        """Test parsing with backslash-escaped quotes."""
        content = 'field1,"field with \\"escaped\\" quotes",field3'
        result = DsvHelper.parse(content, delimiter=",", bookend='"')

        # Our parser doesn't handle backslash escaping, so this will work as-is
        assert len(result) == 3
        assert result[1] == 'field with \\"escaped\\" quotes'  # Quotes removed but content preserved

    def test_quote_at_eof(self) -> None:
        """Test parsing file ending with unclosed quote."""
        content = 'field1,field2,"field3'
        result = DsvHelper.parse(content, delimiter=",", bookend='"')

        assert len(result) == 3
        assert result[2] == '"field3'  # Unclosed quote preserved

    def test_multiple_unclosed_quotes(self) -> None:
        """Test parsing with multiple unclosed quotes."""
        content = '"field1,"field2,"field3'
        result = DsvHelper.parse(content, delimiter=",", bookend='"')

        # Each unclosed quote will cause splitting issues
        assert len(result) >= 3

    def test_quotes_with_delimiters_inside(self) -> None:
        """Test quotes containing delimiters."""
        content = '"field,1","field,2",field3'
        result = DsvHelper.parse(content, delimiter=",", bookend='"')

        # Our parser splits first, then removes quotes, so this won't work correctly
        # The commas inside quotes will cause incorrect splitting
        assert len(result) >= 3  # Will be split incorrectly

    def test_empty_quoted_fields(self) -> None:
        """Test empty fields with quotes."""
        content = '"","field2",""'
        result = DsvHelper.parse(content, delimiter=",", bookend='"')

        assert len(result) == 3
        assert result[0] == ""  # Empty quoted field
        assert result[1] == "field2"
        assert result[2] == ""  # Empty quoted field

    def test_quotes_with_only_whitespace(self) -> None:
        """Test quoted fields containing only whitespace."""
        content = '" ","field2","   "'
        result = DsvHelper.parse(content, delimiter=",", bookend='"')

        assert len(result) == 3
        assert result[0] == " "  # Single space preserved
        assert result[1] == "field2"
        assert result[2] == "   "  # Multiple spaces preserved

    def test_mismatched_quote_lengths(self) -> None:
        """Test quotes of different lengths."""
        content = '"""field1""","field2"'
        result = DsvHelper.parse(content, delimiter=",", bookend='"')

        # With single quote bookend, this won't match properly
        assert len(result) == 2
        assert result[0] == '""field1""'  # One quote removed from each end
        assert result[1] == "field2"

    def test_quotes_with_newlines(self) -> None:
        """Test quoted fields containing newlines."""
        # Note: This tests single-line parsing, not multi-line CSV
        content = '"field\n1","field\n2"'
        result = DsvHelper.parse(content, delimiter=",", bookend='"')

        assert len(result) == 2
        assert result[0] == "field\n1"  # Newlines preserved
        assert result[1] == "field\n2"

    def test_delimiter_as_quote(self) -> None:
        """Test using delimiter character as quote."""
        content = ",field1,,field2,"
        result = DsvHelper.parse(content, delimiter=",", bookend=",")

        # Using comma as both delimiter and bookend is problematic
        assert len(result) >= 3
