---
doc_id: INT-OPS-SLO-001
title: "Intelligence Plane Observability, SLIs, SLOs & Alerting"
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
    - "src/shared/observability/metrics.py"
    - "src/serving/api/modules/agent_api/presentation/router.py"
    - "src/intelligence/tools/gateway.py"
    - "deploy/observability/prometheus/alerts.yml"
related_docs:
  - INT-ROOT-001
  - INT-ARCH-EVAL-001
  - CAP-INT-ORC-NFR-001
  - APP-OPS-SLO-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Audited Intelligence Plane telemetry gaps, defined bounded-label SLI proposals, and documented OPEN SLO targets with measurement methodology."
---

# Intelligence Plane Observability, SLIs, SLOs & Alerting

## 1. Instrumented Telemetry (`AS-IS` Audit)

- **Prometheus `/metrics` (`src/shared/observability/metrics.py`)**: Currently exports **zero** Intelligence Plane metrics (`fmdp_*` metrics cover Data Plane ingestion/lag/DQ/Gold/observability routes only).
- **Prometheus Alerts (`deploy/observability/prometheus/alerts.yml`)**: Contains `PLANE-A` alerts (`FMDPDeadLetterQueueSpike`, `FMDPConsumerLagHigh`) only; **zero** Plane C alerts exist.
- **In-Memory Run Telemetry (`AS-IS`)**: `AgentWorkflowState` tracks `visited_nodes`, `tokens_consumed`, `evidence_trail`, and `status` exposed via `GET /api/v1/agents/runs/{run_id}` and replayed via SSE `/runs/{run_id}/events`.
- **Missing Instrumentation (`GAP`)**: Per-node latency, per-tool latency, `worker_queue_depth`, LLM provider error rates, and denied/timed-out tool counters are **not** instrumented in Python.

## 2. Candidate SLIs, Measurement Plan & Unapproved Targets (`OPEN`)

> [!IMPORTANT]
> Per `GOV-STD-NFR-001`, no synthetic latency, availability, or error-rate SLO numbers are fabricated below. All numeric targets remain **`OPEN`** pending stakeholder sign-off and benchmark execution.

| SLI Name | Proposed Bounded Prometheus Metric (`TARGET`) | Label Cardinality Guard | Target SLO | How to Benchmark & Determine Target |
|---|---|---|---|---|
| **Agent Run Completion Rate** | `fmdp_agent_runs_total{trigger_mode, status}` | Bounded enum (`ON_DEMAND`, `EVENT_TRIGGERED`; `COMPLETED`, `FAILED`, `CANCELLED`) — never `run_id` or `symbol` if unbounded | `OPEN` | Measure baseline pass/fail ratio across 100 synthetic + real-provider runs after error wrapping is fixed. |
| **Investigation E2E Duration** | `fmdp_agent_run_duration_ms{trigger_mode, provider}` | Histogram buckets (`50ms..90000ms`); bounded provider label | `OPEN` (`.env.example` sets `AGENT_RUN_TIMEOUT_SECONDS=90`) | Measure P50/P95/P99 separately for `mock` vs target external LLM provider in staging. |
| **Per-Tool Execution Latency** | `fmdp_agent_tool_duration_ms{tool_name, status}` | `10` fixed `ApprovedAgentTool` values x status enum | `OPEN` (bounded per tool by `timeout_seconds`: `1.5s..8.0s`) | Measure against live Redis, ClickHouse (`fmdp_agent_ro`), and Postgres (`fmdp_agent_rw`). |
| **Tool Guardrail & Provenance Failures** | `fmdp_agent_guardrail_rejections_total{reason}` | Fixed reason enum (`UNWHITELISTED`, `PERMISSION_DENIED`, `LIMIT_EXCEEDED`, `TIMEOUT`, `PROVENANCE_ERROR`) | `OPEN` | Alert on sudden spikes indicating prompt injection, LLM schema drift, or downstream store slowdown. |
| **Token Budget Consumption** | `fmdp_agent_tokens_consumed_total{provider, role}` | Bounded (`prompt` vs `completion`) | `OPEN` (`token_budget=8000` code default) | Track P95 tokens per run across real LLM prompts before fixing budget ceilings. |
| **Worker Queue Age (`TARGET`)** | `fmdp_agent_queue_oldest_age_seconds` | Unlabeled gauge | `OPEN` | Measure time from Postgres `QUEUED` insert to `RUNNING` pickup under expected concurrency. |

