---
doc_id: CAP-INT-ORC-RULE-001
title: "Business Rules & Invariants: Market Intelligence Workflow & Tool Gateway"
doc_type: specification
plane: intelligence-plane
scope_level: capability
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: business-analyst
accountable_role: ai-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/orchestrator/graph.py"
    - "src/intelligence/workflows/investigation.py"
    - "src/intelligence/tools/contracts.py"
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/reporting/validator.py"
    - "src/shared/domain/quant.py"
related_docs:
  - CAP-INT-ORC-DOC-001
  - CAP-INT-ORC-REQ-001
  - ADR-OVR-003
  - ADR-INT-0001
requirement_ids:
  - RULE-INT-001
  - RULE-INT-002
  - RULE-INT-003
  - RULE-INT-004
  - RULE-INT-005
  - RULE-INT-006
  - RULE-INT-007
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Cataloged deterministic business rules, formulas, loop guardrails, and AS-IS enforcement gaps."
---

# Business Rules & Invariants: Market Intelligence Workflow & Tool Gateway

## 1. Deterministic Rules & Formulas

| Rule ID | Rule Name | Exact Formula / Constraint | `AS-IS` Code Enforcement | Gap / Exception Behavior |
|---|---|---|---|---|
| `RULE-INT-001` | **Symbol Allowlist Guard** | `symbol.upper().strip()` MUST exist in `monitored_symbols` before entering planning loop. | Enforced in `intake_and_guardrail_node` (`graph.py:123-127`). Sets `status="FAILED"`. | Static tuple snapshot at init; misses instruments added dynamically via Catalog API. |
| `RULE-INT-002` | **Planning Budget Ceiling** | Planning continues iff `current_iteration < max_iterations` (`6`) AND `tokens_consumed < int(token_budget * 0.8)` (`6400`) AND `status == "RUNNING"`. | Enforced in `AgentWorkflowState.can_continue_planning()` (`investigation.py:37-43`). | Node 5 synthesis runs outside this check and adds `540` tokens regardless of remaining budget; `PlatformConfig` values ignored. |
| `RULE-INT-003` | **Evidence Sufficiency Early Exit** | Planning loop exits early once `len(state.evidence_trail) >= 3`. | Enforced in `evidence_verifier_node` (`graph.py:153-155`). | Counts envelope quantity only; does not validate tool success or data non-emptiness. |
| `RULE-INT-004` | **Tool Whitelist & Row Bounds** | `tool_name` MUST map to `ApprovedAgentTool` AND `int(limit or lookback_periods or 1) <= policy.max_rows_or_periods`. | Enforced in `ControlledToolGateway.execute_tool()` (`gateway.py:51-69`). | Lower bound (`>= 1`), non-integer types, and `start_time`/`end_time` spans are not validated by gateway. |
| `RULE-INT-005` | **Deterministic Quantitative Math** | Log returns `ln(P_t / P_{t-1})`, annualized volatility `std(r) * sqrt(periods_per_year)` (default `365 * 24`), Pearson correlation `cov / (std_a * std_b)`, and Bessel Z-score `(latest - mean) / std_dev` (`threshold = 2.5`) MUST execute in Python, never LLM text. | Enforced in `src/shared/domain/quant.py` and `anomaly_detector.py`. Raises `ValueError` on prices `<= 0`. | Handlers silently fall back to synthetic price lists when ClickHouse stats are empty (`runtime.py:453,466,480,492`). |
| `RULE-INT-006` | **Citation Provenance Requirement** | Report MUST have non-empty `provenance_citations`, and every `invocation_id` MUST belong to `{env.provenance.invocation_id for env in evidence_trail}`. | Enforced in `ReportValidator.validate_report()` (`validator.py:19-31`). Raises `ReportProvenanceError`. | Does not validate numeric values inside prose `summary` or consistency of `row_count`/`symbol`/`tool_name` on citations. |
| `RULE-INT-007` | **Write Side-Effect Governance `[TARGET]`** | State-mutating tools (`generate_analysis_report`, `detect_anomalies`) MUST declare `is_read_only_market_data=False`, enforce caller authorization, and define approval/idempotency bounds. | **NOT ENFORCED (`GAP-INT-005`)**: `ToolGovernancePolicy.is_read_only_market_data` defaults to `True` on all 10 tools; permissions are hardcoded. | `detect_anomalies` triggers 900s alert cooldown side effects during read investigations. |

## 2. Violation Responses (`AS-IS`)

- `RULE-INT-001` violation -> `AgentWorkflowState.status = "FAILED"`, `final_report = {"error": ...}`.
- `RULE-INT-004` violation -> raises `UnauthorizedToolAccessError` or `ToolQueryLimitExceededError` (unhandled by graph -> HTTP `500`).
- `RULE-INT-006` violation -> raises `ReportProvenanceError` (unhandled by graph -> HTTP `500`, leaves run `status = "RUNNING"` in memory).

