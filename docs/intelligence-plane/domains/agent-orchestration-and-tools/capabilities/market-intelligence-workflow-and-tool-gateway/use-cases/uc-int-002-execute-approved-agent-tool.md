---
doc_id: CAP-INT-ORC-UC-002
title: "Use Case UC-INT-002: Execute an Approved Agent Tool"
doc_type: specification
plane: intelligence-plane
scope_level: use-case
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
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/tools/contracts.py"
    - "src/serving/infrastructure/runtime.py"
related_docs:
  - CAP-INT-ORC-REQ-001
  - INT-ARCH-GW-001
  - DIAG-INT-ORC-SEQ-002
requirement_ids:
  - UC-INT-002
  - AC-INT-002
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Specified approved tool dispatch lifecycle, policy gates, provenance creation, and exception cases."
---

# Use Case UC-INT-002: Execute an Approved Agent Tool

## 1. Identification, Actors & Trigger

- **Use Case ID**: `UC-INT-002`
- **Primary Actor**: `MarketIntelligenceGraph` (Node 3 `tool_gateway_executor_node` or Node 5 persistence step).
- **Supporting Actors**: `ControlledToolGateway`, `APPROVED_TOOL_POLICIES`, Injected Data/Runtime Handlers.
- **Trigger**: Orchestrator invokes `await gateway.execute_tool(tool_name, params, granted_permissions)`.

## 2. Preconditions, Permissions & Input/Output

- **Preconditions**: `ControlledToolGateway` instantiated; handlers registered for non-stub execution.
- **Permissions**: `granted_permissions` MUST contain `APPROVED_TOOL_POLICIES[tool].required_permission` (`market:read`, `historical:read`, `analytics:read`, or `agent:trigger`).
- **Inputs**: `tool_name: str`, `params: dict[str, Any]`, `granted_permissions: frozenset[str]`.
- **Outputs**: `ToolExecutionEnvelope(status="SUCCESS", data=..., provenance=ToolProvenanceMetadata)`.

## 3. Main, Alternative & Exception Flows

### 3.1 Main Flow

1. Gateway validates `ApprovedAgentTool(tool_name)` whitelist membership.
2. Gateway checks `policy.required_permission in granted_permissions`.
3. Gateway computes `requested_limit = int(params.get("limit") or params.get("lookback_periods") or 1)` and verifies `requested_limit <= policy.max_rows_or_periods`.
4. Gateway resolves handler from `self._handlers` and runs `await asyncio.wait_for(handler(params), timeout=policy.timeout_seconds)`.
5. Gateway generates UUIDv4 `invocation_id`, builds `ToolProvenanceMetadata`, wraps output into `ToolExecutionEnvelope(status="SUCCESS", ...)`, appends it to `self._audit_log`, and returns the envelope.

### 3.2 Alternative Flows

- **A1 (Unregistered Handler Stub)**: If `self._handlers.get(approved_tool)` is `None`, gateway skips `wait_for` and returns `{"status": "stub_ok", "tool": approved_tool.value}` (`gateway.py:76-77`).
- **A2 (Static Data Fallback Inside Handler)**: On missing ClickHouse close prices, `calculate_returns`, `calculate_volatility`, `calculate_correlation`, and `detect_anomalies` silently compute over hardcoded fallback price lists (`runtime.py:453,466,480,492`).

### 3.3 Exception Flows

- **E1 (Unwhitelisted Tool)**: Raises `UnauthorizedToolAccessError` (not written to `_audit_log`).
- **E2 (Missing Permission)**: Raises `UnauthorizedToolAccessError` (not written to `_audit_log`).
- **E3 (Row/Period Cap Exceeded)**: Raises `ToolQueryLimitExceededError` (not written to `_audit_log`).
- **E4 (Handler Timeout / Invalid Input)**: `asyncio.TimeoutError` or `ValueError` propagates unhandled (not converted to `ToolExecutionEnvelope(status="TIMEOUT"|"VALIDATION_ERROR")`).

## 4. Business Rules, State Transitions, Tool Contracts & Acceptance Criteria

- **Business Rules**: `RULE-INT-004`, `RULE-INT-005`, `RULE-INT-007`.
- **State Transitions**: Appends `ToolExecutionEnvelope` to `ControlledToolGateway._audit_log` and caller `AgentWorkflowState.evidence_trail`; `detect_anomalies` additionally mutates cooldown registry and `runtime.detected_anomalies` when triggered.
- **Relevant Tool Contracts**: All 10 tools in [tool-contracts.yaml](../../../../../shared-contracts/tool-contracts.yaml).
- **Acceptance Criteria (`AC-INT-002`)**: Unwhitelisted tools (`execute_raw_sql`) and unauthorized scopes raise `UnauthorizedToolAccessError`; `limit > max_rows_or_periods` raises `ToolQueryLimitExceededError`; valid calls return `ToolExecutionEnvelope(status="SUCCESS")` with valid UUIDv4 `invocation_id` recorded in `audit_log`.
- **Related Diagrams**: [tool-invocation-sequence.md](../workflows/tool-invocation-sequence.md) (`DIAG-INT-ORC-SEQ-002`), [tool-gateway-boundaries.md](../../../../../architecture/diagrams/tool-gateway-boundaries.md) (`DIAG-INT-GW-001`).
- **Open Questions**: `OPEN-INT-002` (side-effect control on `detect_anomalies`), fail-closed policy on missing handler, and input Pydantic schema enforcement.
