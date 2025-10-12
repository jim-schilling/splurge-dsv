# Bug: Empty-line produced as empty row during streaming (IndexError in CLI)

Date: 2025-10-09
Reporter: automated refactor agent (local test run)

Summary
-------
When streaming a CSV file with `Dsv.parse_file_stream` (used by the CLI `--stream` mode), the streaming reader can emit an empty row `[]` for certain input boundaries (blank lines or buffer boundaries). The CLI's pretty table printer assumed every row had the same number of columns as the header and raised "list index out of range" when it tried to index into an empty row.

This doc describes how to reproduce the failure locally, root-cause analysis, and recommended fixes. The eventual plan is to release a patched `splurge-safe-io` that avoids emitting empty rows when appropriate and update `splurge-dsv` if necessary.

Reproduction steps
------------------
Prerequisites:
- checkout `refactor/replace-low-level-io-modules` branch of `splurge-dsv` into a Python 3.12 venv
- ensure `splurge-safe-io` is installed in the same environment (the migration assumes this dependency is present)

1. Create a CSV file with a header and many rows (the test file used by the repo contains 1000 rows). The important facet is that the file may contain blank lines or the streaming reader may encounter an I/O buffer boundary exposing an empty row.

2. Run the CLI in stream mode (example run used in tests):

   python -m splurge_dsv <path-to-large.csv> --delimiter , --stream

3. Observe output. In the failing case the program prints the first chunk (500 rows), prints the second chunk header and rows, then fails partway through the second chunk with:

   Unexpected error: list index out of range

4. Reproduce using the library API to capture chunk contents, e.g.:

   from splurge_dsv.dsv import Dsv, DsvConfig
   config = DsvConfig(delimiter=',')
   d = Dsv(config)
   for n, chunk in enumerate(d.parse_file_stream('large.csv'), start=1):
       print('chunk', n, 'len', len(chunk))
       for i, row in enumerate(chunk):
           if len(row) != len(chunk[0]):
               print('mismatch', n, i, len(row), row)

In the failing run, an empty row `[]` was observed in chunk 2 at row index 207.

Root-cause analysis
-------------------
There are two likely causes for an empty row `[]` being emitted by the streaming path:

1. The underlying safe-text-reader implementation (`splurge-safe-io`) is emitting an empty row for blank lines in the file. A blank line should typically be translated to a row with a single empty string (['']) if the CSV/DSV semantics treat blank lines as records with zero fields, or omitted entirely if blank lines are to be ignored.

2. The streaming reader may be splitting at an I/O boundary and producing an intermediate empty buffer which the tokenization layer translates into an empty row `[]`.

Either way, `splurge-dsv`'s CLI `print_results` assumed every row had the same number of columns as the header and attempted to index into every column position. When a row is `[]` this assumption fails and raises IndexError.

Immediate fix applied
---------------------
To avoid crashing, `splurge-dsv`'s CLI printer was made defensive: it now computes the maximum number of columns across all rows in a chunk and pads any missing values with empty strings when formatting the ASCII table. This prevents the crash and keeps the CLI usable without changing lower-level semantics.

Recommended long-term fixes
---------------------------
There are multiple possible fixes; pick one or combine them:

1. Fix in `splurge-safe-io` (preferred):
   - Ensure the safe-text-reader does not emit empty `[]` rows. For blank lines, either emit `['']` or skip the row entirely depending on the library's policy and documented behavior (recommend default: skip blank lines unless `preserve_blank_lines=True` is set).
   - Handle buffer boundary edge-cases so that a partial read doesn't produce an empty record.

2. Add configurable behavior in `splurge-safe-io` or the shim:
   - Introduce a `skip_empty_rows: bool = True` flag at the reader/open helper level so callers can opt into automatically skipping empty rows.

3. Filter at the consumer level in `splurge-dsv`:
   - Drop rows where `len(row) == 0` in `DsvHelper.parse_file_stream` or in `Dsv.parse_file_stream` wrapper. This is an easy, local change but modifies the sequence of rows returned by the API (removes empty records), which might be considered a behavioral change.

4. Keep the current defensive rendering change in the CLI (already applied) and document the behavior. This is least invasive but leaves the stream API returning `[]` rows to callers that must be defensive.

Acceptance criteria for patched behavior
---------------------------------------
- CLI does not crash when encountering blank or partial rows while streaming.
- `Dsv.parse_file_stream` either never yields `[]` rows (preferred) or the README/doc mentions that empty rows may appear and advises callers to filter them.
- If the fix is made in `splurge-safe-io`, add unit tests that simulate blank lines and buffer-boundary splits to verify the library does not emit `[]` rows.

Files changed in this repo (delta)
----------------------------------
- `splurge_dsv/cli.py` — Made `print_results` defensive to avoid IndexError on empty rows.
- This doc added: `docs/issues/bug-empty-line-2025-10-09.md` (you are reading it now).

Next steps for you (as you said you'll fix upstream)
---------------------------------------------------
1. In the `splurge-safe-io` repository:
   - Add tests reproducing the empty-row emission: include blank lines and produce chunked reads that simulate I/O boundaries.
   - Implement changes so blank lines are either skipped or normalized to `['']` depending on the desired policy. Prefer making this configurable with a default that preserves backward compatibility or aligns with common CSV semantics.
   - Release a new `splurge-safe-io` version (e.g., 2025.10.1) and publish to PyPI/local index as appropriate.

2. In `splurge-dsv` after upstream release:
   - Update `pyproject.toml` to require the patched `splurge-safe-io` version.
   - (Optional) If you want stricter behavior inside `splurge-dsv`, implement `DsvConfig(skip_empty_rows=True)` and filter rows in `DsvHelper.parse_file_stream`.
   - Run full test suite and verify the streaming CLI end-to-end test passes.

Appendix: Observed failing test details
--------------------------------------
- Test: `tests/integration/test_e2e_workflows.py::TestEndToEndCLIWorkflows::test_streaming_workflow`
- Symptom: CLI printed chunk 1 and part of chunk 2, then crashed with: `Unexpected error: list index out of range`.
- Repro snippet used locally:

  from splurge_dsv.dsv import Dsv, DsvConfig
  config = DsvConfig(delimiter=',')
  d = Dsv(config)
  for n, chunk in enumerate(d.parse_file_stream(fp), start=1):
      print('chunk', n, 'len', len(chunk))

- Observed: chunk 2 contained an empty row at index 207. Chunk sizes reported were 500, 500, 2 (so file had 1002 rows including header or such.)

Contact
-------
If you want, I can also prepare a small unit test for `splurge-safe-io` that reproduces the buffer-boundary/blank-line emission case and include it as a failing test in that repository to ease local development.


---
Generated by the migration automation run on 2025-10-09.