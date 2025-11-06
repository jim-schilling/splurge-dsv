"""
Example: Dsv parsing with PubSub event tracking and correlation_id tracing.

This example demonstrates the end-to-end workflow of parsing DSV files while
subscribing to events published by both Dsv and DsvHelper instances. Events are
tracked using correlation_id to trace operations across the parsing pipeline.

The callback prints Message.topic for each event, allowing monitoring of the
parsing lifecycle and event flow.
"""

from pathlib import Path

from splurge_dsv._vendor.splurge_pub_sub.message import Message
from splurge_dsv._vendor.splurge_pub_sub.utility import generate_correlation_id
from splurge_dsv.dsv import Dsv
from splurge_dsv.dsv_config import DsvConfig
from splurge_dsv.dsv_helper import DsvHelper


def event_callback(message: Message) -> None:
    """Callback to print event topics during parsing operations.

    Args:
        message: Message object from PubSub containing topic, data, and correlation_id.
    """
    print(f"[EVENT] Topic: {message.topic:40s} | Correlation ID: {message.correlation_id}")


def example_basic_parsing_with_events() -> None:
    """Example 1: Basic string parsing with event tracking."""
    print("\n" + "=" * 90)
    print("Example 1: Basic String Parsing with Event Tracking")
    print("=" * 90)

    # Create Dsv instance
    config = DsvConfig(delimiter=",", strip=True)
    dsv_obj = Dsv(config)
    correlation_id = dsv_obj.correlation_id

    print(f"\nCreated Dsv instance with correlation_id: {correlation_id}")

    # Subscribe to all topics for this correlation_id on both PubSub instances
    dsv_pubsub = Dsv.get_pubsub()
    dsv_helper_pubsub = DsvHelper.get_pubsub()

    dsv_pubsub.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id)
    dsv_helper_pubsub.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id)

    print("Subscribed to all events (*) for both Dsv and DsvHelper PubSub instances\n")

    # Parse a single string
    content = "name,age,city"
    print(f"Parsing: {content}")
    result = dsv_obj.parse(content)
    print(f"Result: {result}")


def example_batch_parsing_with_events() -> None:
    """Example 2: Batch string parsing with event tracking."""
    print("\n" + "=" * 90)
    print("Example 2: Batch String Parsing with Event Tracking")
    print("=" * 90)

    # Create Dsv instance
    config = DsvConfig(delimiter=",", strip=True)
    dsv_obj = Dsv(config)
    correlation_id = dsv_obj.correlation_id

    print(f"\nCreated Dsv instance with correlation_id: {correlation_id}")

    # Subscribe to all topics for this correlation_id
    dsv_pubsub = Dsv.get_pubsub()
    dsv_helper_pubsub = DsvHelper.get_pubsub()

    dsv_pubsub.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id)
    dsv_helper_pubsub.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id)

    print("Subscribed to all events (*) for both PubSub instances\n")

    # Parse multiple strings
    content = [
        "name,age,city",
        "John Doe,30,New York",
        "Jane Smith,25,Los Angeles",
    ]
    print(f"Parsing {len(content)} rows:")
    for line in content:
        print(f"  {line}")
    result = dsv_obj.parses(content)
    print(f"\nResult ({len(result)} rows):")
    for row in result:
        print(f"  {row}")


def example_file_parsing_with_events(tmp_file: Path) -> None:
    """Example 3: File parsing with event tracking.

    Args:
        tmp_file: Path to temporary test file.
    """
    print("\n" + "=" * 90)
    print("Example 3: File Parsing with Event Tracking")
    print("=" * 90)

    # Create Dsv instance
    config = DsvConfig(delimiter=",", strip=True, skip_header_rows=1)
    dsv_obj = Dsv(config)
    correlation_id = dsv_obj.correlation_id

    print(f"\nCreated Dsv instance with correlation_id: {correlation_id}")

    # Subscribe to all topics for this correlation_id
    dsv_pubsub = Dsv.get_pubsub()
    dsv_helper_pubsub = DsvHelper.get_pubsub()

    dsv_pubsub.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id)
    dsv_helper_pubsub.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id)

    print("Subscribed to all events (*) for both PubSub instances")
    print(f"Parsing file: {tmp_file}\n")

    # Parse file
    result = dsv_obj.parse_file(tmp_file)
    print(f"\nResult ({len(result)} rows):")
    for row in result[:3]:  # Print first 3 rows
        print(f"  {row}")
    if len(result) > 3:
        print(f"  ... ({len(result) - 3} more rows)")


