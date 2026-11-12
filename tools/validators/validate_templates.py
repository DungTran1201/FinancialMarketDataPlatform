"""Validates the 14 template categories and .template.md files in docs/templates/."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TPL_ROOT = REPO_ROOT / "docs" / "templates"

EXPECTED_CATEGORIES = {
    "discovery",
    "planning",
    "requirements",
    "business-process",
    "use-cases",
    "architecture",
    "domain",
    "api",
    "behavior",
    "security",
    "ux",
    "testing",
    "operations",
    "governance",
}

REQUIRED_TEMPLATE_FIELDS = [
    "**Document ID**",
    "**Title**",
    "**Version**",
    "**Status**",
    "**Authoring Role**",
    "**Review Role**",
    "**Canonical Model Reference**",
    "## 1. Purpose `[MANDATORY]`",
    "## 2. Scope & Boundaries `[MANDATORY]`",
    "Assumptions `[MANDATORY]`",
    "Open Questions `[MANDATORY]`",
    "Dependencies `[MANDATORY]`",
    "Bidirectional Traceability `[MANDATORY]`",
]


def main() -> int:
    errors = 0
    if not TPL_ROOT.exists():
        print("[ERROR] docs/templates/ directory does not exist.")
        return 1

    existing_cats = {p.name for p in TPL_ROOT.iterdir() if p.is_dir()}
    missing_cats = EXPECTED_CATEGORIES - existing_cats
    if missing_cats:
        print(f"[ERROR] Missing template categories: {sorted(missing_cats)}")
        errors += 1

    tpl_files = sorted(TPL_ROOT.rglob("*.template.md"))
    if len(tpl_files) < 50:
        print(f"[ERROR] Expected >= 50 .template.md files, found {len(tpl_files)}")
        errors += 1

    for tf in tpl_files:
        rel = tf.relative_to(REPO_ROOT).as_posix()
        text = tf.read_text(encoding="utf-8")
        for field in REQUIRED_TEMPLATE_FIELDS:
            if field not in text:
                print(f"[ERROR] {rel}: Missing required template field/section '{field}'")
                errors += 1
        if "[TO BE COMPLETED]" not in text:
            print(f"[ERROR] {rel}: Missing standard placeholder '[TO BE COMPLETED]'")
            errors += 1
        if "| **Status** | `APPROVED`" in text or "| **Status** | `BASELINED`" in text:
            print(f"[ERROR] {rel}: Template must not be hardcoded as APPROVED or BASELINED")
            errors += 1

    print(
        f"[validate_templates] Checked {len(existing_cats)} categories and {len(tpl_files)} templates -> {errors} error(s)."
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
