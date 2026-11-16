---
doc_id: CAP-APP-AGT-NFR-001
title: "Non-Functional Requirements: Agent Run & Report Portal"
doc_type: specification
plane: application-plane
scope_level: capability
domain: agent-experience-and-reporting
capability_id: CAP-APP-AGT-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: ai-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/agent_api/presentation/router.py"
    - "src/serving/api/modules/iam/presentation/router.py"
related_docs:
  - CAP-APP-AGT-REQ-001
  - APP-OPS-SLO-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Documented AGENT_TRIGGER rate-limit ceiling, blocking async defect, and unapproved latency targets."
---

# Non-Functional Requirements: Agent Run & Report Portal

## 1. Edge Rate Limits & Sync Execution Reality (`AS-IS`)

- **Rate Limiting**: `SlidingWindowRateLimiter` classifies `/api/v1/agents/*` under `RateLimitTier.AGENT_TRIGGER` (`5` req/min per IP hash) on gateway `8000` (bypassed on standalone port `8006`).
- **List Limit**: `GET /api/v1/agents/runs` clamps `limit` between `1..200`.
- **Execution Risk**: Inline `await runtime.execute_agent_investigation(...)` ties up HTTP connections for full LLM + tool durations when external LLMs replace `DeterministicMockLLMAdapter`.

## 2. Target Latency & Retention Objectives (`OPEN`)

- Maximum run queueing latency and report DB retention periods remain **`OPEN`**.
