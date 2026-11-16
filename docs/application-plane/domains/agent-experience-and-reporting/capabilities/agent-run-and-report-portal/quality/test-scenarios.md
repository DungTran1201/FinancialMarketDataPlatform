---
doc_id: CAP-APP-AGT-TS-001
title: "Test Scenarios: Agent Run & Report Portal"
doc_type: specification
plane: application-plane
scope_level: capability
domain: agent-experience-and-reporting
capability_id: CAP-APP-AGT-001
status: IN_REVIEW
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
related_docs:
  - CAP-APP-AGT-DOC-001
  - CAP-APP-AGT-REQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: qa-lead
    summary: "Documented verified API run/SSE/report checks and UI/persistence test gaps."
---

# Test Scenarios: Agent Run & Report Portal

## 1. Covered `AS-IS` Scenarios (`test_three_planes_framework.py`)

- **`TS-AGT-001`**: Trigger `POST /api/v1/agents/runs` with `Idempotency-Key`, re-submit duplicate key verifying single execution, query `GET /runs` and `GET /runs/{run_id}`.
- **`TS-AGT-002`**: Stream SSE events via `GET /api/v1/agents/runs/{run_id}/events`, inspect `tool_invocation` & `run_completed` frames, and fetch verified report via `GET /api/v1/reports/{run_id}`.

## 2. Coverage Gaps

- Missing RBAC `401`/`403` enforcement tests, missing real Postgres `agent_runs` persistence tests, and unverified `#/ai-workspace` TypeScript UI tests.
