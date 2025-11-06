# End-to-End Dsv to DsvHelper PubSub Workflow Tests

## Overview

Created comprehensive end-to-end tests that capture the complete workflow from `Dsv()` to `DsvHelper()` with event subscriptions and correlation tracking. These tests verify that events are properly published and captured throughout the parsing lifecycle.

## File Created

- `tests/integration/test_e2e_dsv_pubsub_workflow.py` - Contains 12 comprehensive integration tests

## Test Coverage

### Tests Implemented

1. **test_parse_single_string_with_event_tracking** - Tests single string parsing with event capture
2. **test_parse_multiple_strings_with_event_tracking** - Tests batch string parsing with events
3. **test_parse_file_with_event_tracking** - Tests file parsing with lifecycle events
4. **test_parse_file_stream_with_event_tracking** - Tests streaming file parsing with events
5. **test_parse_error_with_event_tracking** - Tests error handling and error event publishing
6. **test_multiple_dsv_instances_independent_correlation_ids** - Verifies each Dsv instance has unique correlation_id
7. **test_dsv_and_dsvhelper_share_separate_pubsub_instances** - Verifies separate PubSub instances
8. **test_event_flow_parse_workflow** - Tests complete event flow and ordering
9. **test_bookend_removal_with_event_tracking** - Tests bookend processing with events
10. **test_detect_columns_with_event_tracking** - Tests column detection with events
11. **test_tab_delimited_with_event_tracking** - Tests tab-delimited parsing with events
12. **test_parse_file_with_skip_header_and_event_tracking** - Tests header skipping with events

## Key Features

### Event Tracking

Each test:
- Creates a `Dsv()` instance with its own unique `correlation_id`
- Subscribes to all topics (`'*'`) for both `Dsv.get_pubsub()` and `DsvHelper.get_pubsub()` global instances
- Uses a single callback function for both subscriptions
- Uses an `event_tracker` fixture to capture all events

### Callback Implementation

The event callback accepts a `Message` object from the PubSub framework:

```python
def callback(message: Message) -> None:
    """Callback to capture events from both Dsv and DsvHelper pubsub instances."""
    event_info = {
        "topic": message.topic,
        "data": message.data,
        "correlation_id": message.correlation_id,
    }
    event_tracker["events"].append(event_info)
    # ... tracking and counting logic
```

### Verification Points

Each test verifies:
- **Parse results** - Correct tokenization and parsing outcomes
- **Event capture** - Events were captured for the operation
- **Correlation ID** - All events include the correct correlation_id
- **Lifecycle events** - Expected begin/end/error events are present
- **Event flow** - Events follow expected ordering

## Event Topics Captured

The tests verify the following event topics are published:

- `dsv.init` - Dsv instance initialization
- `dsv.parse.begin` / `dsv.parse.end` - Single string parsing lifecycle
- `dsv.parses.begin` / `dsv.parses.end` - Batch string parsing lifecycle
- `dsv.parse.file.begin` / `dsv.parse.file.end` - File parsing lifecycle
- `dsv.parse.file.stream.begin` / `dsv.parse.file.stream.end` - Stream parsing lifecycle
- `dsv.parse.error` / `dsv.parse.file.error` - Error events
- `dsv.helper.parse.begin` / `dsv.helper.parse.end` - Helper method lifecycle
- `dsv.helper.parses.begin` / `dsv.helper.parses.end` - Helper batch lifecycle
- `dsv.helper.parse.file.begin` / `dsv.helper.parse.file.end` - Helper file lifecycle
- `dsv.helper.parse.file.stream.begin` / `dsv.helper.parse.file.stream.end` - Helper stream lifecycle
- `dsv.helper.parse.error` / `dsv.parses.error` - Helper error events

## Test Fixtures

- **event_tracker** - Dictionary tracking captured events, counts by topic, and counts by correlation_id
- **event_callback** - Callable that captures events from PubSub messages

## Workflow Example

```python
# Create Dsv instance
config = DsvConfig(delimiter=",")
dsv_obj = Dsv(config)
correlation_id = dsv_obj.correlation_id

# Subscribe to all topics for this correlation_id
dsv_pubsub = Dsv.get_pubsub()
dsv_helper_pubsub = DsvHelper.get_pubsub()

dsv_pubsub.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id)
dsv_helper_pubsub.subscribe(topic="*", callback=event_callback, correlation_id=correlation_id)

# Parse content
result = dsv_obj.parse("a,b,c")

# Events captured with correlation_id tracing
# event_tracker["events"] contains all published events
```

## Test Results

All 12 tests pass successfully:

```
tests/integration/test_e2e_dsv_pubsub_workflow.py::TestDsvToDsvHelperPubSubWorkflow::test_parse_single_string_with_event_tracking PASSED
tests/integration/test_e2e_dsv_pubsub_workflow.py::TestDsvToDsvHelperPubSubWorkflow::test_parse_multiple_strings_with_event_tracking PASSED
tests/integration/test_e2e_dsv_pubsub_workflow.py::TestDsvToDsvHelperPubSubWorkflow::test_parse_file_with_event_tracking PASSED
tests/integration/test_e2e_dsv_pubsub_workflow.py::TestDsvToDsvHelperPubSubWorkflow::test_parse_file_stream_with_event_tracking PASSED
tests/integration/test_e2e_dsv_pubsub_workflow.py::TestDsvToDsvHelperPubSubWorkflow::test_parse_error_with_event_tracking PASSED
tests/integration/test_e2e_dsv_pubsub_workflow.py::TestDsvToDsvHelperPubSubWorkflow::test_multiple_dsv_instances_independent_correlation_ids PASSED
tests/integration/test_e2e_dsv_pubsub_workflow.py::TestDsvToDsvHelperPubSubWorkflow::test_dsv_and_dsvhelper_share_separate_pubsub_instances PASSED
tests/integration/test_e2e_dsv_pubsub_workflow.py::TestDsvToDsvHelperPubSubWorkflow::test_event_flow_parse_workflow PASSED
tests/integration/test_e2e_dsv_pubsub_workflow.py::TestDsvToDsvHelperPubSubWorkflow::test_bookend_removal_with_event_tracking PASSED
tests/integration/test_e2e_dsv_pubsub_workflow.py::TestDsvToDsvHelperPubSubWorkflow::test_detect_columns_with_event_tracking PASSED
tests/integration/test_e2e_dsv_pubsub_workflow.py::TestDsvToDsvHelperPubSubWorkflow::test_tab_delimited_with_event_tracking PASSED
tests/integration/test_e2e_dsv_pubsub_workflow.py::TestDsvToDsvHelperPubSubWorkflow::test_parse_file_with_skip_header_and_event_tracking PASSED

======================== 12 passed ========================
```

## Integration with Existing Tests

- All 66 integration tests pass (2 skipped for platform compatibility)
- All 191 unit tests pass
- No breaking changes to existing functionality

## Usage

Run the new tests:

```bash
python -m pytest tests/integration/test_e2e_dsv_pubsub_workflow.py -v
```

Run all tests:

```bash
python -m pytest tests/ -v
```
