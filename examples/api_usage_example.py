#!/usr/bin/env python3
"""
Comprehensive API Usage Example for splurge-dsv

This example demonstrates all the key features of the splurge-dsv library:
- DSV (Delimiter-Separated Values) parsing and processing
- Text file operations with streaming and chunking
- Path validation and security
- Resource management with context managers
- Error handling with custom exceptions

Copyright (c) 2025 Jim Schilling

This example is licensed under the MIT License.
"""

import os
import tempfile
from pathlib import Path
from typing import List, Dict, Any

from splurge_dsv.dsv_helper import DsvHelper
from splurge_dsv.text_file_helper import TextFileHelper
from splurge_dsv.path_validator import PathValidator
from splurge_dsv.resource_manager import (
    FileResourceManager,
    StreamResourceManager,
    safe_file_operation,
    safe_stream_operation
)
from splurge_dsv.string_tokenizer import StringTokenizer
from splurge_dsv.exceptions import (
    SplurgePathValidationError,
    SplurgeFileNotFoundError,
    SplurgeFilePermissionError,
    SplurgeFileEncodingError,
    SplurgeResourceAcquisitionError,
    SplurgeResourceReleaseError,
    SplurgeParameterError
)


def create_sample_data() -> str:
    """Create sample DSV data for demonstration."""
    return """name,age,city,occupation
John Doe,30,New York,Engineer
Jane Smith,25,Los Angeles,Designer
Bob Johnson,35,Chicago,Manager
Alice Brown,28,Boston,Developer
Charlie Wilson,32,Seattle,Analyst
Diana Davis,29,Austin,Consultant
Eve Miller,31,Denver,Architect
Frank Garcia,27,Miami,Designer
Grace Lee,33,Portland,Engineer
Henry Taylor,26,Atlanta,Developer"""


def create_sample_file(file_path: Path, content: str) -> None:
    """Create a sample file with the given content."""
    with safe_file_operation(file_path, mode="w") as file_handle:
        file_handle.write(content)
    print(f"✓ Created sample file: {file_path}")


def demonstrate_string_tokenizer() -> None:
    """Demonstrate the StringTokenizer functionality."""
    print("\n" + "="*60)
    print("STRING TOKENIZER EXAMPLES")
    print("="*60)
    
    # Basic tokenization
    text = "apple,banana,cherry,date"
    tokens = StringTokenizer.parse(text, delimiter=",")
    print(f"Basic parsing: {tokens}")
    
    # Tokenization with stripping
    text_with_spaces = "  apple  ,  banana  ,  cherry  ,  date  "
    tokens_stripped = StringTokenizer.parse(text_with_spaces, delimiter=",", strip=True)
    print(f"With stripping: {tokens_stripped}")
    
    # Preserving empty tokens
    text_with_empty = "apple,,cherry,"
    tokens_with_empty = StringTokenizer.parse(text_with_empty, delimiter=",", strip=False)
    print(f"Preserving empty tokens: {tokens_with_empty}")
    
    # Different delimiters
    pipe_text = "red|green|blue|yellow"
    pipe_tokens = StringTokenizer.parse(pipe_text, delimiter="|")
    print(f"Pipe delimiter: {pipe_tokens}")
    
    # Multiple string parsing
    multiple_texts = ["a,b,c", "d,e,f", "g,h,i"]
    multiple_tokens = StringTokenizer.parses(multiple_texts, delimiter=",")
    print(f"Multiple strings: {multiple_tokens}")
    
    # Bookend removal
    bookend_text = "**important**"
    bookend_result = StringTokenizer.remove_bookends(bookend_text, bookend="**")
    print(f"Bookend removal: {bookend_result}")


def demonstrate_path_validation() -> None:
    """Demonstrate path validation functionality."""
    print("\n" + "="*60)
    print("PATH VALIDATION EXAMPLES")
    print("="*60)
    
    # Valid paths
    valid_paths = [
        "data/input.csv",
        "C:/Users/username/Documents/file.txt",
        "/home/user/data/sample.json",
        "relative/path/to/file.dat"
    ]
    
    for path in valid_paths:
        try:
            validated_path = PathValidator.validate_path(path)
            print(f"✓ Valid path: {path} -> {validated_path}")
        except SplurgePathValidationError as e:
            print(f"✗ Invalid path: {path} - {e.message}")
    
    # Invalid paths (these should fail)
    invalid_paths = [
        "../../../etc/passwd",  # Path traversal
        "file<with>invalid:chars?.txt",  # Invalid characters
        "//absolute/path",  # Multiple slashes
        "C:file.txt",  # Invalid colon usage
    ]
    
    for path in invalid_paths:
        try:
            PathValidator.validate_path(path)
            print(f"✗ Unexpectedly valid: {path}")
        except SplurgePathValidationError as e:
            print(f"✓ Correctly rejected: {path} - {e.message}")


