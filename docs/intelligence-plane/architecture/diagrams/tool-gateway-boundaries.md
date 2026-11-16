---
doc_id: DIAG-INT-GW-001
title: "Tool Gateway Trust Boundary Diagram"
doc_type: diagram
plane: intelligence-plane
scope_level: plane
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
    - "docs/intelligence-plane/architecture/tool-gateway-architecture.md"
    - "src/intelligence/tools/gateway.py"
related_docs:
  - INT-ARCH-ROOT-001
  - INT-ARCH-GW-001
  - INT-ARCH-SEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Created Tool Gateway trust boundary diagram illustrating validation gates and store bindings."
---

# Tool Gateway Trust Boundary Diagram

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-INT-GW-001` |
| **Purpose** | Depict trust boundaries and security checks enforced by `ControlledToolGateway` before touching backing stores. |
| **Scope & Owner** | `plane` (`intelligence-plane`) / `security-architect` |
| **Authoritative Source** | [tool-gateway-architecture.md](../tool-gateway-architecture.md) (`INT-ARCH-GW-001`) |
| **Notation** | Mermaid `flowchart TB` (Trust Boundary DFD) |
| **Version & Status** | `2.0.0` / `DRAFT` (`PARTIALLY_IMPLEMENTED`) |

```mermaid
flowchart TB
    subgraph Z1["Untrusted / Planner Zone"]
        PLAN["Planner Tool Request (tool_name, params)"]
    end

    subgraph Z2["ControlledToolGateway Firewall"]
        WL["1. Whitelist Check (ApprovedAgentTool)"]
        RBAC["2. Permission Check (required_permission in granted_permissions)"]
        CAP["3. Row/Period Cap Check (limit <= max_rows_or_periods)"]
        TO["4. Timeout Guard (asyncio.wait_for)"]
        PROV["5. Provenance & In-Memory Audit Log"]
    end

    subgraph Z3["Backing Store Handlers (runtime.py)"]
        RO["Read-Only Handlers (Tools 1-7, 9 -> Redis/ClickHouse)"]
        ANOM["Stateful Side-Effect (Tool 8: detect_anomalies -> detected_anomalies)"]
        RW["Write Handler (Tool 10: generate_analysis_report -> runtime.reports)"]
    end

    PLAN -->|"tool_name, params, hardcoded perms"| WL
    WL -->|"Valid enum"| RBAC
    RBAC -->|"Authorized"| CAP
    CAP -->|"Within bounds"| TO
    TO -->|"Read tools"| RO
    TO -->|"Anomaly tool"| ANOM
    TO -->|"Report tool"| RW
    RO -->|"result_data"| PROV
    ANOM -->|"result_data"| PROV
    RW -->|"result_data"| PROV
```

**Legend**: Boxes represent trust zones (`Z1` Planner, `Z2` Gateway Firewall, `Z3` Injected Store Handlers). `Z2` enforces whitelist, RBAC, row cap, and timeout before any handler runs.

