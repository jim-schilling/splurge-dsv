"""
End-to-end workflow tests for splurge-dsv.

Tests complete workflows including file processing,
error handling, and integration scenarios.
"""

# Standard library imports
import os
import subprocess
import sys
from pathlib import Path

# Third-party imports
import pytest


class TestEndToEndCLIWorkflows:
    """Test complete CLI workflows with real files."""

    @pytest.fixture
    def cli_command(self) -> str:
        """Get the CLI command to run."""
        # Try to find the CLI script
        possible_paths = [
            "splurge-dsv",
            "python -m splurge_dsv",
            f"{sys.executable} -m splurge_dsv",
        ]

        for cmd in possible_paths:
            try:
                # Split the command if it contains spaces
                if " " in cmd:
                    cmd_parts = cmd.split() + ["--help"]
                else:
                    cmd_parts = [cmd, "--help"]

                result = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return cmd
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                continue

        # Fallback to module execution
        return f"{sys.executable} -m splurge_dsv"

    @pytest.fixture
    def sample_csv_file(self, tmp_path: Path) -> Path:
        """Create a sample CSV file for testing."""
        csv_content = """name,age,city,occupation
John Doe,30,New York,Engineer
Jane Smith,25,Los Angeles,Designer
Bob Johnson,35,Chicago,Manager
Alice Brown,28,Boston,Developer
Charlie Wilson,32,Seattle,Analyst"""

        file_path = tmp_path / "sample.csv"
        file_path.write_text(csv_content)
        return file_path

    @pytest.fixture
    def sample_tsv_file(self, tmp_path: Path) -> Path:
        """Create a sample TSV file for testing."""
        tsv_content = """name\tage\tcity\toccupation
John Doe\t30\tNew York\tEngineer
Jane Smith\t25\tLos Angeles\tDesigner
Bob Johnson\t35\tChicago\tManager
Alice Brown\t28\tBoston\tDeveloper
Charlie Wilson\t32\tSeattle\tAnalyst"""

        file_path = tmp_path / "sample.tsv"
        file_path.write_text(tsv_content)
        return file_path

    @pytest.fixture
    def large_csv_file(self, tmp_path: Path) -> Path:
        """Create a large CSV file for testing streaming."""
        file_path = tmp_path / "large.csv"

        # Create header
        lines = ["id,name,value,description"]

        # Create 1000 data rows
        for i in range(1000):
            lines.append(f"{i},Item{i},Value{i},Description for item {i}")

        file_path.write_text("\n".join(lines))
        return file_path

    @pytest.fixture
    def unicode_csv_file(self, tmp_path: Path) -> Path:
        """Create a CSV file with unicode content."""
        unicode_content = """name,age,city,occupation
José García,30,México,Ingeniero
François Dubois,25,Paris,Développeur
李小明,28,北京,工程师
Анна Иванова,32,Москва,Архитектор
محمد أحمد,29,القاهرة,مطور"""

        file_path = tmp_path / "unicode.csv"
        file_path.write_text(unicode_content, encoding="utf-8")
        return file_path

    @pytest.fixture
    def malformed_csv_file(self, tmp_path: Path) -> Path:
        """Create a malformed CSV file for testing error handling."""
        malformed_content = """name,age,city,occupation
John Doe,30,New York,Engineer
Jane Smith,25,Los Angeles,Designer
Bob Johnson,35,Chicago,Manager
Alice Brown,28,Boston,Developer
Charlie Wilson,32,Seattle,Analyst
Incomplete,row,with,missing,columns
Another,incomplete,row"""

        file_path = tmp_path / "malformed.csv"
        file_path.write_text(malformed_content)
        return file_path

    def run_cli_command(self, cli_command: str, args: list[str]) -> tuple[int, str, str]:
        """Run the CLI command and return results."""
        try:
            # Split the command if it contains spaces
            if " " in cli_command:
                cmd_parts = cli_command.split() + args
            else:
                cmd_parts = [cli_command] + args

            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.getcwd(),
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", f"Command execution error: {e}"

    def test_basic_csv_parsing_workflow(self, cli_command: str, sample_csv_file: Path) -> None:
        """Test basic CSV parsing workflow."""
        returncode, stdout, stderr = self.run_cli_command(cli_command, [str(sample_csv_file), "--delimiter", ","])

        assert returncode == 0, f"CLI failed with stderr: {stderr}"
        assert "John Doe" in stdout
        assert "Jane Smith" in stdout
        assert "Bob Johnson" in stdout
        assert "Engineer" in stdout
        assert "Designer" in stdout

    def test_tsv_parsing_workflow(self, cli_command: str, sample_tsv_file: Path) -> None:
        """Test TSV parsing workflow."""
        returncode, stdout, stderr = self.run_cli_command(cli_command, [str(sample_tsv_file), "--delimiter", "\t"])

        assert returncode == 0, f"CLI failed with stderr: {stderr}"
        assert "John Doe" in stdout
        assert "Jane Smith" in stdout
        assert "Engineer" in stdout

    def test_custom_delimiter_workflow(self, cli_command: str, tmp_path: Path) -> None:
        """Test custom delimiter parsing workflow."""
        # Create file with pipe delimiter
        pipe_content = """name|age|city|occupation
John Doe|30|New York|Engineer
Jane Smith|25|Los Angeles|Designer"""

        pipe_file = tmp_path / "pipe.txt"
        pipe_file.write_text(pipe_content)

        returncode, stdout, stderr = self.run_cli_command(cli_command, [str(pipe_file), "--delimiter", "|"])

        assert returncode == 0, f"CLI failed with stderr: {stderr}"
        assert "John Doe" in stdout
        assert "Jane Smith" in stdout

    def test_header_skipping_workflow(self, cli_command: str, sample_csv_file: Path) -> None:
        """Test header skipping workflow."""
        returncode, stdout, stderr = self.run_cli_command(
            cli_command, [str(sample_csv_file), "--delimiter", ",", "--skip-header", "1"]
        )

        assert returncode == 0, f"CLI failed with stderr: {stderr}"
        # Header should be skipped, so "name,age,city,occupation" should not appear
        assert "name,age,city,occupation" not in stdout
        # But data should still be there
        assert "John Doe" in stdout
        assert "Jane Smith" in stdout

    def test_footer_skipping_workflow(self, cli_command: str, sample_csv_file: Path) -> None:
        """Test footer skipping workflow."""
        returncode, stdout, stderr = self.run_cli_command(
            cli_command, [str(sample_csv_file), "--delimiter", ",", "--skip-footer", "1"]
        )

        assert returncode == 0, f"CLI failed with stderr: {stderr}"
        # Last row should be skipped
        assert "Charlie Wilson" not in stdout
        # But other data should still be there
        assert "John Doe" in stdout
        assert "Jane Smith" in stdout

    def test_streaming_workflow(self, cli_command: str, large_csv_file: Path) -> None:
        """Test streaming workflow with large file."""
        returncode, stdout, stderr = self.run_cli_command(
            cli_command, [str(large_csv_file), "--delimiter", ",", "--stream"]
        )

        assert returncode == 0, f"CLI failed with stderr: {stderr}"
        # Should process all 1000 rows
        assert "Item0" in stdout
        assert "Item999" in stdout
        # Check that we have the expected number of lines in output
        output_lines = [line for line in stdout.split("\n") if line.strip()]
        assert len(output_lines) >= 1000

    def test_unicode_workflow(self, cli_command: str, unicode_csv_file: Path) -> None:
        """Test unicode content workflow."""
        # Skip this test on Windows due to encoding issues in CLI output
        if os.name == "nt":  # Windows
            pytest.skip("Unicode test skipped on Windows due to CLI output encoding issues")

        returncode, stdout, stderr = self.run_cli_command(
            cli_command, [str(unicode_csv_file), "--delimiter", ",", "--encoding", "utf-8"]
        )

        assert returncode == 0, f"CLI failed with stderr: {stderr}"
        assert "José García" in stdout
        assert "François Dubois" in stdout
        assert "李小明" in stdout
        assert "Анна Иванова" in stdout
        assert "محمد أحمد" in stdout

    def test_no_strip_workflow(self, cli_command: str, tmp_path: Path) -> None:
        """Test no-strip workflow."""
        # Create file with spaces around values
        spaced_content = """name , age , city , occupation
 John Doe , 30 , New York , Engineer
 Jane Smith , 25 , Los Angeles , Designer"""

        spaced_file = tmp_path / "spaced.csv"
        spaced_file.write_text(spaced_content)

        returncode, stdout, stderr = self.run_cli_command(
            cli_command, [str(spaced_file), "--delimiter", ",", "--no-strip"]
        )

        assert returncode == 0, f"CLI failed with stderr: {stderr}"
        # Spaces should be preserved
        assert " John Doe " in stdout
        assert " 30 " in stdout

    def test_bookend_workflow(self, cli_command: str, tmp_path: Path) -> None:
        """Test bookend removal workflow."""
        # Create file with quoted values
        quoted_content = """name,age,city,occupation
"John Doe",30,"New York","Engineer"
"Jane Smith",25,"Los Angeles","Designer" """

        quoted_file = tmp_path / "quoted.csv"
        quoted_file.write_text(quoted_content)

        returncode, stdout, stderr = self.run_cli_command(
            cli_command, [str(quoted_file), "--delimiter", ",", "--bookend", '"']
        )

        assert returncode == 0, f"CLI failed with stderr: {stderr}"
        # Quotes should be removed
        assert "John Doe" in stdout
        assert "New York" in stdout
        assert '"John Doe"' not in stdout

    def test_chunk_size_workflow(self, cli_command: str, large_csv_file: Path) -> None:
        """Test chunk size workflow."""
        returncode, stdout, stderr = self.run_cli_command(
            cli_command, [str(large_csv_file), "--delimiter", ",", "--stream", "--chunk-size", "100"]
        )

        assert returncode == 0, f"CLI failed with stderr: {stderr}"
        # Should process all rows with chunking
        assert "Item0" in stdout
        assert "Item999" in stdout

    def test_file_not_found_error_workflow(self, cli_command: str, tmp_path: Path) -> None:
        """Test file not found error workflow."""
        nonexistent_file = tmp_path / "nonexistent.csv"

        returncode, stdout, stderr = self.run_cli_command(cli_command, [str(nonexistent_file), "--delimiter", ","])

        assert returncode == 1, "CLI should fail with non-existent file"
        assert "not found" in stderr.lower() or "does not exist" in stderr.lower()

    def test_invalid_delimiter_error_workflow(self, cli_command: str, sample_csv_file: Path) -> None:
        """Test invalid delimiter error workflow."""
        returncode, stdout, stderr = self.run_cli_command(cli_command, [str(sample_csv_file), "--delimiter", ""])

        assert returncode == 1, "CLI should fail with empty delimiter"
        assert "delimiter" in stderr.lower() or "parameter" in stderr.lower()

    def test_directory_path_error_workflow(self, cli_command: str, tmp_path: Path) -> None:
        """Test directory path error workflow."""
        # Create a directory
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()

        returncode, stdout, stderr = self.run_cli_command(cli_command, [str(test_dir), "--delimiter", ","])

        assert returncode == 1, "CLI should fail with directory path"
        assert "not a file" in stderr.lower() or "is a directory" in stderr.lower()

    def test_encoding_error_workflow(self, cli_command: str, tmp_path: Path) -> None:
        """Test encoding error workflow."""
        # Create file with invalid encoding
        encoding_file = tmp_path / "encoding_error.csv"
        # Write binary data that's not valid UTF-8
        encoding_file.write_bytes(b"name,age\nJohn,30\n\xff\xfe\nJane,25")

        returncode, stdout, stderr = self.run_cli_command(
            cli_command, [str(encoding_file), "--delimiter", ",", "--encoding", "utf-8"]
        )

        assert returncode == 1, "CLI should fail with encoding error"
        assert "encoding" in stderr.lower() or "utf" in stderr.lower()

    def test_complex_workflow_with_multiple_options(self, cli_command: str, tmp_path: Path) -> None:
        """Test complex workflow with multiple options."""
        # Create complex file with headers, footers, and quoted values
        complex_content = """name,age,city,occupation,salary
"John Doe",30,"New York","Engineer",75000
"Jane Smith",25,"Los Angeles","Designer",65000
"Bob Johnson",35,"Chicago","Manager",85000
"Alice Brown",28,"Boston","Developer",70000
"Charlie Wilson",32,"Seattle","Analyst",72000"""

        complex_file = tmp_path / "complex.csv"
        complex_file.write_text(complex_content)

        returncode, stdout, stderr = self.run_cli_command(
            cli_command, [str(complex_file), "--delimiter", ",", "--skip-header", "1", "--bookend", '"']
        )

        assert returncode == 0, f"CLI failed with stderr: {stderr}"
        # Should skip header line
        assert "name,age,city,occupation,salary" not in stdout
        # But data should still be there
        assert "John Doe" in stdout
        assert "Jane Smith" in stdout
        assert "Bob Johnson" in stdout
        assert "Alice Brown" in stdout
        assert "Charlie Wilson" in stdout

    def test_performance_workflow_large_file(self, cli_command: str, tmp_path: Path) -> None:
        """Test performance with very large file."""
        # Create a very large file (10,000 rows)
        large_file = tmp_path / "very_large.csv"

        lines = ["id,name,value,description"]
        for i in range(10000):
            lines.append(f"{i},Item{i},Value{i},Description for item {i}")

        large_file.write_text("\n".join(lines))

        # Test streaming mode
        returncode, stdout, stderr = self.run_cli_command(
            cli_command, [str(large_file), "--delimiter", ",", "--stream", "--chunk-size", "500"]
        )

        assert returncode == 0, f"CLI failed with stderr: {stderr}"
        # Should process all rows
        assert "Item0" in stdout
        assert "Item9999" in stdout

    def test_mixed_line_endings_workflow(self, cli_command: str, tmp_path: Path) -> None:
        """Test mixed line endings workflow."""
        # Create file with mixed line endings
        mixed_file = tmp_path / "mixed.csv"
        content = "name,age\r\nJohn,30\nJane,25\rBob,35"
        mixed_file.write_text(content, newline="")

        returncode, stdout, stderr = self.run_cli_command(cli_command, [str(mixed_file), "--delimiter", ","])

        assert returncode == 0, f"CLI failed with stderr: {stderr}"
        # Should handle mixed line endings
        assert "John" in stdout
        assert "Jane" in stdout
        assert "Bob" in stdout

    def test_empty_file_workflow(self, cli_command: str, tmp_path: Path) -> None:
        """Test empty file workflow."""
        empty_file = tmp_path / "empty.csv"
        empty_file.write_text("")

        returncode, stdout, stderr = self.run_cli_command(cli_command, [str(empty_file), "--delimiter", ","])

        assert returncode == 0, f"CLI failed with stderr: {stderr}"
        assert "No data found" in stdout or len(stdout.strip()) == 0

    def test_single_line_workflow(self, cli_command: str, tmp_path: Path) -> None:
        """Test single line file workflow."""
        single_line_file = tmp_path / "single.csv"
        single_line_file.write_text("name,age,city")

        returncode, stdout, stderr = self.run_cli_command(cli_command, [str(single_line_file), "--delimiter", ","])

        assert returncode == 0, f"CLI failed with stderr: {stderr}"
        assert "name" in stdout
        assert "age" in stdout
        assert "city" in stdout


