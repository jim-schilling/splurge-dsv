"""
End-to-end tests capturing the Dsv to DsvHelper workflow with event subscriptions.

These tests instantiate Dsv objects and subscribe to all topics ('*') for both
the Dsv and DsvHelper global PubSub instances, capturing events throughout the
parsing lifecycle for monitoring and tracing operations.
"""

# Standard library imports
from collections.abc import Callable
from pathlib import Path
from typing import Any

# Third-party imports
import pytest

# Local imports
from splurge_dsv._vendor.splurge_pub_sub.message import Message
from splurge_dsv._vendor.splurge_pub_sub.pubsub_solo import PubSubSolo
from splurge_dsv.dsv import Dsv
from splurge_dsv.dsv_config import DsvConfig
from splurge_dsv.exceptions import SplurgeDsvOSError


class TestDsvToDsvHelperPubSubWorkflow:
    """Test complete workflows from Dsv to DsvHelper with event subscriptions."""

    @pytest.fixture
    def event_tracker(self) -> dict[str, Any]:
        """Create a tracker to capture all events."""
        return {
            "events": [],
            "count_by_topic": {},
            "count_by_correlation_id": {},
        }

    @pytest.fixture
    def event_callback(self, event_tracker: dict[str, Any]) -> Callable:
        """Create a callback that captures events."""

        def callback(message: Message) -> None:
            """Callback to capture events from both Dsv and DsvHelper pubsub instances."""
            event_info = {
                "topic": message.topic,
                "data": message.data,
                "correlation_id": message.correlation_id,
            }
            event_tracker["events"].append(event_info)

            # Track count by topic
            if message.topic not in event_tracker["count_by_topic"]:
                event_tracker["count_by_topic"][message.topic] = 0
            event_tracker["count_by_topic"][message.topic] += 1

            # Track count by correlation_id
            if message.correlation_id is not None:
                if message.correlation_id not in event_tracker["count_by_correlation_id"]:
                    event_tracker["count_by_correlation_id"][message.correlation_id] = 0
                event_tracker["count_by_correlation_id"][message.correlation_id] += 1

        return callback

    def test_parse_single_string_with_event_tracking(
        self, event_tracker: dict[str, Any], event_callback: Callable
    ) -> None:
        """Test parse() method with event tracking from both Dsv and DsvHelper."""
        # Create Dsv instance and subscribe to events
        config = DsvConfig(delimiter=",")
        dsv_obj = Dsv(config)
        correlation_id = dsv_obj.correlation_id

        # Subscribe to all topics for this correlation_id
        PubSubSolo.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id, scope="splurge-dsv")

        # Parse a single string
        content = "a,b,c"
        result = dsv_obj.parse(content)
        PubSubSolo.drain(2000, scope="splurge-dsv")

        # Verify parse result
        assert result == ["a", "b", "c"], "Parse should return correct tokens"

        # Verify events were captured
        assert len(event_tracker["events"]) > 0, "Should have captured events"
        assert correlation_id in event_tracker["count_by_correlation_id"], "Events should include correlation_id"

        # Verify lifecycle events
        topics = {event["topic"] for event in event_tracker["events"]}
        assert "dsv.parse.begin" in topics, "Should have dsv.parse.begin event"
        assert "dsv.parse.end" in topics, "Should have dsv.parse.end event"
        assert "dsv.helper.parse.begin" in topics, "Should have dsv.helper.parse.begin event"
        assert "dsv.helper.parse.end" in topics, "Should have dsv.helper.parse.end event"

        # Verify all events have correct correlation_id
        for event in event_tracker["events"]:
            assert event["correlation_id"] == correlation_id, (
                f"Event {event['topic']} should have correct correlation_id"
            )

    def test_parse_multiple_strings_with_event_tracking(
        self, event_tracker: dict[str, Any], event_callback: Callable
    ) -> None:
        """Test parses() method with event tracking from both Dsv and DsvHelper."""
        # Create Dsv instance and subscribe to events
        config = DsvConfig(delimiter=",")
        dsv_obj = Dsv(config)
        correlation_id = dsv_obj.correlation_id

        # Subscribe to all topics for this correlation_id
        PubSubSolo.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id, scope="splurge-dsv")

        # Parse multiple strings
        content = ["a,b,c", "d,e,f", "g,h,i"]
        result = dsv_obj.parses(content)
        PubSubSolo.drain(2000, scope="splurge-dsv")

        # Verify parse result
        assert result == [["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]], "Parses should return correct tokens"

        # Verify events were captured
        assert len(event_tracker["events"]) > 0, "Should have captured events"
        assert correlation_id in event_tracker["count_by_correlation_id"], "Events should include correlation_id"

        # Verify lifecycle events
        topics = {event["topic"] for event in event_tracker["events"]}
        assert "dsv.parses.begin" in topics, "Should have dsv.parses.begin event"
        assert "dsv.parses.end" in topics, "Should have dsv.parses.end event"
        assert "dsv.helper.parses.begin" in topics, "Should have dsv.helper.parses.begin event"
        assert "dsv.helper.parses.end" in topics, "Should have dsv.helper.parses.end event"

        # Verify all events have correct correlation_id
        for event in event_tracker["events"]:
            assert event["correlation_id"] == correlation_id, (
                f"Event {event['topic']} should have correct correlation_id"
            )

    def test_parse_file_with_event_tracking(
        self, event_tracker: dict[str, Any], event_callback: Callable, tmp_path: Path
    ) -> None:
        """Test parse_file() method with event tracking from both Dsv and DsvHelper."""
        # Create a test CSV file
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,age,city\nJohn,30,NYC\nJane,25,LA")

        # Create Dsv instance and subscribe to events
        config = DsvConfig(delimiter=",")
        dsv_obj = Dsv(config)
        correlation_id = dsv_obj.correlation_id

        # Subscribe to all topics for this correlation_id
        PubSubSolo.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id, scope="splurge-dsv")

        # Parse file
        result = dsv_obj.parse_file(csv_file)
        PubSubSolo.drain(2000, scope="splurge-dsv")

        # Verify parse result
        assert len(result) == 3, "Should parse 3 rows"
        assert result[0] == ["name", "age", "city"], "First row should be header"

        # Verify events were captured
        assert len(event_tracker["events"]) > 0, "Should have captured events"
        assert correlation_id in event_tracker["count_by_correlation_id"], "Events should include correlation_id"

        # Verify lifecycle events
        topics = {event["topic"] for event in event_tracker["events"]}
        assert "dsv.parse.file.begin" in topics, "Should have dsv.parse.file.begin event"
        assert "dsv.parse.file.end" in topics, "Should have dsv.parse.file.end event"
        assert "dsv.helper.parse.file.begin" in topics, "Should have dsv.helper.parse.file.begin event"
        assert "dsv.helper.parse.file.end" in topics, "Should have dsv.helper.parse.file.end event"

        # Verify all events have correct correlation_id
        for event in event_tracker["events"]:
            assert event["correlation_id"] == correlation_id, (
                f"Event {event['topic']} should have correct correlation_id"
            )

    def test_parse_file_stream_with_event_tracking(
        self, event_tracker: dict[str, Any], event_callback: Callable, tmp_path: Path
    ) -> None:
        """Test parse_file_stream() method with event tracking from both Dsv and DsvHelper."""
        # Create a test CSV file with multiple chunks
        csv_file = tmp_path / "test_stream.csv"
        lines = ["name,age,city"]
        for i in range(100):
            lines.append(f"person{i},{20 + i},city{i}")
        csv_file.write_text("\n".join(lines))

        # Create Dsv instance with small chunk size and subscribe to events
        config = DsvConfig(delimiter=",", chunk_size=25)
        dsv_obj = Dsv(config)
        correlation_id = dsv_obj.correlation_id

        # Subscribe to all topics for this correlation_id
        PubSubSolo.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id, scope="splurge-dsv")

        # Parse file stream
        chunks = list(dsv_obj.parse_file_stream(csv_file))
        PubSubSolo.drain(2000, scope="splurge-dsv")

        # Verify stream results
        assert len(chunks) > 0, "Should have parsed chunks"
        total_rows = sum(len(chunk) for chunk in chunks)
        assert total_rows == 101, "Should parse all 101 rows (header + 100 data)"

        # Verify events were captured
        assert len(event_tracker["events"]) > 0, "Should have captured events"
        assert correlation_id in event_tracker["count_by_correlation_id"], "Events should include correlation_id"

        # Verify lifecycle events
        topics = {event["topic"] for event in event_tracker["events"]}
        assert "dsv.parse.file.stream.begin" in topics, "Should have dsv.parse.file.stream.begin event"
        assert "dsv.parse.file.stream.end" in topics, "Should have dsv.parse.file.stream.end event"
        assert "dsv.helper.parse.file.stream.begin" in topics, "Should have dsv.helper.parse.file.stream.begin event"
        assert "dsv.helper.parse.file.stream.end" in topics, "Should have dsv.helper.parse.file.stream.end event"

        # Verify all events have correct correlation_id
        for event in event_tracker["events"]:
            assert event["correlation_id"] == correlation_id, (
                f"Event {event['topic']} should have correct correlation_id"
            )

    def test_parse_error_with_event_tracking(
        self, event_tracker: dict[str, Any], event_callback: Callable, tmp_path: Path
    ) -> None:
        """Test error handling with event tracking from both Dsv and DsvHelper."""
        # Create a CSV file with inconsistent column counts
        csv_file = tmp_path / "incomplete.csv"
        csv_file.write_text("a,b,c\nd,e")  # Second row has fewer columns

        # Create Dsv instance with raise_on_missing_columns and subscribe to events
        config = DsvConfig(delimiter=",", raise_on_missing_columns=True)
        dsv_obj = Dsv(config)
        correlation_id = dsv_obj.correlation_id

        # Subscribe to all topics for this correlation_id
        PubSubSolo.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id, scope="splurge-dsv")

        # Attempt to parse with mismatched columns - this should work since normalize_columns wasn't set
        # Let's try a different error - parse content with file not found
        nonexistent_file = tmp_path / "nonexistent.csv"

        with pytest.raises(SplurgeDsvOSError):  # Should raise SplurgeDsvOSError
            dsv_obj.parse_file(nonexistent_file)
        PubSubSolo.drain(2000, scope="splurge-dsv")

        # Verify events were captured
        assert len(event_tracker["events"]) > 0, "Should have captured events"
        assert correlation_id in event_tracker["count_by_correlation_id"], "Events should include correlation_id"

        # Verify error event
        topics = {event["topic"] for event in event_tracker["events"]}
        assert "dsv.parse.file.begin" in topics, "Should have dsv.parse.file.begin event"
        assert "dsv.parse.file.error" in topics or "dsv.helper.parse.file.error" in topics, "Should have error event"

        # Verify all events have correct correlation_id
        for event in event_tracker["events"]:
            assert event["correlation_id"] == correlation_id, (
                f"Event {event['topic']} should have correct correlation_id"
            )

    def test_multiple_dsv_instances_independent_correlation_ids(self, event_callback: Callable) -> None:
        """Test that multiple Dsv instances have independent correlation_ids."""
        # Create two Dsv instances
        config = DsvConfig(delimiter=",")
        dsv_obj1 = Dsv(config)
        dsv_obj2 = Dsv(config)

        # Verify they have different correlation_ids
        assert dsv_obj1.correlation_id != dsv_obj2.correlation_id, "Each Dsv instance should have unique correlation_id"

    def test_event_flow_parse_workflow(self, event_tracker: dict[str, Any], event_callback: Callable) -> None:
        """Test the complete event flow for a parse workflow."""
        # Create Dsv instance and subscribe to events
        config = DsvConfig(delimiter=",", strip=True)
        dsv_obj = Dsv(config)
        correlation_id = dsv_obj.correlation_id

        # Subscribe to all topics for this correlation_id
        PubSubSolo.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id, scope="splurge-dsv")

        # Clear events from __init__
        event_tracker["events"].clear()

        # Parse a string
        content = " a , b , c "
        result = dsv_obj.parse(content)
        PubSubSolo.drain(2000, scope="splurge-dsv")

        # Verify parse result
        assert result == ["a", "b", "c"], "Should strip whitespace and parse correctly"

        # Extract event flow
        event_flow = [event["topic"] for event in event_tracker["events"]]

        # Verify event sequence
        # Expected order: dsv.parse.begin -> dsv.helper.parse.begin -> dsv.helper.parse.end -> dsv.parse.end
        assert "dsv.parse.begin" in event_flow, "Should have dsv.parse.begin"
        assert "dsv.helper.parse.begin" in event_flow, "Should have dsv.helper.parse.begin"
        assert "dsv.helper.parse.end" in event_flow, "Should have dsv.helper.parse.end"
        assert "dsv.parse.end" in event_flow, "Should have dsv.parse.end"

        # Verify reasonable ordering (dsv.parse.begin should come before dsv.helper.parse.begin)
        dsv_begin_idx = event_flow.index("dsv.parse.begin")
        helper_begin_idx = event_flow.index("dsv.helper.parse.begin")
        assert dsv_begin_idx < helper_begin_idx, "dsv.parse.begin should come before dsv.helper.parse.begin"

    def test_bookend_removal_with_event_tracking(self, event_tracker: dict[str, Any], event_callback: Callable) -> None:
        """Test bookend removal with event tracking."""
        # Create Dsv instance with bookend and subscribe to events
        config = DsvConfig(delimiter=",", bookend='"', bookend_strip=True)
        dsv_obj = Dsv(config)
        correlation_id = dsv_obj.correlation_id

        # Subscribe to all topics for this correlation_id
        PubSubSolo.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id, scope="splurge-dsv")

        # Parse with bookended content
        content = '"a","b","c"'
        result = dsv_obj.parse(content)
        PubSubSolo.drain(2000, scope="splurge-dsv")

        # Verify bookends were removed
        assert result == ["a", "b", "c"], "Should remove bookends"

        # Verify events were captured
        assert len(event_tracker["events"]) > 0, "Should have captured events"
        topics = {event["topic"] for event in event_tracker["events"]}
        assert "dsv.parse.begin" in topics, "Should have parse events"

    def test_detect_columns_with_event_tracking(self, event_tracker: dict[str, Any], event_callback: Callable) -> None:
        """Test column detection with event tracking."""
        # Create Dsv instance with detect_columns enabled
        config = DsvConfig(delimiter=",", detect_columns=True)
        dsv_obj = Dsv(config)
        correlation_id = dsv_obj.correlation_id

        # Subscribe to all topics for this correlation_id
        PubSubSolo.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id, scope="splurge-dsv")

        # Parse multiple strings to trigger column detection
        content = ["a,b,c", "d,e,f"]
        result = dsv_obj.parses(content)
        PubSubSolo.drain(2000, scope="splurge-dsv")

        # Verify parse results
        assert result == [["a", "b", "c"], ["d", "e", "f"]], "Should parse correctly with column detection"

        # Verify events were captured
        assert len(event_tracker["events"]) > 0, "Should have captured events"
        topics = {event["topic"] for event in event_tracker["events"]}
        assert "dsv.parses.begin" in topics, "Should have parses events"

    def test_tab_delimited_with_event_tracking(self, event_tracker: dict[str, Any], event_callback: Callable) -> None:
        """Test tab-delimited parsing with event tracking."""
        # Create Dsv instance with tab delimiter
        config = DsvConfig(delimiter="\t")
        dsv_obj = Dsv(config)
        correlation_id = dsv_obj.correlation_id

        # Subscribe to all topics for this correlation_id
        PubSubSolo.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id, scope="splurge-dsv")

        # Parse tab-delimited content
        content = "a\tb\tc"
        result = dsv_obj.parse(content)
        PubSubSolo.drain(2000, scope="splurge-dsv")

        # Verify parse result
        assert result == ["a", "b", "c"], "Should parse tab-delimited content"

        # Verify events were captured
        assert len(event_tracker["events"]) > 0, "Should have captured events"
        topics = {event["topic"] for event in event_tracker["events"]}
        assert "dsv.parse.begin" in topics, "Should have parse events"

    def test_parse_file_with_skip_header_and_event_tracking(
        self, event_tracker: dict[str, Any], event_callback: Callable, tmp_path: Path
    ) -> None:
        """Test parse_file() with header skipping and event tracking."""
        # Create a test CSV file with header
        csv_file = tmp_path / "test_header.csv"
        csv_file.write_text("# Comment line\nname,age,city\nJohn,30,NYC\nJane,25,LA")

        # Create Dsv instance with skip_header_rows and subscribe to events
        config = DsvConfig(delimiter=",", skip_header_rows=1)
        dsv_obj = Dsv(config)
        correlation_id = dsv_obj.correlation_id

        # Subscribe to all topics for this correlation_id
        PubSubSolo.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id, scope="splurge-dsv")

        # Parse file
        result = dsv_obj.parse_file(csv_file)
        PubSubSolo.drain(2000, scope="splurge-dsv")

        # Verify header was skipped
        assert result[0] == ["name", "age", "city"], "First row should be actual header after skip"

        # Verify events were captured
        assert len(event_tracker["events"]) > 0, "Should have captured events"
        topics = {event["topic"] for event in event_tracker["events"]}
        assert "dsv.parse.file.begin" in topics, "Should have parse.file events"
