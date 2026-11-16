---
doc_id: DIAG-APP-OPS-FLOW-001
title: "Cross-Functional Swimlane Flow: Operator Telemetry & Control Trigger"
doc_type: diagram
plane: application-plane
scope_level: capability
domain: platform-operations-and-control
capability_id: CAP-APP-OPS-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: business-analyst
accountable_role: devops-sre
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/application-plane/domains/platform-operations-and-control/capabilities/observability-control-and-gateway/use-cases/uc-ops-002-data-flow-dag-traces-and-simulation.md"
related_docs:
  - CAP-APP-OPS-UC-002
  - CAP-APP-OPS-UC-003
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Rendered Mermaid Swimlane-style Flowchart (explicitly non-BPMN 2.0.2 XML) across SPA Operator, Gateway Router, and Runtime Container."
---

# Cross-Functional Swimlane Flow: Operator Telemetry & Control Trigger

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-APP-OPS-FLOW-001` |
| **Title & Purpose** | Swimlane-Style Control Execution (`demo/emit`, `live/probe`, `data-platform/v01/run`) |
| **Owner Role & Scope** | `business-analyst / CAP-APP-OPS-001` |
| **Authoritative Source** | [uc-ops-002-data-flow-dag-traces-and-simulation.md](../use-cases/uc-ops-002-data-flow-dag-traces-and-simulation.md) (`CAP-APP-OPS-UC-002`) |
| **Notation** | `Mermaid Swimlane-style Flowchart (NOT formal BPMN 2.0.2 XML)` |
| **Version & Status** | `2.0.0 — DRAFT` |

## 2. Diagram

```mermaid
flowchart TD
    subgraph lane_op["Lane 1: Operator UI (#/data-flow)"]
        op_act(["Click Trigger (emit_batch / live_probe / run_v01)"])
        op_view["Update DAG & Trace Table"]
    end

    subgraph lane_gw["Lane 2: FastAPI Ops Gateway"]
        gw_auth{"RBAC Check? (MISSING AS-IS)"}
        gw_exec["Invoke Gateway Handler"]
    end

    subgraph lane_rt["Lane 3: PlatformRuntimeContainer & TraceRegistry"]
        rt_run["Execute Data Plane Stage(s)"]
        rt_pub["Push EventLifecycleTrace to WS/SSE Queues"]
    end

    op_act --> gw_auth
    gw_auth -.->|"AS-IS: Unauthenticated Pass-Through"| gw_exec
    gw_exec --> rt_run --> rt_pub --> op_view
```

## 3. Legend

- **Notation Disclosure**: Uses Mermaid `flowchart TD` with subgraph lanes (`Swimlane-style Flowchart`); not OMG BPMN 2.0.2 XML.