class TestEndToEndErrorHandling:
    """Test end-to-end error handling scenarios."""

    @pytest.fixture
    def cli_command(self) -> str:
        """Get the CLI command to run."""
        return f"{sys.executable} -m splurge_dsv"

    def test_invalid_arguments_workflow(self, cli_command: str) -> None:
        """Test invalid arguments workflow."""
        returncode, stdout, stderr = self.run_cli_command(cli_command, ["--invalid-option"])

        assert returncode != 0, "CLI should fail with invalid arguments"
        assert "error" in stderr.lower() or "invalid" in stderr.lower()

    def test_missing_file_argument_workflow(self, cli_command: str) -> None:
        """Test missing file argument workflow."""
        returncode, stdout, stderr = self.run_cli_command(cli_command, ["--delimiter", ","])

        assert returncode != 0, "CLI should fail with missing file argument"
        assert "file" in stderr.lower() or "argument" in stderr.lower()

    def test_missing_delimiter_argument_workflow(self, cli_command: str, tmp_path: Path) -> None:
        """Test missing delimiter argument workflow."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("a,b,c")

        returncode, stdout, stderr = self.run_cli_command(cli_command, [str(test_file)])

        assert returncode != 0, "CLI should fail with missing delimiter"
        assert "delimiter" in stderr.lower() or "required" in stderr.lower()

    def run_cli_command(self, cli_command: str, args: list[str]) -> tuple[int, str, str]:
        """Run the CLI command and return results."""
        try:
            cmd_parts = cli_command.split() + args
            result = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=30)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", f"Command execution error: {e}"


class TestEndToEndIntegrationScenarios:
    """Test real-world integration scenarios."""

    @pytest.fixture
    def cli_command(self) -> str:
        """Get the CLI command to run."""
        return f"{sys.executable} -m splurge_dsv"

    def test_data_analysis_workflow(self, cli_command: str, tmp_path: Path) -> None:
        """Test complete data analysis workflow."""
        # Create a dataset for analysis
        data_content = """id,name,age,city,salary,department
