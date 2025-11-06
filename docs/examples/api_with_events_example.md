# End-to-End DSV Parsing with Event Tracking - Example API

## Overview

Created `examples/api_with_events.py` - A comprehensive example demonstrating end-to-end DSV parsing with PubSub event subscriptions and correlation_id tracing.

## File Details

**Location**: `d:\repos\splurge-dsv\examples\api_with_events.py`  
**Size**: 289 lines  
**Type**: Executable example with 6 demonstration scenarios  

## Features

### 1. Event Subscription Pattern

Each example demonstrates:
- Creating a `Dsv()` instance with unique `correlation_id`
- Subscribing to all topics (`'*'`) on both `Dsv.get_pubsub()` and `DsvHelper.get_pubsub()`
- Using a callback that prints `Message.topic`
- Tracking events throughout the parsing lifecycle

### 2. Event Callback

```python
def event_callback(message: Message) -> None:
    """Callback to print event topics during parsing operations."""
    print(f"[EVENT] Topic: {message.topic:40s} | Correlation ID: {message.correlation_id}")
```

The callback accepts a `Message` object and prints:
- Topic name (aligned to 40 characters)
- Correlation ID for operation tracing

### 3. Example Scenarios

#### Example 1: Basic String Parsing
- Single string tokenization
- Shows 4 events: `dsv.parse.begin`, `dsv.helper.parse.begin`, `dsv.helper.parse.end`, `dsv.parse.end`

#### Example 2: Batch String Parsing
- Multiple strings (3 rows)
- Shows nested events for each row: `dsv.parses.begin` → multiple `dsv.helper.parse` events → `dsv.parses.end`

#### Example 3: File Parsing
- Complete file read with header skipping
- Shows `dsv.parse.file.*` events at higher level
- Shows `dsv.helper.parse.*` and `dsv.helper.parses.*` events for each row

#### Example 4: Streaming File Parsing
- Large file processing with chunk_size=50
- Shows stream-specific events: `dsv.parse.file.stream.begin/end`
- Tracks chunked processing within stream

#### Example 5: Bookend Removal
- Parsing quoted CSV values with `bookend='"'`
- Shows parsing events with special character handling
- Result: `['John Doe', '30', 'New York']` (quotes removed)

#### Example 6: Multiple Instances
- Two independent `Dsv` instances with different delimiters
- Shows independent correlation IDs
- Demonstrates filtering events by correlation_id

## Running the Example

### Method 1: Module Execution (Recommended)
```bash
python -m examples.api_with_events
```

### Method 2: Direct Execution
```bash
PYTHONPATH=. python examples/api_with_events.py
```

On Windows:
```cmd
set PYTHONPATH=.
python examples/api_with_events.py
```

## Sample Output

```
##########################################################################################
# Splurge-DSV: End-to-End Parsing with Event Tracking and Correlation IDs
##########################################################################################

==========================================================================================
Example 1: Basic String Parsing with Event Tracking
==========================================================================================

Created Dsv instance with correlation_id: fcd37078-b534-4cc5-bb02-769cbdb63e25
Subscribed to all events (*) for both Dsv and DsvHelper PubSub instances

Parsing: name,age,city
[EVENT] Topic: dsv.parse.begin                          | Correlation ID: fcd37078-b534-4cc5-bb02-769cbdb63e25
[EVENT] Topic: dsv.helper.parse.begin                   | Correlation ID: fcd37078-b534-4cc5-bb02-769cbdb63e25
[EVENT] Topic: dsv.helper.parse.end                     | Correlation ID: fcd37078-b534-4cc5-bb02-769cbdb63e25
[EVENT] Topic: dsv.parse.end                            | Correlation ID: fcd37078-b534-4cc5-bb02-769cbdb63e25
Result: ['name', 'age', 'city']
```

## Event Topics Demonstrated

### Initialization Events
- `dsv.init` - Instance creation

### String Parsing Events
- `dsv.parse.begin` / `dsv.parse.end` - Single string parsing
- `dsv.parses.begin` / `dsv.parses.end` - Batch string parsing

### File Operations Events
- `dsv.parse.file.begin` / `dsv.parse.file.end` - File parsing
- `dsv.parse.file.stream.begin` / `dsv.parse.file.stream.end` - Stream parsing

### Helper Method Events
- `dsv.helper.parse.begin` / `dsv.helper.parse.end` - Helper parsing
- `dsv.helper.parses.begin` / `dsv.helper.parses.end` - Helper batch
- `dsv.helper.parse.file.begin` / `dsv.helper.parse.file.end` - Helper file
- `dsv.helper.parse.file.stream.begin` / `dsv.helper.parse.file.stream.end` - Helper stream

### Error Events
- `dsv.parse.error` - Parse operation error
- `dsv.helper.parse.error` - Helper operation error

## Key Learning Points

1. **Correlation ID**: Each operation gets unique UUID for tracing
2. **Event Flow**: Events flow from Dsv → DsvHelper with same correlation_id
3. **Topic Naming**: Topics use dot notation for hierarchical organization
4. **Subscription**: Subscribe once for all events with specific correlation_id
5. **Message Structure**: Each event is a Message with topic, data, and correlation_id

## Integration with Examples Directory

The example has been added to `examples/README.md` with:
- Feature documentation
- Running instructions
- Sample output
- Learning patterns

## Files Updated

- `examples/api_with_events.py` - **Created** (new example)
- `examples/README.md` - **Updated** (added documentation)

## Compatibility

- ✅ Works with Python 3.10+
- ✅ Compatible with current splurge-dsv version
- ✅ Uses public APIs only
- ✅ No external dependencies beyond splurge-dsv
- ✅ Cross-platform (Windows, Linux, macOS)

## Usage in Tests

The example aligns with the test suite in:
- `tests/integration/test_e2e_dsv_pubsub_workflow.py` (12 comprehensive tests)

All 12 tests pass, demonstrating the same patterns shown in this example.
