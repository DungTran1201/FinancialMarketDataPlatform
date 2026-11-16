---
doc_id: CAP-INT-ORC-ERR-001
title: "Error Catalog: Intelligence Plane"
doc_type: specification
plane: intelligence-plane
scope_level: capability
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: ai-engineer
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/reporting/validator.py"
    - "src/intelligence/orchestrator/graph.py"
related_docs:
  - CAP-INT-ORC-DOC-001
  - CAP-INT-ORC-UC-005
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Cataloged Intelligence Plane exceptions and failure payloads."
---

# Error Catalog: Intelligence Plane (`CAP-INT-ORC-001`)

| Exception / Error | Raised By | Trigger Condition | `AS-IS` Handling |
|---|---|---|---|
| `UnauthorizedToolAccessError` | `ControlledToolGateway.execute_tool()` | Tool not in `ApprovedAgentTool` or `required_permission` missing | Propagates uncaught out of `run_investigation()` |
| `ToolQueryLimitExceededError` | `ControlledToolGateway.execute_tool()` | `limit` or `lookback_periods` > `policy.max_rows_or_periods` | Propagates uncaught out of `run_investigation()` |
| `asyncio.TimeoutError` | `ControlledToolGateway.execute_tool()` | Handler exceeds `policy.timeout_seconds` | Propagates uncaught out of `run_investigation()` |
| `ReportProvenanceError` | `ReportValidator.validate_report()` | Empty `provenance_citations` or unknown `invocation_id` | Propagates uncaught out of `run_investigation()` |
| Unmonitored Symbol Error | `MarketIntelligenceGraph` (Node 1) | `symbol` not in `_monitored_symbols` | Sets `status="FAILED"`, `final_report={"error": ...}` |

