---
doc_id: TPL-INT-ERR-001
title: "Template: Error Catalog Specification"
doc_type: template
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/templates/interfaces-and-data/error-catalog.template.md"
related_docs:
  - GOV-STD-API-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created Error Catalog template mapping HTTP status, machine codes, retryability, and DLQ handling."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Initial V2 error catalog template."
---

# Template: Error Catalog Specification

Defines canonical HTTP/WS/event error codes without duplicating full OpenAPI/AsyncAPI schemas.

---

# Error Catalog: `<Capability or Plane Name>`

## 1. Error Codes Registry `[REQUIRED]`

| Error Code | HTTP / Event Status | Trigger Condition | Retryable (`Yes / No`) | Client / Operator Action |
|---|---|---|---|---|
| `ERR_<DOM>_VALIDATION` | `422` / `DLQ` | `<Invalid boundary or invariant violation>` | `No` | `<Fix input or inspect DLQ payload>` |

## 2. Redaction & Security Rules `[REQUIRED]`

- Stack traces, internal container IPs/ports, SQL queries, and secrets MUST NOT be returned in external error payloads.
