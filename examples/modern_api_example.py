#!/usr/bin/env python3
"""
Modern Dsv API Usage Example for splurge-dsv

This example demonstrates the new object-oriented Dsv API with DsvConfig dataclass:
- Configuration encapsulation and reuse
- Factory methods for common formats
- Type safety and validation
- Backwards compatibility with existing DsvHelper API

Copyright (c) 2025 Jim Schilling

This example is licensed under the MIT License.
"""

# Standard library imports
import tempfile
from pathlib import Path

# Local imports
from splurge_dsv import Dsv, DsvConfig, DsvHelper


def create_sample_csv_data() -> str:
    """Create sample CSV data for demonstration."""
    return """name,age,city,occupation
John Doe,30,New York,Engineer
Jane Smith,25,Los Angeles,Designer
Bob Johnson,35,Chicago,Manager
Alice Brown,28,Boston,Developer"""


def create_sample_tsv_data() -> str:
    """Create sample TSV data for demonstration."""
    return """product\tprice\tcategory\tdescription
Widget\t19.99\tElectronics\t"A useful widget"
Gadget\t29.99\tTools\t"Gadget with ""quotes"" in description"
Tool\t9.99\tHardware\tBasic tool for repairs"""


def demonstrate_dsv_config() -> None:
    """Demonstrate DsvConfig dataclass functionality."""
    print("\n" + "=" * 60)
    print("DSV CONFIG EXAMPLES")
    print("=" * 60)

    # Basic configuration creation
    config = DsvConfig(delimiter=",", skip_header_rows=1, strip=True)
    print(f"✓ Created basic config: delimiter='{config.delimiter}', skip_header_rows={config.skip_header_rows}")

    # Factory methods for common formats
    csv_config = DsvConfig.csv(skip_header_rows=1)
    print(f"✓ CSV factory config: delimiter='{csv_config.delimiter}', skip_header_rows={csv_config.skip_header_rows}")

    tsv_config = DsvConfig.tsv(bookend='"')
    print(f"✓ TSV factory config: delimiter='{tsv_config.delimiter}', bookend='{tsv_config.bookend}'")

    # Configuration with overrides
    custom_csv = DsvConfig.csv(skip_header_rows=2, skip_footer_rows=1, strip=False)
    print(
        f"✓ Custom CSV config: skip_header_rows={custom_csv.skip_header_rows}, skip_footer_rows={custom_csv.skip_footer_rows}, strip={custom_csv.strip}"
    )

    # Configuration validation
    try:
        DsvConfig(delimiter="", skip_header_rows=-1)
    except Exception as e:
        print(f"✓ Configuration validation works: {e}")


def demonstrate_dsv_class() -> None:
    """Demonstrate Dsv class functionality."""
    print("\n" + "=" * 60)
    print("DSV CLASS EXAMPLES")
    print("=" * 60)

    # Create sample data
    csv_data = create_sample_csv_data()
    tsv_data = create_sample_tsv_data()

    # Basic Dsv instance creation
    config = DsvConfig.csv(skip_header_rows=1)
    dsv = Dsv(config)
    print("✓ Created Dsv instance with CSV configuration")

    # Parse string
    tokens = dsv.parse("apple,banana,cherry")
    print(f"✓ Parsed string: {tokens}")

    # Parse multiple strings
    rows = dsv.parses(["a,b,c", "d,e,f", "g,h,i"])
    print(f"✓ Parsed multiple strings: {rows}")

    # Parse CSV data
    csv_rows = dsv.parse(csv_data)
    print(f"✓ Parsed CSV data ({len(csv_rows)} rows)")

    # TSV parsing
    tsv_config = DsvConfig.tsv(bookend='"')
    tsv_dsv = Dsv(tsv_config)
    tsv_rows = tsv_dsv.parse(tsv_data)
    print(f"✓ Parsed TSV data ({len(tsv_rows)} rows)")

    # Demonstrate configuration reuse
    print("\n--- Configuration Reuse ---")
    config = DsvConfig(delimiter=",", skip_header_rows=1)
    dsv = Dsv(config)

    # Simulate multiple files with same config
    test_data = ["header1,header2\nval1,val2", "header1,header2\nval3,val4", "header1,header2\nval5,val6"]

    for i, data in enumerate(test_data, 1):
        result = dsv.parse(data)
        print(f"✓ File {i} parsed: {result}")