def demonstrate_text_file_operations() -> None:
    """Demonstrate text file helper operations."""
    print("\n" + "="*60)
    print("TEXT FILE OPERATIONS")
    print("="*60)
    
    # Create a temporary file for demonstration
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        temp_path = Path(temp_file.name)
        sample_content = """Line 1: Basic content
Line 2: More content
Line 3: Even more content
Line 4: Final line"""
        temp_file.write(sample_content)
    
    try:
        # Line counting
        line_count = TextFileHelper.line_count(temp_path)
        print(f"✓ Line count: {line_count}")
        
        # File preview
        preview = TextFileHelper.preview(temp_path, max_lines=2)
        print(f"✓ Preview (2 lines): {preview}")
        
        # Complete file reading
        full_content = TextFileHelper.read(temp_path)
        print(f"✓ Full content ({len(full_content)} lines): {full_content[:2]}...")
        
        # Streaming with chunking
        print("✓ Streaming content:")
        for chunk in TextFileHelper.read_as_stream(temp_path, chunk_size=2):
            print(f"  Chunk: {chunk}")
        
        # Reading with header skipping
        content_with_header = TextFileHelper.read(
            temp_path, 
            skip_header_rows=1
        )
        print(f"✓ Content with header skipped: {content_with_header}")
        
    finally:
        # Clean up
        temp_path.unlink()


def demonstrate_dsv_parsing() -> None:
    """Demonstrate DSV parsing functionality."""
    print("\n" + "="*60)
    print("DSV PARSING EXAMPLES")
    print("="*60)
    
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        temp_path = Path(temp_file.name)
        sample_data = create_sample_data()
        temp_file.write(sample_data)
    
    try:
        # Basic parsing
        parsed_data = DsvHelper.parse_file(temp_path, delimiter=",")
        print(f"✓ Parsed {len(parsed_data)} rows")
        print(f"✓ First row: {parsed_data[0]}")
        
        # Parsing with custom delimiter
        pipe_data = "name|age|city\nJohn|30|NYC\nJane|25|LA"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as pipe_file:
            pipe_path = Path(pipe_file.name)
            pipe_file.write(pipe_data)
        
        try:
            pipe_parsed = DsvHelper.parse_file(pipe_path, delimiter="|")
            print(f"✓ Pipe-delimited parsing: {pipe_parsed}")
        finally:
            pipe_path.unlink()
        
        # Streaming parsing
        print("✓ Streaming parsing:")
        for chunk in DsvHelper.parse_stream(temp_path, delimiter=",", chunk_size=2):
            print(f"  Chunk: {chunk}")
        
        # Parsing with header skipping
        parsed_no_header = DsvHelper.parse_file(
            temp_path, 
            delimiter=",",
            skip_header_rows=1
        )
        print(f"✓ Parsed without header: {len(parsed_no_header)} rows")
        
        # Parsing with custom options
        parsed_custom = DsvHelper.parse_file(
            temp_path,
            delimiter=",",
            strip=True
        )
        print(f"✓ Custom parsing: {len(parsed_custom)} rows")
        
    finally:
        # Clean up
        temp_path.unlink()


def demonstrate_resource_management() -> None:
    """Demonstrate resource management functionality."""
    print("\n" + "="*60)
    print("RESOURCE MANAGEMENT EXAMPLES")
    print("="*60)
    
    # Create a temporary file for demonstration
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        temp_path = Path(temp_file.name)
        temp_file.write("Resource management test content")
    
    try:
        # FileResourceManager example
        print("✓ FileResourceManager:")
        with FileResourceManager(temp_path, mode="r") as file_handle:
            content = file_handle.read()
            print(f"  Read content: {content}")
        
        # safe_file_operation example
        print("✓ safe_file_operation:")
        with safe_file_operation(temp_path, mode="r") as file_handle:
            content = file_handle.read()
            print(f"  Read content: {content}")
        
        # StreamResourceManager example
        print("✓ StreamResourceManager:")
        stream = iter(["item1", "item2", "item3"])
        with StreamResourceManager(stream) as managed_stream:
            items = list(managed_stream)
            print(f"  Stream items: {items}")
        
        # safe_stream_operation example
        print("✓ safe_stream_operation:")
        stream2 = iter(["data1", "data2", "data3"])
        with safe_stream_operation(stream2) as managed_stream:
            items = list(managed_stream)
            print(f"  Stream items: {items}")
        
        # Writing with resource management
        output_path = temp_path.parent / "output.txt"
        with safe_file_operation(output_path, mode="w") as file_handle:
            file_handle.write("Written with safe_file_operation")
        
        print(f"✓ Wrote to: {output_path}")
        
        # Clean up output file
        output_path.unlink()
        
    finally:
        # Clean up
        temp_path.unlink()


