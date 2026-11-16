"""Stop hook executing greenfield validation suite before ending work."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_ALL = REPO_ROOT / "tools" / "validators" / "run_all.py"


def _preferred_python() -> str:
    for candidate in (
        REPO_ROOT / ".venv" / "Scripts" / "python.exe",
        REPO_ROOT / ".venv" / "bin" / "python",
    ):
        if candidate.is_file():
            return str(candidate)
    return sys.executable


def main() -> int:
    proc = subprocess.run(
        [_preferred_python(), str(RUN_ALL)],
        cwd=str(REPO_ROOT),
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(
            json.dumps(
                {
                    "decision": "continue",
                    "reason": "Greenfield validation suite failed; resolve issues before completing turn.",
                }
            )
        )
        return 0
    print(json.dumps({"decision": "stop"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
