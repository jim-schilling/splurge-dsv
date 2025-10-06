"""
Property-based tests for dsv_helper module using Hypothesis.

This module contains property-based tests to verify invariants and edge cases
for the DsvHelper class methods.
"""

# Standard library imports
import tempfile
from pathlib import Path

# Third-party imports
import pytest
from hypothesis import given
from hypothesis import strategies as st

# Local imports
from splurge_dsv.dsv_helper import DsvHelper


class TestDsvHelperProperties:
    """Property-based tests for DsvHelper class."""

    @given(content=st.text(min_size=1), delimiter=st.sampled_from([",", ";", "|", "\t", ":", "#"]), strip=st.booleans())
    def test_parse_preserves_token_count(self, content: str, delimiter: str, strip: bool) -> None:
        """Test that parsing preserves the number of tokens (except for empty tokens when stripped)."""
        # Skip if this would create problematic edge cases
        if delimiter in content and (content.startswith(delimiter) or content.endswith(delimiter)):
            if strip:
                pytest.skip("Edge case with delimiters at boundaries and strip")

        result = DsvHelper.parse(content, delimiter=delimiter, strip=strip)

        # If content is empty/whitespace and strip=True, result should be empty
        if strip and not content.strip():
            assert result == []
            return

        if delimiter not in content:
            # No delimiter means single token (unless content is empty after stripping)
            if strip and not content.strip():
                assert result == []
            else:
                assert len(result) == 1
        else:
            # With delimiter, check token count is reasonable
            raw_tokens = content.split(delimiter)
            if strip:
                # Stripping might remove empty tokens
                expected_min = sum(1 for token in raw_tokens if token.strip())
                assert len(result) >= expected_min
            else:
                assert len(result) == len(raw_tokens)

    @given(
        content=st.lists(
            st.lists(
                st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=32, max_codepoint=126)),
                min_size=1,
                max_size=5,
            ),
            min_size=1,
            max_size=5,
        ),
        delimiter=st.sampled_from([",", ";", "|", "\t", ":", "#"]),
    )
    def test_parse_file_round_trip(self, content: list[list[str]], delimiter: str) -> None:
        """Test that writing content to file and parsing it back works correctly."""
        # Skip if any cell contains the delimiter (would break round-trip)
        for row in content:
            for cell in row:
                if delimiter in cell:
                    pytest.skip("Content contains delimiter - would break round-trip")

        # Create CSV-like content
        csv_lines = [delimiter.join(row) for row in content]
        csv_content = "\n".join(csv_lines)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            result = DsvHelper.parse_file(temp_path, delimiter=delimiter)

            # Should have same structure
            assert len(result) == len(content)
            for i, row in enumerate(result):
                assert len(row) == len(content[i])

        finally:
            Path(temp_path).unlink(missing_ok=True)
