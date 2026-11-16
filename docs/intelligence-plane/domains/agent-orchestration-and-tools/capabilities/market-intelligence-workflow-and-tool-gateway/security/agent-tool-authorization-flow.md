---
doc_id: DIAG-INT-ORC-AUTHZ-001
title: "Agent Tool Authorization Flow (AS-IS Hardcoded vs TARGET Caller RBAC)"
doc_type: diagram
plane: intelligence-plane
scope_level: capability
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: security-architect
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/intelligence-plane/domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/security/side-effect-and-approval-policy.md"
    - "docs/intelligence-plane/domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/security/authorization-matrix.yaml"
related_docs:
  - CAP-INT-ORC-POL-001
  - CAP-INT-ORC-SEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Rendered AS-IS hardcoded workflow permission flow vs TARGET JWT capability propagation and write-tool guarding."
---

# Agent Tool Authorization Flow (`AS-IS` Hardcoded vs `TARGET` Caller RBAC)

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-INT-ORC-AUTHZ-001` |
| **Title & Purpose** | Contrast between `AS-IS` hardcoded `_agent_permissions` and `TARGET` caller JWT RBAC + write-tool separation |
| **Owner Role & Scope** | `security-architect / CAP-INT-ORC-001` |
| **Authoritative Source** | [side-effect-and-approval-policy.md](side-effect-and-approval-policy.md) (`CAP-INT-ORC-POL-001`) |
| **Notation** | `Mermaid flowchart TD` (`Authorization Flow`) |
| **Version & Status** | `2.0.0 — DRAFT` |

## 2. Diagram

```mermaid
flowchart TD
    caller["HTTP Caller / Event Trigger"]

    subgraph asis["AS-IS Authorization Path (GAP-INT-004)"]
        no_jwt["agent_api router: Zero JWT Depends Check"]
        hc_perm["MarketIntelligenceGraph: Hardcoded _agent_permissions (4 scopes)"]
        gw_asis{"ControlledToolGateway: required_permission in _agent_permissions?"}
    end

    subgraph target["TARGET Authorization Path (SEC-INT-001, SEC-INT-003)"]
        jwt_chk{"Verify JWT / API Key + Require agent:trigger"}
        cap_int["Propagate Caller JwtClaims.capabilities Intersected w/ Ceiling"]
        gw_tgt{"Gateway: Whitelist + Caller Permission + Pydantic Schema + Write Gate"}
        deny(["403 Forbidden / PERMISSION_DENIED Audit Row"])
    end

    exec["Execute Deterministic Tool Handler"]

    caller -->|"AS-IS"| no_jwt --> hc_perm --> gw_asis
    gw_asis -->|"Always True for Known Tools"| exec

    caller -.->|"TARGET"| jwt_chk
    jwt_chk -.->|"Missing/Viewer Role"| deny
    jwt_chk -.->|"Analyst/Operator/Admin"| cap_int -.-> gw_tgt
    gw_tgt -.->|"Missing Scope or Invalid Schema"| deny
    gw_tgt -.->|"Authorized"| exec
```

## 3. Legend

- **Solid Path (`-->`)**: Active `AS-IS` path where caller identity is unchecked and `MarketIntelligenceGraph` injects hardcoded permissions.
- **Dashed Path (`-.->`)**: `TARGET` end-to-end RBAC enforcement required by `SEC-INT-001` and `SEC-INT-003`.

