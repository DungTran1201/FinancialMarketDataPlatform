---
doc_id: DIAG-INT-ORC-TM-001
title: "Threat Model Diagram: Intelligence Plane Attack Paths & Controls"
doc_type: diagram
plane: intelligence-plane
scope_level: capability
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: security-architect
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/intelligence-plane/domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/security/threat-model.md"
    - "docs/intelligence-plane/domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/security/security-requirements.md"
related_docs:
  - CAP-INT-ORC-TM-001
  - CAP-INT-ORC-SEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Rendered threat paths across TB-INT-1..4 distinguishing AS-IS unauthenticated/side-effect bypasses from TARGET external-LLM vectors."
---

# Threat Model Diagram: Intelligence Plane Attack Paths & Controls

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-INT-ORC-TM-001` |
| **Title & Purpose** | Attack Vectors, Trust Boundaries (`TB-INT-1..4`), and Control Gaps in `CAP-INT-ORC-001` |
| **Owner Role & Scope** | `security-architect / CAP-INT-ORC-001` |
| **Authoritative Source** | [threat-model.md](threat-model.md) (`CAP-INT-ORC-TM-001`) |
| **Notation** | `Mermaid flowchart TB` (`Threat Model DFD`) |
| **Version & Status** | `2.0.0 — DRAFT` |

## 2. Diagram

```mermaid
flowchart TB
    atk["Untrusted Caller / Attacker"]

    subgraph tb1["TB-INT-1: Application Trigger -> Graph Intake"]
        api_in["POST /api/v1/agents/runs (Zero Auth Depends AS-IS)"]
        graph_in["MarketIntelligenceGraph (Hardcoded _agent_permissions)"]
    end

    subgraph tb2["TB-INT-2: Planner -> ControlledToolGateway"]
        planner["Model Adapter (AS-IS: Mock | TARGET: External LLM)"]
        gw["ControlledToolGateway (Whitelist + Max Cap + Timeout)"]
    end

    subgraph tb3["TB-INT-3: Handlers & Report Persistence"]
        anom_mut["detect_anomalies -> Mutates 900s Cooldown & detected_anomalies"]
        rep_val["ReportValidator (Checks invocation_id Set Only)"]
        rep_mut["generate_analysis_report -> Writes runtime.reports"]
    end

    ext_llm["TB-INT-4 TARGET: External LLM Provider"]

    atk -.->|"THR-INT-001 Bypass Auth & Escalate via Hardcoded Perms"| api_in --> graph_in
    atk -.->|"THR-INT-005 Sync Request Thread Exhaustion"| api_in
    graph_in -->|"Pass prompt_summary"| planner
    planner -.->|"THR-INT-006 Injection / Malformed Params (TARGET)"| gw
    planner -.->|"THR-INT-008 Prompt/Key Egress (TARGET)"| ext_llm
    gw -->|"THR-INT-002 Cooldown DoS"| anom_mut
    planner -->|"THR-INT-004 Fabricated Numbers w/ Valid IDs"| rep_val
    rep_val -->|"THR-INT-003 Write Side Effect Marked Read-Only"| rep_mut
```

## 3. Legend

- **Dashed Arrows (`-.->`)**: Unmitigated `AS-IS` exploit paths (`THR-INT-001`, `THR-INT-005`) or `TARGET` external-LLM threat vectors (`THR-INT-006`, `THR-INT-008`).
- **Solid Arrows (`-->`)**: Active internal execution hops exhibiting metadata/validation weaknesses (`THR-INT-002`, `THR-INT-003`, `THR-INT-004`).

