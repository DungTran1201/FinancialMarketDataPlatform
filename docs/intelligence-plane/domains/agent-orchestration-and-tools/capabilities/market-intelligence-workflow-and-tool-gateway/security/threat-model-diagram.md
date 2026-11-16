---
doc_id: DIAG-INT-ORC-TM-001
title: "Threat Model Diagram: CAP-INT-ORC-001"
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
    - "docs/intelligence-plane/domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/security/threat-model.md"
related_docs:
  - CAP-INT-ORC-TM-001
  - CAP-INT-ORC-SEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Created Threat Model Diagram mapping THR-INT-001..005 across trust boundaries."
---

# Threat Model Diagram (`CAP-INT-ORC-001`)

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-INT-ORC-TM-001` |
| **Purpose** | Visualize trust boundaries and threat vectors (`THR-INT-001..005`) across Plane B -> Plane C -> Stores. |
| **Scope & Owner** | `capability` (`CAP-INT-ORC-001`) / `security-architect` |
| **Authoritative Source** | [threat-model.md](threat-model.md) (`CAP-INT-ORC-TM-001`) |
| **Notation** | Mermaid `flowchart TB` (Trust Boundary Diagram) |
| **Version & Status** | `2.0.0` / `DRAFT` (`PARTIALLY_IMPLEMENTED`) |

```mermaid
flowchart TB
    subgraph B1["Boundary 1: Plane B Trigger"]
        CALLER["HTTP Caller -> POST /api/v1/agents/runs"]
    end

    subgraph B2["Boundary 2: Orchestrator & LLM"]
        GRAPH["MarketIntelligenceGraph (Hardcoded _agent_permissions THR-INT-001)"]
        LLM["LLM Adapter (Mock AS-IS / External TARGET THR-INT-005)"]
        VAL["ReportValidator (ID-only check THR-INT-004)"]
    end

    subgraph B3["Boundary 3: ControlledToolGateway"]
        GW["Whitelist + RBAC + Row Cap + Timeout (THR-INT-003)"]
    end

    subgraph B4["Boundary 4: Store Handlers"]
        STORES["Redis / ClickHouse / runtime.reports & detected_anomalies (THR-INT-002)"]
    end

    CALLER -->|"No route RBAC (SEC-AUDIT-003)"| GRAPH
    GRAPH <-->|"prompt_summary / narrative"| LLM
    GRAPH -->|"execute_tool()"| GW
    GW -->|"Handlers"| STORES
    GRAPH -->|"validate_report()"| VAL
```

**Legend**: Subgraphs `B1..B4` represent security trust boundaries; threat IDs (`THR-INT-001..005`) annotate active and `TARGET` risks.

