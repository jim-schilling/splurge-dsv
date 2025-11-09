"""
Example: Dsv parsing with PubSub event tracking and correlation_id tracing.

This example demonstrates the end-to-end workflow of parsing DSV files while
subscribing to events published by both Dsv and DsvHelper instances. Events are
tracked using correlation_id to trace operations across the parsing pipeline.

The callback prints Message.topic for each event, allowing monitoring of the
parsing lifecycle and event flow.
"""

from splurge_dsv._vendor.splurge_pub_sub.message import Message
from splurge_dsv._vendor.splurge_pub_sub.pubsub_solo import PubSubSolo
from splurge_dsv._vendor.splurge_pub_sub.utility import generate_correlation_id
from splurge_dsv.dsv import Dsv
from splurge_dsv.dsv_config import DsvConfig


def event_callback(message: Message) -> None:
    """Callback to print event topics during parsing operations.

    Args:
        message: Message object from PubSub containing topic, data, and correlation_id.
    """
    print(
        f"[EVENT] Topic: {message.topic:40s} | Correlation ID: {message.correlation_id} | Timestamp: {message.timestamp}"
    )


def example_basic_parsing_with_events() -> None:
    """Example 1: Basic string parsing with event tracking."""
    print("\n" + "=" * 90)
    print("Example 1: Basic String Parsing with Event Tracking")
    print("=" * 90)

    # Create Dsv instance
    correlation_id = generate_correlation_id()
    config = DsvConfig(delimiter=",", strip=True)

    # Subscribe to all topics for this correlation_id and scope
    PubSubSolo.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id, scope="splurge-dsv")
    print(f"Subscribed to all events (*) for correlation_id: {correlation_id} and scope 'splurge-dsv'")

    dsv_obj = Dsv(config=config, correlation_id=correlation_id)

    # Parse a single string
    content = "name,age,city"
    print(f"Parsing: {content}")
    result = dsv_obj.parse(content)
    PubSubSolo.drain(2000, scope="splurge-dsv")
    print(f"Result: {result}")


def main() -> None:
    """Run all examples."""
    print("\n" + "#" * 90)
    print("# Splurge-DSV: End-to-End Parsing with Event Tracking and Correlation IDs")
    print("#" * 90)

    try:
        # Run examples
        example_basic_parsing_with_events()

        print("\n" + "#" * 90)
        print("# All examples completed successfully!")
        print("#" * 90 + "\n")

    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    main()
