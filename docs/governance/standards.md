---
doc_id: "DOC-GOV-STD-001"
title: "Greenfield Documentation Standards, Metadata Policy & Validator Rationale"
version: "1.0.0"
status: "IN_REVIEW"
implementation_status: "IMPLEMENTED"
owner: "System Analyst & Principal Software Architect"
purpose: "Defines documentation quality gates, status taxonomy, validator architecture, and rationale for replacing the legacy V2 validator."
scope: "All documentation and work-item artifacts on branch greenfield/main."
dependencies:
  - "AGENTS.md"
  - "docs/governance/README.md"
references:
  - ".agents/README.md"
  - "tools/validators/validate_greenfield.py"
assumptions:
  - "All specs are reviewed against phase acceptance criteria before advancing phases."
open_issues: []
review_criteria:
  - "Metadata keys enforced identically by validate_greenfield.py"
  - "Work-item status lifecycle enforces BACKLOG..COMPLETE with evidence gate"
---

# Greenfield Documentation Standards & Validator Rationale

## 1. Document Lifecycle & Status Separation

Every engineering artifact separates **review governance** from **code reality**:
- **`status`** (Documentation Review): `DRAFT` | `IN_REVIEW` | `ACCEPTED` | `APPROVED` | `DEPRECATED`
- **`implementation_status`** (Code/Runtime Verification): `NOT_APPLICABLE` | `PLANNED` | `NOT_IMPLEMENTED` | `POC_VALIDATED` | `PARTIALLY_IMPLEMENTED` | `IMPLEMENTED` | `VERIFIED`

## 2. Mandatory Metadata Frontmatter (`Section 6.3`)

Every Markdown file under `docs/` MUST provide YAML frontmatter defining:
`doc_id`, `title`, `version`, `status`, `owner`, `purpose`, `scope`, `dependencies`, `references`, `assumptions`, `open_issues`, `review_criteria`.

## 3. Work-Item Lifecycle (`Section 9`)

Work items under [docs/work-items/](../work-items/README.md) follow:
`BACKLOG -> READY -> IN_PROGRESS -> [BLOCKED] -> IN_REVIEW -> TESTING -> ACCEPTED -> COMPLETE`
No work item may transition to `COMPLETE` with an empty `evidence` list.

## 4. Validator Replacement Decision (`DEC-P0-001` Conditions 8–10)

Prior to creating `greenfield/main`, `.agents/hooks.json` and the legacy V2 validator (`scripts/docs/validate_docs.py`) were inspected:
- **Why Replaced**: The V2 validator required legacy V2 directories (`docs/docs-index.yaml`, `docs/governance/catalog/artifact-catalog.yaml`, legacy `capability.yaml` manifests referencing legacy `src/ingestion`, `src/serving`, `src/intelligence`), had no schema for greenfield work items or phase reports, and hooks invoked bare `python` (Python 3.8 on host `PATH`).
- **New Configuration**: [validate_greenfield.py](../../tools/validators/validate_greenfield.py) + [run_all.py](../../tools/validators/run_all.py) + [.agents/hooks.json](../../.agents/hooks.json) actively enforce metadata completeness, directory `README.md` presence, zero legacy directory pollution (`GF-CLEAN-001`), link/anchor integrity, Mermaid block validity, and Work-Item schema constraints without ever disabling validation.

