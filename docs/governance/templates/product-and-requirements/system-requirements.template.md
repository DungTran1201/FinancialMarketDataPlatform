---
doc_id: TPL-REQ-SYS-001
title: "Template: System / Capability Requirements Specification"
doc_type: template
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: business-analyst
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/templates/product-and-requirements/system-requirements.template.md"
related_docs:
  - GOV-STD-REQ-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created ISO/IEC/IEEE 29148-aligned functional requirements template."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Initial V2 system requirements template."
---

# Template: System / Capability Requirements Specification

Instantiated inside `<capability>/requirements/` (or `<plane>/` for strictly cross-domain constraints). Every requirement MUST be atomic, unambiguous, feasible, necessary, consistent, verifiable, and traceable (`ISO/IEC/IEEE 29148`). Separate **WHAT** from **HOW**.

---

# Requirements: `<Capability or Scope Name>`

## 1. Scope & Upstream Traceability `[REQUIRED]`

- **Capability**: `<CAP-DOM-NNN>`
- **Parent Business Requirements**: `<BR-DOM-NNN>`
- **Constraints**: `<CON-DOM-NNN or None>`

## 2. Functional Requirements `[REQUIRED]`

| ID | Statement (`The system MUST...`) | Priority (`P0..P3`) | Parent BR | Verification Method (`Test | Inspection | Demo`) | Status (`DRAFT | APPROVED`) |
|---|---|---|---|---|---|
| `FR-<DOM>-001` | `<Atomic, implementation-neutral requirement>` | `P0` | `BR-<DOM>-001` | `Test` | `DRAFT` |

## 3. Acceptance Criteria `[REQUIRED]`

| AC ID | Parent FR | Given (Precondition) | When (Trigger) | Then (Verifiable Outcome) | Linked TC |
|---|---|---|---|---|---|
| `AC-<DOM>-001` | `FR-<DOM>-001` | `<Initial state>` | `<Action or input>` | `<Deterministic observable output>` | `TC-<DOM>-001` |

## 4. Assumptions & Open Questions `[CONDITIONAL: Required if any assumption or ambiguity exists]`

| ID | Classification (`ASSUMPTION | OPEN | BLOCKED`) | Description | Owner | Blocking Impact |
|---|---|---|---|---|
| `OQ-<DOM>-001` | `OPEN` | `<Unresolved product or technical question>` | `<role>` | `<Which FR/AC is blocked>` |
