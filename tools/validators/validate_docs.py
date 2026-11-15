"""Validates markdown structure, titles, preserved baseline files, and absence of duplicate roots."""

from __future__ import annotations

import re
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


BACKTICK_PATH_RE = re.compile(
    r"`((?:docs/(?:architecture|diagrams|templates|specifications|operations|contracts)"
    r"|models|tools)/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*\.(?:md|yaml|yml|py))`"
)
MD_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SKIP_LINK_PREFIXES = ("http://", "https://", "mailto:", "tel:", "javascript:", "conversation://", "#")
HISTORICAL_LINE_MARKERS = ("deprecated", "superseded", "historical", "before:", "deleted", "planned", "proposed")


def _strip_fences_and_inline_code(text: str, strip_inline_code: bool) -> list[tuple[int, str]]:
    """Return (1-based line_no, line_text) outside fenced code blocks."""
    results: list[tuple[int, str]] = []
    in_fence = False
    for idx, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        line = re.sub(r"`[^`]*`", "", raw_line) if strip_inline_code else raw_line
        results.append((idx, line))
    return results


def _is_historical_doc(rel_path: str) -> bool:
    return (
        rel_path.startswith("docs/archive/")
        or rel_path.startswith("docs/templates/")
        or rel_path.startswith("work-items/DOCS-002")
        or rel_path.startswith("work-items/DOCS-003")
    )


def _check_markdown_links(repo_root: Path, md: Path, rel_path: str, text: str) -> int:
    """Validate relative Markdown file and directory links inside a document."""
    if _is_historical_doc(rel_path):
        return 0
    errors = 0
    for line_no, line in _strip_fences_and_inline_code(text, strip_inline_code=True):
        for match in MD_LINK_RE.finditer(line):
            raw_target = match.group(1).strip()
            if not raw_target or raw_target.startswith(SKIP_LINK_PREFIXES) or "://" in raw_target:
                continue
            if any(ch in raw_target for ch in ("<", ">", "{", "}", "*")):
                continue
            target_token = raw_target.split()[0].strip("<>")
            path_part = target_token.split("#", 1)[0]
            if not path_part:
                continue
            resolved = (md.parent / path_part).resolve()
            if not resolved.exists():
                print(
                    f"[ERROR] {rel_path}:{line_no}: Broken relative markdown link '{raw_target}' "
                    f"(resolved to '{resolved}')"
                )
                errors += 1
    return errors


def _check_backtick_paths(repo_root: Path, rel_path: str, text: str) -> int:
    """Validate backticked repository file paths in active documents."""
    if _is_historical_doc(rel_path) or rel_path.startswith(".agents/skills/"):
        return 0
    errors = 0
    for line_no, line in _strip_fences_and_inline_code(text, strip_inline_code=False):
        lowered = line.lower()
        if any(marker in lowered for marker in HISTORICAL_LINE_MARKERS):
            continue
        for match in BACKTICK_PATH_RE.finditer(line):
            candidate = match.group(1)
            if ".." in candidate:
                continue
            if not (repo_root / candidate).exists():
                print(f"[ERROR] {rel_path}:{line_no}: Backticked path does not exist: '{candidate}'")
                errors += 1
    return errors


def validate_repo(repo_root: Path = REPO_ROOT) -> int:
    errors = 0
    # 1. Verify no competing top-level /diagrams root exists outside docs/diagrams/
    if (repo_root / "diagrams").exists():
        print("[ERROR] Unauthorized duplicate diagram root '/diagrams' found; use 'docs/diagrams/' only.")
        errors += 1

    # 2. Verify all 25 preserved baseline architecture & specification files exist
    for rel_path in PRESERVED_BASELINE_FILES:
        p = repo_root / rel_path
        if not p.exists() or p.stat().st_size == 0:
            print(f"[ERROR] Preserved baseline file missing or empty: {rel_path}")
            errors += 1

    # 3. Verify all markdown files in docs/, work-items/, .agents/, root AGENTS.md and README.md
    md_files = sorted(
        {
            *(repo_root / "docs").rglob("*.md"),
            *(repo_root / "work-items").rglob("*.md"),
            *(repo_root / ".agents").rglob("*.md"),
            repo_root / "AGENTS.md",
            repo_root / "README.md",
        }
    )
    for md in md_files:
        if not md.exists():
            print(f"[ERROR] Missing markdown file: {md}")
            errors += 1
            continue
        rel_path = md.relative_to(repo_root).as_posix()
        text = md.read_text(encoding="utf-8").strip()
        if not text:
            print(f"[ERROR] Empty markdown file: {rel_path}")
            errors += 1
            continue
        # Allow YAML frontmatter in SKILL.md
        if text.startswith("---"):
            parts = text.split("---", 2)
            body = parts[2].lstrip() if len(parts) >= 3 else ""
            if not body.startswith("# "):
                print(f"[ERROR] {rel_path}: Missing H1 title after frontmatter")
                errors += 1
        elif not text.startswith("# "):
            print(f"[ERROR] {rel_path}: Missing top-level H1 title")
            errors += 1

        errors += _check_markdown_links(repo_root, md, rel_path, text)
        errors += _check_backtick_paths(repo_root, rel_path, text)

    print(f"[validate_docs] Checked {len(md_files)} markdown files -> {errors} error(s).")
    return 1 if errors else 0


def main() -> int:
    return validate_repo(REPO_ROOT)


if __name__ == "__main__":
    sys.exit(main())
