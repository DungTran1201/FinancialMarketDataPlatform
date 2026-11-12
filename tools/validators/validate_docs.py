"""Validates markdown structure, titles, preserved baseline files, and absence of duplicate roots."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

PRESERVED_BASELINE_FILES = [
    "docs/architecture/00-architecture-overview.md",
    "docs/architecture/01-system-context.md",
    "docs/architecture/02-system-container-architecture.md",
    "docs/architecture/03-component-architecture.md",
    "docs/architecture/04-data-platform-architecture.md",
    "docs/architecture/05-backend-architecture.md",
    "docs/architecture/06-agentic-intelligence-architecture.md",
    "docs/architecture/07-data-storage-and-modeling.md",
    "docs/architecture/08-data-flow-and-event-contracts.md",
    "docs/architecture/09-api-and-integration-architecture.md",
    "docs/architecture/10-security-and-governance.md",
    "docs/architecture/11-reliability-and-observability.md",
    "docs/architecture/12-deployment-architecture.md",
    "docs/architecture/13-performance-and-scalability.md",
    "docs/architecture/adr/ADR-001-overall-architecture.md",
    "docs/architecture/adr/ADR-002-event-driven-data-platform.md",
    "docs/architecture/adr/ADR-003-storage-strategy.md",
    "docs/architecture/adr/ADR-004-backend-architecture.md",
    "docs/architecture/adr/ADR-005-query-and-caching-strategy.md",
    "docs/architecture/adr/ADR-006-agent-integration.md",
    "docs/specifications/data-requirements.md",
    "docs/specifications/data-dictionary.md",
    "docs/specifications/data-contracts.md",
    "docs/specifications/api-specification.md",
    "docs/specifications/non-functional-requirements.md",
]


def main() -> int:
    errors = 0
    # 1. Verify no competing top-level /diagrams root exists outside docs/diagrams/
    if (REPO_ROOT / "diagrams").exists():
        print("[ERROR] Unauthorized duplicate diagram root '/diagrams' found; use 'docs/diagrams/' only.")
        errors += 1

    # 2. Verify all 25 preserved baseline architecture & specification files exist
    for rel_path in PRESERVED_BASELINE_FILES:
        p = REPO_ROOT / rel_path
        if not p.exists() or p.stat().st_size == 0:
            print(f"[ERROR] Preserved baseline file missing or empty: {rel_path}")
            errors += 1

    # 3. Verify all markdown files in docs/, work-items/, .agents/, and root AGENTS.md have titles
    md_files = (
        list((REPO_ROOT / "docs").rglob("*.md"))
        + list((REPO_ROOT / "work-items").rglob("*.md"))
        + list((REPO_ROOT / ".agents").rglob("*.md"))
        + [REPO_ROOT / "AGENTS.md", REPO_ROOT / "README.md"]
    )
    for md in md_files:
        if not md.exists():
            print(f"[ERROR] Missing markdown file: {md}")
            errors += 1
            continue
        text = md.read_text(encoding="utf-8").strip()
        if not text:
            print(f"[ERROR] Empty markdown file: {md.relative_to(REPO_ROOT).as_posix()}")
            errors += 1
            continue
        # Allow YAML frontmatter in SKILL.md
        if text.startswith("---"):
            parts = text.split("---", 2)
            body = parts[2].lstrip() if len(parts) >= 3 else ""
            if not body.startswith("# "):
                print(f"[ERROR] {md.relative_to(REPO_ROOT).as_posix()}: Missing H1 title after frontmatter")
                errors += 1
        elif not text.startswith("# "):
            print(f"[ERROR] {md.relative_to(REPO_ROOT).as_posix()}: Missing top-level H1 title")
            errors += 1

    print(f"[validate_docs] Checked {len(md_files)} markdown files -> {errors} error(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
