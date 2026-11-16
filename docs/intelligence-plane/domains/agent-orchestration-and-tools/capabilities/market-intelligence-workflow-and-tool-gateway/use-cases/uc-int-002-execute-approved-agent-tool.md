---
doc_id: CAP-INT-ORC-UC-002
title: "UC-INT-002: Execute an Approved Agent Tool"
doc_type: specification
plane: intelligence-plane
scope_level: use-case
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: ai-engineer
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/tools/contracts.py"
related_docs:
  - CAP-INT-ORC-REQ-001
  - DIAG-INT-ORC-TOOL-SEQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Specified UC-INT-002 Execute an Approved Agent Tool."
---

# UC-INT-002: Execute an Approved Agent Tool

| Attribute | Value |
|---|---|
| **Use Case ID** | `UC-INT-002` |
| **Primary Actor** | `MarketIntelligenceGraph` (or authorized test/service caller) |
| **Supporting Actors** | `ControlledToolGateway`, injected Data/App handler closure |
| **Trigger** | `await gateway.execute_tool(tool_name, params, granted_permissions)` |
| **Preconditions** | `APPROVED_TOOL_POLICIES` defines the tool; handler is registered (or `stub_ok` fallback applies). |
| **Postconditions** | `ToolExecutionEnvelope(status="SUCCESS")` returned and appended to `gateway._audit_log`. |
| **Permissions** | Caller `granted_permissions` must include `policy.required_permission` (`market:read`, `historical:read`, `analytics:read`, or `agent:trigger`). |
| **State Transitions** | Stateless per call; appends to in-memory `_audit_log`. |
| **Related Diagrams** | [tool-invocation-sequence.md](../workflows/tool-invocation-sequence.md), [agent-tool-authorization-flow.md](../security/agent-tool-authorization-flow.md) |
| **Relevant Contracts** | `tool-contracts.yaml` |

## Main Flow
1. Validate `tool_name` is a member of `ApprovedAgentTool`.
2. Lookup `policy = APPROVED_TOOL_POLICIES[approved_tool]` and verify `policy.required_permission in granted_permissions`.
3. Extract `requested_limit = int(params.get("limit") or params.get("lookback_periods") or 1)` and verify `requested_limit <= policy.max_rows_or_periods`.
4. Generate `invocation_id = uuid.uuid4()` and dispatch `await asyncio.wait_for(handler(params), timeout=policy.timeout_seconds)`.
5. Construct `ToolProvenanceMetadata` and `ToolExecutionEnvelope(status="SUCCESS")`, append to `self._audit_log`, and return.

## Alternative & Exception Flows
- **Alt 1 (Unregistered Handler)**: If `handler is None`, returns `{"status": "stub_ok", "tool": approved_tool.value}` wrapped in `ToolExecutionEnvelope`.
- **Exc 1 (Unlisted Tool / Missing Permission)**: Raises `UnauthorizedToolAccessError`.
- **Exc 2 (Row Cap Exceeded)**: Raises `ToolQueryLimitExceededError`.
- **Exc 3 (Timeout)**: `asyncio.TimeoutError` propagates.

## Business Rules & Acceptance Criteria
- Enforces `BR-INT-002`, `BR-INT-003`.
- **AC-INT-002**: Unapproved tools and oversized limits raise their respective exceptions before any handler executes.

## Open Questions
- `OPEN-INT-005`: Should `ControlledToolGateway` enforce full JSON Schema validation and `limit >= 1` lower bounds?

