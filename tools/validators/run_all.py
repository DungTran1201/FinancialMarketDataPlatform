"""Compatibility entrypoint delegating validation to Documentation V2."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_VALIDATOR = REPO_ROOT / "scripts" / "docs" / "validate_docs.py"


def main() -> int:
    print("=== Running Documentation V2 Validation Suite (via tools/validators/run_all.py) ===")
    proc = subprocess.run([sys.executable, str(DOCS_VALIDATOR), *sys.argv[1:]], cwd=REPO_ROOT)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
