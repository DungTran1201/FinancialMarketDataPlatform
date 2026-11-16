#!/usr/bin/env python3
"""Documentation V2 Validation Suite for FinancialMarketDataPlatform.

Enforces Documentation V2 governance standards, JSON Schemas, applicability rules,
referential integrity, traceability links, Mermaid/contract structure, and checks
optional external validators (mmdc, spectral, asyncapi, xmllint) via shutil.which.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import jsonschema
import yaml

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

REQ_ID_ROW_RE = re.compile(
    r"^\|\s*((?:BR|FR|NFR|RULE|UC|AC|CON|THR|SEC|TS|TC)-[A-Z][A-Z0-9-]*-\d{3})\s*\|"
)
MD_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
UNRESOLVED_TOKEN_RE = re.compile(r"(?:\bTBD\b|\bTODO\b|\bFIXME\b|\[TO BE COMPLETED\])")

TIER_RANK = {"LOW": 0, "MEDIUM": 1, "HIGH_CRITICAL": 2}


@dataclass
class ValidationIssue:
    severity: str  # ERROR | WARNING
    rule_id: str
    path: str
    message: str
    line: int | None = None

    def format(self) -> str:
        loc = f"{self.path}:{self.line}" if self.line is not None else self.path
        return f"[{self.severity}] {self.rule_id} ({loc}): {self.message}"


@dataclass
class ValidationReport:
    root: Path
    issues: list[ValidationIssue] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)
    external_tools: dict[str, str] = field(default_factory=dict)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "ERROR"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "WARNING"]

    def add_error(
        self, rule_id: str, path: Path | str, message: str, line: int | None = None
    ) -> None:
        rel = self._rel(path)
        self.issues.append(ValidationIssue("ERROR", rule_id, rel, message, line))

    def add_warning(
        self, rule_id: str, path: Path | str, message: str, line: int | None = None
    ) -> None:
        rel = self._rel(path)
        self.issues.append(ValidationIssue("WARNING", rule_id, rel, message, line))

    def _rel(self, path: Path | str) -> str:
        if isinstance(path, Path):
            try:
                return path.resolve().relative_to(self.root.resolve()).as_posix()
            except ValueError:
                return path.as_posix()
        return path


def _strip_fenced_blocks_preserve_lines(lines: list[str]) -> list[str]:
    """Return lines with content inside fenced code blocks blanked out, preserving indices."""
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
            elif marker[0] == fence_char and len(marker) >= fence_len and stripped[len(marker) :].strip() == "":
                in_fence = False
                out.append("")
                continue
        out.append("" if in_fence else line)
    return out


def _extract_fenced_blocks(text: str, target_lang: str | None = None) -> list[tuple[int, str, str]]:
    """Extract (start_line_1idx, lang, content) for fenced blocks."""
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


def _parse_frontmatter(text: str) -> tuple[dict[str, Any] | None, str, int, str | None]:
    """Parse YAML frontmatter at top of Markdown text.

    Returns (frontmatter_dict, body_text, body_start_line_1idx, error_msg).
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text, 1, "Document MUST start with YAML frontmatter delimiter '---' on line 1."
    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        return None, text, 1, "Unterminated YAML frontmatter block (missing closing '---')."
    raw_yaml = "\n".join(lines[1:end_idx])
    try:
        parsed = yaml.safe_load(raw_yaml)
    except yaml.YAMLError as exc:
        return None, text, end_idx + 2, f"Invalid YAML in frontmatter: {exc}"
    if not isinstance(parsed, dict):
        return None, text, end_idx + 2, "YAML frontmatter must parse as a mapping/object."
    body = "\n".join(lines[end_idx + 1 :])
    return parsed, body, end_idx + 2, None


def _github_anchor_slug(heading_text: str) -> str:
    """Compute GitHub-style Markdown anchor slug matching common renderers."""
    text = re.sub(r"`([^`]+)`", r"\1", heading_text.strip().lower())
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s", "-", text)
    return text.strip("-")


def _extract_headings_and_anchors(md_text: str) -> tuple[list[tuple[int, int, str]], set[str]]:
    _, body, body_start, _ = _parse_frontmatter(md_text)
    if _ is None:
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


def _is_path_like(value: str) -> bool:
    if value.startswith(("http://", "https://", "<")):
        return False
    exts = (".md", ".yaml", ".yml", ".json", ".py", ".ts", ".sql", ".bpmn")
    return "/" in value or "\\" in value or value.endswith(exts)


def _load_json_schema(schema_path: Path) -> dict[str, Any]:
    return json.loads(schema_path.read_text(encoding="utf-8"))


def _validate_against_schema(
    data: Any, schema: dict[str, Any], report: ValidationReport, rule_id: str, path: Path
) -> None:
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as exc:
        loc = ".".join(str(p) for p in exc.absolute_path) or "<root>"
        report.add_error(rule_id, path, f"Schema error at '{loc}': {exc.message}")


