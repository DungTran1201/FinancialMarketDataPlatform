"""PostToolUse hook running canonical model and identifier validators after YAML model edits."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    r1 = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools/validators/validate_models.py")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    r2 = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools/validators/validate_identifiers.py")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if r1.returncode != 0 or r2.returncode != 0:
        sys.stderr.write((r1.stdout or "") + (r1.stderr or "") + (r2.stdout or "") + (r2.stderr or ""))
        return 1
    print(json.dumps({}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

