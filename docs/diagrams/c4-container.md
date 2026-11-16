---
doc_id: "DIAG-C4-CNT-001"
title: "C4 Level 2 — Container & Process Isolation Architecture"
version: "1.0.0"
status: "IN_REVIEW"
implementation_status: "PLANNED"
owner: "Principal Software Architect"
purpose: "Visualizes the three isolated runtime units (Realtime Core, NATS JetStream Container, Batch/Quant Worker) enforcing 8 GB resource discipline."
scope: "Hybrid Native Windows + Containerized NATS topology (DEC-P0-002)."
dependencies:
  - "docs/architecture/system-architecture-document.md"
  - "docs/architecture/resource-budget.md"
references:
  - "docs/architecture/decisions/adr-0001-three-plane-hybrid-runtime.md"
assumptions:
  - "Runtime Units B and C run as distinct OS processes on Python 3.12 during PoC and initial build."
open_issues:
  - "Empirical RSS breakdown per unit recorded in WI-P2-003."
review_criteria:
  - "Demonstrates strict separation of async hot path from DuckDB/ML analytical bursts"
---

# C4 Level 2 — Container & Process Boundaries

```mermaid
flowchart TB
    EX["Binance & OKX<br/>WSS + REST Endpoints"]
    SPA["Browser SPA<br/>(Vanilla TS + Canvas Charts<br/>15 Analytical Modules)"]

    subgraph UNIT_B["Unit B: fmdp-realtime-api (Native Python 3.12 asyncio / <= 450 MB)"]
        CONN["Exchange Connectors & Canonical Normalizers"]
        PROC["Event-Time Bar, L2 Book Sync & OFI/CVD Engine"]
        HOT["Bounded In-Process Hot LRU Cache"]
        API["FastAPI Gateway (Auth/RBAC + Conflated WS/SSE)"]
        CONN --> PROC --> HOT --> API
    end

    subgraph UNIT_A["Unit A: Docker Container (<= 256 MB cap)"]
        NATS["NATS JetStream<br/>127.0.0.1:4222 (FileStore WAL)"]
    end

    subgraph UNIT_C["Unit C: fmdp-batch-quant-worker (Isolated Python Process / <= 1024 MB)"]
        ARCH["Single-Writer Parquet Micro-Batcher + Compactor"]
        SQLW["Centralized Async SQLite WAL Writer"]
        DUCK["Bounded DuckDB + Polars Query Engine"]
        QUANT["Dataset Builder + Walk-Forward Trainer + Online Scorer"]
    end

    DISK_SQL[("SQLite WAL DB<br/>Catalog, Watermarks, Jobs,<br/>Models, Forecasts")]
    DISK_PQ[("Partitioned Parquet (ZSTD)<br/>Bronze / Silver / Gold / Features")]

    EX -->|Async WSS / Rate-Limited REST| CONN
    CONN -->|Publish w/ PubAck| NATS
    CONN -.->|Startup Reload & Checkpoints| SQLW
    NATS -->|Durable Pull Consumer| PROC
    NATS -->|Durable Pull Consumer| ARCH
    NATS -.->|Invalid Frames| NATS

    ARCH -->|Atomic os.replace| DISK_PQ
    SQLW -->|Serialized Transactions| DISK_SQL
    DUCK <-->|Read-Only Parquet Scans| DISK_PQ
    QUANT -->|Read Datasets & Run Evals| DUCK
    QUANT <-->|Log Experiments & Forecasts| SQLW
    QUANT -.->|Push Forecast Events| NATS

    API -.->|Delegated Analytical Query / Train Trigger| UNIT_C
    SPA <-->|HTTPS + Conflated WSS/SSE| API
```

## Legend & Diagram Metadata

- **Solid Arrows (`-->`)**: Primary real-time ingestion, JetStream delivery, and storage write paths.
- **Dashed Arrows (`-.->`)**: Metadata checkpoints, DLQ routing, and isolated worker delegation.
- **Authoritative Spec**: [system-architecture-document.md](../architecture/system-architecture-document.md).

