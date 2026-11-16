---
doc_id: CAP-INT-ORC-TS-001
title: "Behavioral & Fault Test Scenarios: Market Intelligence Workflow & Tool Gateway"
doc_type: specification
plane: intelligence-plane
scope_level: capability
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: qa-lead
accountable_role: qa-lead
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
  - CAP-INT-ORC-REQ-001
  - CAP-INT-ORC-SEC-001
  - INT-QA-PLAN-001
requirement_ids:
  - TS-INT-001
  - TS-INT-002
  - TS-INT-003
  - TS-INT-004
  - TS-INT-005
  - TS-INT-006
  - TS-INT-007
  - TS-INT-008
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: qa-lead
    summary: "Enumerated positive, negative, boundary, security, and fault test scenarios linked to FR/NFR/SEC requirements."
---

# Behavioral & Fault Test Scenarios: Market Intelligence Workflow & Tool Gateway

## 1. Test Scenarios Catalog

| Scenario ID | Linked Requirement(s) | Category | Scenario Summary | `AS-IS` Automation Coverage |
|---|---|---|---|---|
| `TS-INT-001` | `FR-INT-001`, `FR-INT-002`, `FR-INT-005` | Positive / Happy Path | Monitored symbol (`BTCUSDT`) runs all 5 workflow nodes, executes 7 investigation tools + Tool #10 persistence, passes `ReportValidator`, and reaches `COMPLETED`. | Covered by code inspection in `test_three_planes_framework.py:328-344` (`MOCK` adapter, in-process; not executed in current sandbox). |
| `TS-INT-002` | `FR-INT-001`, `RULE-INT-001` | Negative / Guardrail | Unmonitored symbol (`DOGEFAKEUSDT`) is rejected at Node 1 (`intake_and_guardrail_node`) with `status="FAILED"` and zero tool invocations. | Covered by code inspection in `test_three_planes_framework.py:345-353`. |
| `TS-INT-003` | `FR-INT-003`, `SEC-INT-002` | Security / Boundary | Unwhitelisted tool name (`execute_raw_sql`, `execute_sql_raw`), missing RBAC permission (`agent:trigger`), and oversized `limit` (`5000` / `999999`) raise `UnauthorizedToolAccessError` or `ToolQueryLimitExceededError`. | Covered by code inspection in `test_contracts_and_guardrails.py:151-174` & `test_three_planes_framework.py:314-326`. |
| `TS-INT-004` | `FR-INT-004`, `NFR-INT-004` | Positive / Determinism | Deterministic Python quantitative calculations (`log_returns`, `realized_volatility`, `pearson_correlation`) produce reproducible values without LLM math. | Covered by code inspection in `test_contracts_and_guardrails.py:185-190` & `test_three_planes_framework.py:303-310`. |
| `TS-INT-005` | `FR-INT-005`, `SEC-INT-004` | Security / Provenance | `ReportValidator` rejects reports citing fabricated `invocation_id` (`inv_fabricated_999999`) with `ReportProvenanceError`. | Covered by code inspection in `test_three_planes_framework.py:355-371`. |
| `TS-INT-006` | `NFR-INT-001`, `SEC-INT-002`, `SEC-INT-005` | Fault / Boundary (`GAP`) | Handler timeout exceeding `timeout_seconds`, negative/zero `limit` (`-1`, `0`), unregistered missing handler fail-closed check, and empty `provenance_citations` rejection. | **NOT_IMPLEMENTED**: Zero automated tests cover timeout, negative limits, or empty citations `AS-IS`. |
| `TS-INT-007` | `SEC-INT-001`, `SEC-INT-003` | Security / Side Effects (`GAP`) | Caller RBAC propagation (`VIEWER` blocked from `agent:trigger`) and isolation of `detect_anomalies` cooldown state during agent investigations. | **NOT_IMPLEMENTED / BLOCKED**: Hardcoded `_agent_permissions` and unauthenticated router allow bypass `AS-IS`. |
| `TS-INT-008` | `FR-INT-006`, `FR-INT-007` | Async Worker & Evals (`GAP`) | `agent-worker` Postgres queue polling, Kafka `market.anomalies.v1` trigger consumption, and external LLM prompt-injection / numeric consistency verification. | **NOT_IMPLEMENTED**: Worker stub exits immediately; external LLM and Postgres persistence unimplemented. |

## 2. Environment Disclosure

- All existing Plane C tests in `tests/` run **in-process** against `PlatformRuntimeContainer` and `DeterministicMockLLMAdapter` without live PostgreSQL, ClickHouse, Redis, Kafka, or external LLM containers.
- Note: In the current workspace environment, `.venv` and `pytest` are not installed; automated tests listed above were **inspected in source**, not executed during this documentation pass.

