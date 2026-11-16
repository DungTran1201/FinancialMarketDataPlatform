---
doc_id: GOV-POL-VER-001
title: "Versioning, Document Status & Implementation Status Policy"
doc_type: governance
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: documentation-architect
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/versioning-and-status.md"
related_docs:
  - GOV-POL-LIFE-001
  - GOV-POL-CHG-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Defined SemVer rules and strict state enums for Document Status and Implementation Status."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: documentation-architect
    summary: "Initial versioning and status policy."
---

# Versioning, Document Status & Implementation Status Policy

## 1. Document Versioning (SemVer `MAJOR.MINOR.PATCH`)

- **MAJOR (`X.0.0`)**: Breaking restructuring, breaking API/event contract version, or major documentation architecture change.
- **MINOR (`0.Y.0`)**: New requirements, new endpoints, new capability sections, or non-breaking design additions.
- **PATCH (`0.0.Z`)**: Clarifications, typo/link fixes, `AS-IS` evidence updates, or status transitions without semantic scope change.

## 2. Document Status Definitions (`status`)

Every governed Markdown document and `capability.yaml` (`document_status`) MUST use exactly one of these four values:

| Status | Meaning | Allowed Transitions | Gate / Condition |
|---|---|---|---|
| `DRAFT` | Initial authoring or revision in progress; MAY contain `[OPEN]` questions or `[ASSUMPTION]` tags | `IN_REVIEW`, `DEPRECATED` | Default for new specifications |
| `IN_REVIEW` | Submitted for peer, architect, security, or QA review | `DRAFT`, `APPROVED`, `DEPRECATED` | Open placeholders resolved or explicitly waived |
| `APPROVED` | Reviewed and signed off by accountable owner (`approved_by` + `approved_at` + `change_summary` required) | `IN_REVIEW`, `DEPRECATED` | Zero `[TO BE COMPLETED]` / `TBD` / `TODO`; validator passes |
| `DEPRECATED` | Superseded or retired from active engineering use (`superseded_by` required when replaced) | None (terminal; delete on cleanup) | Migration/sunset note recorded |

## 3. Implementation Status Definitions (`implementation_status`)

| Implementation Status | Meaning | Required Evidence |
|---|---|---|
| `PLANNED` | Scoped in roadmap/capability manifest; no code exists yet | `capability.yaml` scope definition |
| `NOT_IMPLEMENTED` | Specification exists, but corresponding source code/endpoints are absent | Source inspection confirms absence |
| `SIMULATED` | Runs via in-memory stubs, mock adapters, or embedded test doubles rather than real infrastructure | Code references showing simulation/mock |
| `PARTIALLY_IMPLEMENTED` | Core logic exists, but required integrations, persistence, auth, or edge handlers are incomplete | Exact implemented vs. missing file paths |
| `IMPLEMENTED` | Production-path code and configs exist, awaiting full verification evidence | Code + config paths recorded |
| `VERIFIED` | Code implementation passed deterministic tests and security/quality gates in target mode | Executed test report & environment disclosure |
| `NOT_APPLICABLE` | Pure governance policy, standard, or reusable template without runtime code | Allowed only on `doc_type: governance | standard | template | index | migration-report` |
