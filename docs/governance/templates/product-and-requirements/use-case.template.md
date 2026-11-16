---
doc_id: TPL-REQ-UC-001
title: "Template: Use Case Specification"
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
    - "docs/governance/templates/product-and-requirements/use-case.template.md"
related_docs:
  - GOV-STD-REQ-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created Use Case template covering actors, preconditions, main flow, alternative/exception paths, and postconditions."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Initial V2 Use Case template."
---

# Template: Use Case Specification

Each non-trivial actor interaction MUST live in its own file under `<capability>/use-cases/`.

---

# Use Case: `<UC-DOM-NNN> — <Verb-Noun Goal>`

## 1. Identification & Traceability `[REQUIRED]`

- **Use Case ID**: `UC-<DOM>-001`
- **Primary Actor**: `<Role or System Actor>`
- **Secondary Actors**: `<Optional external system / worker>`
- **Parent Requirements**: `FR-<DOM>-001`
- **Applied Business Rules**: `RULE-<DOM>-001`

## 2. Trigger, Preconditions & Postconditions `[REQUIRED]`

- **Trigger**: `<Event or user action initiating the use case>`
- **Preconditions**: `<Required system/auth/data state before entry>`
- **Success Postconditions**: `<Guaranteed state upon completion>`
- **Failure Postconditions**: `<Rollback, DLQ, or error state preserved on failure>`

## 3. Main Success Flow `[REQUIRED]`

1. `<Actor action or incoming event>`
2. `<System validation and state lookup>`
3. `<Outcome returned or persisted>`

## 4. Alternative & Exception Flows `[REQUIRED]`

| Branch ID | Condition / Error Trigger | System Behavior | Outcome / Error Code |
|---|---|---|---|
| `ALT-1` | `<Valid alternative path>` | `<System action>` | `<Result>` |
| `EXC-1` | `<Validation / auth / downstream failure>` | `<Safe handling, audit log, rollback>` | `<RFC 7807 / DLQ>` |

## 5. Non-Functional & Security Notes `[CONDITIONAL: Required if latency, rate-limit, or auth constraints apply]`

- `<Linked NFR or SEC IDs>`
