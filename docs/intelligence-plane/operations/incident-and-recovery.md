---
doc_id: INT-OPS-INC-001
title: "Intelligence Plane Incident & Recovery Guide"
doc_type: specification
plane: intelligence-plane
scope_level: plane
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
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
related_docs:
  - INT-ROOT-001
  - INT-OPS-RUN-001
  - CAP-INT-ORC-ERR-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Documented failure modes, timeout/retry behavior, and state/report recovery gaps."
---

# Intelligence Plane Incident & Recovery Guide

| Incident Scenario | `AS-IS` Symptom & Behavior | Immediate Operator Action / Recovery | `TARGET` Remediation |
|---|---|---|---|
| **Tool Execution Failure / Timeout** | `asyncio.TimeoutError`, `UnauthorizedToolAccessError`, or `ToolQueryLimitExceededError` propagates uncaught; `state.status` remains `"RUNNING"`. | Inspect application logs; re-submit `POST /api/v1/agents/runs` with a **new** `Idempotency-Key`. | Catch exceptions in `run_investigation()`, transition to `FAILED`, and add bounded retry for transient timeouts. |
| **Failed Investigation (Unmonitored Symbol)** | Node 1 sets `status="FAILED"` and `final_report={"error": ...}`. | Verify symbol is in `_monitored_symbols` (`BTCUSDT`, `ETHUSDT`, `SOLUSDT`, `BNBUSDT`, `XRPUSDT`). | Sync Node 1 allowlist dynamically with `monitored_instruments` table. |
| **Invalid Evidence / Citation** | `ReportValidator` raises `ReportProvenanceError` if citations are empty or `invocation_id` is unknown. | Check `evidence_trail` length and tool handler registration; re-run investigation. | Persist failure reason to `agent_runs` and alert on provenance violations. |
| **State & Report Loss on Restart** | Process restart clears `runtime.agent_runs`, `runtime.reports`, and `idempotency_keys` (in-memory only). | No `AS-IS` recovery for historical in-memory runs; re-trigger investigation. | Persist `AgentWorkflowState`, `agent_tool_invocations`, and `structured_report` in PostgreSQL (`01_schema.sql`). |

