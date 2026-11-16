---
doc_id: DP-DIAG-C4-001
title: "Diagram: Data Plane C4 Container Topology"
doc_type: diagram
plane: data-plane
scope_level: plane
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: data-architect
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/data-plane/architecture/data-plane-architecture.md"
related_docs:
  - DP-ARCH-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Derived Data Plane C4 Container diagram separating in-process simulation engines from Compose target services."
---

# Diagram: Data Plane C4 Container Topology

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-DP-C4-001` |
| **Title & Purpose** | C4 Level 2 Container view across Data Plane ingestion, streaming, medallion processing, and storage tiers |
| **C4 Level** | Level 2 — Container |
| **Owner Role & Scope** | `data-architect / data-plane` |
| **Authoritative Source** | [data-plane-architecture.md](../data-plane-architecture.md) (`DP-ARCH-001`) |
| **Notation** | `Mermaid flowchart TB` (`C4 Model`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram `[REQUIRED]`

```mermaid
flowchart TB
    ext_rest["Binance REST / Embedded ASGI Simulator"]
    ext_ws["Binance WebSocket (TARGET - Unimplemented in src/)"]

    subgraph dp_scope["Data Plane Engines (In-Process in backend-api AS-IS)"]
        ing["Ingestion Engine (Normalizer + HistoricalRestBackfillWorker + WebSocketStreamCollector)"]
        broker["PartitionedEventStreamingBroker (6 Topics + DLQ) [In-Memory Sim]"]
        hot["HotStateProjector [Dicts AS-IS / Redis Target]"]
        olap["ClickHouseBatchSink + AnomalyDetector [Dicts AS-IS / CH Target]"]
        lak["BronzeParquetArchiver -> SilverMergeEngine -> DQ Gates -> GoldMartEngine"]
        store_wm[("SQLite .local_storage/control_watermarks.db (AS-IS)")]
        store_lh[("Local Disk .local_lakehouse/ Parquet + Iceberg JSON")]
    end

    ext_rest -->|"JSON Klines / ExchangeInfo"| ing
    ext_ws -.->|"WSS Frames (TARGET)"| ing
    ing -->|"SQLite WAL"| store_wm
    ing -->|"EventEnvelopeV1 / DLQ"| broker
    broker -->|"cg.hot.redis.v1"| hot
    broker -->|"cg.analytics.clickhouse.v1"| olap
    broker -->|"cg.lakehouse.bronze.v1"| lak
    lak -->|"Atomic ZSTD Parquet"| store_lh
```

## 3. Legend `[REQUIRED]`

- **Solid Arrows (`-->`)**: Active in-process execution & local persistence paths verified in `DataPlatformV01Pipeline` and `PlatformRuntimeContainer`.
- **Dashed Arrows (`-.->`)**: `TARGET` external exchange WebSocket stream not yet wired in `src/`.
