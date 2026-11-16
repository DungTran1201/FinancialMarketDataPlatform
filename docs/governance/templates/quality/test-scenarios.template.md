---
doc_id: TPL-QA-SCEN-001
title: "Template: Test Scenarios"
doc_type: template
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: qa-lead
accountable_role: qa-lead
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/templates/quality/test-scenarios.template.md"
related_docs:
  - GOV-STD-QA-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created Test Scenarios template covering positive, boundary, negative, concurrency, recovery, and security abuse scenarios."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: qa-lead
    summary: "Initial V2 Test Scenarios template."
---

# Template: Test Scenarios

Maps functional, non-functional, and abuse conditions into test scenarios (`TS-...`) prior to concrete test case scripting.

---

# Test Scenarios: `<Capability Name>`

## 1. Scenario Catalog `[REQUIRED]`

| Scenario ID | Scenario Type (`Positive | Boundary | Negative | Recovery | Security | Performance`) | Target Requirement / Threat | Description & Expected Behavior | Linked Test Cases |
|---|---|---|---|---|
| `TS-<DOM>-001` | `Positive` | `FR-<DOM>-001` | `<Core happy-path scenario>` | `TC-<DOM>-001` |
| `TS-<DOM>-002` | `Security` | `THR-<DOM>-001` | `<Unauthorized caller or privilege escalation attempt MUST return 401/403>` | `TC-<DOM>-002` |
