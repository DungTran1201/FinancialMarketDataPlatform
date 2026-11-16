"""PostToolUse hook running the greenfield validator after doc/contract writes."""

from __future__ import annotations

import json
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
    if not VALIDATOR.is_file():
        sys.stderr.write(f"Validator script missing: {VALIDATOR}\n")
        return 1
    result = subprocess.run(
        [_preferred_python(), str(VALIDATOR)],
        cwd=str(REPO_ROOT),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.stderr.write((result.stdout or "") + (result.stderr or ""))
        return 1
    print(json.dumps({}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
