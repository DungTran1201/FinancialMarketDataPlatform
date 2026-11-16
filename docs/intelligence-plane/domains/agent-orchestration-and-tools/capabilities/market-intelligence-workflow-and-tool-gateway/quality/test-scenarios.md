---
doc_id: CAP-INT-ORC-TS-001
title: "Test Scenarios: Market Intelligence Workflow & Tool Gateway"
doc_type: specification
plane: intelligence-plane
scope_level: capability
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: qa-lead
accountable_role: ai-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "tests/integration/test_three_planes_framework.py"
    - "tests/contract/test_contracts_and_guardrails.py"
    - "tests/architecture/test_clean_architecture_boundaries.py"
related_docs:
  - CAP-INT-ORC-DOC-001
  - INT-QA-PLAN-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: qa-lead
    summary: "Defined capability test scenarios mapped to existing tests and coverage gaps."
---

# Test Scenarios (`CAP-INT-ORC-001`)

| Scenario ID | Scenario | Expected Outcome | Current Coverage |
|---|---|---|---|
| `TS-INT-001` | Valid on-demand investigation (`BTCUSDT`) | Completes 5 nodes, `8` envelopes, `7` citations, `status="COMPLETED"` | `test_three_planes_framework.py` |
| `TS-INT-002` | Unapproved tool or missing permission | Raises `UnauthorizedToolAccessError` | `test_contracts_and_guardrails.py` & `test_three_planes_framework.py` |
| `TS-INT-003` | Excessive row limit (`limit=999999`) | Raises `ToolQueryLimitExceededError` | `test_contracts_and_guardrails.py` & `test_three_planes_framework.py` |
| `TS-INT-004` | Fabricated `invocation_id` in report | Raises `ReportProvenanceError` | `test_three_planes_framework.py` |
| `TS-INT-005` | Unmonitored symbol (`DOGEFAKEUSDT`) | Node 1 sets `status="FAILED"` | `test_three_planes_framework.py` |
| `TS-INT-006` | Clean Architecture import boundary | Zero forbidden imports from `serving`/`streaming`/`ingestion`/`lakehouse` | `test_clean_architecture_boundaries.py` |
| `TS-INT-007` | Tool timeout, numeric prose consistency, Postgres persistence, Kafka `market.anomalies.v1` trigger | Graceful `FAILED` state / durable audit | `NOT_IMPLEMENTED` |