def example_file_stream_parsing_with_events(tmp_file: Path) -> None:
    """Example 4: Streaming file parsing with event tracking.

    Args:
        tmp_file: Path to temporary test file.
    """
    print("\n" + "=" * 90)
    print("Example 4: Streaming File Parsing with Event Tracking")
    print("=" * 90)

    # Create Dsv instance with small chunk size for demonstration
    correlation_id = generate_correlation_id()
    config = DsvConfig(delimiter=",", strip=True, chunk_size=50)

    print(f"\nCreated Dsv instance with correlation_id: {correlation_id}")

    # Subscribe to all topics for this correlation_id
    dsv_pubsub = Dsv.get_pubsub()
    dsv_helper_pubsub = DsvHelper.get_pubsub()

    dsv_pubsub.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id)
    dsv_helper_pubsub.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id)

    print("Subscribed to all events (*) for both PubSub instances")
    print(f"Parsing file stream: {tmp_file} (chunk_size: 50)\n")

    # late initialization so that subscriber is registered before events are published
    dsv_obj = Dsv(config, correlation_id=correlation_id)
    # Parse file stream
    total_rows = 0
    for chunk_num, chunk in enumerate(dsv_obj.parse_file_stream(tmp_file), 1):
        total_rows += len(chunk)
        print(f"[STREAM] Chunk {chunk_num}: {len(chunk)} rows (total: {total_rows})")

    print(f"\nStreaming complete: {total_rows} total rows")


def example_bookend_parsing_with_events() -> None:
    """Example 5: Parsing with bookend removal and event tracking."""
    print("\n" + "=" * 90)
    print("Example 5: Parsing with Bookend Removal and Event Tracking")
    print("=" * 90)

    # Create Dsv instance with bookend configuration
    config = DsvConfig(delimiter=",", bookend='"', bookend_strip=True, strip=True)
    dsv_obj = Dsv(config)
    correlation_id = dsv_obj.correlation_id

    print(f"\nCreated Dsv instance with correlation_id: {correlation_id}")
    print("Configuration: delimiter=',', bookend='\"', bookend_strip=True, strip=True")

    # Subscribe to all topics for this correlation_id
    dsv_pubsub = Dsv.get_pubsub()
    dsv_helper_pubsub = DsvHelper.get_pubsub()

    dsv_pubsub.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id)
    dsv_helper_pubsub.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id)

    print("Subscribed to all events (*) for both PubSub instances\n")

    # Parse content with bookends
    content = '"John Doe","30","New York"'
    print(f"Parsing: {content}")
    result = dsv_obj.parse(content)
    print(f"Result: {result}")


def example_multiple_instances_with_different_correlation_ids() -> None:
    """Example 6: Multiple Dsv instances with independent correlation_ids."""
    print("\n" + "=" * 90)
    print("Example 6: Multiple Dsv Instances with Independent Correlation IDs")
    print("=" * 90)

    # Create first Dsv instance
    config1 = DsvConfig(delimiter=",")
    dsv_obj1 = Dsv(config1)
    correlation_id1 = dsv_obj1.correlation_id

    # Create second Dsv instance
    config2 = DsvConfig(delimiter="\t")
    dsv_obj2 = Dsv(config2)
    correlation_id2 = dsv_obj2.correlation_id

    print(f"\nCreated Dsv instance 1 with correlation_id: {correlation_id1}")
    print(f"Created Dsv instance 2 with correlation_id: {correlation_id2}")
    print(f"Correlation IDs are independent: {correlation_id1 != correlation_id2}")

    # Subscribe to events from instance 1
    print("\nSubscribing to instance 1 events (CSV parsing):")
    dsv_pubsub = Dsv.get_pubsub()
    dsv_pubsub.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id1)

    content1 = "a,b,c"
    print(f"Parsing with instance 1: {content1}")
    result1 = dsv_obj1.parse(content1)
    print(f"Result: {result1}")

    # Subscribe to events from instance 2
    print("\nSubscribing to instance 2 events (TSV parsing):")
    dsv_pubsub.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id2)

    content2 = "x\ty\tz"
    print(f"Parsing with instance 2: {content2}")
    result2 = dsv_obj2.parse(content2)
    print(f"Result: {result2}")


def main() -> None:
    """Run all examples."""
    print("\n" + "#" * 90)
    print("# Splurge-DSV: End-to-End Parsing with Event Tracking and Correlation IDs")
    print("#" * 90)

    # Create a temporary file for file-based examples
    tmp_dir = Path("tmp")
    tmp_dir.mkdir(exist_ok=True)
    tmp_file = tmp_dir / "example_data.csv"

    # Create sample data file if it doesn't exist
    if not tmp_file.exists():
        content = """name,age,city,occupation
John Doe,30,New York,Engineer
Jane Smith,25,Los Angeles,Designer
Bob Johnson,35,Chicago,Manager
Alice Brown,28,Boston,Developer
Charlie Wilson,32,Seattle,Analyst
Diana Davis,29,Austin,Consultant
Eve Miller,31,Denver,Analyst
Frank Garcia,27,Miami,Developer
Grace Lee,33,Portland,Engineer
Henry Taylor,26,Atlanta,Designer
Isabel Rodriguez,34,Phoenix,Manager
Jack Martinez,28,Las Vegas,Consultant
Karen Johnson,30,Houston,Developer
Leo Anderson,29,Dallas,Engineer
Megan White,26,San Antonio,Designer"""
        tmp_file.write_text(content)
        print(f"Created sample data file: {tmp_file}")

    try:
        # Run examples
        example_basic_parsing_with_events()
        example_batch_parsing_with_events()
        example_file_parsing_with_events(tmp_file)
        example_file_stream_parsing_with_events(tmp_file)
        example_bookend_parsing_with_events()
        example_multiple_instances_with_different_correlation_ids()

        print("\n" + "#" * 90)
        print("# All examples completed successfully!")
        print("#" * 90 + "\n")

    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    main()
