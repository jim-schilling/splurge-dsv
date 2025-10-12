"""Compatibility shim delegating to splurge_safe_io.path_validator.

This module preserves the public API of `splurge_dsv.path_validator` while
delegating implementation to the external `splurge_safe_io` package. The
shim deliberately remains small so it can be removed once callers migrate
to `splurge_safe_io` directly.
"""

from __future__ import annotations

from pathlib import Path

from splurge_safe_io import path_validator as _safe

from splurge_dsv import exceptions as _sd_ex

# Primary wrapper delegating to external implementation but mapping
# exception classes to splurge_dsv equivalents so callers receive the
# original exception types.


class PathValidator:
    """Wrapper around splurge_safe_io.PathValidator that preserves public API.

    Methods delegate to the external implementation and translate exceptions
    to splurge_dsv exception classes where appropriate.
    """

    @classmethod
    def validate_path(
        cls,
        file_path: str | Path,
        *,
        must_exist: bool = False,
        must_be_file: bool = False,
        must_be_readable: bool = False,
        allow_relative: bool = True,
        base_directory: str | Path | None = None,
    ) -> Path:
        # Delegate validation entirely to splurge_safe_io.PathValidator.
        # We no longer perform additional ad-hoc pre-checks here so the
        # external library is the authoritative source of truth for path
        # validation rules and security checks.

        try:
            return _safe.PathValidator.validate_path(
                file_path,
                must_exist=must_exist,
                must_be_file=must_be_file,
                must_be_readable=must_be_readable,
                allow_relative=allow_relative,
                base_directory=base_directory,
            )
        except _safe.SplurgeSafeIoFileNotFoundError as e:
            raise _sd_ex.SplurgeDsvFileNotFoundError(str(e)) from e
        except _safe.SplurgeSafeIoFilePermissionError as e:
            raise _sd_ex.SplurgeDsvFilePermissionError(str(e)) from e
        except _safe.SplurgeSafeIoPathValidationError as e:
            raise _sd_ex.SplurgeDsvPathValidationError(str(e)) from e

    @classmethod
    def is_safe_path(cls, file_path: str | Path) -> bool:
        """Delegate safety checks entirely to splurge_safe_io.

        The legacy project included additional ad-hoc checks here (tilde,
        UNC slashes, parent-directory segments). Those legacy checks are
        intentionally removed: `splurge_safe_io` is the authoritative
        implementation for path safety. This shim simply forwards the call
        and returns the external implementation's result (or False on
        unexpected errors).
        """
        try:
            return _safe.PathValidator.is_safe_path(file_path)
        except Exception:
            return False

    # Expose any attributes from the external class that callers might expect.
    MAX_PATH_LENGTH = getattr(_safe.PathValidator, "MAX_PATH_LENGTH", None)

    @classmethod
    def sanitize_filename(cls, name: str, default: str = "unnamed_file") -> str:
        """Sanitize filename using the external implementation.

        Kept as a classmethod for backward compatibility with callers that
        reference `PathValidator.sanitize_filename`.
        """
        # Call external implementation using positional argument to avoid
        # signature mismatches between versions of splurge_safe_io.
        return _safe.PathValidator.sanitize_filename(name)


# Map external exception classes to the splurge-dsv names so existing code
# that imports and checks for splurge_dsv exceptions keeps working.


class SplurgeDsvPathValidationError(_sd_ex.SplurgeDsvPathValidationError):
    """Compatibility wrapper for path validation errors."""


class SplurgeDsvFileNotFoundError(_sd_ex.SplurgeDsvFileNotFoundError):
    pass


class SplurgeDsvFilePermissionError(_sd_ex.SplurgeDsvFilePermissionError):
    pass


# Convenience re-exports for functions that callers may import directly.
_external_validate = _safe.PathValidator.validate_path
_external_is_safe = _safe.PathValidator.is_safe_path

# Module-level convenience alias for callers who import the function
# directly as `from splurge_dsv.path_validator import sanitize_filename`.
sanitize_filename = PathValidator.sanitize_filename


def validate_path(
    file_path: str | Path,
    *,
    must_exist: bool = False,
    must_be_file: bool = False,
    must_be_readable: bool = False,
    allow_relative: bool = True,
    base_directory: str | Path | None = None,
) -> Path:
    """Wrapper around splurge_safe_io.PathValidator.validate_path that maps
    external exceptions to splurge_dsv exception types.
    """
    try:
        return _external_validate(
            file_path,
            must_exist=must_exist,
            must_be_file=must_be_file,
            must_be_readable=must_be_readable,
            allow_relative=allow_relative,
            base_directory=base_directory,
        )
    except _safe.SplurgeSafeIoFileNotFoundError as e:
        raise _sd_ex.SplurgeDsvFileNotFoundError(str(e)) from e
    except _safe.SplurgeSafeIoFilePermissionError as e:
        raise _sd_ex.SplurgeDsvFilePermissionError(str(e)) from e
    except _safe.SplurgeSafeIoPathValidationError as e:
        raise _sd_ex.SplurgeDsvPathValidationError(str(e)) from e


def is_safe_path(file_path: str | Path) -> bool:
    try:
        return _external_is_safe(file_path)
    except Exception:
        # External implementation returns boolean or raises specialized errors;
        # on unexpected errors, return False to preserve legacy behavior.
        return False
