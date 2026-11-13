"""Stop hook executing the complete validation suite before task completion."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    r = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools/validators/run_all.py")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        print(
            json.dumps(
                {
                    "decision": "continue",
                    "reason": "Validation suite failed; fix validator errors before stopping.",
                }
            )
        )
        return 0
    print(json.dumps({"decision": "stop"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

