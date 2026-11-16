---
doc_id: DIAG-DP-STR2-DFD-001
title: "Diagram: Streaming Projections (Hot Cache, OLAP & Anomaly Detection)"
doc_type: diagram
plane: data-plane
scope_level: capability
domain: event-streaming
capability_id: CAP-DP-STR-002
status: IN_REVIEW
implementation_status: SIMULATED
version: "2.0.0"
owner_role: data-architect
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/data-plane/domains/event-streaming/capabilities/realtime-hot-state-and-olap-projection/design/component-design.md"
related_docs:
  - CAP-DP-STR2-COMP-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Derived DFD depicting hot monotonic filter, CH batch flush/rollup, and anomaly cooldown branch."
---

# Diagram: Streaming Projections Data Flow

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-DP-STR2-DFD-001` |
| **Title & Purpose** | Shows streaming fan-out into HotStateProjector, ClickHouseBatchSink, and StatisticalAnomalyDetector |
| **Owner Role & Scope** | `data-architect / CAP-DP-STR-002` |
| **Authoritative Source** | [component-design.md](component-design.md) (`CAP-DP-STR2-COMP-001`) |
| **Notation** | `Mermaid flowchart LR` (`DFD`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram `[REQUIRED]`

```mermaid
flowchart LR
    in_bus[("market.raw.*.v1 (EventEnvelopeV1)")]
    guard_ts{"incoming_ts >= current_ts?"}
    hot_dict[("HotStateProjector Python Dicts (market:v1:*)")]
    red_lua[("Redis 7 Lua (TARGET - Unused _redis_client)")]
    ch_buf["MicroBatchBuffer (max_rows=5000)"]
    ch_dict[("ClickHouseBatchSink Python Tables + Rollups")]
    anom_eval{"|z_score| >= 2.5 AND Cooldown Expired?"}
    anom_out[("market.anomalies.v1")]

    in_bus -->|"cg.hot.redis.v1"| guard_ts
    guard_ts -->|"True"| hot_dict
    hot_dict -.->|"price_key only if _redis_client"| red_lua
    in_bus -->|"cg.analytics.clickhouse.v1"| ch_buf
    ch_buf -->|"flush() ReplacingMergeTree Sim"| ch_dict
    ch_dict -->|"Series (N>=5)"| anom_eval
    anom_eval -->|"True (Set 900s Cooldown)"| anom_out
```

## 3. Legend `[REQUIRED]`

- **Solid Arrows (`-->`)**: Active in-process simulation data flow.
- **Dashed Arrows (`-.->`)**: Optional un-wired live Redis Lua bridge.
