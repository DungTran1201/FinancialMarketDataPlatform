"""PostToolUse hook running canonical model and identifier validators after YAML model edits."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    r1 = subprocess.run([sys.executable, str(REPO_ROOT / "tools/validators/validate_models.py")], cwd=REPO_ROOT)
    r2 = subprocess.run([sys.executable, str(REPO_ROOT / "tools/validators/validate_identifiers.py")], cwd=REPO_ROOT)
    return 1 if (r1.returncode != 0 or r2.returncode != 0) else 0


if __name__ == "__main__":
    sys.exit(main())
