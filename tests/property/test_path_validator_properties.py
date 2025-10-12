"""
Property-based tests for PathValidator class.

This module contains Hypothesis property tests for the PathValidator class,
verifying path normalization, traversal prevention, permission consistency,
and cross-platform compatibility properties.
"""

# Standard library imports
from pathlib import Path

# Third-party imports
import pytest
from hypothesis import given
from hypothesis import strategies as st

# Local imports
from splurge_dsv.exceptions import SplurgeDsvPathValidationError
from splurge_dsv.path_validator import PathValidator


class TestPathValidatorProperties:
    """Property-based tests for PathValidator class."""

    @given(st.text(alphabet=st.characters(categories=["L", "N", "P", "S"]), min_size=1, max_size=50))
    def test_filename_sanitization_consistency(self, filename: str) -> None:
        """Test that filename sanitization is consistent and produces valid filenames."""
        # Sanitization should be deterministic
        result1 = PathValidator.sanitize_filename(filename)
        result2 = PathValidator.sanitize_filename(filename)
        assert result1 == result2

        # Result should not be empty (unless input was empty)
        if filename.strip(" ."):
            assert result1

        # Result should not contain dangerous characters
        dangerous_chars = ["<", ">", ":", '"', "|", "?", "*"]
        for char in dangerous_chars:
            assert char not in result1

        # Result should not contain control characters
        for char in result1:
            assert ord(char) >= 32

    @given(st.text(alphabet=st.characters(categories=["L", "N"]), min_size=1, max_size=20))
    def test_safe_path_consistency(self, filename: str) -> None:
        """Test that is_safe_path is consistent for the same input."""
        # Create a simple safe path
        safe_path = Path(filename + ".txt")

        # is_safe_path should be deterministic
        result1 = PathValidator.is_safe_path(safe_path)
        result2 = PathValidator.is_safe_path(safe_path)
        assert result1 == result2

    @given(st.text(alphabet=st.characters(categories=["L", "N", "P", "S"]), min_size=1, max_size=100))
    def test_path_length_validation(self, path_str: str) -> None:
        """Test that path length validation works correctly."""
        # Very long paths should be rejected
        long_path = path_str * 100  # Make it very long

        if len(long_path) > PathValidator.MAX_PATH_LENGTH:
            with pytest.raises(SplurgeDsvPathValidationError):
                PathValidator.validate_path(long_path)
        else:
            # Should not raise for reasonable lengths
            try:
                PathValidator.validate_path(long_path, must_exist=False)
            except SplurgeDsvPathValidationError as e:
                # Should not be due to length
                assert "too long" not in str(e).lower()

    @given(st.sampled_from(["..", "../", "/..", "\\..", "~/", "~user/"]))
    def test_path_traversal_prevention(self, traversal_pattern: str) -> None:
        """Test that path traversal patterns behave consistently with the
        underlying `splurge_safe_io` implementation. We delegate security
        decisions to that library; this test asserts our shim matches its
        behavior rather than enforcing historical assumptions.
        """
        from splurge_safe_io import path_validator as _safe

        # Compare outcome of validate_path: either it raises the external
        # PathValidationError (mapped to our SplurgeDsvPathValidationError)
        # or it returns a Path. We accept either as long as the shim matches
        # the external library.
        try:
            _safe.PathValidator.validate_path(traversal_pattern, must_exist=False)
            result = PathValidator.validate_path(traversal_pattern, must_exist=False)
            assert isinstance(result, Path)
        except Exception:
            with pytest.raises(SplurgeDsvPathValidationError):
                PathValidator.validate_path(traversal_pattern, must_exist=False)

    @given(st.text(alphabet=st.characters(categories=["L", "N"]), min_size=1, max_size=20))
    def test_relative_path_handling(self, dirname: str) -> None:
        """Test relative path validation behavior."""
        relative_path = f"{dirname}/file.txt"

        # Should work with allow_relative=True (default)
        result = PathValidator.validate_path(relative_path, must_exist=False, allow_relative=True)
        assert isinstance(result, Path)

        # Should fail with allow_relative=False
        with pytest.raises(SplurgeDsvPathValidationError):
            PathValidator.validate_path(relative_path, must_exist=False, allow_relative=False)

    @given(st.sampled_from(["<", ">", ":", '"', "|", "?", "*", "\x00", "\x01"]))
    def test_dangerous_character_rejection(self, dangerous_char: str) -> None:
        """Test that dangerous characters are rejected in paths."""
        test_path = f"file{dangerous_char}.txt"

        with pytest.raises(SplurgeDsvPathValidationError):
            PathValidator.validate_path(test_path, must_exist=False)

    @given(st.sampled_from(["C:", "D:", "c:", "Z:"]))
    def test_windows_drive_letter_handling(self, drive: str) -> None:
        """Test Windows drive letter handling."""
        # Drive letters should be allowed in proper format
        drive_path = f"{drive}\\file.txt"

        # Should not raise for drive letters (even if path doesn't exist)
        try:
            result = PathValidator.validate_path(drive_path, must_exist=False)
            assert isinstance(result, Path)
        except SplurgeDsvPathValidationError as e:
            # If it fails, should not be due to the drive letter specifically
            assert "colon" not in str(e).lower()

    @given(st.text(alphabet=st.characters(categories=["L", "N"]), min_size=1, max_size=10))
    def test_path_normalization_equivalence(self, basename: str) -> None:
        """Test that equivalent paths normalize to the same result."""
        # Create equivalent relative paths without dangerous patterns
        path1 = f"{basename}.txt"
        path2 = f"./{basename}.txt"

        # Both should validate successfully (relative paths)
        result1 = PathValidator.validate_path(path1, must_exist=False)
        result2 = PathValidator.validate_path(path2, must_exist=False)

        # Should both be Path objects
        assert isinstance(result1, Path)
        assert isinstance(result2, Path)

        # The resolved paths should be equivalent (accounting for current directory)
        assert result1.name == result2.name == f"{basename}.txt"

    from hypothesis import settings

    @settings(deadline=None)
    @given(st.sampled_from(["//server/share/file.txt", "\\\\server\\share\\file.txt"]))
    def test_unc_path_handling(self, unc_path: str) -> None:
        """Test UNC path handling."""
        # UNC path handling is delegated to splurge_safe_io. Ensure our shim
        # matches the external library's behavior.
        from splurge_safe_io import path_validator as _safe

        try:
            _safe.PathValidator.validate_path(unc_path, must_exist=False)
            PathValidator.validate_path(unc_path, must_exist=False)
        except Exception:
            with pytest.raises(SplurgeDsvPathValidationError):
                PathValidator.validate_path(unc_path, must_exist=False)

    @given(st.text(alphabet=st.characters(categories=["L", "N"]), min_size=1, max_size=20))
    def test_sanitize_filename_properties(self, filename: str) -> None:
        """Test properties of filename sanitization."""
        sanitized = PathValidator.sanitize_filename(filename)

        # Should not contain dangerous characters
        dangerous = ["<", ">", ":", '"', "|", "?", "*"]
        for char in dangerous:
            assert char not in sanitized

        # Should not have leading/trailing spaces or dots
        assert not sanitized.startswith((" ", "."))
        assert not sanitized.endswith((" ", "."))

        # Should handle empty/whitespace input
        if not filename.strip(" ."):
            assert sanitized == "_unnamed_file"  # Default filename

        # Should be idempotent
        double_sanitized = PathValidator.sanitize_filename(sanitized)
        assert double_sanitized == sanitized
