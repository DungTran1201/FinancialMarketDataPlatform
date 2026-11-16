---
doc_id: DP-ARCH-001
title: "Data Plane Architecture Description"
doc_type: architecture
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
  is_authoritative: true
  authoritative_source:
    - "src/ingestion/"
    - "src/streaming/"
    - "src/lakehouse/"
related_docs:
  - DP-ROOT-001
  - DP-DIAG-C4-001
  - DP-DIAG-DFD-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Documented Data Plane layer decomposition, streaming vs medallion paths, and AS-IS vs TARGET infrastructure boundaries."
---

# Data Plane Architecture Description

Derived visual views: [data-plane-c4-container.md](diagrams/data-plane-c4-container.md) (`DIAG-DP-C4-001`) and [medallion-and-streaming-dfd.md](diagrams/medallion-and-streaming-dfd.md) (`DIAG-DP-DFD-001`).

## 1. Architectural Scope, Goals & Constraints `[REQUIRED]`

- **Scope**: External exchange ingestion (`src/ingestion/`), partitioned event bus & real-time consumers (`src/streaming/`), medallion Bronze/Silver/Gold storage, DQ gates, lineage, and orchestration (`src/lakehouse/`).
- **Goals**: Deterministic financial precision (`Decimal`), idempotent replay without duplicate candles/trades, isolation between low-latency hot reads and batch medallion compaction, and auditable provenance/lineage.
- **Constraints**: Clean Architecture domain purity (`ingestion/domain/`), AST package DAG isolation (zero imports of `src/serving/` or `src/intelligence/`).

## 2. Context & External Boundaries `[REQUIRED]`

- **Upstream**: Binance Spot REST (`https://api.binance.com/api/v3`, mocked via embedded ASGI app by default in `rest_client.py`) and target Binance WS (`wss://stream.binance.com:9443/ws`, unimplemented in `src/`), plus manual API ingestion (`POST /api/v1/market/ingest`, `POST /api/v1/historical/backfill-jobs`, `POST /api/v1/data-platform/v01/run`).
- **Downstream**: Application Plane (`PlatformRuntimeContainer` reads hot dicts/ClickHouse dicts/Parquet/lineage) and Intelligence Plane (`ControlledToolGateway` handlers).

## 3. Building Block & Dependency Structure `[REQUIRED]`

| Building Block | Responsibility | Upstream Dependencies | Downstream Consumers |
|---|---|---|---|
| **Ingestion (`src/ingestion/`)** | `BinancePayloadNormalizer`, `ProductionExchangeHistoricalCollector`, `WebSocketStreamCollector`, `HistoricalRestBackfillWorker`, `IngestionWatermarkStore` | `src/shared/`, Binance REST/frames | Kafka topics, DLQ, SQLite watermarks |
| **Streaming (`src/streaming/`)** | `PartitionedEventStreamingBroker` (6 topics), `HotStateProjector`, `ClickHouseBatchSink`, `StatisticalAnomalyDetector` | `src/shared/`, Ingestion events | Hot/OLAP APIs, `market.anomalies.v1`, Bronze archiver |
| **Lakehouse (`src/lakehouse/`)** | `BronzeParquetArchiver`, `SilverLakehouseMergeEngine`, `DataQualityGateEngine`, `GoldLayerMartEngine`, `DataLineageGovernanceRegistry`, `DataPlatformV01Pipeline` | `src/shared/`, Streaming broker & ingestion | `/data-platform/v01/*`, Catalog Service |

## 4. Runtime & Cross-Cutting Concepts

- **Hot vs. Historical Separation**: Real-time events fan out independently to three consumer groups: `cg.hot.redis.v1` (latest price/24h/orderbook), `cg.analytics.clickhouse.v1` (historical klines/trades/VWAP/volatility), and `cg.lakehouse.bronze.v1` (immutable Parquet archival).
- **Orchestration Order Note (`DataPlatformV01Pipeline`)**: `run_end_to_end_pipeline` executes Stage 8 (`DataQualityGateEngine`) **before** Stage 7 (`GoldLayerMartEngine`) so invalid Silver rows block Gold promotion (`can_promote_to_gold=False`).

## 5. Current Implementation (`AS-IS`) vs. Target Architecture (`TARGET`) `[REQUIRED]`

| Mechanism | `AS-IS` Reality (`7880c85`) | `TARGET` Design Intent | Migration Gap |
|---|---|---|---|
| **Worker Containers** | `ws_collector.py`, `rest_backfill.py`, `hot_redis.py`, `analytics_ch.py`, `bronze/consumer.py` log startup config and exit (`main()` stubs). Pipelines run in-process inside `backend-api`. | Always-on async worker loops consuming Kafka & Postgres watermarks continuously. | `GAP-DATA-001` |
| **Binance WS & REST** | No `websockets` loop in `src/`; REST collector defaults to embedded FastAPI ASGI simulator (`use_embedded_asgi_transport=True`, and lacks stored attribute). | Live WSS stream + TLS HTTP fallback (`use_embedded_asgi_transport=False`) controlled explicitly via settings. | `GAP-DATA-001` |
| **Broker & Sinks** | In-process `PartitionedEventStreamingBroker`, Python dict `HotStateProjector`, Python dict `ClickHouseBatchSink`, local `.local_storage/control_watermarks.db` SQLite, local `.local_lakehouse/` Parquet + custom Iceberg JSON manifests. | Confluent Kafka KRaft (`kafka:9092`), Redis 7 Lua, ClickHouse `ReplacingMergeTree` (`market_data.*`), PostgreSQL `ingestion_watermarks`, MinIO S3 (`lakehouse-*`), Iceberg REST, Spark/dbt execution. | `GAP-DATA-001`, `GAP-DATA-002` |

## 6. Decisions & Risks `[REQUIRED]`

- Linked ADR: [adr-0001-async-delivery-and-idempotent-keys.md](decisions/adr-0001-async-delivery-and-idempotent-keys.md).
- Linked Risk Register: [phase-2-risk-and-gap-register.md](../../governance/migration/phase-2-risk-and-gap-register.md) (`GAP-DATA-001`, `GAP-DATA-002`).
