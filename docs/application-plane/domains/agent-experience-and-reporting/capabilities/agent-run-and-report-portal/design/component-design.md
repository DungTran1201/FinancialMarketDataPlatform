---
doc_id: CAP-APP-AGT-COMP-001
title: "Component & Screen Design: Agent/Reporting Routers & AiWorkspaceModule"
doc_type: specification
plane: application-plane
scope_level: capability
domain: agent-experience-and-reporting
capability_id: CAP-APP-AGT-001
status: IN_REVIEW
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
    - "src/serving/api/modules/reporting/presentation/router.py"
    - "frontend/src/modules/ai-workspace/AiWorkspaceModule.ts"
    - "frontend/src/services/api/agent.service.ts"
related_docs:
  - CAP-APP-AGT-REQ-001
  - APP-ARCH-COMPAT-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Documented backend agent/report serving components and AiWorkspaceModule UI behavior and synthetic timing fallback."
---

# Component & Screen Design: Agent/Reporting Routers & AiWorkspaceModule

## 1. Backend Presentation Modules

- **`agent_api/presentation/router.py`**: Mounts `GET /runs?limit=20` (added in `7880c85`), `POST /runs` (`202`), `GET /runs/{run_id}`, `GET /runs/{run_id}/events` (`StreamingResponse` `text/event-stream`).
- **`reporting/presentation/router.py`**: Mounts `GET /reports?symbol=...` and `GET /reports/{run_id}` reading `runtime.reports`.

## 2. Frontend Screen Specification: `#/ai-workspace` (`AiWorkspaceModule.ts`)

- **Panels**: Investigation trigger form (`symbol`, `prompt_summary`), Run History table (`GET /agents/runs`), Workflow Node Execution Graph, Tool Invocation Evidence Trail, and Citation-Grounded Structured Report viewer.
- **UI Defect (`agent.service.ts`)**: When run telemetry omits node durations, `AgentService.getRuns()` populates hardcoded per-node timings instead of showing `"N/A"`.