1,John Doe,30,New York,75000,Engineering
2,Jane Smith,25,Los Angeles,65000,Design
3,Bob Johnson,35,Chicago,85000,Management
4,Alice Brown,28,Boston,70000,Engineering
5,Charlie Wilson,32,Seattle,72000,Analytics
6,Diana Davis,29,Austin,68000,Design
7,Eve Miller,31,Denver,78000,Engineering
8,Frank Garcia,27,Miami,62000,Design
9,Grace Lee,33,Portland,80000,Engineering
10,Henry Taylor,26,Atlanta,65000,Analytics"""

        data_file = tmp_path / "employees.csv"
        data_file.write_text(data_content)

        # Test various analysis scenarios

        # 1. Basic parsing
        returncode, stdout, stderr = self.run_cli_command(cli_command, [str(data_file), "--delimiter", ","])
        assert returncode == 0, f"Basic parsing failed: {stderr}"

        # 2. Skip header and analyze data
        returncode, stdout, stderr = self.run_cli_command(
            cli_command, [str(data_file), "--delimiter", ",", "--skip-header", "1"]
        )
        assert returncode == 0, f"Header skipping failed: {stderr}"

        # 3. Stream processing for large datasets
        returncode, stdout, stderr = self.run_cli_command(
            cli_command, [str(data_file), "--delimiter", ",", "--stream", "--chunk-size", "100"]
        )
        assert returncode == 0, f"Streaming failed: {stderr}"

    def test_data_transformation_workflow(self, cli_command: str, tmp_path: Path) -> None:
        """Test data transformation workflow."""
        # Create source data
        source_content = """product_id,product_name,price,category
