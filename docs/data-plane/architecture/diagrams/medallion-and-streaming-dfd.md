---
doc_id: DP-DIAG-DFD-001
title: "Diagram: Streaming & Medallion 12-Stage Data Flow (DFD)"
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
    - "src/lakehouse/orchestration/pipeline.py"
related_docs:
  - DP-ARCH-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Derived end-to-end streaming and medallion lineage DFD matching DataPlatformV01Pipeline Stage 8-before-7 execution order."
---

# Diagram: Streaming & Medallion 12-Stage Data Flow (DFD)

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-DP-DFD-001` |
| **Title & Purpose** | Depicts normalized event streaming fan-out, DLQ quarantine, Stage 8 blocking DQ gate, and Stage 7/9 medallion sinks |
| **Owner Role & Scope** | `data-architect / data-plane` |
| **Authoritative Source** | [data-plane-architecture.md](../data-plane-architecture.md) (`DP-ARCH-001`) |
| **Notation** | `Mermaid flowchart LR` (`DFD`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram `[REQUIRED]`

```mermaid
flowchart LR
    src_in["Raw Exchange Frame / REST Bar"]
    proc_norm["Stage 2-3: BinancePayloadNormalizer"]
    bus_kaf["Stage 4: Kafka Broker Topics (6 Topics)"]
    sink_dlq[("market.dlq.v1 Quarantine")]
    sink_hot[("HotStateProjector (Redis Sim)")]
    sink_olap[("ClickHouseBatchSink + AnomalyDetector")]
    proc_brz["Stage 5: BronzeParquetArchiver"]
    proc_slv["Stage 6: SilverLakehouseMergeEngine + Stage 9 Compact"]
    gate_dq{"Stage 8: DataQualityGateEngine (Runs Before Gold)"}
    sink_gold[("Stage 7: GoldLayerMartEngine (3 Marts)")]
    reg_lin["Stage 11-12: Metrics, t0-t9 Traces & Lineage"]

    src_in -->|"Raw Dict"| proc_norm
    proc_norm -->|"Valid EventEnvelopeV1"| bus_kaf
    proc_norm -.->|"Invalid Payload (DeadLetterEnvelopeV1)"| sink_dlq
    bus_kaf -->|"cg.hot.redis.v1"| sink_hot
    bus_kaf -->|"cg.analytics.clickhouse.v1"| sink_olap
    bus_kaf -->|"cg.lakehouse.bronze.v1"| proc_brz
    proc_brz -->|"Bronze ZSTD Parquet"| proc_slv
    proc_slv -->|"Silver Rows"| gate_dq
    gate_dq -->|"DQ Passed (can_promote_to_gold=True)"| sink_gold
    gate_dq -.->|"DQ Failed (Blocked Promotion)"| reg_lin
    sink_hot -->|"Serving Verified"| reg_lin
    sink_gold -->|"Gold Counts + Lineage"| reg_lin
```

## 3. Legend `[REQUIRED]`

- **Solid Arrows (`-->`)**: Primary nominal data pipeline path (`Stage 1..12`). Note Stage 8 (`DataQualityGateEngine`) validates Silver outputs immediately prior to Stage 7 (`GoldLayerMartEngine`).
- **Dashed Arrows (`-.->`)**: Error quarantine (`market.dlq.v1`) and blocked Gold promotion gate failure path.
