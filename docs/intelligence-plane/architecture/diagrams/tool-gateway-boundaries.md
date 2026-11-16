---
doc_id: DIAG-INT-GW-001
title: "Tool Gateway Trust Boundary & Guardrail Pipeline Diagram"
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
    - "docs/intelligence-plane/architecture/agent-security-architecture.md"
related_docs:
  - INT-ARCH-ROOT-001
  - INT-ARCH-GW-001
  - INT-ARCH-SEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Rendered ControlledToolGateway validation gates, trust boundaries, and AS-IS side-effect/fallback paths."
---

# Tool Gateway Trust Boundary & Guardrail Pipeline Diagram

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-INT-GW-001` |
| **Title & Purpose** | ControlledToolGateway Security Gates, Timeout Bounds, Provenance Wrapping & Side-Effect Paths |
| **Owner Role & Scope** | `security-architect / intelligence-plane` |
| **Authoritative Source** | [tool-gateway-architecture.md](../tool-gateway-architecture.md) (`INT-ARCH-GW-001`) |
| **Notation** | `Mermaid flowchart TB` (`Trust Boundary Flow`) |
| **Version & Status** | `2.0.0 — DRAFT` |

## 2. Diagram

```mermaid
flowchart TB
    caller["Planner / Orchestrator (Hardcoded _agent_permissions AS-IS)"]

    subgraph tb_gateway["Trust Boundary TB-INT-2: ControlledToolGateway.execute_tool()"]
        g_wl{"1. Whitelist Check (ApprovedAgentTool)"}
        g_rbac{"2. RBAC Check (required_permission)"}
        g_lim{"3. Row/Period Cap Check (<= max_rows_or_periods)"}
        g_reg{"4. Handler Registered?"}
        g_to["5. asyncio.wait_for(handler, timeout_seconds)"]
        g_stub["Return synthetic stub_ok (GAP: Does Not Fail Closed)"]
        g_prov["6. Attach ToolProvenanceMetadata (UUIDv4) & Append _audit_log"]
    end

    subgraph tb_stores["Trust Boundary TB-INT-3: Injected Runtime Handlers (AS-IS In-Memory)"]
        ro_mem["Read Tools 1..7, 9: HotStateProjector / ClickHouseBatchSink"]
        mut_anom["Tool 8 detect_anomalies: Mutates _cooldown_registry & detected_anomalies"]
        mut_rep["Tool 10 generate_analysis_report: Writes runtime.reports[run_id]"]
    end

    err_unauth(["Raise UnauthorizedToolAccessError"])
    err_limit(["Raise ToolQueryLimitExceededError"])
    err_to(["Raise Unhandled asyncio.TimeoutError"])

    caller -->|"tool_name, params, granted_permissions"| g_wl
    g_wl -->|"Invalid Tool Name"| err_unauth
    g_wl -->|"Whitelisted"| g_rbac
    g_rbac -->|"Missing Scope"| err_unauth
    g_rbac -->|"Authorized"| g_lim
    g_lim -->|"limit > cap"| err_limit
    g_lim -->|"Within Cap (Note: <=0 Unchecked)"| g_reg
    g_reg -->|"Handler Present"| g_to
    g_reg -.->|"Handler None"| g_stub --> g_prov
    g_to -.->|"Timeout Exceeded"| err_to
    g_to -->|"Read Tools"| ro_mem --> g_prov
    g_to -->|"Anomaly Tool"| mut_anom --> g_prov
    g_to -->|"Report Tool"| mut_rep --> g_prov
```

## 3. Legend

- **Diamond (`{...}`)**: Sequential deterministic policy gate inside `src/intelligence/tools/gateway.py`.
- **Rounded Pill (`([...])`)**: Unhandled exception propagation paths (not currently logged into `ControlledToolGateway._audit_log`).
- **Dashed Arrows (`-.->`)**: Fallback stub path when no handler is registered or timeout failure branch.

