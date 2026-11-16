"""Unified validation entrypoint for greenfield repository hygiene & docs."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "tools" / "validators" / "validate_greenfield.py"


def _preferred_python() -> str:
    for candidate in (
        REPO_ROOT / ".venv" / "Scripts" / "python.exe",
        REPO_ROOT / ".venv" / "bin" / "python",
    ):
        if candidate.is_file():
            return str(candidate)
    return sys.executable


def main() -> int:
    print("=== Running Greenfield Validation Suite (tools/validators/run_all.py) ===")
    proc = subprocess.run(
        [_preferred_python(), str(VALIDATOR), *sys.argv[1:]],
        cwd=REPO_ROOT,
        check=False,
    )
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
