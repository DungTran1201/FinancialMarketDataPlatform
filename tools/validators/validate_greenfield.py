#!/usr/bin/env python3
"""Greenfield Documentation, Diagram, Reference & Work-Item Validator.

Replaces the legacy Documentation V2 validator on branch `greenfield/main` so that
authoritative greenfield docs, work items, and Mermaid diagrams are strictly validated
without pulling in retired legacy V1/V2 governance files.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ALLOWED_DOC_STATUSES = {"DRAFT", "IN_REVIEW", "ACCEPTED", "APPROVED", "DEPRECATED"}
ALLOWED_IMPL_STATUSES = {
    "NOT_APPLICABLE",
    "PLANNED",
    "NOT_IMPLEMENTED",
    "POC_VALIDATED",
    "PARTIALLY_IMPLEMENTED",
    "IMPLEMENTED",
    "VERIFIED",
}
ALLOWED_WORK_ITEM_STATUSES = {
    "BACKLOG",
    "READY",
    "IN_PROGRESS",
    "BLOCKED",
    "IN_REVIEW",
    "TESTING",
    "ACCEPTED",
    "COMPLETE",
}
REQUIRED_FRONTMATTER_KEYS = (
    "doc_id",
    "title",
    "version",
    "status",
    "owner",
    "purpose",
    "scope",
    "dependencies",
    "references",
    "assumptions",
    "open_issues",
    "review_criteria",
)
REQUIRED_WORK_ITEM_KEYS = (
    "work_item_id",
    "objective",
    "scope",
    "dependencies",
    "prerequisites",
    "steps",
    "affected_modules",
    "test_requirements",
    "acceptance_criteria",
    "risks",
    "evidence",
    "status",
)
ALLOWED_MERMAID_HEADERS = (
    "flowchart",
    "graph",
    "sequenceDiagram",
    "stateDiagram-v2",
    "stateDiagram",
    "erDiagram",
    "classDiagram",
    "C4Context",
    "C4Container",
    "C4Component",
    "C4Deployment",
)
FORBIDDEN_LEGACY_PATHS = (
    "docs/archive",
    "docs/governance/catalog",
    "docs/data-plane",
    "docs/application-plane",
    "docs/intelligence-plane",
    "src/ingestion",
    "src/streaming",
    "src/lakehouse",
    "src/serving",
    "src/intelligence",
)

MD_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
UNRESOLVED_TOKEN_RE = re.compile(r"(?:\bTBD\b|\bTODO\b|\bFIXME\b|\[TO BE COMPLETED\])")


@dataclass
class Issue:
    severity: str
    rule_id: str
    path: str
    message: str
    line: int | None = None

    def format(self) -> str:
        loc = f"{self.path}:{self.line}" if self.line is not None else self.path
        return f"[{self.severity}] {self.rule_id} ({loc}): {self.message}"


@dataclass
class Report:
    root: Path
    issues: list[Issue] = field(default_factory=list)
    stats: dict[str, int] = field(default_factory=dict)

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "ERROR"]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "WARNING"]

    def add_error(self, rule_id: str, path: Path | str, message: str, line: int | None = None) -> None:
        self.issues.append(Issue("ERROR", rule_id, self._rel(path), message, line))

    def _rel(self, path: Path | str) -> str:
        if isinstance(path, Path):
            try:
                return path.resolve().relative_to(self.root.resolve()).as_posix()
            except ValueError:
                return path.as_posix()
        return path


def _parse_frontmatter(text: str) -> tuple[dict[str, Any] | None, str, int, str | None]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text, 1, "Missing YAML frontmatter delimiter '---' on line 1."
    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        return None, text, 1, "Unterminated YAML frontmatter block."
    try:
        parsed = yaml.safe_load("\n".join(lines[1:end_idx]))
    except yaml.YAMLError as exc:
        return None, text, end_idx + 2, f"Invalid YAML frontmatter: {exc}"
    if not isinstance(parsed, dict):
        return None, text, end_idx + 2, "YAML frontmatter must decode as an object/mapping."
    return parsed, "\n".join(lines[end_idx + 1 :]), end_idx + 2, None


def _strip_fenced_blocks_preserve_lines(lines: list[str]) -> list[str]:
    out: list[str] = []
    in_fence = False
    fence_char = ""
    fence_len = 0
    for line in lines:
        stripped = line.lstrip()
        m = re.match(r"^(`{3,}|~{3,})", stripped)
        if m:
            marker = m.group(1)
            if not in_fence:
                in_fence = True
                fence_char = marker[0]
                fence_len = len(marker)
                out.append("")
                continue
            if marker[0] == fence_char and len(marker) >= fence_len and stripped[len(marker) :].strip() == "":
                in_fence = False
                out.append("")
                continue
        out.append("" if in_fence else line)
    return out


def _extract_fenced_blocks(text: str, target_lang: str | None = None) -> list[tuple[int, str, str]]:
    lines = text.splitlines()
    blocks: list[tuple[int, str, str]] = []
    in_fence = False
    fence_char = ""
    fence_len = 0
    block_lang = ""
    block_start = 0
    buf: list[str] = []
    for idx, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        m = re.match(r"^(`{3,}|~{3,})(.*)$", stripped)
        if m and not in_fence:
            in_fence = True
            fence_char = m.group(1)[0]
            fence_len = len(m.group(1))
            block_lang = m.group(2).strip().split()[0].lower() if m.group(2).strip() else ""
            block_start = idx
            buf = []
            continue
        if in_fence:
            close_m = re.match(r"^(`{3,}|~{3,})\s*$", stripped)
            if close_m and close_m.group(1)[0] == fence_char and len(close_m.group(1)) >= fence_len:
                if target_lang is None or block_lang == target_lang.lower():
                    blocks.append((block_start, block_lang, "\n".join(buf)))
                in_fence = False
                continue
            buf.append(line)
    if in_fence:
        blocks.append((block_start, "__UNCLOSED__", "\n".join(buf)))
    return blocks


def _github_anchor_slug(heading_text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", heading_text.strip().lower())
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s", "-", text)
    return text.strip("-")


def _extract_headings_and_anchors(md_text: str) -> tuple[list[tuple[int, int, str]], set[str]]:
    fm, body, body_start, _ = _parse_frontmatter(md_text)
    if fm is None:
        body = md_text
        body_start = 1
    lines = _strip_fenced_blocks_preserve_lines(body.splitlines())
    headings: list[tuple[int, int, str]] = []
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for offset, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            headings.append((body_start + offset, level, title))
            slug = _github_anchor_slug(title)
            if slug:
                count = counts.get(slug, 0)
                counts[slug] = count + 1
                anchors.add(slug if count == 0 else f"{slug}-{count}")
    return headings, anchors


def _validate_mermaid(md_path: Path, body: str, report: Report, body_start: int) -> None:
    blocks = _extract_fenced_blocks(body, "mermaid")
    unclosed = [b for b in _extract_fenced_blocks(body, None) if b[1] == "__UNCLOSED__"]
    for start_line, _, _ in unclosed:
        report.add_error("GF-MERMAID-001", md_path, "Unclosed fenced code block.", body_start + start_line - 1)
    for start_line, _, content in blocks:
        abs_line = body_start + start_line - 1
        stripped = [ln.strip() for ln in content.splitlines() if ln.strip() and not ln.strip().startswith("%%")]
        idx = 0
        if idx < len(stripped) and stripped[idx] == "---":
            idx += 1
            while idx < len(stripped) and stripped[idx] != "---":
                idx += 1
            idx += 1
        if idx >= len(stripped):
            report.add_error("GF-MERMAID-001", md_path, "Empty Mermaid block.", abs_line)
            continue
        first_stmt = stripped[idx]
        matched = next((h for h in ALLOWED_MERMAID_HEADERS if first_stmt.startswith(h)), None)
        if not matched:
            report.add_error("GF-MERMAID-001", md_path, f"Unsupported Mermaid header '{first_stmt}'.", abs_line)
            continue
        if matched in ("flowchart", "graph"):
            subgraphs = sum(1 for ln in stripped if ln.startswith("subgraph "))
            ends = sum(1 for ln in stripped if ln == "end")
            if subgraphs != ends:
                report.add_error(
                    "GF-MERMAID-001",
                    md_path,
                    f"Unbalanced Mermaid subgraph/end blocks ({subgraphs} vs {ends}).",
                    abs_line,
                )


def validate_repository(root: Path) -> Report:
    root = root.resolve()
    report = Report(root=root)

    # 1. Core greenfield entrypoints
    for required in ("AGENTS.md", "README.md", ".gitignore", ".agents/hooks.json", "docs/README.md"):
        if not (root / required).is_file():
            report.add_error("GF-CORE-001", root / required, f"Missing required repository file '{required}'.")

    # 2. Prevent accidental mixing of legacy directories on greenfield/main
    for legacy_rel in FORBIDDEN_LEGACY_PATHS:
        legacy_path = root / legacy_rel
        if legacy_path.exists() and any(legacy_path.rglob("*")):
            report.add_error(
                "GF-CLEAN-001",
                legacy_path,
                f"Legacy path '{legacy_rel}' contains files; greenfield/main must stay isolated from legacy artifacts.",
            )

    docs_dir = root / "docs"
    if not docs_dir.is_dir():
        return report

    # 3. Directory hygiene & Section 6.2 README mandate
    dir_count = 0
    for d in [docs_dir, *sorted(p for p in docs_dir.rglob("*") if p.is_dir())]:
        dir_count += 1
        if not any(d.iterdir()):
            report.add_error("GF-STRUCT-001", d, "Empty placeholder directory under docs/ is prohibited.")
        elif not (d / "README.md").is_file():
            report.add_error(
                "GF-STRUCT-002",
                d,
                "Every documentation directory must contain a README.md explaining purpose, naming, and dependencies.",
            )

    # 4. Markdown metadata, structure, Mermaid & Work Items
    md_files = sorted(docs_dir.rglob("*.md"))
    seen_doc_ids: dict[str, Path] = {}
    seen_work_items: dict[str, Path] = {}
    heading_cache: dict[Path, tuple[list[tuple[int, int, str]], set[str]]] = {}
    parsed_docs: list[tuple[Path, dict[str, Any] | None, str, int]] = []

    for md_path in md_files:
        text = md_path.read_text(encoding="utf-8")
        if not text.strip():
            report.add_error("GF-EMPTY-001", md_path, "Empty Markdown file is prohibited.")
            continue

        fm, body, body_start, fm_err = _parse_frontmatter(text)
        if fm_err:
            report.add_error("GF-META-001", md_path, fm_err, 1)
            parsed_docs.append((md_path, None, body, body_start))
            continue

        assert fm is not None
        parsed_docs.append((md_path, fm, body, body_start))
        is_template = "templates" in md_path.parts

        for req_key in REQUIRED_FRONTMATTER_KEYS:
            if req_key not in fm or fm[req_key] is None or (isinstance(fm[req_key], str) and not fm[req_key].strip()):
                report.add_error("GF-META-002", md_path, f"Missing required frontmatter metadata key '{req_key}'.", 2)

        doc_id = fm.get("doc_id")
        if isinstance(doc_id, str) and not is_template:
            if doc_id in seen_doc_ids:
                prev = report._rel(seen_doc_ids[doc_id])
                report.add_error("GF-ID-001", md_path, f"Duplicate doc_id '{doc_id}' (already defined in {prev}).", 2)
            else:
                seen_doc_ids[doc_id] = md_path

        st = fm.get("status")
        if st not in ALLOWED_DOC_STATUSES:
            report.add_error("GF-META-003", md_path, f"Invalid status '{st}'. Allowed: {sorted(ALLOWED_DOC_STATUSES)}.", 2)

        impl_st = fm.get("implementation_status")
        if impl_st is not None and impl_st not in ALLOWED_IMPL_STATUSES:
            report.add_error(
                "GF-META-004",
                md_path,
                f"Invalid implementation_status '{impl_st}'. Allowed: {sorted(ALLOWED_IMPL_STATUSES)}.",
                2,
            )

        headings, anchors = _extract_headings_and_anchors(text)
        heading_cache[md_path.resolve()] = (headings, anchors)

        if not body.strip():
            report.add_error("GF-EMPTY-002", md_path, "Document has empty body.", body_start)
        elif not is_template:
            h1s = [h for h in headings if h[1] == 1]
            if len(h1s) != 1:
                report.add_error("GF-STRUCT-003", md_path, f"Expected exactly 1 H1 heading, found {len(h1s)}.", body_start)
            prev_lvl = 0
            for ln, lvl, title in headings:
                if prev_lvl and lvl > prev_lvl + 1:
                    report.add_error(
                        "GF-STRUCT-003",
                        md_path,
                        f"Skipped heading level H{prev_lvl} -> H{lvl} ('{title}').",
                        ln,
                    )
                prev_lvl = lvl

        if st in ("APPROVED", "ACCEPTED") and not is_template:
            body_lines = _strip_fenced_blocks_preserve_lines(body.splitlines())
            for idx, line in enumerate(body_lines):
                cleaned = re.sub(r"`[^`]*`", "", line)
                if UNRESOLVED_TOKEN_RE.search(cleaned):
                    report.add_error(
                        "GF-STATUS-001",
                        md_path,
                        f"Document with status={st} contains unresolved TBD/TODO/FIXME token.",
                        body_start + idx,
                    )

        if "```mermaid" in body:
            _validate_mermaid(md_path, body, report, body_start)

        # Work-item tracking schema check
        if isinstance(fm.get("work_items"), list):
            for idx, wi in enumerate(fm["work_items"]):
                if not isinstance(wi, dict):
                    report.add_error("GF-WI-001", md_path, f"work_items[{idx}] must be a mapping.")
                    continue
                for wkey in REQUIRED_WORK_ITEM_KEYS:
                    if wkey not in wi or wi[wkey] is None:
                        report.add_error("GF-WI-001", md_path, f"Work item missing required field '{wkey}'.")
                wid = str(wi.get("work_item_id") or "")
                if wid in seen_work_items:
                    report.add_error("GF-WI-002", md_path, f"Duplicate work_item_id '{wid}'.")
                elif wid:
                    seen_work_items[wid] = md_path
                wstatus = wi.get("status")
                if wstatus not in ALLOWED_WORK_ITEM_STATUSES:
                    report.add_error("GF-WI-003", md_path, f"{wid}: invalid status '{wstatus}'.")
                if wstatus == "COMPLETE" and not wi.get("evidence"):
                    report.add_error("GF-WI-004", md_path, f"{wid}: status COMPLETE requires non-empty evidence.")

    # 5. Relative link & anchor check across docs + root Markdown files
    all_md = list(md_files)
    for extra in (root / "AGENTS.md", root / "README.md", root / ".agents" / "README.md"):
        if extra.is_file():
            all_md.append(extra)
            heading_cache[extra.resolve()] = _extract_headings_and_anchors(extra.read_text(encoding="utf-8"))
    for p in (root / ".agents").rglob("*.md") if (root / ".agents").is_dir() else []:
        if p not in all_md:
            all_md.append(p)
            heading_cache[p.resolve()] = _extract_headings_and_anchors(p.read_text(encoding="utf-8"))

    parsed_map = {p: (fm, body, bs) for p, fm, body, bs in parsed_docs}
    for md_path in all_md:
        text = md_path.read_text(encoding="utf-8")
        fm, body, body_start = parsed_map.get(md_path, (None, text, 1))
        stripped_lines = _strip_fenced_blocks_preserve_lines(body.splitlines())
        for idx, line in enumerate(stripped_lines):
            cleaned = re.sub(r"`[^`]*`", "", line)
            for match in MD_LINK_RE.finditer(cleaned):
                target = match.group(1).strip().strip("<>").split()[0]
                if not target or target.startswith(("http://", "https://", "mailto:", "<")):
                    continue
                if target.startswith("#"):
                    anchor = target[1:].lower()
                    _, anchors = heading_cache.get(md_path.resolve(), ([], set()))
                    if anchor and anchor not in anchors:
                        report.add_error("GF-LINK-002", md_path, f"Broken anchor '#{anchor}'.", body_start + idx)
                    continue
                file_part, anchor_part = target.split("#", 1) if "#" in target else (target, "")
                resolved = (md_path.parent / file_part).resolve()
                if not resolved.exists():
                    repo_resolved = (root / file_part).resolve()
                    if repo_resolved.exists():
                        resolved = repo_resolved
                    else:
                        report.add_error("GF-LINK-001", md_path, f"Broken link '{target}'.", body_start + idx)
                        continue
                if anchor_part and resolved.is_file() and resolved.suffix.lower() == ".md":
                    if resolved not in heading_cache:
                        heading_cache[resolved] = _extract_headings_and_anchors(resolved.read_text(encoding="utf-8"))
                    _, target_anchors = heading_cache[resolved]
                    if anchor_part.lower() not in target_anchors:
                        report.add_error(
                            "GF-LINK-002",
                            md_path,
                            f"Broken anchor '#{anchor_part}' in '{target}'.",
                            body_start + idx,
                        )

    report.stats = {
        "directories": dir_count,
        "markdown_files": len(md_files),
        "unique_doc_ids": len(seen_doc_ids),
        "work_items": len(seen_work_items),
        "errors": len(report.errors),
        "warnings": len(report.warnings),
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Greenfield FinancialMarketDataPlatform docs.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = validate_repository(args.root)
    if args.json:
        print(json.dumps({"stats": report.stats, "errors": [i.__dict__ for i in report.errors]}, indent=2))
    else:
        print("=== Greenfield Repository Documentation & Work-Item Validator ===")
        print(
            f"Scanned: {report.stats.get('directories', 0)} dirs, "
            f"{report.stats.get('markdown_files', 0)} docs, "
            f"{report.stats.get('unique_doc_ids', 0)} doc_ids, "
            f"{report.stats.get('work_items', 0)} work items"
        )
        for issue in report.issues:
            print(issue.format())
        if not report.errors:
            print(f"PASS: 0 errors, {len(report.warnings)} warnings.")
        else:
            print(f"FAIL: {len(report.errors)} errors, {len(report.warnings)} warnings.")
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
