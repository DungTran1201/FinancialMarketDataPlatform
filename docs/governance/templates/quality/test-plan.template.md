---
doc_id: TPL-QA-PLAN-001
title: "Template: Test Plan"
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
    - "docs/governance/templates/quality/test-plan.template.md"
related_docs:
  - GOV-STD-QA-001
  - GOV-POL-DOD-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created Test Plan template covering scope, environments, entry/exit criteria, and evidence disclosure."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: qa-lead
    summary: "Initial V2 Test Plan template."
---

# Template: Test Plan

Instantiated inside `<capability>/quality/test-plan.md`. Separates planning from scenarios, deterministic test cases, and execution reports.

---

# Test Plan: `<Capability Name>` (`<CAP-DOM-NNN>`)

## 1. Test Scope & Coverage Matrix `[REQUIRED]`

- **In Scope**: `<FR / NFR / SEC / RULE IDs covered>`
- **Out of Scope**: `<Explicit exclusions>`
- **Test Levels**: `<Unit | Contract | Architecture | Data Quality | Integration | E2E | Performance | Security>`

## 2. Test Environments & Test Doubles Disclosure `[REQUIRED]`

| Environment | Backing Infrastructure (`In-Memory / Embedded ASGI / Live Containers`) | Purpose | Limitations |
|---|---|---|---|
| `unit-inprocess` | `In-memory doubles + TestClient` | `Fast CI deterministic verification` | `Does NOT verify live network/broker behavior` |

## 3. Entry & Exit Criteria `[REQUIRED]`

- **Entry Criteria**: `<Requirements APPROVED, contracts valid, test data ready>`
- **Exit Criteria**: `<100% P0 tests pass, zero unwaived HIGH/CRITICAL bugs, evidence captured>`

## 4. Risks & Execution Evidence Reference `[REQUIRED]`

- **Test Scenarios**: `[test-scenarios.md](test-scenarios.md)`
- **Test Cases**: `[test-cases.yaml](test-cases.yaml)`
- **Latest Execution Evidence**: `<Exact command, date, commit SHA, pass/fail counts, environment mode>`
