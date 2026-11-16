---
doc_id: TPL-REQ-NFR-001
title: "Template: Non-Functional Requirements (NFR)"
doc_type: template
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: devops-sre
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/templates/product-and-requirements/nfr.template.md"
related_docs:
  - GOV-STD-NFR-001
  - GOV-STD-REQ-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created 10-attribute NFR template enforcing unresolved-target honesty."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Initial V2 NFR template."
---

# Template: Non-Functional Requirements (NFR)

Covers the 10-attribute quality model ([nfr-and-operations-standards.md](../../standards/nfr-and-operations-standards.md)). **Never invent latency, throughput, availability, RTO, or RPO numbers; record `TARGET_UNRESOLVED` (`OPEN`) if unconfirmed.**

---

# Non-Functional Requirements: `<Scope Name>`

## 1. Measurable Quality Requirements `[REQUIRED]`

| NFR ID | Quality Attribute | Requirement Statement | Approved Target (or `TARGET_UNRESOLVED`) | Workload / Environment Condition | Verification Method (`Test / Benchmark / Inspection`) |
|---|---|---|---|---|---|
| `NFR-<DOM>-001` | `Performance` | `<Latency or resource constraint>` | `<Measured/Approved target or TARGET_UNRESOLVED [OPEN]>` | `<Concurrency, dataset size>` | `<Benchmark / Load Test>` |

## 2. Graceful Degradation & Failure Boundaries `[CONDITIONAL: Required for MEDIUM and HIGH_CRITICAL capabilities]`

| Dependency Outage / Fault | Required System Behavior | Blast Radius Containment |
|---|---|---|
| `<Upstream store or external API failure>` | `<Fallback, queuing, or explicit error response>` | `<Components unaffected>` |