def demonstrate_file_operations() -> None:
    """Demonstrate file parsing with Dsv class."""
    print("\n" + "=" * 60)
    print("FILE OPERATIONS EXAMPLES")
    print("=" * 60)

    # Create temporary files
    with tempfile.TemporaryDirectory() as temp_dir:
        csv_file = Path(temp_dir) / "sample.csv"
        tsv_file = Path(temp_dir) / "sample.tsv"

        # Write sample data
        csv_file.write_text(create_sample_csv_data())
        tsv_file.write_text(create_sample_tsv_data())

        # Parse CSV file
        csv_config = DsvConfig.csv(skip_header_rows=1)
        csv_dsv = Dsv(csv_config)
        csv_rows = csv_dsv.parse_file(str(csv_file))
        print(f"✓ Parsed CSV file: {len(csv_rows)} data rows")

        # Parse TSV file
        tsv_config = DsvConfig.tsv(bookend='"')
        tsv_dsv = Dsv(tsv_config)
        tsv_rows = tsv_dsv.parse_file(str(tsv_file))
        print(f"✓ Parsed TSV file: {len(tsv_rows)} data rows")

        # Stream parsing (for larger files)
        print("\n--- Streaming Example ---")
        chunk_count = 0
        total_rows = 0
        for chunk in csv_dsv.parse_file_stream(str(csv_file)):
            chunk_count += 1
            total_rows += len(chunk)
            print(f"✓ Processed chunk {chunk_count}: {len(chunk)} rows")

        print(f"✓ Total rows from streaming: {total_rows}")


def demonstrate_backwards_compatibility() -> None:
    """Demonstrate that the new API is fully backwards compatible."""
    print("\n" + "=" * 60)
    print("BACKWARDS COMPATIBILITY")
    print("=" * 60)

    # Same operations with old and new APIs
    test_string = "a,b,c"
    test_strings = ["x,y,z", "1,2,3"]

    # Old API
    old_result = DsvHelper.parse(test_string, delimiter=",")
    old_results = DsvHelper.parses(test_strings, delimiter=",")

    # New API
    config = DsvConfig.csv()
    dsv = Dsv(config)
    new_result = dsv.parse(test_string)
    new_results = dsv.parses(test_strings)

    # Verify identical results
    assert old_result == new_result, "String parsing results differ!"
    assert old_results == new_results, "Multiple string parsing results differ!"

    print("✓ New Dsv API produces identical results to DsvHelper")
    print(f"  String parse: {old_result}")
    print(f"  Multiple parse: {old_results}")


def demonstrate_error_handling() -> None:
    """Demonstrate error handling with the new API."""
    print("\n" + "=" * 60)
    print("ERROR HANDLING EXAMPLES")
    print("=" * 60)

    config = DsvConfig.csv()
    dsv = Dsv(config)

    # Invalid configuration
    try:
        DsvConfig(delimiter="", chunk_size=0)
    except Exception as e:
        print(f"✓ Configuration validation: {e}")

    # File not found
    try:
        dsv.parse_file("nonexistent.csv")
    except Exception as e:
        print(f"✓ File not found handling: {e}")

    print("✓ Error handling works correctly")


def main() -> None:
    """Main demonstration function."""
    print("SPLURGE-DSV MODERN API USAGE EXAMPLE")
    print("=" * 60)
    print("This example demonstrates the new Dsv class and DsvConfig dataclass.")
    print("It shows configuration management, parsing operations, and backwards compatibility.")

    try:
        demonstrate_dsv_config()
        demonstrate_dsv_class()
        demonstrate_file_operations()
        demonstrate_backwards_compatibility()
        demonstrate_error_handling()

        print("\n" + "=" * 60)
        print("✓ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        raise


if __name__ == "__main__":
    main()
