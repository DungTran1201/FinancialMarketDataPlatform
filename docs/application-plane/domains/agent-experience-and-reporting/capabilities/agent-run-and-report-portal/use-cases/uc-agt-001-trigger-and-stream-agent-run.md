---
doc_id: CAP-APP-AGT-UC-001
title: "Use Case UC-AGT-001: Trigger Investigation Run & Replay SSE Progress"
doc_type: specification
plane: application-plane
scope_level: use-case
domain: agent-experience-and-reporting
capability_id: CAP-APP-AGT-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: business-analyst
accountable_role: ai-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/agent_api/presentation/router.py"
    - "frontend/src/modules/ai-workspace/AiWorkspaceModule.ts"
related_docs:
  - CAP-APP-AGT-REQ-001
  - DIAG-APP-AGT-SEQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Documented POST /agents/runs trigger, Idempotency-Key reuse, and SSE event replay."
---

# Use Case UC-AGT-001: Trigger Investigation Run & Replay SSE Progress

## 1. Actors & Preconditions

- **Actor**: Quant Analyst (`#/ai-workspace`) or API caller. (`TARGET`: requires `agent:trigger`; `AS-IS`: unauthenticated, rate-limited at 5 req/min on `:8000`.)

## 2. Main Flow & Exceptions

1. Analyst submits `POST /api/v1/agents/runs` with `{ symbol, prompt_summary, trigger_mode }` and optional `Idempotency-Key` header.
2. Runtime checks `_idempotency_index`; if unseen, synchronously awaits `MarketInvestigationWorkflow` (`CAP-INT-ORC-001`) through all 5 nodes before returning HTTP `202` with `run_id`, `status`, and `tool_calls_executed`.
3. Client polls `GET /api/v1/agents/runs` (added in `7880c85`) or `GET /api/v1/agents/runs/{run_id}`, or subscribes to `GET /api/v1/agents/runs/{run_id}/events` (`text/event-stream`).
4. SSE replays `event: tool_invocation` per entry in `state.evidence_trail` followed by `event: run_completed`.
- **Exception E1 (`404 ERR_AGENT_RUN_NOT_FOUND`)**: Requested `run_id` is absent from in-memory `runtime.agent_runs` (e.g., after server restart).
