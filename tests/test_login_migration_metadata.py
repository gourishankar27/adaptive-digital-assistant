"""The operator's fresh Alembic process must register every installed login table."""

import os
import subprocess
import sys
from pathlib import Path


def test_fresh_alembic_check_recognizes_login_tables(harness):
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "check"],
        cwd=Path(__file__).resolve().parents[1],
        env=os.environ.copy(),
        capture_output=True,
        timeout=60,
    )
    # Never expose an operational connection string from a failed subprocess.
    assert result.returncode == 0, "Fresh Alembic process detected schema drift"
