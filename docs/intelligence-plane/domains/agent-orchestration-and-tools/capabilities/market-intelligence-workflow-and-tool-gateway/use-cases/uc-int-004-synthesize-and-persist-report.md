---
doc_id: CAP-INT-ORC-UC-004
title: "Use Case UC-INT-004: Synthesize and Persist an Analysis Report"
doc_type: specification
plane: intelligence-plane
scope_level: use-case
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: SIMULATED
version: "2.0.0"
owner_role: business-analyst
accountable_role: ai-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/orchestrator/graph.py"
    - "src/serving/infrastructure/runtime.py"
    - "src/serving/api/modules/reporting/domain/ports.py"
related_docs:
  - CAP-INT-ORC-REQ-001
  - CAP-APP-AGT-UC-002
  - CAP-INT-ORC-DM-001
requirement_ids:
  - UC-INT-004
  - AC-INT-004
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Specified report synthesis and persistence via Tool #10, contrasting AS-IS memory dict with TARGET PostgreSQL storage."
---

# Use Case UC-INT-004: Synthesize and Persist an Analysis Report

## 1. Identification, Actors & Trigger

- **Use Case ID**: `UC-INT-004`
- **Primary Actor**: `MarketIntelligenceGraph` (Node 5 `report_synthesizer_node`).
- **Supporting Actors**: Model Adapter (`DeterministicMockLLMAdapter`), `ReportValidator`, `ControlledToolGateway` (`generate_analysis_report`), `PlatformRuntimeContainer.reports` (`TARGET`: PostgreSQL `agent_runs.structured_report`).
- **Trigger**: Planning loop terminates in `MarketIntelligenceGraph.run_investigation()` (`graph.py:157`).

## 2. Preconditions, Permissions & Input/Output

- **Preconditions**: Node 1 succeeded (`status == "RUNNING"`); `evidence_trail` holds >= 1 `ToolExecutionEnvelope`.
- **Permissions**: Requires `agent:trigger` in `granted_permissions` (`contracts.py:104`).
- **Inputs**: `AgentWorkflowState` (`run_id`, `symbol`, `trigger_mode`, `evidence_trail`).
- **Outputs**: `StructuredAnalysisReport` stored in `runtime.reports[run_id]`, `state.final_report`, `state.status = "COMPLETED"`, and persistence envelope appended to `state.evidence_trail`.

## 3. Main, Alternative & Exception Flows

### 3.1 Main Flow

1. Node 5 appends `"report_synthesizer_node"` to `state.visited_nodes`.
2. Calls `self._llm.synthesize_narrative(state)` producing report dict (`quantitative_evidence`, `anomalies_detected`, `provenance_citations`, `limitations_disclaimer`, `data_quality_status="HEALTHY"`, `summary`) and adds `540` tokens to `state.tokens_consumed`.
3. Invokes `ReportValidator.validate_report(report, state.evidence_trail)` (`UC-INT-003`).
4. Dispatches `ApprovedAgentTool.GENERATE_ANALYSIS_REPORT` through `ControlledToolGateway.execute_tool()` with `{"symbol": state.symbol, "report": report}`.
5. Tool handler constructs `StructuredAnalysisReport` (`ProvenanceCitation` tuples) and writes `self.reports[run_id] = structured` (`runtime.py:515-542`).
6. Node 5 appends persistence envelope to `state.evidence_trail` (total 8 envelopes in mock run), sets `state.final_report = report`, and sets `state.status = "COMPLETED"`.

### 3.2 Alternative Flows

- **A1 (`TARGET` PostgreSQL Persistence)**: Persist `structured_report` JSONB and `completed_at` into `agent_runs` via `fmdp_agent_rw` instead of ephemeral `runtime.reports` dict (`NOT_IMPLEMENTED AS-IS`).

### 3.3 Exception Flows

- **E1 (Validation Failure)**: `ReportValidator` raises `ReportProvenanceError` before Tool #10 executes (`UC-INT-005`).
- **E2 (Missing `agent:trigger` Permission)**: `ControlledToolGateway` raises `UnauthorizedToolAccessError`, leaving report unpersisted.
- **E3 (Malformed Citation Timestamp)**: `datetime.fromisoformat(...)` inside `_tool_generate_analysis_report` raises `ValueError`.

## 4. Business Rules, State Transitions, Tool Contracts & Acceptance Criteria

- **Business Rules**: `RULE-INT-006`, `RULE-INT-007`.
- **State Transitions**: `RUNNING -> COMPLETED` upon Tool #10 return.
- **Relevant Tool Contracts**: `generate_analysis_report` in [tool-contracts.yaml](../../../../../shared-contracts/tool-contracts.yaml).
- **Acceptance Criteria (`AC-INT-004`)**: Report passes `ReportValidator`, `StructuredAnalysisReport` is retrievable via `runtime.reports[run_id]` (and `GET /api/v1/reports/{run_id}`), and `len(provenance_citations) == 7` in mock baseline runs.
- **Related Diagrams**: [agent-workflow-diagram.md](../workflows/agent-workflow-diagram.md) (`DIAG-INT-ORC-AGT-001`), [evidence-provenance-flow.md](../workflows/evidence-provenance-flow.md) (`DIAG-INT-ORC-DFD-001`).
- **Open Questions**: `OPEN-INT-004` (Postgres `agent_runs` persistence wiring), `OPEN-INT-003` (post-budget Node 5 token enforcement).
