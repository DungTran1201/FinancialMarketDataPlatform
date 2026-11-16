---
doc_id: INT-OPS-INC-001
title: "Intelligence Plane Incident Response & Recovery Procedures"
doc_type: specification
plane: intelligence-plane
scope_level: plane
status: DRAFT
implementation_status: SIMULATED
version: "2.0.0"
owner_role: devops-sre
accountable_role: ai-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/orchestrator/graph.py"
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/reporting/validator.py"
    - "src/serving/infrastructure/runtime.py"
related_docs:
  - INT-ROOT-001
  - INT-OPS-RUN-001
  - CAP-INT-ORC-ERR-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Documented failure triage, timeout/retry limitations, state/report recovery gaps, and invalid evidence handling."
---

# Intelligence Plane Incident Response & Recovery Procedures

## 1. Failure Modes & Triage Playbook

| Incident Scenario | Symptoms (`AS-IS`) | Root Cause / Code Path | Operator Response (`AS-IS` vs `TARGET`) |
|---|---|---|---|
| **Tool Execution Failure / Unauthorized Call** | `POST /api/v1/agents/runs` returns HTTP `500`; run appears stuck with `status="RUNNING"` in `GET /api/v1/agents/runs/{run_id}`. | `UnauthorizedToolAccessError`, `ToolQueryLimitExceededError`, or handler `ValueError` propagates unhandled out of `run_investigation()`. | Inspect server logs for tool name & exception; restart or re-trigger with valid `symbol`/`params`. (`TARGET`: catch exception, record audit failure, set `status="FAILED"`.) |
| **Tool Timeout (`asyncio.TimeoutError`)** | Handler exceeds `ToolGovernancePolicy.timeout_seconds` (`1.5s`–`8.0s`); HTTP `500` returned; no audit entry recorded. | `asyncio.wait_for` in `gateway.py:79`; no automatic retry or timeout envelope wrapper exists. | Verify Data Plane store health (`GET /api/v1/observability/overview`); retry with a fresh `Idempotency-Key` (reusing old key returns cached `RUNNING` state!). |
| **Failed Investigation (`Node 1` Rejected)** | `status="FAILED"` and `final_report={"error": "Symbol '...' is not in monitored catalog."}` returned inside HTTP `202`. | Symbol missing from static `_monitored_symbols` tuple captured at container boot (`runtime.py:175`). | If symbol was added dynamically via `PUT /api/v1/catalog/instruments`, restart API container (`AS-IS` limitation `GAP-INT-007`). |
| **Invalid Evidence / Citation (`ReportProvenanceError`)** | Node 5 aborts before Tool #10; `GET /api/v1/reports/{run_id}` returns `404 ERR_REPORT_NOT_FOUND`. | `ReportValidator.validate_report()` detected empty `provenance_citations` or unverified `invocation_id`. | Do not manually insert unverified reports; inspect `evidence_trail` in `GET /api/v1/agents/runs/{run_id}` and fix LLM adapter output. |
| **Model Provider Outage (`TARGET`)** | External LLM HTTP `429`/`5xx`/timeout (`NOT_IMPLEMENTED AS-IS`). | External provider unavailable or quota exhausted. | Activate deterministic fallback mode (`LLM_PROVIDER=mock`) or allow bounded retries; never fabricate analytical metrics. |
| **Anomaly Cooldown Side Effect (`detect_anomalies`)** | Genuine Data Plane anomaly alerts suppressed for 900s after agent investigation ran. | `_tool_detect_anomalies` shares `runtime.anomaly_detector` instance (`runtime.py:493`). | Wait 900s cooldown expiration or inspect `GET /api/v1/analytics/anomalies` (`OPEN-INT-002`). |

## 2. State & Report Recovery (`AS-IS` Reality vs `TARGET`)

- **State Recovery (`AS-IS`)**: **NONE** — `runtime.agent_runs`, `runtime.idempotency_keys`, `runtime.reports`, and `ControlledToolGateway._audit_log` are ephemeral RAM structures lost permanently on process restart.
- **Report Recovery (`AS-IS`)**: **NONE** — If a completed run was cleared by restart, re-submit `POST /api/v1/agents/runs` to synthesize a new report (note: `Idempotency-Key` cache also clears on restart).
- **`TARGET` Recovery Objectives (`RPO / RTO`)**: Marked **`OPEN`** until PostgreSQL `agent_runs` / `agent_tool_invocations` persistence and `agent-worker` lease recovery are implemented (`NFR-INT-005`).

