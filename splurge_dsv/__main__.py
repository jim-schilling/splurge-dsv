"""
Command-line interface entry point for splurge-dsv.

This module serves as the entry point when running the package as a module.
It imports and calls the run_cli function from the cli module.
"""

# Standard library imports
import sys

# Local imports
from splurge_dsv.cli import run_cli

if __name__ == "__main__":
    sys.exit(run_cli())
