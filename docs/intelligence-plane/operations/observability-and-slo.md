---
doc_id: INT-OPS-SLO-001
title: "Intelligence Plane Observability & SLOs"
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
    - "src/intelligence/workflows/investigation.py"
    - "src/intelligence/tools/gateway.py"
    - "src/shared/observability/metrics.py"
related_docs:
  - INT-ROOT-001
  - INT-ARCH-EVAL-001
  - CAP-INT-ORC-NFR-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Documented Intelligence Plane telemetry gaps and OPEN SLO measurement plan."
---

# Intelligence Plane Observability & SLOs

## 1. Current Telemetry (`AS-IS`)

- `AgentWorkflowState` tracks `current_iteration`, `tokens_consumed`, `visited_nodes`, `evidence_trail`, and `status` in memory.
- `ControlledToolGateway` appends `ToolExecutionEnvelope`s (with `executed_at` and `row_count`) to `_audit_log`.
- **Gap**: `src/intelligence/` does **not** emit dedicated Prometheus counters/histograms for agent run duration, per-tool latency, token spend, or failure rates (`NOT_IMPLEMENTED`).

## 2. Target Metrics & Alerts (`TARGET`)

- `agent_runs_total{trigger_mode, status}`
- `agent_run_duration_seconds` (histogram)
- `agent_tool_invocations_total{tool_name, status}` and `agent_tool_latency_seconds{tool_name}`
- `agent_tokens_consumed_total{adapter}`
- Alerts on elevated `ReportProvenanceError` count, tool timeout spikes, and `agent-worker` queue lag.

## 3. Service Level Objectives (`OPEN`)

- **Run Latency P95, Tool Success Rate & Worker Availability**: Marked **`OPEN`** (`OPEN-INT-001`). Do not invent arbitrary thresholds before external LLM integration and PostgreSQL persistence are wired.
- **Proposed Measurement Method**: Benchmark 100 concurrent runs under `LLM_PROVIDER=mock` and target external LLM provider against live Redis/ClickHouse/PostgreSQL to establish baseline P50/P95/P99 latency and error budgets.

