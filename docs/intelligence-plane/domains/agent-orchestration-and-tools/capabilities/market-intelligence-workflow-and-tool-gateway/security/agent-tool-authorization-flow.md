---
doc_id: DIAG-INT-ORC-AUTHZ-001
title: "Agent Tool Authorization Flow"
doc_type: diagram
plane: intelligence-plane
scope_level: capability
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: security-architect
accountable_role: ai-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/intelligence-plane/domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/security/authorization-matrix.yaml"
    - "src/intelligence/tools/gateway.py"
related_docs:
  - CAP-INT-ORC-SEC-001
  - DIAG-INT-ORC-TM-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Created Agent Tool Authorization Flow diagram."
---

# Agent Tool Authorization Flow

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-INT-ORC-AUTHZ-001` |
| **Purpose** | Show how `granted_permissions` are evaluated in `ControlledToolGateway` (`AS-IS` hardcoded vs `TARGET` JWT-propagated). |
| **Scope & Owner** | `capability` (`CAP-INT-ORC-001`) / `security-architect` |
| **Authoritative Source** | [authorization-matrix.yaml](authorization-matrix.yaml) |
| **Notation** | Mermaid `flowchart TD` |
| **Version & Status** | `2.0.0` / `DRAFT` (`PARTIALLY_IMPLEMENTED`) |

```mermaid
flowchart TD
    REQ["Tool Call (tool_name, params)"] --> WL{"In ApprovedAgentTool?"}
    WL -->|"No"| DENY1["raise UnauthorizedToolAccessError"]
    WL -->|"Yes"| PERMS["Resolve policy.required_permission"]
    PERMS --> CHK{"In granted_permissions? (Hardcoded AS-IS / JWT TARGET)"}
    CHK -->|"No"| DENY2["raise UnauthorizedToolAccessError"]
    CHK -->|"Yes"| LIM{"limit <= max_rows_or_periods?"}
    LIM -->|"No"| DENY3["raise ToolQueryLimitExceededError"]
    LIM -->|"Yes"| EXEC["Execute Handler under timeout_seconds"]
```

**Legend**: Decision diamonds mark sequential authorization and resource-bound gates inside `ControlledToolGateway.execute_tool()`.

