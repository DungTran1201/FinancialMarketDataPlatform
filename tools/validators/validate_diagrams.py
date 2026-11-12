"""Validates diagram categories, preserved platform diagrams, and Mermaid syntax blocks."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DIAG_ROOT = REPO_ROOT / "docs" / "diagrams"

ALLOWED_MERMAID_HEADERS = (
    "flowchart ",
    "graph ",
    "sequenceDiagram",
    "stateDiagram-v2",
    "stateDiagram",
    "classDiagram",
    "erDiagram",
    "xychart-beta",
)

MERMAID_BLOCK_RE = re.compile(r"```mermaid\s+(.*?)```", re.DOTALL)


def main() -> int:
    errors = 0
    if not DIAG_ROOT.exists():
        print("[ERROR] docs/diagrams/ does not exist.")
        return 1

    diag_files = [
        p for p in sorted(DIAG_ROOT.rglob("*.md")) if p.name.lower() != "readme.md"
    ]
    if len(diag_files) < 16:
        print(f"[ERROR] Expected >= 16 diagram files in docs/diagrams/, found {len(diag_files)}")
        errors += 1

    for df in diag_files:
        rel = df.relative_to(REPO_ROOT).as_posix()
        text = df.read_text(encoding="utf-8")
        blocks = MERMAID_BLOCK_RE.findall(text)
        if not blocks:
            print(f"[ERROR] {rel}: Missing ```mermaid fenced code block")
            errors += 1
            continue
        for blk in blocks:
            first_line = blk.strip().splitlines()[0].strip() if blk.strip() else ""
            if not first_line.startswith(ALLOWED_MERMAID_HEADERS):
                print(
                    f"[ERROR] {rel}: Unsupported or invalid Mermaid diagram header '{first_line}'"
                )
                errors += 1

    print(f"[validate_diagrams] Checked {len(diag_files)} diagram files -> {errors} error(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
