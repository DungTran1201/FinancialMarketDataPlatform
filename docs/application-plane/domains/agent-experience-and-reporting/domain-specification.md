---
doc_id: APP-DOM-AGT-SPEC-001
title: "Domain Specification: Agent Experience & Analytical Reporting"
doc_type: specification
plane: application-plane
scope_level: domain
domain: agent-experience-and-reporting
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
  - APP-DOM-AGT-001
  - CAP-APP-AGT-DOC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Defined Application Plane responsibilities vs Intelligence Plane orchestration boundaries."
---

# Domain Specification: Agent Experience & Analytical Reporting

## 1. Domain Boundaries (`Application Plane` vs `Intelligence Plane`)

- **Application Plane Owns (`CAP-APP-AGT-001`)**: Accepting HTTP triggers (`/api/v1/agents/runs` with `Idempotency-Key`), listing/retrieving runs & evidence trails, replaying SSE tool invocations (`/runs/{run_id}/events`), serving verified structured reports (`/api/v1/reports`), and rendering `#/ai-workspace` (`AiWorkspaceModule.ts`).
- **Intelligence Plane Owns (`CAP-INT-ORC-001`)**: Executing the 5-node `MarketInvestigationWorkflow` state machine, deterministic tool gateway calls, iteration/token governance, and `ReportValidator`.

## 2. Observed `AS-IS` Functional & Security Gaps

- `POST /api/v1/agents/runs` awaits full workflow execution before returning HTTP `202` (`async_202_accepted` label is misleading).
- Zero RBAC `Depends` guards (`agent:trigger` / `reports:read` unenforced `AS-IS`).
- `AgentService.getRuns()` on frontend injects synthetic node durations when telemetry is omitted; run state lives only in `runtime.agent_runs` and `runtime.reports` memory dicts.
