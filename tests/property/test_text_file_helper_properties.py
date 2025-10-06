"""
Property-based tests for TextFileHelper class.

This module contains Hypothesis property tests for the TextFileHelper class,
verifying line counting accuracy, streaming consistency, encoding preservation,
and header/footer skipping properties.
"""

# Third-party imports
from hypothesis import given
from hypothesis import strategies as st

# Local imports
from splurge_dsv.text_file_helper import TextFileHelper


class TestTextFileHelperProperties:
    """Property-based tests for TextFileHelper class."""

    @given(
        st.lists(
            st.text(
                alphabet=st.characters(categories=["L", "N", "P", "Zs"], max_codepoint=127), min_size=1, max_size=50
            ),
            min_size=1,
            max_size=100,
        ),
        st.sampled_from(["utf-8", "utf-16", "latin-1"]),
    )
    def test_line_count_accuracy(self, lines: list[str], encoding: str) -> None:
        """Test that line counting matches actual content."""
        # Create content with explicit newlines
        content = "\n".join(lines) + "\n"  # Add trailing newline

        # Create temporary file
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", encoding=encoding, delete=False, suffix=".txt") as f:
            f.write(content)
            temp_path = f.name

        try:
            # Count lines using TextFileHelper
            counted_lines = TextFileHelper.line_count(temp_path, encoding=encoding)

            # Should match the number of lines we created
            expected_count = len(lines)
            assert counted_lines == expected_count

        finally:
            os.unlink(temp_path)

    @given(
        st.lists(
            st.text(
                alphabet=st.characters(categories=["L", "N", "P", "Zs"], max_codepoint=127), min_size=1, max_size=30
            ),
            min_size=1,
            max_size=50,
        ),
        st.sampled_from(["utf-8", "utf-16", "latin-1"]),
        st.integers(min_value=1, max_value=10),
        st.booleans(),
    )
    def test_preview_consistency(self, lines: list[str], encoding: str, max_lines: int, strip: bool) -> None:
        """Test that preview returns correct number of lines."""
        content = "\n".join(lines) + "\n"

        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", encoding=encoding, delete=False, suffix=".txt") as f:
            f.write(content)
            temp_path = f.name

        try:
            # Get preview
            preview_lines = TextFileHelper.preview(temp_path, max_lines=max_lines, encoding=encoding, strip=strip)

            # Should not exceed max_lines
            assert len(preview_lines) <= max_lines

            # Should not exceed total lines available
            assert len(preview_lines) <= len(lines)

            # If we have lines, should get at least 1 (unless max_lines is 0, but that's invalid)
            if lines and max_lines > 0:
                assert len(preview_lines) > 0

        finally:
            os.unlink(temp_path)

    @given(
        st.lists(
            st.text(
                alphabet=st.characters(categories=["L", "N", "P", "Zs"], max_codepoint=127), min_size=1, max_size=20
            ),
            min_size=5,
            max_size=30,
        ),
        st.sampled_from(["utf-8", "utf-16", "latin-1"]),
        st.integers(min_value=0, max_value=3),  # skip_header_rows
        st.integers(min_value=0, max_value=3),  # skip_footer_rows
        st.booleans(),  # strip
    )
    def test_read_skip_consistency(
        self, lines: list[str], encoding: str, skip_header: int, skip_footer: int, strip: bool
    ) -> None:
        """Test that header/footer skipping works correctly."""
        content = "\n".join(lines) + "\n"

        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", encoding=encoding, delete=False, suffix=".txt") as f:
            f.write(content)
            temp_path = f.name

        try:
            # Read with skipping
            result_lines = TextFileHelper.read(
                temp_path, encoding=encoding, skip_header_rows=skip_header, skip_footer_rows=skip_footer, strip=strip
            )

            total_lines = len(lines)
            expected_lines = max(0, total_lines - skip_header - skip_footer)

            # Should have correct number of lines after skipping
            assert len(result_lines) == expected_lines

            # If we have enough lines, the content should match expected slice
            if expected_lines > 0:
                expected_content = lines[skip_header : total_lines - skip_footer]
                if strip:
                    expected_content = [line.strip() for line in expected_content]

                # Compare the actual result with expected
                assert result_lines == expected_content

        finally:
            os.unlink(temp_path)

    @given(
        st.lists(
            st.text(
                alphabet=st.characters(categories=["L", "N", "P", "Zs"], max_codepoint=127), min_size=1, max_size=15
            ),
            min_size=10,
            max_size=40,
        ),
        st.sampled_from(["utf-8", "utf-16", "latin-1"]),
        st.booleans(),  # strip
    )
    def test_streaming_consistency(self, lines: list[str], encoding: str, strip: bool) -> None:
        """Test that streaming read matches full read."""
        content = "\n".join(lines) + "\n"

        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", encoding=encoding, delete=False, suffix=".txt") as f:
            f.write(content)
            temp_path = f.name

        try:
            # Get full read result
            full_read = TextFileHelper.read(temp_path, encoding=encoding, strip=strip)

            # Get streaming result with default chunk size
            stream_chunks = list(TextFileHelper.read_as_stream(temp_path, encoding=encoding, strip=strip))

            # Flatten stream chunks
            stream_read = []
            for chunk in stream_chunks:
                stream_read.extend(chunk)

            # Should match full read
            assert stream_read == full_read

            # Should have at least one chunk if we have data
            if full_read:
                assert len(stream_chunks) >= 1

        finally:
            os.unlink(temp_path)

    @given(
        st.lists(
            st.text(
                alphabet=st.characters(categories=["L", "N", "P", "Zs"], max_codepoint=127), min_size=1, max_size=20
            ),
            min_size=1,
            max_size=20,
        ),
        st.sampled_from(["utf-8", "utf-16", "latin-1"]),
    )
    def test_encoding_preservation(self, lines: list[str], encoding: str) -> None:
        """Test that content is preserved through encoding/decoding."""
        # Create content with various characters
        content = "\n".join(lines) + "\n"

        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", encoding=encoding, delete=False, suffix=".txt") as f:
            f.write(content)
            temp_path = f.name

        try:
            # Read back the content
            read_lines = TextFileHelper.read(temp_path, encoding=encoding, strip=False)

            # Should match original lines
            assert read_lines == lines

            # Test line count matches
            line_count = TextFileHelper.line_count(temp_path, encoding=encoding)
            assert line_count == len(lines)

        finally:
            os.unlink(temp_path)

    @given(
        st.integers(min_value=1, max_value=100),  # max_lines
        st.lists(
            st.text(
                alphabet=st.characters(categories=["L", "N", "P", "Zs"], max_codepoint=127), min_size=1, max_size=10
            ),
            min_size=1,
            max_size=20,
        ),
    )
    def test_preview_bounds(self, max_lines: int, lines: list[str]) -> None:
        """Test that preview respects max_lines bounds."""
        content = "\n".join(lines) + "\n"

        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, suffix=".txt") as f:
            f.write(content)
            temp_path = f.name

        try:
            # Preview should never return more than max_lines
            preview_lines = TextFileHelper.preview(temp_path, max_lines=max_lines)
            assert len(preview_lines) <= max_lines

            # Should not exceed available lines
            assert len(preview_lines) <= len(lines)

        finally:
            os.unlink(temp_path)
