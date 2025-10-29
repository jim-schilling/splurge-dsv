import sys
from pathlib import Path

# Ensure repository root is on sys.path for local package imports when tests run
try:
    from splurge_dsv._vendor.splurge_safe_io import SafeTextFileReader, open_safe_text_reader
    from splurge_dsv.dsv_helper import DsvHelper
    from splurge_dsv.string_tokenizer import StringTokenizer
except Exception:
    # Fallback for running the test as a script: add repository root to sys.path
    ROOT = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(ROOT))
    from splurge_safe_io.safe_text_file_reader import SafeTextFileReader, open_safe_text_reader

    from splurge_dsv.dsv_helper import DsvHelper
    from splurge_dsv.string_tokenizer import StringTokenizer

TEST_DIR = Path("tmp")
TEST_DIR.mkdir(exist_ok=True)
TEST_FILE = TEST_DIR / "test_reader_consistency.txt"
NUM_LINES = 10_000


def write_test_file(path: Path, n: int) -> list[str]:
    """Writes a test file with n lines of predictable content."""
    expected: list[str] = []
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for i in range(1, n + 1):
            fh.write(f"cell-{i:06}-0),cell-{i:06}-1,cell-{i:06}-2\n")
            expected.append(f"cell-{i:06}-0),cell-{i:06}-1,cell-{i:06}-2")
    return expected


def test_reader_consistency_roundtrip():
    """Writes NUM_LINES lines and asserts three read methods agree.

    - SafeTextFileReader.readlines()
    - SafeTextFileReader.readlines_as_stream() flattened
    - open_safe_text_reader() result
    """
    expected = write_test_file(TEST_FILE, NUM_LINES)

    for _ in range(10):
        reader = SafeTextFileReader(TEST_FILE, buffer_size=8192, chunk_size=500)

        actual0 = reader.readlines()

        # Flatten streamed chunks into a single list
        actual1 = []
        for chunk in reader.readlines_as_stream():
            actual1.extend(chunk)

        # open_safe_text_reader yields a StringIO with normalized content
        with open_safe_text_reader(TEST_FILE) as sio:
            actual2 = list(sio.read().splitlines())

        assert actual0 == actual1
        assert actual0 == actual2
        assert actual1 == actual2
        assert actual0 == expected

        for idx in range(len(actual0)):
            s0 = StringTokenizer.parse(actual0[idx], delimiter=",", strip=True)
            s1 = StringTokenizer.parse(actual1[idx], delimiter=",", strip=True)
            s2 = StringTokenizer.parse(actual2[idx], delimiter=",", strip=True)
            assert s0 == s1
            assert s0 == s2
            assert s1 == s2
            assert s0 == StringTokenizer.parse(expected[idx], delimiter=",", strip=True)

        s0 = StringTokenizer.parses(actual0, delimiter=",", strip=True)
        s1 = StringTokenizer.parses(actual1, delimiter=",", strip=True)
        s2 = StringTokenizer.parses(actual2, delimiter=",", strip=True)
        assert s0 == s1
        assert s0 == s2
        assert s1 == s2
        assert s0 == StringTokenizer.parses(expected, delimiter=",", strip=True)

        dh0 = DsvHelper.parses(actual0, delimiter=",", strip=True)
        dh1 = DsvHelper.parses(actual1, delimiter=",", strip=True)
        dh2 = DsvHelper.parses(actual2, delimiter=",", strip=True)
        assert dh0 == dh1
        assert dh0 == dh2
        assert dh1 == dh2
        assert dh0 == DsvHelper.parses(expected, delimiter=",", strip=True)

        tmp = DsvHelper.parse_file_stream(TEST_FILE, delimiter=",", strip=True)
        # Flatten list of lists
        dh3 = [row for chunk in tmp for row in chunk]
        assert dh0 == dh3
