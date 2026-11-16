---
doc_id: CAP-INT-ORC-ERR-001
title: "Error Catalog: Market Intelligence Workflow & Tool Gateway"
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
    - "src/intelligence/tools/contracts.py"
    - "src/intelligence/reporting/validator.py"
    - "src/intelligence/orchestrator/graph.py"
related_docs:
  - CAP-INT-ORC-DOC-001
  - INT-CTR-ROOT-001
  - CAP-APP-AGT-ERR-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Documented internal exceptions, AS-IS unhandled propagation gaps, and alignment with Postgres/contract status enums."
---

# Error Catalog: Market Intelligence Workflow & Tool Gateway

For tool-specific parameter errors, refer to the authoritative [tool-contracts.yaml](../../../../../shared-contracts/tool-contracts.yaml). For HTTP error envelopes exposed to clients, refer to Application Plane `CAP-APP-AGT-001` [error-catalog.md](../../../../../../application-plane/domains/agent-experience-and-reporting/capabilities/agent-run-and-report-portal/contracts/error-catalog.md).

## 1. Internal Exceptions & Failure States

| Error / Exception | Trigger Condition | `AS-IS` Handling Behavior | Retryable | Target Disposition |
|---|---|---|---|---|
| `Node1 UnmonitoredSymbolError` (soft state) | `symbol.upper().strip()` absent from `_monitored_symbols` (`graph.py:124-127`). | Sets `state.status = "FAILED"`, `final_report = {"error": ...}` cleanly. | No | Keep deterministic `FAILED` transition; sync symbol list dynamically with Catalog. |
| `UnauthorizedToolAccessError` (`PermissionError`) | Tool name not in `ApprovedAgentTool` OR `policy.required_permission not in granted_permissions` (`gateway.py:51-62`). | Propagates unhandled out of `run_investigation()`; not recorded in `_audit_log`; leaves `status="RUNNING"`. | No | Log `PERMISSION_DENIED` audit row, fail run cleanly (`status="FAILED"`). |
| `ToolQueryLimitExceededError` (`ValueError`) | `int(limit or lookback_periods or 1) > policy.max_rows_or_periods` (`gateway.py:64-69`). | Propagates unhandled; not recorded in `_audit_log`; leaves `status="RUNNING"`. | No | Log `VALIDATION_ERROR` audit row; return bounded hint or mark run `FAILED`. |
| `asyncio.TimeoutError` | Registered handler exceeds `policy.timeout_seconds` inside `asyncio.wait_for` (`gateway.py:79`). | Propagates unhandled; not mapped to `ToolExecutionEnvelope(status="TIMEOUT")`. | Yes (bounded) | Wrap into `ToolExecutionEnvelope(status="TIMEOUT")`, persist audit row, retry or fail run cleanly. |
| `ReportProvenanceError` (`ValueError`) | Empty `provenance_citations` OR citation `invocation_id` missing from `evidence_trail` (`validator.py:25-30`). | Propagates unhandled out of Node 5 before Tool #10 executes; leaves `status="RUNNING"`. | No (retry synthesis only in `TARGET`) | Mark run `FAILED` (or bounded re-synthesis attempt in `TARGET`). |
| `ValueError / TypeError` (Handler / Quant) | Non-numeric `limit`, prices `<= 0` in `quant.py`, or malformed ISO timestamp in `generate_analysis_report`. | Propagates unhandled out of gateway/graph. | No | Enforce Pydantic input validation prior to handler dispatch. |

## 2. Redaction & Security Rules

- Exception messages and `final_report["error"]` payloads MUST NEVER expose internal Python stack traces, database credentials, `LLM_API_KEY`, or internal container IP/port bindings.
- Denied and timed-out tool invocations MUST be captured in audit telemetry without leaking secret parameters.