def _validate_mermaid_blocks(md_path: Path, body: str, report: ValidationReport, body_start: int) -> list[str]:
    blocks = _extract_fenced_blocks(body, "mermaid")
    unclosed = [b for b in _extract_fenced_blocks(body, None) if b[1] == "__UNCLOSED__"]
    for start_line, _, _ in unclosed:
        report.add_error(
            "VAL-DIAG-MERMAID-001",
            md_path,
            "Unclosed fenced code block detected.",
            body_start + start_line - 1,
        )

    valid_headers: list[str] = []
    for start_line, _, content in blocks:
        abs_line = body_start + start_line - 1
        stripped_lines = [
            ln.strip()
            for ln in content.splitlines()
            if ln.strip() and not ln.strip().startswith("%%")
        ]
        # Skip Mermaid %%{init:...}%% or frontmatter --- title: ... ---
        idx = 0
        if idx < len(stripped_lines) and stripped_lines[idx] == "---":
            idx += 1
            while idx < len(stripped_lines) and stripped_lines[idx] != "---":
                idx += 1
            idx += 1
        if idx >= len(stripped_lines):
            report.add_error("VAL-DIAG-MERMAID-001", md_path, "Empty Mermaid diagram block.", abs_line)
            continue
        first_stmt = stripped_lines[idx]
        matched_header = next((h for h in ALLOWED_MERMAID_HEADERS if first_stmt.startswith(h)), None)
        if not matched_header:
            report.add_error(
                "VAL-DIAG-MERMAID-001",
                md_path,
                f"Invalid Mermaid header '{first_stmt}'. Expected one of {', '.join(ALLOWED_MERMAID_HEADERS)}.",
                abs_line,
            )
            continue
        if matched_header in ("flowchart", "graph"):
            subgraphs = sum(1 for ln in stripped_lines if ln.startswith("subgraph "))
            ends = sum(1 for ln in stripped_lines if ln == "end")
            if subgraphs != ends:
                report.add_error(
                    "VAL-DIAG-MERMAID-001",
                    md_path,
                    f"Mismatched Mermaid subgraph/end count ({subgraphs} subgraph vs {ends} end).",
                    abs_line,
                )
        valid_headers.append(matched_header)
    return valid_headers


def _check_openapi_or_asyncapi(yaml_path: Path, data: Any, report: ValidationReport) -> None:
    if not isinstance(data, dict):
        return
    if "openapi" in data:
        version = str(data.get("openapi", ""))
        if not version.startswith("3."):
            report.add_error("VAL-OPENAPI-001", yaml_path, f"Unsupported OpenAPI version '{version}'; expected 3.x.")
        info = data.get("info")
        if not isinstance(info, dict) or not info.get("title") or not info.get("version"):
            report.add_error("VAL-OPENAPI-001", yaml_path, "OpenAPI document missing info.title or info.version.")
        if "paths" not in data and "webhooks" not in data:
            report.add_error("VAL-OPENAPI-001", yaml_path, "OpenAPI document must define 'paths' or 'webhooks'.")
    if "asyncapi" in data:
        version = str(data.get("asyncapi", ""))
        if not version.startswith("3."):
            report.add_error("VAL-ASYNCAPI-001", yaml_path, f"Unsupported AsyncAPI version '{version}'; expected 3.x.")
        info = data.get("info")
        if not isinstance(info, dict) or not info.get("title") or not info.get("version"):
            report.add_error("VAL-ASYNCAPI-001", yaml_path, "AsyncAPI document missing info.title or info.version.")
        if "channels" not in data or "operations" not in data:
            report.add_error(
                "VAL-ASYNCAPI-001",
                yaml_path,
                "AsyncAPI 3.x document must define 'channels' and 'operations'.",
            )


def _compute_required_artifacts(
    cap_data: dict[str, Any], matrix: dict[str, Any]
) -> tuple[str, set[str]]:
    """Compute effective minimum risk tier and required ART-* IDs from applicability matrix."""
    declared_tier = str(cap_data.get("risk_tier", "LOW"))
    signals = cap_data.get("risk_signals") or {}

    effective_tier = declared_tier
    signal_defs = {s["signal"]: s["minimum_tier"] for s in matrix["risk_assessment"]["assessment_signals"]}
    for sig, min_tier in signal_defs.items():
        if signals.get(sig) is True and TIER_RANK[min_tier] > TIER_RANK[effective_tier]:
            effective_tier = min_tier

    required: set[str] = set(matrix["capability_baseline_by_tier"][declared_tier]["REQUIRED"])
    for ov in matrix.get("signal_overrides", []):
        if signals.get(ov["signal"]) is True:
            required.update(ov.get("required_artifacts", []))

    plane = cap_data.get("plane")
    if plane == "intelligence-plane":
        plane_ov = matrix.get("plane_overrides", {}).get("intelligence-plane", {})
        if signals.get("agent_write_capable_tools"):
            required.update(plane_ov.get("additional_required_if_agent_capability", []))

    return effective_tier, required


