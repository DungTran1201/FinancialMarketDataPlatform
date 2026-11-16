---
doc_id: DIAG-DP-STR1-DFD-001
title: "Diagram: Kafka Event Bus Topic Routing & Consumer Fan-Out"
doc_type: diagram
plane: data-plane
scope_level: capability
domain: event-streaming
capability_id: CAP-DP-STR-001
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
    - "docs/data-plane/domains/event-streaming/capabilities/kafka-event-bus-and-dlq/design/component-design.md"
related_docs:
  - CAP-DP-STR1-COMP-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Derived streaming DFD across 6 topics and 4 consumer groups."
---

# Diagram: Kafka Event Bus Topic Routing & Consumer Fan-Out

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-DP-STR1-DFD-001` |
| **Title & Purpose** | Illustrates partition routing across all 6 canonical topics, 4 consumer groups, and manual offset commits |
| **Owner Role & Scope** | `data-architect / CAP-DP-STR-001` |
| **Authoritative Source** | [component-design.md](component-design.md) (`CAP-DP-STR1-COMP-001`) |
| **Notation** | `Mermaid flowchart LR` (`DFD`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram `[REQUIRED]`

```mermaid
flowchart LR
    prod["Producers (Normalizer / Backfill / AnomalyDetector)"]
    router{"resolve_topic_for_event (Partition % 6)"}
    t_raw[("market.raw.{trades,klines,tickers,orderbook}.v1")]
    t_anom[("market.anomalies.v1")]
    t_dlq[("market.dlq.v1 (Partition 0)")]
    cg_hot["cg.hot.redis.v1 (HotStateProjector)"]
    cg_ch["cg.analytics.clickhouse.v1 (ClickHouseBatchSink)"]
    cg_brz["cg.lakehouse.bronze.v1 (BronzeParquetArchiver)"]
    cg_agt["cg.anomaly.detector.v1 / agent-worker (TARGET)"]

    prod -->|"EventEnvelopeV1"| router
    prod -.->|"publish_dlq()"| t_dlq
    router -->|"Market Events"| t_raw
    router -->|"Anomaly Alert"| t_anom
    t_raw -->|"poll_topic + manual commit"| cg_hot
    t_raw -->|"poll_topic + manual commit"| cg_ch
    t_raw -->|"poll_topic + manual commit"| cg_brz
    t_anom -.->|"TARGET Consume"| cg_agt
```

## 3. Legend `[REQUIRED]`

- **Solid Arrows (`-->`)**: In-process broker publish & manual-commit poll channels.
- **Dashed Arrows (`-.->`)**: DLQ quarantine path and unimplemented `agent-worker` anomaly consumer loop.
