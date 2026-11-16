---
doc_id: INT-QA-PLAN-001
title: "Intelligence Plane Quality & Verification Test Plan"
doc_type: specification
plane: intelligence-plane
scope_level: plane
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
    - "tests/README.md"
related_docs:
  - INT-ROOT-001
  - CAP-INT-ORC-TS-001
  - APP-QA-PLAN-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: qa-lead
    summary: "Defined Intelligence Plane test strategy, AS-IS test coverage vs missing suites, and execution constraints."
---

# Intelligence Plane Quality & Verification Test Plan

## 1. Verification Scope & Test Levels

| Test Level | Suite Path | What Is Verified (`AS-IS` Inspected) | Coverage Gaps (`TARGET` Required) |
|---|---|---|---|
| **Architecture (`AST`)** | `tests/architecture/test_clean_architecture_boundaries.py` | `src/intelligence/` package existence & zero prohibited imports (`ingestion`, `streaming`, `lakehouse`, `serving`). | None for import DAG (`TC-INT-006`). |
| **Unit (`Quant Math`)** | `tests/contract/test_contracts_and_guardrails.py` | `compute_deterministic_log_returns`, `realized_volatility`, `pearson_correlation`. | Edge-case negative prices / empty lists in tool handlers. |
| **Contract (`Tool Gateway`)** | `tests/contract/test_contracts_and_guardrails.py` | Unwhitelisted tool rejection, missing RBAC permission (`agent:trigger`), upper `limit` rejection (`>500`), provenance metadata creation. | Negative/zero limits, timeout envelope, fail-closed missing handler, input schemas, all 10 tool outputs individually. |
| **Integration (Plane C & Cross-Plane)** | `tests/integration/test_three_planes_framework.py` | 5-node mock investigation (`BTCUSDT`), Node 1 unmonitored symbol rejection (`DOGEFAKEUSDT`), `ReportValidator` fabricated `invocation_id` rejection, `POST /agents/runs` + `Idempotency-Key` + SSE replay + `GET /reports/{run_id}`. | Empty citations validation, numeric prose consistency checks, `detect_anomalies` cooldown isolation, `VIEWER` role denial (`SEC-INT-001`), Postgres persistence, `agent-worker` loop, `market.anomalies.v1` trigger. |
| **E2E / Live Containers** | `NOT_IMPLEMENTED` for Plane C | `tests/e2e/test_data_platform_v01_e2e.py` exercises Data Plane & microservices dispatch only (`svc-intelligence-agent` health only). | Live Compose `agent-worker` + Postgres + ClickHouse + Redis + external LLM golden eval suite (`OPEN`). |

## 2. Entry, Exit & Execution Status Disclosure

- **Execution Disclosure**: Existing tests were audited by source inspection. Local execution via `.\.venv\Scripts\python.exe -m pytest tests/ -v` requires a populated `.venv` with project dependencies (`pytest`, `fastapi`, `pydantic`, `pyyaml`, etc.), which is absent in this workspace environment.
- **Exit Criteria Before `VERIFIED` Status**:
  1. Resolve `SEC-INT-001..005` (`BLOCKED` auth & side-effect gaps) and wire `agent-worker` + PostgreSQL state persistence.
  2. Implement `TC-INT-007` and `TC-INT-008` covering timeouts, negative bounds, RBAC enforcement, side-effect isolation, and numeric consistency checks.
  3. Execute full `pytest` suite and live-container integration tests with archived output logs.

