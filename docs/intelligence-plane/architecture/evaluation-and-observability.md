---
doc_id: INT-ARCH-EVAL-001
title: "Evaluation, Provenance & Observability Architecture"
doc_type: architecture
plane: intelligence-plane
scope_level: plane
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: ai-engineer
accountable_role: qa-lead
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/reporting/validator.py"
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/orchestrator/graph.py"
    - "src/shared/observability/metrics.py"
related_docs:
  - INT-ARCH-ROOT-001
  - INT-ARCH-001
  - INT-OPS-SLO-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Documented provenance checks, explicit ReportValidator limitations against hallucinations, audit gaps, and observability metrics."
---

# Evaluation, Provenance & Observability Architecture

## 1. Evidence Provenance & Citation Verification

Every tool execution through `ControlledToolGateway` generates a `ToolProvenanceMetadata` record (`invocation_id`, `tool_name`, `source_store`, `symbol`, `window_start`, `window_end`, `row_count`, `executed_at`) wrapped in `ToolExecutionEnvelope`.

- **What `ReportValidator.validate_report()` Actually Checks (`AS-IS`)**:
  1. `provenance_citations` is non-empty (otherwise raises `ReportProvenanceError`).
  2. Every citation's `invocation_id` exists in `{env.provenance.invocation_id for env in evidence_trail}` (otherwise raises `ReportProvenanceError`).
- **Explicit Anti-Hallucination Limitation**:
  - `ReportValidator` is a **structural citation-ID check**, **NOT a complete anti-hallucination solution**. It does **not** verify that numbers, percentages, timestamps, or directional claims inside `report["summary"]` match the values in `evidence_trail` or `quantitative_evidence`.

## 2. Tool Audit & Telemetry (`AS-IS` vs `TARGET`)

| Dimension | `AS-IS` State | `TARGET` State |
|---|---|---|
| **Tool Execution Audit** | Appended in memory to `ControlledToolGateway._audit_log` | Persisted to PostgreSQL `agent_tool_invocations` (`01_schema.sql`) |
| **Token Usage** | Accumulated in `AgentWorkflowState.tokens_consumed` (`960` mock tokens/run) | Split `prompt_tokens`/`completion_tokens` persisted & exported to Prometheus |
| **Workflow Duration & Tool Latency** | Not timed per run or per tool inside `src/intelligence/` | Histograms (`agent_run_duration_seconds`, `agent_tool_latency_seconds`) exported to Prometheus |
| **Error & Failure Rate** | `status="FAILED"` on invalid symbol; exceptions propagate otherwise | Structured error counters by `error_code` and `tool_name` |

## 3. Model Evaluation, Report Quality & Reproducibility (`TARGET`)

- **Numeric Consistency Verification (`GAP-INT-006`)**: `TARGET` requires deterministic post-synthesis numeric extraction verifying that any numeric claim in narrative text matches `quantitative_evidence` within tolerance.
- **Model & Hallucination Evaluation**: Golden evaluation dataset (`tests/` or eval harness) measuring tool-selection accuracy, citation grounding, and factual consistency before promoting any external LLM adapter (`NOT_IMPLEMENTED`).
- **Replay & Reproducibility**:
  - `AS-IS`: `DeterministicMockLLMAdapter` is deterministic in tool selection, but `invocation_id` (`uuid.uuid4()`) and timestamps vary per run, and historical store state is mutable in memory.
  - `TARGET`: Persist frozen `evidence_trail` snapshots alongside `agent_runs` to support deterministic audit replay.

