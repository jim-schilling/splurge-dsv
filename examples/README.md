# Splurge-DSV Examples

This directory contains comprehensive examples demonstrating how to use the splurge-dsv library.

## End-to-End Parsing with Event Tracking

The `api_with_events.py` file demonstrates end-to-end DSV parsing workflows with event subscriptions and correlation tracking using the PubSub framework.

### Features Demonstrated

- **Event-Driven Architecture**: Subscribe to parsing lifecycle events
- **Correlation Tracking**: Track operations using correlation_id across parsing pipeline
- **Multiple PubSub Instances**: Separate subscriptions for Dsv and DsvHelper
- **Event Topics**: Understand all lifecycle events (begin, end, error)
- **Basic Parsing**: Single strings, batch operations with full event tracking
- **File Operations**: Complete file parsing with event monitoring
- **Streaming**: Large file processing with chunk-level events
- **Advanced Features**: Bookend removal, column detection, multiple instances

### Running the End-to-End Event Example

From the project root directory:

```bash
# Using module execution (recommended)
python -m examples.api_with_events

# Or directly
PYTHONPATH=. python examples/api_with_events.py
```

### Key Patterns Demonstrated

- **Event Subscription**: How to subscribe to all topics with specific correlation_id
- **Callback Implementation**: Receiving Message objects from PubSub
- **Lifecycle Tracking**: From parse.begin through parse.end or parse.error
- **Correlation Tracing**: Following operations across multiple services

## Modern API Example

The `modern_api_example.py` file demonstrates the new object-oriented Dsv API introduced in version 2025.1.x.

### Features Demonstrated

- **Configuration Management**: DsvConfig dataclass with validation and factory methods
- **Object-Oriented API**: Dsv class for encapsulated parsing operations
- **Configuration Reuse**: Single configuration instance used across multiple operations
- **Type Safety**: Immutable configurations with runtime validation
- **Backwards Compatibility**: New API works alongside existing DsvHelper methods
- **Factory Methods**: Convenient constructors for CSV and TSV formats

### Running the Modern API Example

From the project root directory:

```bash
# Set PYTHONPATH to include the current directory
PYTHONPATH=. python examples/modern_api_example.py
```

On Windows:

```cmd
set PYTHONPATH=.
python examples/modern_api_example.py
```

## API Usage Example

The `api_usage_example.py` file provides a comprehensive demonstration of all the key features of the splurge-dsv library.

### Features Demonstrated

- **String Tokenization**: Basic parsing, stripping, empty token handling, multiple delimiters, and bookend removal
- **Path Validation**: Security checks, dangerous character detection, and traversal pattern prevention
- **Text File Operations**: Line counting, file previewing, streaming, and chunking
- **DSV Parsing**: File parsing, streaming, custom delimiters, and header/footer skipping
- **Resource Management**: Context managers, safe file operations, and stream management
- **Error Handling**: Custom exception handling and error recovery
- **Advanced Features**: Complex data processing and analysis

### Running the Example

From the project root directory:

```bash
# Set PYTHONPATH to include the current directory
PYTHONPATH=. python examples/api_usage_example.py
```

On Windows:

```cmd
set PYTHONPATH=.
python examples/api_usage_example.py
```

### Expected Output

The example will output detailed demonstrations of each feature with clear success/failure indicators:

```
SPLURGE-DSV COMPREHENSIVE API USAGE EXAMPLE
============================================================
This example demonstrates all key features of the splurge-dsv library.
Each section shows practical usage patterns and error handling.

============================================================
STRING TOKENIZER EXAMPLES
============================================================
Basic parsing: ['apple', 'banana', 'cherry', 'date']
With stripping: ['apple', 'banana', 'cherry', 'date']
...
```

### Learning from the Example

1. **Start with the sections that interest you most** - each section is self-contained
2. **Study the error handling patterns** - shows how to handle various failure scenarios
3. **Examine the resource management examples** - demonstrates safe file and stream operations
4. **Look at the advanced features** - shows how to combine multiple features for complex tasks

### Key Patterns Demonstrated

- **Safe file operations** with automatic cleanup
- **Path validation** before file operations
- **Streaming** for memory-efficient processing
- **Error handling** with custom exceptions
- **Resource management** with context managers
- **Data processing** with configurable options

This example serves as both documentation and a practical reference for using the splurge-dsv library effectively.
