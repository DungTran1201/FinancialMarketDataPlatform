---
doc_id: INT-ARCH-EVAL-001
title: "Intelligence Evaluation, Provenance & Observability Architecture"
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
    - "src/serving/api/modules/agent_api/presentation/router.py"
related_docs:
  - INT-ARCH-ROOT-001
  - INT-ARCH-001
  - INT-OPS-SLO-001
  - DIAG-INT-ORC-DFD-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Documented provenance metadata, ReportValidator scope boundaries, missing Prometheus metrics for Plane C, and hallucination/replay evaluation gaps."
---

# Intelligence Evaluation, Provenance & Observability Architecture

Derived view: [evidence-provenance-flow.md](../domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/workflows/evidence-provenance-flow.md) (`DIAG-INT-ORC-DFD-001`).

## 1. Scope and Grounding Philosophy

Per `ADR-OVR-003` and `ai-agent-and-discovery-standards.md`, the Intelligence Plane MUST prevent ungrounded financial narratives by forcing deterministic computation inside tools and requiring verifiable citations in every published report.

## 2. Context: Provenance & Citation Verification (`AS-IS` Reality vs Limits)

### 2.1 Evidence Provenance Attachment

Every successful execution through `ControlledToolGateway.execute_tool()` (`gateway.py:81-96`) generates a `ToolProvenanceMetadata` record (`invocation_id` UUIDv4, `tool_name`, `source_store`, `symbol`, `window_start`, `window_end`, `row_count`, `executed_at`) wrapped into a `ToolExecutionEnvelope`.

### 2.2 What `ReportValidator` Actually Verifies (`validator.py:15-31`)

`ReportValidator.validate_report(report, evidence_trail)` verifies **ONLY**:

1. `report.get("provenance_citations", [])` is non-empty (`ReportProvenanceError` if empty).
2. Every citation's `invocation_id` exists in `{env.provenance.invocation_id for env in evidence_trail}` (`ReportProvenanceError` if unknown/fabricated).

### 2.3 Why Citation ID Checking Is NOT Complete Anti-Hallucination

> [!IMPORTANT]
> **Explicit Limitation**: `ReportValidator` verifies **citation ID existence only**. It does **NOT** prevent hallucinations in prose or payload values (`GAP-INT-EVAL-001`).

Specifically, `ReportValidator` currently does **NOT** check:
- **Numeric Consistency**: Whether numbers mentioned inside `report["summary"]` or `quantitative_evidence` actually match `ToolExecutionEnvelope.data` from the cited `invocation_id`s.
- **Citation Field Integrity**: Whether `tool_name`, `symbol`, `source_store`, `window_start`, `window_end`, or `row_count` in a `provenance_citations` entry match the underlying envelope.
- **Sufficiency / Completeness**: `evidence_verifier_node` (`graph.py:154`) exits planning once `len(evidence_trail) >= 3`, without validating that the gathered tools actually answer `prompt_summary` or cover data freshness.
- **Degraded/Fallback Flagging**: Tool handlers (`runtime.py:453,466,480,492`) silently substitute hardcoded fallback price arrays (`[89500.0, 89550.0, 89600.0]`) when ClickHouse stats are empty, while `DeterministicMockLLMAdapter` still hardcodes `"data_quality_status": "HEALTHY"`.

## 3. Building Blocks: Telemetry, Evaluation & Reproducibility

| Telemetry / Evaluation Dimension | `AS-IS` Implemented Mechanism | Observed Gap & `TARGET` Design |
|---|---|---|
| **Tool Execution Audit** | `ControlledToolGateway._audit_log` stores successful `ToolExecutionEnvelope` objects in process memory (`gateway.py:35,96`). | Denied (`UnauthorizedToolAccessError`), limit-exceeded (`ToolQueryLimitExceededError`), and timed-out invocations are **not** audited; Postgres `agent_tool_invocations` table is unwired (`OPEN`). |
| **Token Usage** | `AgentWorkflowState.tokens_consumed` accumulates mock integer constants (`420`, `110`, `540`) and returns via `GET /api/v1/agents/runs`. | Postgres `agent_runs.token_usage` (`prompt_tokens`, `completion_tokens`, `total_tokens`) unused; no Prometheus token counter (`OPEN`). |
| **Workflow Duration & Tool Latency** | **NOT_IMPLEMENTED in Plane C**: Neither `MarketIntelligenceGraph` nor `ControlledToolGateway` records per-node or per-tool execution duration! (Note: `frontend/src/services/api/agent.service.ts` injects synthetic durations when missing.) | Add monotonic `perf_counter` timers per node and tool (`TARGET`) and bounded-label Prometheus histograms (`fmdp_agent_run_duration_ms`, `fmdp_agent_tool_duration_ms`). |
| **Error & Failure Rate** | Node 1 invalid symbol sets `state.status = "FAILED"`; exceptions during Nodes 2–5 propagate unhandled without setting `FAILED` or incrementing Prometheus error counters. | Catch node/gateway/validation exceptions cleanly, record `status="FAILED"`, and increment bounded failure counters (`OPEN`). |
| **Model & Report Quality Evaluation** | Tested solely via unit/integration assertions on mock outputs (`test_three_planes_framework.py`). | Requires golden evaluation dataset, numeric-extraction cross-check against `evidence_trail`, and offline/CI regression harness prior to external LLM activation (`OPEN`). |
| **Replay & Reproducibility** | `DeterministicMockLLMAdapter` is deterministic given identical in-memory market state; however, `invocation_id` (UUIDv4) and `now_utc` vary per run, and `window_start`/`window_end` default to `now_utc`. | Persist full `input_params`, `output_metadata`, `evidence_trail`, and model prompt/response snapshots in Postgres to allow deterministic post-hoc audit replay (`OPEN`). |

