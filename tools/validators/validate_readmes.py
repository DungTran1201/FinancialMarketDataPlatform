"""Validates 100% README.md coverage and mandatory 12-section contract across all managed directories."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

MANAGED_ROOTS = [
    REPO_ROOT / ".agents",
    REPO_ROOT / "docs",
    REPO_ROOT / "models",
    REPO_ROOT / "work-items",
    REPO_ROOT / "tools",
]

MANDATORY_SECTIONS = [
    "## 1. Directory Purpose",
    "## 2. Scope and Boundaries",
    "## 3. Agent Role and Responsibilities",
    "## 4. Authoritative Inputs",
    "## 5. Required Artifacts",
    "## 6. Directory and File Organization",
    "## 7. Document Creation Rules",
    "## 8. Creation Workflow",
    "## 9. Relationships and Dependencies",
    "## 10. Quality Gate",
    "## 11. Validation Commands",
    "## 12. Agent Restrictions",
]


def get_managed_directories() -> list[Path]:
    dirs: list[Path] = []
    for root in MANAGED_ROOTS:
        if not root.exists():
            continue
        dirs.append(root)
        for p in sorted(root.rglob("*")):
            if p.is_dir() and not p.name.startswith((".", "__pycache__")):
                dirs.append(p)
    return dirs


def main() -> int:
    errors = 0
    managed_dirs = get_managed_directories()
    for d in managed_dirs:
        rel = d.relative_to(REPO_ROOT).as_posix()
        readme = d / "README.md"
        if not readme.exists():
            print(f"[ERROR] Missing README.md in managed directory: {rel}")
            errors += 1
            continue
        text = readme.read_text(encoding="utf-8")
        if not text.lstrip().startswith("# "):
            print(f"[ERROR] {rel}/README.md: Missing top-level H1 title")
            errors += 1
        for sec in MANDATORY_SECTIONS:
            if sec not in text:
                print(f"[ERROR] {rel}/README.md: Missing mandatory section '{sec}'")
                errors += 1
        if "| Artifact | Purpose | Required / Conditional | Template |" not in text:
            print(f"[ERROR] {rel}/README.md: Missing Required Artifacts table header")
            errors += 1

    print(
        f"[validate_readmes] Checked {len(managed_dirs)} managed directories -> {errors} error(s)."
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
