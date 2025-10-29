"""Module entrypoint for running splurge-dsv as a script.

When executed (``python -m splurge_dsv``), this module delegates to
``splurge_dsv.cli.run_cli`` and returns the resulting exit code.

License: MIT
Copyright (c) 2025 Jim Schilling
"""

from __future__ import annotations

# Standard library
import sys

# Local
from .cli import run_cli

if __name__ == "__main__":
    sys.exit(run_cli())
