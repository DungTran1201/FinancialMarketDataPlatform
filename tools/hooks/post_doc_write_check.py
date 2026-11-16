"""PostToolUse hook running Documentation V2 validator after Markdown/YAML doc writes."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_VALIDATOR = REPO_ROOT / "scripts" / "docs" / "validate_docs.py"


def main() -> int:
    result = subprocess.run(
        [sys.executable, str(DOCS_VALIDATOR)],
        cwd=REPO_ROOT,
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
