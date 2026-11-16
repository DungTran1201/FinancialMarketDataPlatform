---
doc_id: CAP-APP-AGT-UC-002
title: "Use Case UC-AGT-002: List & Inspect Citation-Verified Analysis Reports"
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
    - "src/serving/api/modules/reporting/presentation/router.py"
    - "frontend/src/modules/ai-workspace/AiWorkspaceModule.ts"
related_docs:
  - CAP-APP-AGT-REQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Documented report list filtering and detailed provenance citation retrieval."
---

# Use Case UC-AGT-002: List & Inspect Citation-Verified Analysis Reports

## 1. Main Flow & Exceptions

1. Analyst opens `#/ai-workspace` report list calling `GET /api/v1/reports` (optionally filtered by `?symbol=...`), returning `run_id`, `symbol`, `summary`, `data_quality_status`, and `citation_count`.
2. Analyst selects a report -> UI calls `GET /api/v1/reports/{run_id}` -> receives full `quantitative_evidence`, `anomalies_detected`, `provenance_citations[]` (`invocation_id`, `tool_name`, `source_store`, `window_start`, `window_end`, `row_count`), and `limitations_disclaimer`.
- **Exception E1 (`404 ERR_REPORT_NOT_FOUND`)**: `run_id` absent from `runtime.reports` (including failed runs where report synthesis was rejected or skipped).

## 2. Postconditions & Security Preconditions (`AS-IS` vs `TARGET`)

- `AS-IS`: Report data lives only in `runtime.reports` memory dict and clears on restart.
- `TARGET`: Enforce `reports:read` RBAC check (`ROLE_CAPABILITIES`) and persist reports in Postgres `agent_runs.structured_report`.
