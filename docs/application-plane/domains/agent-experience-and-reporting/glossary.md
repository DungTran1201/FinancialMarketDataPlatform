---
doc_id: APP-DOM-AGT-GLOSS-001
title: "Glossary: Agent Experience & Analytical Reporting"
doc_type: glossary
plane: application-plane
scope_level: domain
domain: agent-experience-and-reporting
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/agent_api/presentation/router.py"
    - "src/serving/api/modules/reporting/presentation/router.py"
related_docs:
  - APP-DOM-AGT-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Defined domain terms for agent run tickets, idempotency header, SSE replay, and provenance citations."
---

# Glossary: Agent Experience & Analytical Reporting

## 1. Domain Terms

- **`Idempotency-Key`**: HTTP header on `POST /api/v1/agents/runs` checked against `runtime._idempotency_index` in memory so retries do not re-execute completed investigations.
- **SSE Run Replay (`GET /agents/runs/{run_id}/events`)**: Replays finished `evidence_trail` entries as `tool_invocation` events followed by `run_completed` (non-blocking replay `AS-IS`).
- **Structured Analysis Report (`/api/v1/reports/{run_id}`)**: Report saved by `generate_analysis_report` containing `summary`, `quantitative_evidence`, `anomalies_detected`, `data_quality_status`, `provenance_citations`, and `limitations_disclaimer`.