P001,Laptop,1200,Electronics
P002,Desk Chair,250,Furniture
P003,Smartphone,800,Electronics
P004,Bookshelf,180,Furniture
P005,Tablet,500,Electronics"""

        source_file = tmp_path / "products.csv"
        source_file.write_text(source_content)

        # Test various transformations

        # 1. Basic parsing
        returncode, stdout, stderr = self.run_cli_command(cli_command, [str(source_file), "--delimiter", ","])
        assert returncode == 0, f"Basic parsing failed: {stderr}"

        # 2. Parse with custom options
        returncode, stdout, stderr = self.run_cli_command(
            cli_command, [str(source_file), "--delimiter", ",", "--no-strip"]
        )
        assert returncode == 0, f"Custom parsing failed: {stderr}"

    def test_multi_format_workflow(self, cli_command: str, tmp_path: Path) -> None:
        """Test workflow with multiple file formats."""
        # Create different format files
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("a,b,c\nd,e,f")

        tsv_file = tmp_path / "data.tsv"
        tsv_file.write_text("a\tb\tc\nd\te\tf")

        pipe_file = tmp_path / "data.txt"
        pipe_file.write_text("a|b|c\nd|e|f")

        # Test each format
        for file_path, delimiter in [
            (csv_file, ","),
            (tsv_file, "\t"),
            (pipe_file, "|"),
        ]:
            returncode, stdout, stderr = self.run_cli_command(cli_command, [str(file_path), "--delimiter", delimiter])
            assert returncode == 0, f"Failed to parse {file_path}: {stderr}"
            assert "a" in stdout and "b" in stdout and "c" in stdout

    def run_cli_command(self, cli_command: str, args: list[str]) -> tuple[int, str, str]:
        """Run the CLI command and return results."""
        try:
            cmd_parts = cli_command.split() + args
            result = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=30)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", f"Command execution error: {e}"
