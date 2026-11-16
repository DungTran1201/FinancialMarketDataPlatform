---
doc_id: CAP-INT-ORC-UC-003
title: "UC-INT-003: Verify Evidence Provenance"
doc_type: specification
plane: intelligence-plane
scope_level: use-case
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
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
related_docs:
  - CAP-INT-ORC-REQ-001
  - DIAG-INT-ORC-PROV-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Specified UC-INT-003 Verify Evidence Provenance."
---

# UC-INT-003: Verify Evidence Provenance

| Attribute | Value |
|---|---|
| **Use Case ID** | `UC-INT-003` |
| **Primary Actor** | `MarketIntelligenceGraph` (Node 5 `report_synthesizer_node`) |
| **Supporting Actors** | `ReportValidator` |
| **Trigger** | `ReportValidator.validate_report(report, state.evidence_trail)` |
| **Preconditions** | `report` dict synthesized; `state.evidence_trail` contains executed `ToolExecutionEnvelope`s. |
| **Postconditions** | Returns `True` if all cited `invocation_id`s exist in `evidence_trail`. |
| **Permissions** | Internal workflow step (no external caller). |
| **State Transitions** | Pre-condition gate before `COMPLETED` status. |
| **Related Diagrams** | [evidence-provenance-flow.md](../workflows/evidence-provenance-flow.md) |
| **Relevant Contracts** | `data-contract.yaml` (`ToolExecutionEnvelope`, `StructuredAnalysisReport`) |

## Main Flow
1. Build `valid_ids = {env.provenance.invocation_id for env in evidence_trail}`.
2. Read `citations = report.get("provenance_citations", [])` and verify it is non-empty.
3. For each citation, verify `invocation_id in valid_ids`.
4. Return `True`.

## Alternative & Exception Flows
- **Exc 1 (Empty Citations)**: Raises `ReportProvenanceError("Report must contain at least one provenance citation.")`.
- **Exc 2 (Fabricated Citation ID)**: Raises `ReportProvenanceError("Fabricated or unknown tool invocation_id ... cited in report.")`.

## Business Rules & Acceptance Criteria
- Enforces `BR-INT-004`.
- **AC-INT-003**: Any citation with an `invocation_id` absent from `evidence_trail` is rejected with `ReportProvenanceError`.

## Open Questions
- `OPEN-INT-006`: How will numeric values in narrative `summary` text be cross-checked against `quantitative_evidence` (`GAP-INT-006`)?

