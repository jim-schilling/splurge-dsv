# Issue: SafeTextFileReader.read_as_stream yields blank-line chunk artifact

Date: 2025-10-09

## Summary

When streaming a clean CSV (no blank lines) using `splurge_safe_io.safe_text_file_reader.SafeTextFileReader.read_as_stream()` with a chunk size (for example, 500), the reader can yield a chunk that contains an empty string (`''`) as one row. That empty raw line is not present in the source file; it appears to be an artifact of chunk slicing.

This artifact causes downstream consumers that expect consistent column counts (for example, pretty-printers or table formatters) to fail with `IndexError` or other errors.

## Environment

- OS: Windows (reproduced locally)
- Python: 3.12.x
- splurge-safe-io: installed in development venv (use project-installed version)
- splurge-dsv: issue discovered when running streaming CLI in `splurge-dsv` but reproduction below uses only `splurge-safe-io`.

## Reproduction (standalone)

1. Create a CSV file with a header and 1000 non-empty data rows (no blank lines). Example generator:

```python
from pathlib import Path
p = Path('large.csv')
lines = ['id,name,value,description'] + [f'{i},Item{i},Value{i},Description for item {i}' for i in range(1000)]
p.write_text("\n".join(lines), encoding='utf-8')
print('wrote', len(lines), 'lines')
```

2. Create a repro script `reproduce_safe_reader.py`:

```python
from pathlib import Path
from splurge_safe_io import safe_text_file_reader

p = Path('large.csv')
chunk_size = 500
reader = safe_text_file_reader.SafeTextFileReader(p, encoding='utf-8', strip=True, chunk_size=chunk_size)

for chunk_idx, chunk in enumerate(reader.read_as_stream(), start=1):
    print(f"Chunk {chunk_idx}: {len(chunk)} lines")
    blanks = [i for i, ln in enumerate(chunk) if not ln.strip()]
    if blanks:
        print(f"  Found blank/empty lines at local indices: {blanks}")
        for idx in blanks[:5]:
            start = max(0, idx - 2)
            end = min(len(chunk), idx + 3)
            print(f"    sample around index {idx}:")
            for j in range(start, end):
                print(f"      {j}: {repr(chunk[j])}")
```

3. Run the repro script:

```bash
python reproduce_safe_reader.py
```

### Observed

On my run the script printed a blank row inside a chunk:

```
Chunk 1: 500 lines
Chunk 2: 500 lines
  Found blank/empty lines at local indices: [207]
    sample around index 207:
      205: '704,Item704,Value704,Description for item 704'
      206: '705,Item705,Value705,Description for item 705'
      207: ''
      208: '707,Item707,Value707,Description for item 707'
      209: '708,Item708,Value708,Description for item 708'
```

However, the source file has no blank lines (inspecting `large.csv` directly shows all lines contain the expected CSV rows). The empty string appears only when iterating `read_as_stream()` with the chunk size used.

### Expected

`read_as_stream()` should yield chunks that contain only actual logical lines from the file. For a file with no blank lines, `read_as_stream()` should never yield `''` lines.

## Quick verification

- `safe_text_file_reader.SafeTextFileReader.read()` (the non-streaming read) returns a full list of lines with no `''` entries.
- Flattening the generator output and comparing to `read()` should be equal.

## Root-cause hypothesis

The artifact likely arises from how the streaming implementation buffers and slices logical lines into chunks. A chunk boundary combined with newline normalization or internal buffering may create an empty logical line inside a chunk even though the source file contains no such blank line.

This is consistent with the fact the artifact appears at predictable chunk-local indices when using certain chunk sizes.

## Suggested fixes

1. Correct the chunking algorithm in `splurge-safe-io` so that the chunk assembly does not introduce empty string logical lines that are not present in the source file. Add unit tests verifying `list(reader.read_as_stream())` flattened equals `reader.read()` for a range of file sizes and chunk sizes.

2. Add a test in `splurge-safe-io` to assert no artifacts are produced for clean inputs (example pytest snippet below).

3. If an immediate change to the reader isn't possible, consider documenting the behavior and providing a stream option to filter artifact blank lines. However, the preferred fix is to remove the artifact at source.

## Minimal pytest to guard against regressions

```python
from splurge_safe_io import safe_text_file_reader

def test_read_as_stream_matches_read(tmp_path):
    p = tmp_path / 'large.csv'
    lines = ['id,name,value,description'] + [f'{i},Item{i},Value{i},Description for item {i}' for i in range(1000)]
    p.write_text('\n'.join(lines), encoding='utf-8')

    reader = safe_text_file_reader.SafeTextFileReader(p, encoding='utf-8', strip=True, chunk_size=500)
    flattened = [ln for chunk in reader.read_as_stream() for ln in chunk]
    read_all = reader.read()
    assert flattened == read_all
```

## Next steps

- I can open a well-documented issue against `splurge-safe-io` including the minimal repro, sample file generation, and the pytest suggested above.
- I can prepare a small branch (PR) that either fixes the chunking logic or, if the fix is non-trivial, add a defensive unit test and/or a configuration option to control artifact filtering.

If you want me to open the issue/PR for you, tell me which repository and I will prepare the patch and test.
