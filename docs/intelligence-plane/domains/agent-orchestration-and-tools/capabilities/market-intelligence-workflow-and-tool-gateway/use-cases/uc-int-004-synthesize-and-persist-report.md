---
doc_id: CAP-INT-ORC-UC-004
title: "UC-INT-004: Synthesize and Persist an Analysis Report"
doc_type: specification
plane: intelligence-plane
scope_level: use-case
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: SIMULATED
version: "2.0.0"
owner_role: ai-engineer
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/orchestrator/graph.py"
    - "src/serving/infrastructure/runtime.py"
related_docs:
  - CAP-INT-ORC-REQ-001
  - CAP-INT-ORC-UC-003
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Specified UC-INT-004 Synthesize and Persist an Analysis Report."
---

# UC-INT-004: Synthesize and Persist an Analysis Report

| Attribute | Value |
|---|---|
| **Use Case ID** | `UC-INT-004` |
| **Primary Actor** | `MarketIntelligenceGraph` (Node 5 `report_synthesizer_node`) |
| **Supporting Actors** | `DeterministicMockLLMAdapter`, `ReportValidator`, `ControlledToolGateway` (`generate_analysis_report`) |
| **Trigger** | Completion of planning/execution loop (`evidence_verifier_node` exit or loop budget exhaustion) |
| **Preconditions** | `state.evidence_trail` contains at least 1 `ToolExecutionEnvelope`. |
| **Postconditions** | `StructuredAnalysisReport` stored in `runtime.reports[run_id]` (`AS-IS`); `state.final_report` set; `state.status = "COMPLETED"`. |
| **Permissions** | Requires `agent:trigger` (hardcoded in `_agent_permissions` `AS-IS`). |
| **State Transitions** | `RUNNING` -> `COMPLETED`. |
| **Related Diagrams** | [agent-workflow-diagram.md](../workflows/agent-workflow-diagram.md), [evidence-provenance-flow.md](../workflows/evidence-provenance-flow.md) |
| **Relevant Contracts** | `tool-contracts.yaml` (`generate_analysis_report`), `data-contract.yaml` (`StructuredAnalysisReport`) |

## Main Flow
1. `self._llm.synthesize_narrative(state)` builds `report` dict from `evidence_trail` and returns `(report, 540)`.
2. `state.tokens_consumed += 540`.
3. `ReportValidator.validate_report(report, state.evidence_trail)` verifies citations.
4. `ControlledToolGateway.execute_tool("generate_analysis_report", {"symbol": state.symbol, "report": report}, self._agent_permissions)` writes `StructuredAnalysisReport` into `runtime.reports[run_id]`.
5. Append returned envelope to `state.evidence_trail`, set `state.final_report = report`, and set `state.status = "COMPLETED"`.

## Alternative & Exception Flows
- **Exc 1 (Empty Evidence Trail)**: `ReportValidator.validate_report()` raises `ReportProvenanceError` before persistence.
- **Exc 2 (Missing Permission)**: `ControlledToolGateway` raises `UnauthorizedToolAccessError`.

## Business Rules & Acceptance Criteria
- Enforces `BR-INT-002`, `BR-INT-004`.
- **AC-INT-004**: Persisted report is retrievable via `runtime.reports[run_id]` with `len(provenance_citations) >= 1`.

## Open Questions
- `OPEN-INT-007`: Should `generate_analysis_report` require an idempotency/insert-once guard to prevent overwriting existing `run_id` reports in PostgreSQL?

