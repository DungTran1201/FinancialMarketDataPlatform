---
doc_id: DIAG-DP-STR2-TM-001
title: "Diagram: Streaming Projections Trust Boundaries"
doc_type: diagram
plane: data-plane
scope_level: capability
domain: event-streaming
capability_id: CAP-DP-STR-002
status: IN_REVIEW
implementation_status: SIMULATED
version: "2.0.0"
owner_role: security-architect
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/data-plane/domains/event-streaming/capabilities/realtime-hot-state-and-olap-projection/security/threat-model.md"
related_docs:
  - CAP-DP-STR2-TM-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Derived trust boundary view for hot/OLAP state mutation and role segregation."
---

# Diagram: Streaming Projections Trust Boundaries

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-DP-STR2-TM-001` |
| **Title & Purpose** | Shows trust boundaries around eviction/anomaly triggers and hot/OLAP dict stores |
| **Owner Role & Scope** | `security-architect / CAP-DP-STR-002` |
| **Authoritative Source** | [threat-model.md](threat-model.md) (`CAP-DP-STR2-TM-001`) |
| **Notation** | `Mermaid flowchart TB` (`Trust Boundary DFD`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram `[REQUIRED]`

```mermaid
flowchart TB
    caller["HTTP Caller / Operator"]

    subgraph tb_api["Trust Boundary 1: App Control Routes [GAP: SEC-AUDIT-003]"]
        ep_evict["POST /market/evict/{symbol} & /anomalies/evaluate"]
    end

    subgraph tb_dp["Trust Boundary 2: Consumers & Stores"]
        hot["HotStateProjector (Monotonic Guard)"]
        olap["ClickHouseBatchSink (Target CH Roles: writer vs reader vs agent_ro)"]
    end

    caller -->|"THR-STR2-001: Unauth Mutation"| ep_evict
    ep_evict -->|"Evict / Evaluate"| hot
    hot -.->|"Target Isolated Read Role"| olap
```

## 3. Legend `[REQUIRED]`

- **Subgraphs**: Privilege zones separating public/gateway triggers from Data Plane consumer stores.
