"""
Property-based tests for string_tokenizer module using Hypothesis.

This module contains property-based tests to verify invariants and edge cases
for the StringTokenizer class methods.
"""

# Standard library imports
import pytest

# Third-party imports
from hypothesis import given
from hypothesis import strategies as st

# Local imports
from splurge_dsv.string_tokenizer import StringTokenizer


class TestStringTokenizerProperties:
    """Property-based tests for StringTokenizer class."""

    @given(content=st.text(), delimiter=st.sampled_from([",", ";", "|", "\t", ":", "#"]), strip=st.booleans())
    def test_parse_round_trip_property(self, content: str, delimiter: str, strip: bool) -> None:
        """Test that parsing and re-joining preserves the original content structure."""
        # Skip if delimiter appears in content in a way that would break round-trip
        if delimiter in content:
            # For round-trip to work, we need to ensure no empty tokens are created
            # when strip is True and content has leading/trailing whitespace
            if strip and (content.startswith(delimiter) or content.endswith(delimiter)):
                pytest.skip("Delimiter at boundaries with strip would create empty tokens")

            # Re-join should give us back something equivalent
            tokens = StringTokenizer.parse(content, delimiter=delimiter, strip=strip)
            rejoined = delimiter.join(tokens)

            if strip:
                # With strip, we expect normalized content
                assert rejoined == content.strip()
            else:
                # Without strip, exact round-trip
                assert rejoined == content
        else:
            # No delimiter in content - should return single token
            tokens = StringTokenizer.parse(content, delimiter=delimiter, strip=strip)
            if strip and content.strip() == "":
                assert tokens == []
            else:
                expected = [content.strip()] if strip else [content]
                assert tokens == expected

    @given(content=st.text(), delimiter=st.sampled_from([",", ";", "|", "\t", ":", "#"]), strip=st.booleans())
    def test_parse_unicode_preservation(self, content: str, delimiter: str, strip: bool) -> None:
        """Test that Unicode characters are preserved through parsing."""
        tokens = StringTokenizer.parse(content, delimiter=delimiter, strip=strip)

        # All tokens should be strings
        assert all(isinstance(token, str) for token in tokens)

        # If no delimiter in content, should be single token
        if delimiter not in content:
            if strip and not content.strip():
                assert tokens == []
            else:
                expected = [content.strip()] if strip else [content]
                assert tokens == expected

    @given(
        contents=st.lists(st.text(), min_size=1, max_size=10),
        delimiter=st.sampled_from([",", ";", "|", "\t", ":", "#"]),
        strip=st.booleans(),
    )
    def test_parses_consistency_with_parse(self, contents: list[str], delimiter: str, strip: bool) -> None:
        """Test that parses() is consistent with calling parse() on each item."""
        result_parses = StringTokenizer.parses(contents, delimiter=delimiter, strip=strip)
        result_individual = [StringTokenizer.parse(content, delimiter=delimiter, strip=strip) for content in contents]

        assert result_parses == result_individual

    @given(content=st.text(), bookend=st.sampled_from(['"', "'", "`"]), strip=st.booleans())
    def test_remove_bookends_symmetry(self, content: str, bookend: str, strip: bool) -> None:
        """Test that remove_bookends is symmetric for properly formed bookends."""
        # Create content with bookends
        if content:
            bookended = f"{bookend}{content}{bookend}"
            result = StringTokenizer.remove_bookends(bookended, bookend=bookend, strip=strip)

            # The method strips first if strip=True, then removes bookends if present
            expected = content
            if strip:
                # Strip the bookended content first, then remove bookends
                stripped_bookended = bookended.strip()
                if stripped_bookended.startswith(bookend) and stripped_bookended.endswith(bookend):
                    expected = stripped_bookended[len(bookend) : -len(bookend)]
                else:
                    expected = stripped_bookended
            else:
                # Just remove bookends if present
                if bookended.startswith(bookend) and bookended.endswith(bookend):
                    expected = bookended[len(bookend) : -len(bookend)]

            assert result == expected
        else:
            # Empty content
            bookended = f"{bookend}{bookend}"
            result = StringTokenizer.remove_bookends(bookended, bookend=bookend, strip=strip)
            assert result == ""

    @given(content=st.text(min_size=1), bookend=st.sampled_from(['"', "'", "`"]), strip=st.booleans())
    def test_remove_bookends_no_change_when_not_bookended(self, content: str, bookend: str, strip: bool) -> None:
        """Test that remove_bookends doesn't change content that doesn't have bookends."""
        # Content that doesn't start and end with bookend
        if not (content.startswith(bookend) and content.endswith(bookend)):
            result = StringTokenizer.remove_bookends(content, bookend=bookend, strip=strip)
            if strip:
                assert result == content.strip()
            else:
                assert result == content

    @given(content=st.text(), delimiter=st.sampled_from([",", ";", "|", "\t", ":", "#"]), strip=st.booleans())
    def test_parse_empty_content_handling(self, content: str, delimiter: str, strip: bool) -> None:
        """Test handling of empty and whitespace-only content."""
        if not content.strip():
            tokens = StringTokenizer.parse(content, delimiter=delimiter, strip=strip)
            if strip:
                assert tokens == []
            else:
                # Without strip, split the content as-is
                expected = content.split(delimiter)
                assert tokens == expected

    @given(content=st.text(min_size=1), delimiter=st.sampled_from([",", ";", "|", "\t", ":", "#"]), strip=st.booleans())
    def test_parse_single_token_preservation(self, content: str, delimiter: str, strip: bool) -> None:
        """Test that content without delimiter is preserved as single token."""
        if delimiter not in content:
            tokens = StringTokenizer.parse(content, delimiter=delimiter, strip=strip)
            if strip and not content.strip():
                assert tokens == []
            else:
                expected = [content.strip()] if strip else [content]
                assert tokens == expected

    @given(delimiter=st.sampled_from([",", ";", "|", "\t", ":", "#"]), strip=st.booleans())
    def test_parse_empty_string_with_strip(self, delimiter: str, strip: bool) -> None:
        """Test parsing empty string."""
        tokens = StringTokenizer.parse("", delimiter=delimiter, strip=strip)
        if strip:
            assert tokens == []
        else:
            # Empty string split returns single empty token
            assert tokens == [""]

    @given(delimiter=st.sampled_from([",", ";", "|", "\t", ":", "#"]), strip=st.booleans())
    def test_parse_whitespace_only_with_strip(self, delimiter: str, strip: bool) -> None:
        """Test parsing whitespace-only string."""
        tokens = StringTokenizer.parse("   ", delimiter=delimiter, strip=strip)
        if strip:
            assert tokens == []
        else:
            assert tokens == ["   "]

    @given(bookend=st.sampled_from(['"', "'", "`"]), strip=st.booleans())
    def test_remove_bookends_empty_content(self, bookend: str, strip: bool) -> None:
        """Test remove_bookends with empty content."""
        result = StringTokenizer.remove_bookends("", bookend=bookend, strip=strip)
        assert result == ""

    @given(content=st.text(), bookend=st.sampled_from(['"', "'", "`"]), strip=st.booleans())
    def test_remove_bookends_minimum_length(self, content: str, bookend: str, strip: bool) -> None:
        """Test remove_bookends with minimum length requirements."""
        # The method removes bookends if: value.startswith(bookend) and value.endswith(bookend)
        # and len(value) > 2 * len(bookend) - 1
        bookended = f"{bookend}{content}{bookend}"
        result = StringTokenizer.remove_bookends(bookended, bookend=bookend, strip=strip)

        # Determine what the method should do
        value = bookended.strip() if strip else bookended
        should_remove = value.startswith(bookend) and value.endswith(bookend) and len(value) > 2 * len(bookend) - 1

        if should_remove:
            expected = value[len(bookend) : -len(bookend)]
        else:
            expected = value

        assert result == expected
