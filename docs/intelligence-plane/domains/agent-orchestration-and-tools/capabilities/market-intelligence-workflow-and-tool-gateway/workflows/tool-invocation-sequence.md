---
doc_id: DIAG-INT-ORC-SEQ-002
title: "Sequence Diagram: ControlledToolGateway Invocation & Provenance Wrapping"
doc_type: diagram
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
  is_authoritative: false
  authoritative_source:
    - "docs/intelligence-plane/domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/use-cases/uc-int-002-execute-approved-agent-tool.md"
    - "docs/intelligence-plane/architecture/tool-gateway-architecture.md"
related_docs:
  - CAP-INT-ORC-UC-002
  - INT-ARCH-GW-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Rendered ControlledToolGateway step-by-step gatekeeping sequence and failure branches."
---

# Sequence Diagram: `ControlledToolGateway` Invocation & Provenance Wrapping

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-INT-ORC-SEQ-002` |
| **Title & Purpose** | Chronological tool validation, timeout execution, provenance wrapping, and audit recording inside `ControlledToolGateway` |
| **Owner Role & Scope** | `ai-engineer / CAP-INT-ORC-001` |
| **Authoritative Source** | [uc-int-002-execute-approved-agent-tool.md](../use-cases/uc-int-002-execute-approved-agent-tool.md) (`CAP-INT-ORC-UC-002`) |
| **Notation** | `Mermaid sequenceDiagram` (`UML 2.5.1`) |
| **Version & Status** | `2.0.0 — DRAFT` |

## 2. Diagram

```mermaid
sequenceDiagram
    autonumber
    participant ORCH as MarketIntelligenceGraph
    participant GW as ControlledToolGateway
    participant POL as APPROVED_TOOL_POLICIES
    participant HND as Registered Handler Closure

    ORCH->>GW: execute_tool(tool_name, params, granted_permissions)
    GW->>POL: ApprovedAgentTool(tool_name)
    alt Not in ApprovedAgentTool Enum
        GW-->>ORCH: Raise UnauthorizedToolAccessError
    else In Whitelist
        GW->>POL: Check policy.required_permission in granted_permissions
        alt Missing Permission
            GW-->>ORCH: Raise UnauthorizedToolAccessError
        else Authorized
            GW->>GW: Check int(limit or lookback_periods or 1) <= max_rows_or_periods
            alt Cap Exceeded
                GW-->>ORCH: Raise ToolQueryLimitExceededError
            else Within Bounds
                alt Handler Registered
                    GW->>HND: asyncio.wait_for(handler(params), timeout=policy.timeout_seconds)
                    HND-->>GW: result_data dict (or TimeoutError propagates)
                else Handler is None
                    GW->>GW: Return synthetic {"status": "stub_ok"}
                end
                GW->>GW: Generate UUIDv4 invocation_id + ToolProvenanceMetadata
                GW->>GW: Append ToolExecutionEnvelope(SUCCESS) to _audit_log
                GW-->>ORCH: Return ToolExecutionEnvelope
            end
        end
    end
```

## 3. Legend

- **Exception Branches**: Errors raised prior to or during handler execution propagate directly and are NOT appended to `_audit_log` `AS-IS`.