def _probe_external_tools(root: Path, docs_dir: Path, report: ValidationReport) -> None:
    tools = {
        "mmdc": shutil.which("mmdc"),
        "spectral": shutil.which("spectral"),
        "asyncapi": shutil.which("asyncapi"),
        "xmllint": shutil.which("xmllint"),
    }
    for name, bin_path in tools.items():
        if bin_path is None:
            report.external_tools[name] = "UNAVAILABLE (not installed on PATH; skipped)"
        else:
            report.external_tools[name] = f"AVAILABLE ({bin_path})"

    # Run xmllint only if installed and .bpmn/.xml files exist under docs/
    if tools["xmllint"]:
        for xml_file in list(docs_dir.rglob("*.bpmn")) + list(docs_dir.rglob("*.xml")):
            proc = subprocess.run(
                [tools["xmllint"], "--noout", str(xml_file)],
                cwd=root,
                capture_output=True,
                text=True,
            )
            if proc.returncode != 0:
                report.add_error("VAL-XML-001", xml_file, f"xmllint failed: {proc.stderr.strip()}")


def validate_repository(root: Path) -> ValidationReport:
    root = root.resolve()
    docs_dir = root / "docs"
    gov_dir = docs_dir / "governance"
    schemas_dir = gov_dir / "schemas"
    templates_dir = gov_dir / "templates"
    report = ValidationReport(root=root)

    if not docs_dir.is_dir():
        report.add_error("VAL-STRUCT-001", docs_dir, "Missing docs/ directory.")
        return report

    # 1. Prohibited archive or empty folders check
    if (docs_dir / "archive").exists():
        report.add_error("VAL-STRUCT-002", docs_dir / "archive", "Legacy docs/archive/ directory is prohibited.")

    for d in sorted(docs_dir.rglob("*")):
        if d.is_dir():
            if not any(d.iterdir()):
                report.add_error("VAL-STRUCT-003", d, "Empty placeholder directory is prohibited under docs/.")

    # 2. Load JSON Schemas
    required_schemas = {
        "frontmatter": schemas_dir / "document-frontmatter.schema.json",
        "capability": schemas_dir / "capability-manifest.schema.json",
        "catalog": schemas_dir / "artifact-catalog.schema.json",
        "matrix": schemas_dir / "artifact-applicability-matrix.schema.json",
        "docs_index": schemas_dir / "docs-index.schema.json",
        "traceability": schemas_dir / "traceability.schema.json",
    }
    loaded_schemas: dict[str, dict[str, Any]] = {}
    for key, spath in required_schemas.items():
        if not spath.is_file():
            report.add_error("VAL-SCHEMA-001", spath, f"Missing required schema file '{spath.name}'.")
            continue
        try:
            loaded_schemas[key] = _load_json_schema(spath)
        except json.JSONDecodeError as exc:
            report.add_error("VAL-SCHEMA-001", spath, f"Invalid JSON schema syntax: {exc}")

    # 3. Validate docs-index.yaml
    docs_index_path = docs_dir / "docs-index.yaml"
    docs_index_data: dict[str, Any] | None = None
    if not docs_index_path.is_file():
        report.add_error("VAL-INDEX-001", docs_index_path, "Missing docs/docs-index.yaml root index.")
    else:
        try:
            docs_index_data = yaml.safe_load(docs_index_path.read_text(encoding="utf-8"))
            if "docs_index" in loaded_schemas:
                _validate_against_schema(
                    docs_index_data, loaded_schemas["docs_index"], report, "VAL-INDEX-001", docs_index_path
                )
            if isinstance(docs_index_data, dict):
                for key, val in (docs_index_data.get("governance") or {}).items():
                    if not (root / val).exists():
                        report.add_error(
                            "VAL-LINK-001", docs_index_path, f"governance.{key} points to missing path '{val}'."
                        )
                for pkey in ("root_entrypoint", "validator_entrypoint"):
                    pval = docs_index_data.get(pkey)
                    if pval and not (root / pval).exists():
                        report.add_error("VAL-LINK-001", docs_index_path, f"{pkey} points to missing path '{pval}'.")
                ae = docs_index_data.get("agent_entrypoints") or {}
                for k in ("primary", "hooks_config"):
                    if ae.get(k) and not (root / ae[k]).exists():
                        report.add_error("VAL-LINK-001", docs_index_path, f"agent_entrypoints.{k} missing '{ae[k]}'.")
                for ro in ae.get("reading_order") or []:
                    if not (root / ro).exists():
                        report.add_error(
                            "VAL-LINK-001", docs_index_path, f"agent_entrypoints.reading_order missing '{ro}'."
                        )
        except yaml.YAMLError as exc:
            report.add_error("VAL-YAML-001", docs_index_path, f"Invalid YAML syntax: {exc}")

    # 4. Validate artifact-catalog.yaml & artifact-applicability-matrix.yaml
    catalog_path = gov_dir / "catalog" / "artifact-catalog.yaml"
    matrix_path = gov_dir / "catalog" / "artifact-applicability-matrix.yaml"
    catalog_data: dict[str, Any] | None = None
    matrix_data: dict[str, Any] | None = None
    catalog_artifact_ids: set[str] = set()
    seen_doc_ids: dict[str, Path] = {}

    if not catalog_path.is_file():
        report.add_error("VAL-CAT-001", catalog_path, "Missing artifact-catalog.yaml.")
    else:
        try:
            catalog_data = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
            if "catalog" in loaded_schemas:
                _validate_against_schema(catalog_data, loaded_schemas["catalog"], report, "VAL-CAT-001", catalog_path)
            if isinstance(catalog_data, dict):
                if catalog_data.get("doc_id"):
                    seen_doc_ids[catalog_data["doc_id"]] = catalog_path
                for art in catalog_data.get("artifacts", []):
                    aid = art.get("artifact_id")
                    if aid in catalog_artifact_ids:
                        report.add_error("VAL-CAT-001", catalog_path, f"Duplicate artifact_id '{aid}'.")
                    if aid:
                        catalog_artifact_ids.add(aid)
                    for path_field in ("template_path", "schema_path"):
                        rel_target = art.get(path_field)
                        if rel_target and not (root / rel_target).is_file():
                            report.add_error(
                                "VAL-LINK-001",
                                catalog_path,
                                f"{aid}.{path_field} references missing file '{rel_target}'.",
                            )
                for art in catalog_data.get("artifacts", []):
                    aid = art.get("artifact_id")
                    for dep_art in art.get("required_related_artifacts", []):
                        if dep_art not in catalog_artifact_ids:
                            report.add_error(
                                "VAL-CAT-001",
                                catalog_path,
                                f"{aid}.required_related_artifacts references unknown artifact '{dep_art}'.",
                            )
        except yaml.YAMLError as exc:
            report.add_error("VAL-YAML-001", catalog_path, f"Invalid YAML syntax: {exc}")

    if not matrix_path.is_file():
        report.add_error("VAL-MAT-001", matrix_path, "Missing artifact-applicability-matrix.yaml.")
    else:
        try:
            matrix_data = yaml.safe_load(matrix_path.read_text(encoding="utf-8"))
            if "matrix" in loaded_schemas:
                _validate_against_schema(
                    matrix_data, loaded_schemas["matrix"], report, "VAL-MAT-001", matrix_path
                )
            if isinstance(matrix_data, dict):
                if matrix_data.get("doc_id"):
                    if matrix_data["doc_id"] in seen_doc_ids:
                        report.add_error(
                            "VAL-ID-UNIQUE-001", matrix_path, f"Duplicate doc_id '{matrix_data['doc_id']}'."
                        )
                    seen_doc_ids[matrix_data["doc_id"]] = matrix_path
                # Check all ART-* IDs in matrix exist in catalog
                if catalog_artifact_ids:
                    for tier_name, bucket in (matrix_data.get("capability_baseline_by_tier") or {}).items():
                        for cls_name, art_list in bucket.items():
                            for aid in art_list or []:
                                if aid not in catalog_artifact_ids:
                                    report.add_error(
                                        "VAL-MAT-001",
                                        matrix_path,
                                        f"Tier {tier_name}.{cls_name} references unknown artifact '{aid}'.",
                                    )
                    for ov in matrix_data.get("signal_overrides", []):
                        for aid in ov.get("required_artifacts", []):
                            if aid not in catalog_artifact_ids:
                                sig_name = ov.get("signal")
                                report.add_error(
                                    "VAL-MAT-001",
                                    matrix_path,
                                    f"signal_override({sig_name}) references unknown artifact '{aid}'.",
                                )
        except yaml.YAMLError as exc:
            report.add_error("VAL-YAML-001", matrix_path, f"Invalid YAML syntax: {exc}")

    # 5. Parse and validate all YAML files under docs/
    yaml_files = sorted(list(docs_dir.rglob("*.yaml")) + list(docs_dir.rglob("*.yml")))
    capability_manifests: list[tuple[Path, dict[str, Any]]] = []
    traceability_files: list[tuple[Path, dict[str, Any]]] = []

    for ypath in yaml_files:
        raw_ytext = ypath.read_text(encoding="utf-8")
        try:
            if ypath.name == "document-frontmatter.template.yaml":
                docs_iter = [d for d in yaml.safe_load_all(raw_ytext) if d is not None]
                ydata = docs_iter[0] if len(docs_iter) == 1 else docs_iter
            else:
                ydata = yaml.safe_load(raw_ytext)
        except yaml.YAMLError as exc:
            report.add_error("VAL-YAML-001", ypath, f"Invalid YAML syntax: {exc}")
            continue

        is_template = templates_dir in ypath.parents
        if not is_template:
            _check_openapi_or_asyncapi(ypath, ydata, report)
            if ypath.name == "capability.yaml":
                if "capability" in loaded_schemas:
                    _validate_against_schema(ydata, loaded_schemas["capability"], report, "VAL-CAP-SCHEMA-001", ypath)
                if isinstance(ydata, dict):
                    capability_manifests.append((ypath, ydata))
            elif ypath.name == "traceability.yaml":
                if "traceability" in loaded_schemas:
                    _validate_against_schema(
                        ydata, loaded_schemas["traceability"], report, "VAL-TRAC-SCHEMA-001", ypath
                    )
                if isinstance(ydata, dict):
                    traceability_files.append((ypath, ydata))

    # 6. Validate Markdown documents under docs/ + AGENTS.md + README.md
    md_files = sorted(docs_dir.rglob("*.md"))
    heading_cache: dict[Path, tuple[list[tuple[int, int, str]], set[str]]] = {}
    parsed_docs: list[tuple[Path, dict[str, Any] | None, str, int]] = []
    seen_req_ids: dict[str, Path] = {}

    for md_path in md_files:
        text = md_path.read_text(encoding="utf-8")
        if not text.strip():
            report.add_error("VAL-EMPTY-001", md_path, "Empty Markdown file is prohibited.")
            continue
        fm, body, body_start, fm_err = _parse_frontmatter(text)
        if fm_err:
            report.add_error("VAL-FM-001", md_path, fm_err, 1)
            parsed_docs.append((md_path, None, body, body_start))
            continue

        assert fm is not None
        if "frontmatter" in loaded_schemas:
            _validate_against_schema(fm, loaded_schemas["frontmatter"], report, "VAL-FM-001", md_path)

        doc_id = fm.get("doc_id")
        if isinstance(doc_id, str):
            if doc_id in seen_doc_ids:
                report.add_error(
                    "VAL-ID-UNIQUE-001",
                    md_path,
                    f"Duplicate doc_id '{doc_id}' (already defined in {report._rel(seen_doc_ids[doc_id])}).",
                    2,
                )
            else:
                seen_doc_ids[doc_id] = md_path

        parsed_docs.append((md_path, fm, body, body_start))
        headings, anchors = _extract_headings_and_anchors(text)
        heading_cache[md_path.resolve()] = (headings, anchors)

        is_template = templates_dir in md_path.parents
        is_governance = gov_dir in md_path.parents
        body_lines = _strip_fenced_blocks_preserve_lines(body.splitlines())

        # Heading hierarchy & non-empty body checks
        if not body.strip():
            report.add_error(
                "VAL-EMPTY-001", md_path, "Markdown document has empty body after frontmatter.", body_start
            )
        if not is_template:
            h1s = [h for h in headings if h[1] == 1]
            if len(h1s) != 1:
                report.add_error(
                    "VAL-STRUCT-004", md_path, f"Expected exactly 1 H1 heading, found {len(h1s)}.", body_start
                )
            prev_level = 0
            for ln, lvl, title in headings:
                if prev_level and lvl > prev_level + 1:
                    report.add_error(
                        "VAL-STRUCT-004",
                        md_path,
                        f"Skipped heading level: H{prev_level} -> H{lvl} ('{title}').",
                        ln,
                    )
                prev_level = lvl

            # Check for empty leaf sections (a heading immediately followed by another heading <= its level or EOF)
            raw_body_lines = body.splitlines()
            heading_line_indices = {h[0] - body_start: h for h in headings}
            sorted_h_offsets = sorted(heading_line_indices.keys())
            for pos, h_off in enumerate(sorted_h_offsets):
                h_line, h_lvl, h_title = heading_line_indices[h_off]
                next_off = sorted_h_offsets[pos + 1] if pos + 1 < len(sorted_h_offsets) else len(raw_body_lines)
                slice_content = "\n".join(raw_body_lines[h_off + 1 : next_off]).strip()
                has_child_heading = (
                    pos + 1 < len(sorted_h_offsets)
                    and heading_line_indices[sorted_h_offsets[pos + 1]][1] > h_lvl
                )
                if not slice_content and not has_child_heading:
                    report.add_error(
                        "VAL-EMPTY-002",
                        md_path,
                        f"Empty section '{h_title}' has no content.",
                        h_line,
                    )

        # Check APPROVED document hygiene
        if fm.get("status") == "APPROVED" and not is_template:
            rev = fm.get("revision_history") or []
            ver = fm.get("version")
            if not any(isinstance(r, dict) and r.get("version") == ver for r in rev):
                report.add_error(
                    "VAL-STATUS-001",
                    md_path,
                    f"APPROVED document version '{ver}' must have a matching entry in revision_history.",
                )
            for idx, line in enumerate(body_lines):
                # Ignore tokens quoted in inline backticks (e.g., rules discussing forbidden `TBD`)
                cleaned = re.sub(r"`[^`]*`", "", line)
                if UNRESOLVED_TOKEN_RE.search(cleaned):
                    report.add_error(
                        "VAL-TBD-001",
                        md_path,
                        "APPROVED document contains unresolved TBD/TODO/FIXME/[TO BE COMPLETED] outside inline code.",
                        body_start + idx,
                    )

        # Required document sections by doc_type / artifact on non-template, non-governance docs
        if not is_template and not is_governance:
            h2_lower = [t.lower() for _, lvl, t in headings if lvl == 2]
            dtype = fm.get("doc_type")
            if dtype == "adr":
                for kw in ("context", "option", "decision", "consequence"):
                    if not any(kw in t for t in h2_lower):
                        report.add_error(
                            "VAL-SECT-001",
                            md_path,
                            f"ADR document missing required section covering '{kw}'.",
                        )
            elif dtype == "architecture":
                for kw in ("scope", "context", "building"):
                    if not any(kw in t for t in h2_lower):
                        report.add_error(
                            "VAL-SECT-001",
                            md_path,
                            f"Architecture document missing required section covering '{kw}'.",
                        )
            elif dtype == "specification" and len(h2_lower) < 2:
                report.add_error(
                    "VAL-SECT-001",
                    md_path,
                    "Specification document must define at least 2 non-empty H2 sections.",
                )
            if md_path.name == "threat-model.md":
                all_h_lower = " ".join(t.lower() for _, _, t in headings) + " " + body.lower()
                for kw in ("asset", "trust boundar", "entry point", "threat", "mitigation", "residual risk"):
                    if kw not in all_h_lower:
                        report.add_error(
                            "VAL-SECT-001",
                            md_path,
                            f"Threat model missing mandatory topic '{kw}'.",
                        )

        # Derived diagram validation
        if fm.get("doc_type") == "diagram" and not is_template:
            sot = fm.get("source_of_truth") or {}
            if sot.get("is_authoritative") is not False:
                report.add_error(
                    "VAL-DIAG-SOT-001",
                    md_path,
                    "Derived diagram must set source_of_truth.is_authoritative: false.",
                )
            auth_sources = sot.get("authoritative_source") or []
            if not auth_sources:
                report.add_error(
                    "VAL-DIAG-SOT-001", md_path, "Derived diagram missing source_of_truth.authoritative_source."
                )
            h_titles_lower = [t.lower() for _, _, t in headings]
            if not any("legend" in t for t in h_titles_lower):
                report.add_error("VAL-DIAG-META-001", md_path, "Diagram document must include a Legend section.")
            if not any("metadata" in t for t in h_titles_lower):
                report.add_error(
                    "VAL-DIAG-META-001", md_path, "Diagram document must include a Diagram Metadata section."
                )
            m_headers = _validate_mermaid_blocks(md_path, body, report, body_start)
            if not m_headers and not re.search(r"\.bpmn\b", body):
                report.add_error(
                    "VAL-DIAG-MERMAID-001",
                    md_path,
                    "Diagram document contains neither a valid Mermaid block nor a .bpmn reference.",
                )
        elif "```mermaid" in body:
            _validate_mermaid_blocks(md_path, body, report, body_start)

        # Unique requirement IDs across non-governance / non-template specs
        if not is_template and not is_governance:
            local_table_ids: set[str] = set()
            for idx, line in enumerate(body_lines):
                m_row = REQ_ID_ROW_RE.match(line.strip())
                if m_row:
                    rid = m_row.group(1)
                    if rid in local_table_ids or (rid in seen_req_ids and seen_req_ids[rid] != md_path):
                        prev_rel = report._rel(seen_req_ids.get(rid, md_path))
                        report.add_error(
                            "VAL-ID-UNIQUE-001",
                            md_path,
                            f"Duplicate requirement table ID '{rid}' (already defined in {prev_rel}).",
                            body_start + idx,
                        )
                    else:
                        local_table_ids.add(rid)
                        seen_req_ids[rid] = md_path
            for req_id in fm.get("requirement_ids") or []:
                if req_id in seen_req_ids and seen_req_ids[req_id] != md_path:
                    prev_rel = report._rel(seen_req_ids[req_id])
                    report.add_error(
                        "VAL-ID-UNIQUE-001",
                        md_path,
                        f"Duplicate requirement_id '{req_id}' (already registered in {prev_rel}).",
                    )
                else:
                    seen_req_ids[req_id] = md_path

    # 7. Pass 2 on Markdown files: validate cross-doc IDs, source_of_truth paths, and local links + anchors
    all_md_check_files = list(md_files)
    for root_extra in (root / "AGENTS.md", root / "README.md", root / ".agents" / "README.md"):
        if root_extra.is_file():
            all_md_check_files.append(root_extra)
            if root_extra.resolve() not in heading_cache:
                heading_cache[root_extra.resolve()] = _extract_headings_and_anchors(
                    root_extra.read_text(encoding="utf-8")
                )

    parsed_by_path = {p: (fm, body, bs) for p, fm, body, bs in parsed_docs}
    for md_path in all_md_check_files:
        text = md_path.read_text(encoding="utf-8")
        if md_path in parsed_by_path:
            fm, body, body_start = parsed_by_path[md_path]
        else:
            fm, body, body_start = None, text, 1

        is_template = templates_dir in md_path.parents
        if fm and not is_template:
            # Verify related_docs & depends_on resolve to known doc_id or existing file
            for field_name in ("related_docs", "depends_on"):
                for ref in fm.get(field_name) or []:
                    if not isinstance(ref, str) or ref.startswith("<"):
                        continue
                    if ref not in seen_doc_ids and not (root / ref).exists() and not (md_path.parent / ref).exists():
                        report.add_error(
                            "VAL-REF-001",
                            md_path,
                            f"Frontmatter '{field_name}' reference '{ref}' does not resolve to a known doc_id or file.",
                        )
            # Verify file-like source_of_truth paths exist
            sot = fm.get("source_of_truth") or {}
            for src in sot.get("authoritative_source") or []:
                if isinstance(src, str) and _is_path_like(src):
                    if not (root / src).exists() and not (md_path.parent / src).exists():
                        report.add_error(
                            "VAL-LINK-001",
                            md_path,
                            f"source_of_truth.authoritative_source path '{src}' does not exist.",
                        )

        # Verify relative Markdown links & anchors
        lines = _strip_fenced_blocks_preserve_lines(body.splitlines())
        for idx, line in enumerate(lines):
            # Ignore links inside inline code spans
            cleaned = re.sub(r"`[^`]*`", "", line)
            for match in MD_LINK_RE.finditer(cleaned):
                raw_target = match.group(1).strip().strip("<>").split()[0]
                if not raw_target or raw_target.startswith(("http://", "https://", "mailto:", "<")):
                    continue
                if raw_target.startswith("#"):
                    anchor = raw_target[1:].lower()
                    _, anchors = heading_cache.get(md_path.resolve(), ([], set()))
                    if anchor and anchor not in anchors:
                        report.add_error(
                            "VAL-LINK-002",
                            md_path,
                            f"Broken same-file anchor '#{anchor}'.",
                            body_start + idx,
                        )
                    continue

                if "#" in raw_target:
                    file_part, anchor_part = raw_target.split("#", 1)
                else:
                    file_part, anchor_part = raw_target, ""

                # Note: template files may link to sibling <...> examples if explicitly bracketed
                if "<" in file_part or ">" in file_part:
                    continue

                resolved = (md_path.parent / file_part).resolve()
                if not resolved.exists():
                    # Also allow repo-root relative links if written cleanly
                    repo_resolved = (root / file_part).resolve()
                    if repo_resolved.exists():
                        resolved = repo_resolved
                    else:
                        report.add_error(
                            "VAL-LINK-001",
                            md_path,
                            f"Broken relative link '{raw_target}'.",
                            body_start + idx,
                        )
                        continue

                if anchor_part and resolved.is_file() and resolved.suffix.lower() == ".md":
                    if resolved not in heading_cache:
                        heading_cache[resolved] = _extract_headings_and_anchors(
                            resolved.read_text(encoding="utf-8")
                        )
                    _, target_anchors = heading_cache[resolved]
                    if anchor_part.lower() not in target_anchors:
                        report.add_error(
                            "VAL-LINK-002",
                            md_path,
                            f"Broken anchor '#{anchor_part}' in link '{raw_target}'.",
                            body_start + idx,
                        )

    # 8. Capability Manifest deep governance & applicability enforcement
    seen_cap_ids: dict[str, Path] = {}
    for cap_path, cap_data in capability_manifests:
        cid = cap_data.get("capability_id")
        if cid:
            if cid in seen_cap_ids:
                report.add_error("VAL-ID-UNIQUE-001", cap_path, f"Duplicate capability_id '{cid}'.")
            else:
                seen_cap_ids[cid] = cap_path

        # Check all paths declared on capability manifest exist cleanly
        for rel_doc in cap_data.get("authoritative_documents") or []:
            if not (cap_path.parent / rel_doc).exists() and not (root / rel_doc).exists():
                report.add_error("VAL-LINK-001", cap_path, f"authoritative_documents path '{rel_doc}' does not exist.")
        for path_group in ("related_contracts", "code_paths", "test_paths"):
            for p_str in cap_data.get(path_group) or []:
                if not (root / p_str).exists() and not (cap_path.parent / p_str).exists():
                    report.add_error("VAL-LINK-001", cap_path, f"{path_group} path '{p_str}' does not exist.")

        # Matrix & catalog rules
        if matrix_data and catalog_artifact_ids:
            declared_tier = str(cap_data.get("risk_tier", "LOW"))
            effective_tier, required_art_ids = _compute_required_artifacts(cap_data, matrix_data)
            if TIER_RANK.get(declared_tier, 0) < TIER_RANK.get(effective_tier, 0):
                report.add_error(
                    "VAL-CAP-MATRIX-001",
                    cap_path,
                    f"Declared risk_tier '{declared_tier}' is below minimum '{effective_tier}' for active signals.",
                )

            declared_items: dict[str, dict[str, Any]] = {}
            for item in cap_data.get("required_artifacts") or []:
                aid = item.get("artifact_id")
                if aid not in catalog_artifact_ids:
                    report.add_error(
                        "VAL-CAP-SCHEMA-001", cap_path, f"Unknown artifact_id '{aid}' not in artifact-catalog.yaml."
                    )
                declared_items[aid] = item
                app = item.get("applicability")
                st = item.get("status")
                reason = str(item.get("not_applicable_reason") or "").strip()
                if (app == "NOT_APPLICABLE_WITH_REASON" or st == "NOT_APPLICABLE") and len(reason) < 5:
                    report.add_error(
                        "VAL-CAP-REASON-001",
                        cap_path,
                        f"Artifact '{aid}' marked not applicable MUST include a non-empty not_applicable_reason.",
                    )
                if st == "PRESENT":
                    ipath = item.get("path")
                    if not ipath or (not (cap_path.parent / ipath).exists() and not (root / ipath).exists()):
                        report.add_error(
                            "VAL-LINK-001",
                            cap_path,
                            f"Artifact '{aid}' has status=PRESENT but path '{ipath}' does not exist.",
                        )

            for req_aid in sorted(required_art_ids):
                if req_aid not in declared_items:
                    report.add_error(
                        "VAL-CAP-MATRIX-001",
                        cap_path,
                        f"Missing required artifact '{req_aid}' mandated by applicability matrix for tier/signals.",
                    )
                else:
                    entry = declared_items[req_aid]
                    if entry.get("applicability") != "REQUIRED":
                        app_val = entry.get("applicability")
                        report.add_error(
                            "VAL-CAP-MATRIX-001",
                            cap_path,
                            f"Artifact '{req_aid}' is REQUIRED by matrix and cannot be downgraded to '{app_val}'.",
                        )
                    doc_st = cap_data.get("document_status")
                    if doc_st in ("IN_REVIEW", "APPROVED") and entry.get("status") != "PRESENT":
                        report.add_error(
                            "VAL-CAP-MATRIX-001",
                            cap_path,
                            f"Required artifact '{req_aid}' must be PRESENT when document_status={doc_st}.",
                        )

    # 9. Traceability checks
    for tpath, tdata in traceability_files:
        for link in tdata.get("links") or []:
            for did in link.get("design_doc_ids") or []:
                if did not in seen_doc_ids and not did.startswith("<"):
                    report.add_error("VAL-TRAC-001", tpath, f"Traceability design_doc_id '{did}' not found among docs.")
            for group in ("contract_paths", "implementation_paths", "test_paths"):
                for p_str in link.get(group) or []:
                    if not (root / p_str).exists() and not (tpath.parent / p_str).exists():
                        report.add_error("VAL-TRAC-001", tpath, f"Traceability {group} path '{p_str}' does not exist.")

    # 10. Optional external CLI validators
    _probe_external_tools(root, docs_dir, report)

    report.stats = {
        "markdown_files": len(md_files),
        "yaml_files": len(yaml_files),
        "unique_doc_ids": len(seen_doc_ids),
        "capability_manifests": len(capability_manifests),
        "traceability_files": len(traceability_files),
        "errors": len(report.errors),
        "warnings": len(report.warnings),
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate FinancialMarketDataPlatform Documentation V2.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Repository root directory (defaults to auto-detected repo root).",
    )
    parser.add_argument("--json", action="store_true", help="Print structured JSON output.")
    args = parser.parse_args(argv)

    report = validate_repository(args.root)
    if args.json:
        payload = {
            "stats": report.stats,
            "external_tools": report.external_tools,
            "errors": [i.__dict__ for i in report.errors],
            "warnings": [i.__dict__ for i in report.warnings],
        }
        print(json.dumps(payload, indent=2))
    else:
        print("=== FMDP Documentation V2 Validator ===")
        print(
            f"Scanned: {report.stats.get('markdown_files', 0)} Markdown files, "
            f"{report.stats.get('yaml_files', 0)} YAML files, "
            f"{report.stats.get('unique_doc_ids', 0)} doc_ids, "
            f"{report.stats.get('capability_manifests', 0)} capability manifests"
        )
        for tool_name, status in report.external_tools.items():
            print(f"[TOOL] {tool_name}: {status}")
        for issue in report.issues:
            print(issue.format())
        if not report.errors:
            print(f"PASS: 0 errors, {len(report.warnings)} warnings.")
        else:
            print(f"FAIL: {len(report.errors)} errors, {len(report.warnings)} warnings.")
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