def demonstrate_error_handling() -> None:
    """Demonstrate error handling with custom exceptions."""
    print("\n" + "="*60)
    print("ERROR HANDLING EXAMPLES")
    print("="*60)
    
    # Path validation errors
    print("✓ Path validation errors:")
    try:
        PathValidator.validate_path("../../../etc/passwd")
    except SplurgePathValidationError as e:
        print(f"  Caught: {e.message}")
    
    try:
        PathValidator.validate_path("file<with>invalid:chars?.txt")
    except SplurgePathValidationError as e:
        print(f"  Caught: {e.message}")
    
    # File operation errors
    print("✓ File operation errors:")
    nonexistent_file = Path("/nonexistent/file.txt")
    try:
        with safe_file_operation(nonexistent_file, mode="r"):
            pass
    except SplurgeFileNotFoundError as e:
        print(f"  Caught: {e.message}")
    
    # Resource management errors
    print("✓ Resource management errors:")
    try:
        with safe_file_operation("file<with>invalid:chars?.txt", mode="r"):
            pass
    except SplurgePathValidationError as e:
        print(f"  Caught: {e.message}")
    
    # Parameter errors
    print("✓ Parameter errors:")
    try:
        StringTokenizer.parse("test", delimiter="")  # Empty delimiter
    except SplurgeParameterError as e:
        print(f"  Caught: {e.message}")


def demonstrate_advanced_features() -> None:
    """Demonstrate advanced features and combinations."""
    print("\n" + "="*60)
    print("ADVANCED FEATURES")
    print("="*60)
    
    # Create a complex DSV file with various features
    complex_data = """# This is a comment
name,age,city,occupation,salary
John Doe,30,New York,Engineer,75000
Jane Smith,25,Los Angeles,Designer,65000
Bob Johnson,35,Chicago,Manager,85000
# Another comment
Alice Brown,28,Boston,Developer,70000
Charlie Wilson,32,Seattle,Analyst,72000
# End of data"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        temp_path = Path(temp_file.name)
        temp_file.write(complex_data)
    
    try:
        # Advanced DSV parsing with multiple options
        
        # Parse with comment handling (skip lines starting with #)
        parsed_data = DsvHelper.parse_file(
            temp_path,
            delimiter=",",
            skip_header_rows=1,
            strip=True
        )
        print(f"✓ Parsed complex data: {len(parsed_data)} rows")
        
        # Process the data
        for i, row in enumerate(parsed_data):
            if len(row) >= 5:  # Ensure we have enough columns
                name, age, city, occupation, salary = row[:5]
                print(f"  Row {i+1}: {name} ({age}) - {occupation} in {city}")
        
        # Streaming with processing
        print("✓ Streaming with processing:")
        total_salary = 0
        count = 0
        
        for chunk in DsvHelper.parse_stream(temp_path, delimiter=",", chunk_size=2):
            for row in chunk:
                if len(row) >= 5 and row[4].isdigit():
                    total_salary += int(row[4])
                    count += 1
        
        if count > 0:
            avg_salary = total_salary / count
            print(f"  Average salary: ${avg_salary:,.2f}")
        
        # File analysis
        print("✓ File analysis:")
        line_count = TextFileHelper.line_count(temp_path)
        preview = TextFileHelper.preview(temp_path, max_lines=3)
        print(f"  Total lines: {line_count}")
        print(f"  Preview: {preview}")
        
    finally:
        # Clean up
        temp_path.unlink()


def main() -> None:
    """Main function to run all demonstrations."""
    print("SPLURGE-DSV COMPREHENSIVE API USAGE EXAMPLE")
    print("="*60)
    print("This example demonstrates all key features of the splurge-dsv library.")
    print("Each section shows practical usage patterns and error handling.")
    
    try:
        # Run all demonstrations
        demonstrate_string_tokenizer()
        demonstrate_path_validation()
        demonstrate_text_file_operations()
        demonstrate_dsv_parsing()
        demonstrate_resource_management()
        demonstrate_error_handling()
        demonstrate_advanced_features()
        
        print("\n" + "="*60)
        print("✓ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*60)
        print("This example demonstrates:")
        print("• String tokenization with various delimiters and options")
        print("• Path validation and security checks")
        print("• Text file operations (reading, streaming, chunking)")
        print("• DSV parsing with custom delimiters and options")
        print("• Resource management with context managers")
        print("• Comprehensive error handling")
        print("• Advanced features and data processing")
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()
