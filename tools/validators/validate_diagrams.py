"""Validates diagram metadata headers, DIAG-* uniqueness, and Mermaid syntax blocks."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

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
DIAG_ID_META_RE = re.compile(r"\*\*Diagram ID\*\*\s*\|\s*`(DIAG-[A-Z0-9-]+)`")
UNQUOTED_PAREN_NODE_RE = re.compile(r"\b[A-Za-z0-9_]+\[([^\"\n\]]*)\]")
DEFAULT_DIAG_PATTERN = r"^DIAG-(CTX|C4|COMP|DATA|BPMN|SWIM|UC|SEQ|STATE|ERD|DOM|API|DEP|SEC|UX)-[0-9]{3}$"


def _load_diag_regex(repo_root: Path) -> re.Pattern[str]:
    reg_path = repo_root / ".agents" / "config" / "identifier-registry.yaml"
    if reg_path.exists():
        reg = yaml.safe_load(reg_path.read_text(encoding="utf-8")) or {}
        pat = reg.get("namespaces", {}).get("DIAG", {}).get("pattern")
        if pat:
            return re.compile(pat)
    return re.compile(DEFAULT_DIAG_PATTERN)


def validate_repo(repo_root: Path = REPO_ROOT) -> int:
    """Validate Mermaid syntax, Diagram ID metadata, and label quoting across `docs/diagrams/`."""
    errors = 0
    diag_root = repo_root / "docs" / "diagrams"
    if not diag_root.exists():
        print("[ERROR] docs/diagrams/ does not exist.")
        return 1

    diag_re = _load_diag_regex(repo_root)
    diag_files = [
        p for p in sorted(diag_root.rglob("*.md")) if p.name.lower() != "readme.md"
    ]
    active_files = [p for p in diag_files if not p.name.endswith(".template.md")]
    if len(active_files) < 22:
        print(f"[ERROR] Expected >= 22 active diagram files in docs/diagrams/, found {len(active_files)}")
        errors += 1

    seen_diag_ids: dict[str, str] = {}
    for df in diag_files:
        rel = df.relative_to(repo_root).as_posix()
        text = df.read_text(encoding="utf-8")
        is_template = df.name.endswith(".template.md")

        if not is_template:
            id_match = DIAG_ID_META_RE.search(text)
            if not id_match:
                print(f"[ERROR] {rel}: Missing metadata field '| **Diagram ID** | `DIAG-...` |'")
                errors += 1
            else:
                diag_id = id_match.group(1)
                if not diag_re.match(diag_id):
                    print(f"[ERROR] {rel}: Diagram ID '{diag_id}' violates DIAG registry pattern")
                    errors += 1
                if diag_id in seen_diag_ids:
                    print(
                        f"[ERROR] {rel}: Duplicate Diagram ID '{diag_id}' "
                        f"(already used in {seen_diag_ids[diag_id]})"
                    )
                    errors += 1
                seen_diag_ids[diag_id] = rel
            if "**Status**" not in text:
                print(f"[ERROR] {rel}: Missing metadata field '**Status**'")
                errors += 1

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
            for line_no, line in enumerate(blk.splitlines(), 1):
                for m in UNQUOTED_PAREN_NODE_RE.finditer(line):
                    inner = m.group(1)
                    if "(" in inner or ")" in inner:
                        print(
                            f"[ERROR] {rel}:{line_no}: Unquoted parentheses in Mermaid label '{m.group(0)}'"
                        )
                        errors += 1

    print(
        f"[validate_diagrams] Checked {len(diag_files)} diagram files "
        f"({len(active_files)} active) -> {errors} error(s)."
    )
    return 1 if errors else 0


def main() -> int:
    return validate_repo(REPO_ROOT)


if __name__ == "__main__":
    sys.exit(main())
