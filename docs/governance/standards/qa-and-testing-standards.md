---
doc_id: GOV-STD-QA-001
title: "QA & Testing Documentation Standards"
doc_type: standard
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
    - "docs/governance/standards/qa-and-testing-standards.md"
related_docs:
  - GOV-STD-REG-001
  - GOV-POL-DOD-001
  - GOV-POL-TRAC-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Established ISTQB-aligned separation of Strategy, Plan, Scenario, Case, Data, Evidence, and Reports plus entry/exit gates."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: qa-lead
    summary: "Initial Documentation V2 QA and testing documentation standard."
---

# QA & Testing Documentation Standards

Uses consistent verification taxonomy informed by the **ISTQB CTFL 4.0 Glossary**.

## 1. Strict Separation of Testing Artifacts

Authors MUST NOT collapse planning, test cases, and execution proof into one document:

| Artifact | Purpose & Content | Template |
|---|---|---|
| **Test Strategy** (Plane / Platform) | Overall test pyramid, test environments (in-memory vs containerized live infra), tooling, and risk-based coverage policy | Defined in Plane `operations/` or `quality/` |
| **Test Plan** (Capability) | Scope, in-scope/out-of-scope, environment assumptions, schedule/gates, entry & exit criteria, risks | [test-plan.template.md](../templates/quality/test-plan.template.md) |
| **Test Scenarios** | High-level behavioral & failure scenarios (happy path, boundary, negative, concurrency, recovery, security abuse) mapped to `FR`/`NFR`/`UC` | [test-scenarios.template.md](../templates/quality/test-scenarios.template.md) |
| **Test Cases** | Deterministic executable specs (`TC-...`) with preconditions, test data specification, exact steps/inputs, expected result, severity, priority, and automated test path | [test-cases.template.yaml](../templates/quality/test-cases.template.yaml) |
| **Test Data** | Synthetic fixtures, edge/corrupt payloads, and anonymization rules (MUST NOT contain production secrets or PII) | Referenced in `test-cases.yaml` |
| **Test Execution Evidence & Report** | Exact command executed, commit/branch, environment mode (`in-memory` vs `live containers`), pass/fail/skip counts, and defects found | Captured in Test Report / PR evidence |
| **Regression, Performance & Security Suites** | Targeted non-functional verification for latency/throughput budgets, fuzzing, RBAC denial, and chaos/replay recovery | Mapped to `NFR-...` and `SEC-...` |

## 2. Entry Criteria, Exit Criteria, Severity & Priority

1. **Entry Criteria**: Authoritative requirements/contracts exist, test scope is classified by risk tier, and test environment conditions (mocked/in-memory vs. containerized) are explicitly declared.
2. **Exit Criteria**:
   - All `P0` / `CRITICAL` test cases pass without skipped or relaxed assertions.
   - Zero open `CRITICAL` or `HIGH` defects remain without an approved waiver.
   - Traceability links (`FR`/`NFR`/`SEC` -> `TC` -> automated file) validate cleanly.
3. **Severity vs. Priority**:
   - **Severity**: Technical/business impact of failure (`CRITICAL | HIGH | MEDIUM | LOW`).
   - **Priority**: Execution and fix urgency (`P0 | P1 | P2 | P3`).

## 3. Anti-Fabrication & Evidence Honesty Rule

1. **Code Does Not Equal Verified**: A capability MUST NOT be marked `implementation_status: VERIFIED` solely because implementation code exists or compiles.
2. **Simulated vs. Real Infrastructure Disclosure**: Verification evidence obtained using in-memory brokers, embedded ASGI servers, or mock LLM adapters MUST explicitly disclose those test doubles and MUST NOT be reported as proof of live multi-container or external exchange integration.
3. **Definition of Done Alignment**: Completion requires passing both documentation validation (`scripts/docs/validate_docs.py`) and applicable automated test suites per [definition-of-done.md](../definition-of-done.md).
