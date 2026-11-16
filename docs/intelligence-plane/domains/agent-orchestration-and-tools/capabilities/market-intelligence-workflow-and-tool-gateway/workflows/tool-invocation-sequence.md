---
doc_id: DIAG-INT-ORC-TOOL-SEQ-001
title: "Tool Invocation Sequence Diagram"
doc_type: diagram
plane: intelligence-plane
scope_level: capability
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
  is_authoritative: false
  authoritative_source:
    - "docs/intelligence-plane/domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/use-cases/uc-int-002-execute-approved-agent-tool.md"
    - "src/intelligence/tools/gateway.py"
related_docs:
  - CAP-INT-ORC-UC-002
  - INT-ARCH-GW-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Created Tool Invocation Sequence Diagram detailing gateway validation and handler dispatch."
---

# Tool Invocation Sequence Diagram

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-INT-ORC-TOOL-SEQ-001` |
| **Purpose** | Show step-by-step validation, timeout wrapping, provenance creation, and error paths in `ControlledToolGateway`. |
| **Scope & Owner** | `capability` (`CAP-INT-ORC-001`) / `ai-engineer` |
| **Authoritative Source** | [uc-int-002-execute-approved-agent-tool.md](../use-cases/uc-int-002-execute-approved-agent-tool.md) (`CAP-INT-ORC-UC-002`) |
| **Notation** | Mermaid `sequenceDiagram` (UML 2.5.1) |
| **Version & Status** | `2.0.0` / `DRAFT` (`PARTIALLY_IMPLEMENTED`) |

```mermaid
sequenceDiagram
    participant Caller as "MarketIntelligenceGraph"
    participant GW as "ControlledToolGateway"
    participant Pol as "APPROVED_TOOL_POLICIES"
    participant H as "Registered Store Handler"

    Caller->>GW: execute_tool(tool_name, params, granted_permissions)
    GW->>Pol: Validate ApprovedAgentTool(tool_name)
    alt Unknown tool or missing permission
        GW-->>Caller: raise UnauthorizedToolAccessError
    else limit > max_rows_or_periods
        GW-->>Caller: raise ToolQueryLimitExceededError
    else Validated
        alt Handler registered
            GW->>H: asyncio.wait_for(handler(params), timeout=policy.timeout_seconds)
            H-->>GW: result_data dict
        else No handler registered
            GW->>GW: result_data = {"status": "stub_ok"}
        end
        GW->>GW: Build ToolProvenanceMetadata + ToolExecutionEnvelope(SUCCESS)
        GW->>GW: Append to _audit_log
        GW-->>Caller: Return ToolExecutionEnvelope
    end
```

**Legend**: `alt` branches depict exception paths (`UnauthorizedToolAccessError`, `ToolQueryLimitExceededError`) vs normal handler or `stub_ok` execution.

