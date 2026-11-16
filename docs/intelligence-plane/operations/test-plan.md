---
doc_id: INT-QA-PLAN-001
title: "Intelligence Plane Test Plan"
doc_type: specification
plane: intelligence-plane
scope_level: plane
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
  - INT-ROOT-001
  - CAP-INT-ORC-TS-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: qa-lead
    summary: "Consolidated Intelligence Plane test coverage and explicit verification gaps."
---

# Intelligence Plane Test Plan

## 1. Existing Automated Tests (`AS-IS`)

- **Integration (`tests/integration/test_three_planes_framework.py`)**: `TestPlaneCIntelligencePlaneIndependently` verifies 5-node workflow completion (`8` envelopes, `7` citations), unmonitored symbol rejection (`FAILED`), `ReportValidator` rejection of fabricated `invocation_id`, and gateway whitelist/row-limit guardrails. `TestInterPlaneCommunicationEndToEnd` verifies `POST /api/v1/agents/runs` (`202` + `Idempotency-Key`), SSE event replay, and `GET /api/v1/reports/{run_id}`.
- **Contract (`tests/contract/test_contracts_and_guardrails.py`)**: Verifies `ControlledToolGateway` whitelist, RBAC permission check (`agent:trigger`), and `max_rows_or_periods` cap.
- **Architecture (`tests/architecture/test_clean_architecture_boundaries.py`)**: AST check ensuring `src/intelligence/` only imports from `src/shared/`.

## 2. Explicit Coverage Gaps (`AS-IS`)

- **Tool Timeout & Error Recovery**: No test exercises `asyncio.TimeoutError` inside `ControlledToolGateway` or uncaught exception handling in `MarketIntelligenceGraph`.
- **Persistence & Worker**: Zero tests cover `src/intelligence/main.py` queue polling, PostgreSQL `agent_runs`/`agent_tool_invocations`, or Kafka `market.anomalies.v1` event triggers (`NOT_IMPLEMENTED`).
- **Numeric Consistency & Prompt Injection Evals**: No evaluation harness tests numeric accuracy in narrative text or prompt injection resistance (`NOT_IMPLEMENTED`).

