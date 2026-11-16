---
doc_id: CAP-APP-AGT-ERR-001
title: "Error Catalog: Agent Run & Report Portal"
doc_type: specification
plane: application-plane
scope_level: capability
domain: agent-experience-and-reporting
capability_id: CAP-APP-AGT-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: qa-lead
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/agent_api/presentation/router.py"
    - "src/serving/api/modules/reporting/presentation/router.py"
related_docs:
  - APP-ERR-SHARED-001
  - CAP-APP-AGT-REQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Cataloged agent/reporting router 404 error payloads and AGENT_TRIGGER rate limits."
---

# Error Catalog: Agent Run & Report Portal

## 1. Domain Error Responses (`{ "detail": { "code", "message" } }`)

| HTTP | Error Code | Route(s) | Trigger |
|---|---|---|---|
| `404` | `ERR_AGENT_RUN_NOT_FOUND` | `GET /agents/runs/{run_id}`, `GET /agents/runs/{run_id}/events` | `run_id` absent from `runtime.agent_runs` |
| `404` | `ERR_REPORT_NOT_FOUND` | `GET /reports/{run_id}` | `run_id` absent from `runtime.reports` (either never run, wiped on restart, or validator failed) |
| `429` | `RATE_LIMIT_EXCEEDED` | `/api/v1/agents/*` (gateway `8000`) | Exceeds `AGENT_TRIGGER` tier (`5` req/min per IP hash) |

## 2. Standalone Port & Authorization Notes

- Gateway port `8000` enforces `AGENT_TRIGGER` rate limit via `install_security_defense_middleware`, whereas standalone `svc-intelligence-agent` (`8006`) omits rate-limit and edge WAF headers (`APP-ARCH-BE-001`).
