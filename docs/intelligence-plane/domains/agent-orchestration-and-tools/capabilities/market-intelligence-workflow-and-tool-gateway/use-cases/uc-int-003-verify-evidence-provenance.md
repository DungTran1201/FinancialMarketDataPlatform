---
doc_id: CAP-INT-ORC-UC-003
title: "Use Case UC-INT-003: Verify Evidence Provenance"
doc_type: specification
plane: intelligence-plane
scope_level: use-case
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: business-analyst
accountable_role: qa-lead
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/reporting/validator.py"
    - "src/intelligence/orchestrator/graph.py"
related_docs:
  - CAP-INT-ORC-REQ-001
  - INT-ARCH-EVAL-001
  - DIAG-INT-ORC-DFD-001
requirement_ids:
  - UC-INT-003
  - AC-INT-003
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Specified provenance verification workflow and documented AS-IS citation-ID-only bounds."
---

# Use Case UC-INT-003: Verify Evidence Provenance

## 1. Identification, Actors & Trigger

- **Use Case ID**: `UC-INT-003`
- **Primary Actor**: `MarketIntelligenceGraph` (Node 5 `report_synthesizer_node`).
- **Supporting Actors**: `ReportValidator`, `AgentWorkflowState.evidence_trail`.
- **Trigger**: Invoked synchronously after narrative synthesis (`graph.py:161`) via `ReportValidator.validate_report(report, state.evidence_trail)`.

## 2. Preconditions, Permissions & Input/Output

- **Preconditions**: `report` dictionary produced by LLM adapter; `evidence_trail` contains `ToolExecutionEnvelope` items from Node 3.
- **Permissions**: Internal orchestrator check (no direct user permission needed).
- **Inputs**: `report: dict[str, Any]`, `evidence_trail: list[ToolExecutionEnvelope]`.
- **Outputs**: `True` on valid citations; raises `ReportProvenanceError` otherwise.

## 3. Main, Alternative & Exception Flows

### 3.1 Main Flow

1. `ReportValidator` extracts `valid_ids = {env.provenance.invocation_id for env in evidence_trail}`.
2. Checks `citations = report.get("provenance_citations", [])` is non-empty.
3. For each citation entry (`dict` or object), extracts `invocation_id` and verifies `inv_id in valid_ids`.
4. Returns `True`.

### 3.2 Alternative Flows

- **A1 (Object vs Dict Citation)**: Supports both `dict` (`cit.get("invocation_id")`) and attribute access (`getattr(cit, "invocation_id", None)`).

### 3.3 Exception Flows

- **E1 (Empty Citations)**: Empty `provenance_citations` raises `ReportProvenanceError("Report must contain at least one provenance citation.")`.
- **E2 (Fabricated / Unknown `invocation_id`)**: Any citation ID absent from `valid_ids` raises `ReportProvenanceError`.

## 4. Business Rules, State Transitions, Tool Contracts & Acceptance Criteria

- **Business Rules**: `RULE-INT-006`.
- **State Transitions**: Blocks transition to Tool #10 persistence (`generate_analysis_report`) and `COMPLETED` when raised.
- **Relevant Tool Contracts**: Precedes `generate_analysis_report` in [tool-contracts.yaml](../../../../../shared-contracts/tool-contracts.yaml).
- **Acceptance Criteria (`AC-INT-003`)**: Report citing genuine `invocation_id`s returns `True`; empty citations or fabricated ID (e.g., `inv_fabricated_999999`) raises `ReportProvenanceError`.
- **Related Diagrams**: [evidence-provenance-flow.md](../workflows/evidence-provenance-flow.md) (`DIAG-INT-ORC-DFD-001`).
- **Open Questions**: `OPEN-INT-003` — How should `ReportValidator` verify numeric consistency in `summary` text and field parity (`symbol`, `tool_name`, `row_count`) beyond `invocation_id` membership?
