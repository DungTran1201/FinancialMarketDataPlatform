---
doc_id: CAP-APP-AGT-REQ-001
title: "Capability Specification: Agent Run & Report Portal"
doc_type: specification
plane: application-plane
scope_level: capability
domain: agent-experience-and-reporting
capability_id: CAP-APP-AGT-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: business-analyst
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/agent_api/presentation/router.py"
    - "src/serving/api/modules/reporting/presentation/router.py"
    - "frontend/src/modules/ai-workspace/AiWorkspaceModule.ts"
related_docs:
  - CAP-APP-AGT-DOC-001
  - CAP-APP-AGT-COMP-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Defined atomic functional requirements and AS-IS execution/persistence gaps for agent runs and reports."
---

# Capability Specification: Agent Run & Report Portal

## 1. Capability Scope & `AS-IS` Reality

Provides HTTP/SSE endpoints (`POST /api/v1/agents/runs`, `GET /runs`, `GET /runs/{run_id}`, `GET /runs/{run_id}/events`, `GET /api/v1/reports`, `GET /api/v1/reports/{run_id}`) and `#/ai-workspace` UI for launching AI market investigations and reviewing citation-linked reports.

## 2. Functional Requirements

| Req ID | Requirement Statement | `AS-IS` Evidence | Target / Gap |
|---|---|---|---|
| `FR-AGT-001` | Analysts MUST trigger agent investigations (`POST /agents/runs`) with optional `Idempotency-Key` deduplication. | `agent_api/router.py:45-75` | Awaits synchronous workflow completion before returning `202`; unauthenticated (`SEC-AUDIT-003`). |
| `FR-AGT-002` | Analysts MUST list past runs (`GET /agents/runs?limit=20`), inspect visited nodes/evidence trail (`GET /runs/{id}`), and consume tool invocation events via SSE (`/events`). | `agent_api/router.py:26-43,77-139` | Stored in ephemeral `runtime.agent_runs` dict; SSE replays finished events instead of streaming live. |
| `FR-AGT-003` | Analysts MUST list (`GET /reports`) and inspect verified reports (`GET /reports/{run_id}`) with `provenance_citations` and `limitations_disclaimer`. | `reporting/router.py:21-70` | Ephemeral `runtime.reports` dict only (`01_schema.sql` `agent_runs.structured_report` unwired). |
| `FR-AGT-004` | `#/ai-workspace` UI MUST render run launcher, node trace graph, tool invocation timeline, and report panel accurately without fake node timings. | `AiWorkspaceModule.ts`, `agent.service.ts` | `AgentService.getRuns()` falls back to hardcoded node durations when backend metadata omits them. |
