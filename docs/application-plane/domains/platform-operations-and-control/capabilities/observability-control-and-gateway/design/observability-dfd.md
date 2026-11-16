---
doc_id: DIAG-APP-OPS-DFD-001
title: "Data Flow Diagram: Live Observability Telemetry & Control Flows"
doc_type: diagram
plane: application-plane
scope_level: capability
domain: platform-operations-and-control
capability_id: CAP-APP-OPS-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: devops-sre
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/application-plane/domains/platform-operations-and-control/capabilities/observability-control-and-gateway/design/component-design.md"
related_docs:
  - CAP-APP-OPS-COMP-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Rendered DFD for live event trace collection, TCP/Binance probing, SSE/WS fan-out, and v01 pipeline invocation."
---

# Data Flow Diagram: Live Observability Telemetry & Control Flows

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-APP-OPS-DFD-001` |
| **Title & Purpose** | Telemetry Collection, TCP Probe & SSE/WS Push Flows |
| **Owner Role & Scope** | `fullstack-engineer / CAP-APP-OPS-001` |
| **Authoritative Source** | [component-design.md](component-design.md) (`CAP-APP-OPS-COMP-001`) |
| **Notation** | `Mermaid flowchart LR` (`Yourdon/Gane-Sarson DFD`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram

```mermaid
flowchart LR
    ext_ui["Operator SPA (#/dashboard, #/data-flow)"]
    ext_prom["Prometheus Scraper (/metrics)"]
    proc_obs(("P1: Observability Router & SSE/WS"))
    proc_probe(("P2: Live TCP & Binance Probe"))
    proc_v01(("P3: DataPlatformV01 & Demo Trigger"))
    ds_tr[("trace_registry Ring Buffer")]
    ds_dp[("Data Plane Stores (Kafka/Redis/CH/LH)")]

    ext_ui -->|"GET /overview, /topology, /traces & WS"| proc_obs
    ds_tr -->|"EventLifecycleTrace stream"| proc_obs -->|"snapshot / trace / heartbeat"| ext_ui
    ext_ui -->|"POST /live/probe"| proc_probe -->|"TCP checks + optional Binance HTTPS"| ds_dp
    ext_ui -->|"POST /demo/emit or /v01/run"| proc_v01 --> ds_dp --> ds_tr
    proc_obs -->|"fmdp_* exposition text"| ext_prom
```

## 3. Legend

- **Circles (`((...))`)**: Telemetry and control execution processes.
- **Cylinders (`[(...)]`)**: In-memory ring buffers (`trace_registry`) and backing Data Plane stores.
