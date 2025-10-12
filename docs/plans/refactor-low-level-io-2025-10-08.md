# Refactor: Replace low-level IO modules with splurge-safe-io

This checklist documents the migration of splurge-dsv's low-level IO modules to the external package `splurge_safe_io`. The goals:

- Replace internal low-level IO implementations in `splurge_dsv` with `splurge_safe_io` equivalents.
- Keep high-level public APIs and behavior of `splurge-dsv` unchanged.
- Remove tests that verify internal implementation details (old low-level modules).
- Update project metadata, CI, and docs.

Notes:
- Assumes `splurge-safe-io` is installed in the project's virtualenv during development and CI.
- This plan intentionally keeps a compatibility shim layer in `splurge_dsv` (small adapters or re-exports) so external callers continue to import from `splurge_dsv` without change.

## Contract (what this migration changes/doesn't)

- Inputs: calls to `splurge_dsv.path_validator.*`, `splurge_dsv.safe_text_file_reader.*`, `splurge_dsv.safe_text_file_writer.*` from internal code and tests and from external users.
- Outputs: the same functions/classes but implemented by `splurge_safe_io`.
- Error modes: preserve raised exception types and messages *where reasonable*; map any new exception classes to the old public ones if those were part of the public API.
- Success criteria: all unit and integration tests that validate public behavior pass; tests that validated the old low-level modules are removed.

## Edge cases to consider

- Code or tests relied on private helper functions inside the old low-level modules.
- Subtle differences in exception classes or messages.
- Differences in path normalization/expansion behavior across platforms.
- Differences in file encoding defaults or newline handling.
- Tests that used monkeypatch to patch internal modules may need updating.

## Checklist

### 1) Discovery and mapping (manual)
- [x] Inventory current low-level modules and the public symbols they expose:
  - `splurge_dsv.path_validator` (functions/classes used by splurge-dsv)
  - `splurge_dsv.safe_text_file_reader`
  - `splurge_dsv.safe_text_file_writer`
- [x] Map each public symbol to the corresponding symbol in `splurge_safe_io`.
- [x] Note any API mismatches or gaps that require adapters.

### 2) Create compatibility shims in `splurge_dsv`
- [ ] Add minimal shim modules that import and re-export or wrap `splurge_safe_io` APIs. Prefer thin wrappers that preserve previous signatures and docstrings.
  - `splurge_dsv/path_validator.py` -> re-export from `splurge_safe_io.path_validator` or wrap when API differs.
  - `splurge_dsv/safe_text_file_reader.py` -> re-export or wrap `splurge_safe_io.safe_text_file_reader`.
  - `splurge_dsv/safe_text_file_writer.py` -> re-export or wrap `splurge_safe_io.safe_text_file_writer`.
- [ ] Ensure shims preserve public names, signatures, and docstrings.
- [ ] If `splurge_dsv` previously defined public exception classes used externally, create adapter exceptions (thin subclasses) that wrap `splurge_safe_io` exceptions while preserving identity.

### 3) Update internal imports
- [ ] Replace internal imports across the codebase to use the shim modules (`splurge_dsv.path_validator`, etc.), not directly `splurge_safe_io`.
- [ ] Run project-wide import search to ensure no code still imports the old internal helper functions that were private.

### 4) Tests: removal and update
- [ ] Identify tests that assert implementation details of the old low-level modules.
  - Files to remove: tests that directly import and test `splurge_dsv.path_validator`, `safe_text_file_reader`, `safe_text_file_writer` implementation details.
- [ ] Remove or replace those tests with higher-level tests that assert public behavior only.
  - For example, if a low-level test validated that a path expansion helper returns a specific normalized string, replace with a test that ensures the high-level function that uses it behaves correctly on edge cases.
- [ ] Update fixtures and conftest if they referenced low-level internal helpers.
- [ ] Add a small adapter test ensuring the shim re-exports the expected symbols from `splurge_safe_io` (smoke test).

### 5) CI and packaging
- [ ] Update `pyproject.toml` to include `splurge-safe-io` as a dependency (or optional extra) with an appropriate version specifier.
- [ ] Update CI workflows to install `splurge-safe-io` in virtualenv before running tests.

### 6) Lint, types, and static checks
- [ ] Run `ruff` and `mypy` (or equivalent) across the codebase.
- [ ] Fix any type errors introduced by the new adapter layer (prefer type annotations and `# type: ignore` sparingly).

### 7) Quality gates and verification
- [ ] Run full test suite (unit, integration, e2e where applicable) and fix regressions.
- [ ] Run ruff and fix style issues.
- [ ] Run coverage report; ensure coverage for public APIs remains acceptable.

### 8) Docs and changelog
- [ ] Update `CHANGELOG.md` with an entry describing the migration and the minimal impact on users.
- [ ] Update `docs/README-details.md` or other docs to list `splurge-safe-io` as a dependency and note compatibility.
- [ ] Add this migration plan file to `docs/plans/` (this file).

### 9) Release and follow-ups
- [ ] Create a feature branch and open a PR referencing this plan.
- [ ] Request code review; address feedback.
- [ ] Merge when CI passes and cut a patch release.
- [ ] Monitor user reports for issues related to IO differences.

## Implementation notes and examples

- Example shim (recommended pattern):

```py
# splurge_dsv/path_validator.py
"""Compatibility shim that forwards to splurge_safe_io.path_validator.

This module preserves the public API while delegating implementation to
`splurge_safe_io`. Keep this module small to make future removal trivial.
"""
from __future__ import annotations

from splurge_safe_io import path_validator as _safe

# Re-export names
is_safe_path = _safe.is_safe_path
validate_path = _safe.validate_path

# If splurge-dsv historically provided an exception class:
# class PathValidationError(Exception):
#     pass
#
# Wrap the external exception if preserving the type is required.
```

- For APIs with signature differences, write thin wrappers that translate arguments and re-map exceptions.

## Acceptance criteria
- All public APIs in `splurge-dsv` behave as before (no visible changes to callers).
- Tests that validated internal implementation removed; high-level tests remain and pass.
- CI installs `splurge-safe-io` and test runs pass.

## Risks and mitigation
- Risk: `splurge_safe_io` changes behave differently on edge cases.
  - Mitigation: add adapter tests for those edge cases and pin a version in pyproject.
- Risk: consumers depended on private implementation details.
  - Mitigation: document the change and provide migration guidance.

### Notable behavior change (path validation)

- `PathValidator.validate_path` now delegates entirely to `splurge_safe_io.PathValidator`.
- We intentionally removed internal ad-hoc pre-checks (tilde, UNC leading slashes,
  parent-directory segments) so behavior is determined by `splurge_safe_io`.
- Tests in this repository were updated to assert delegation (compare results
  against `splurge_safe_io`) instead of enforcing legacy assumptions about
  which inputs must be rejected.

If downstream users relied on the previous ad-hoc rejections, document this in
the changelog and provide migration guidance (e.g., wrap calls with an
additional pre-check if they need the previous stricter behavior).

## Rollback plan
- Revert the shim commits and restore the original low-level modules from git history.
- Revert `pyproject.toml` and CI changes.

## Time estimate
- Discovery and shim creation: 1-2 hours.
- Tests update and CI changes: 1-3 hours depending on test coverage.
- Review and stabilization: 1-2 hours.


---

Generated: 2025-10-08
