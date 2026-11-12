"""Master validation runner executing all 10 Documentation Engineering validators."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

VALIDATORS = [
    "tools/validators/validate_agent_config.py",
    "tools/validators/validate_artifact_matrix.py",
    "tools/validators/validate_readmes.py",
    "tools/validators/validate_templates.py",
    "tools/validators/validate_models.py",
    "tools/validators/validate_identifiers.py",
    "tools/validators/validate_diagrams.py",
    "tools/validators/validate_docs.py",
    "tools/validators/validate_traceability.py",
    "tools/validators/validate_work_items.py",
]


def main() -> int:
    failed = 0
    print("=" * 76)
    print("FINANCIAL MARKET DATA PLATFORM — DOCUMENTATION ENGINEERING VALIDATION SUITE")
    print("=" * 76)
    for script in VALIDATORS:
        proc = subprocess.run([sys.executable, str(REPO_ROOT / script)], cwd=REPO_ROOT)
        if proc.returncode != 0:
            failed += 1
    print("=" * 76)
    print(f"SUMMARY: Executed {len(VALIDATORS)} validators | Failed: {failed}")
    print("=" * 76)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
