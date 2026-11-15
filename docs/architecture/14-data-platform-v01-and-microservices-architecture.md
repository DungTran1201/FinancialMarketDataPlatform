# 14 — End-to-End Data Platform v0.1 & Domain Microservices Architecture

## 1. Purpose & Architectural Scope

This document specifies the production-grade **End-to-End Data Platform v0.1** (`Plane A`) and the **Domain Microservices Architecture** (`ADR-007`) implemented on branch `arch/microservices`. It eliminates all transport/storage mocks from the Data Plane and establishes independently deployable microservice runtimes across Planes A, B, and C.

See also:
- [ADR-007: Zero-Mock End-to-End Data Platform v0.1 & Domain Microservices Decomposition](adr/ADR-007-microservices-and-data-platform-v01.md)
- [Diagram 08: End-to-End Data Platform v0.1 12-Stage Pipeline](../diagrams/data-platform/08-end-to-end-data-platform-v01-pipeline.md)
- [Diagram 09: Watermark Backfill & Iceberg Compaction Lifecycle](../diagrams/data-platform/09-watermark-backfill-and-compaction-lifecycle.md)
- [Diagram 17: Microservices Decomposition Topology](../diagrams/architecture/17-microservices-decomposition-topology.md)
- [Diagram 18: Microservices Container Deployment](../diagrams/deployment/18-microservices-container-deployment.md)

---

## 2. Zero-Mock Data Platform v0.1 — 12-Stage Production Specification

| Stage | Stage Name | Production Engine / Module | Persistence / Protocol Artifact |
|---|---|---|---|
| **Stage 1** | **Data Source Discovery** | `ProductionExchangeHistoricalCollector.discover_exchange_metadata` (`src/ingestion/providers/binance/rest_client.py`) | Real HTTP `GET /api/v3/exchangeInfo` validating `TRADING` status, `tick_size`, `lot_size`, and `min_notional`. |
| **Stage 2** | **Real-Time WS & Historical REST Ingestion** | `WebSocketStreamCollector`, `HistoricalRestBackfillWorker`, `TokenBucketRateLimiter`, `SequenceAndGapDetector`, `IngestionWatermarkStore` | Jittered reconnect backoff, `TokenBucketRateLimiter` (`X-MBX-USED-WEIGHT-1M`), gap detection, and SQLite/PostgreSQL watermarks. *(Note: standalone CLI entrypoints `ws_collector.py` and `rest_backfill.py` currently run config-logging stubs; see `PROP-APP-002`.)* |
| **Stage 3** | **Validation, Normalization & DLQ** | `BinancePayloadNormalizer` (`src/ingestion/providers/binance/normalizer.py`) | Canonical `EventEnvelopeV1` with deterministic UUIDv5 `event_id`, `Decimal` parsing, and `DeadLetterEnvelopeV1` routing to `market.dlq.v1`. |
| **Stage 4** | **Partitioned Event Streaming** | `PartitionedEventStreamingBroker` (`src/streaming/infrastructure/kafka_broker.py`) | 6-partition deterministic symbol hashing (`hash("{provider}:{symbol}") % 6`) and per-consumer-group committed offset tracking. |
| **Stage 5** | **Bronze Layer Archival** | `BronzeParquetArchiver` (`src/lakehouse/bronze/archiver.py`) | Immutable ZSTD-compressed Apache Parquet files partitioned locally under `.local_lakehouse` (`bronze/{event_type}/provider={p}/ingestion_date={YYYY-MM-DD}`; MinIO S3 bucket target `lakehouse-bronze` provisioned). |
| **Stage 6** | **Silver Standardization & Hot/OLAP Sinks** | `SilverLakehouseMergeEngine` (`src/lakehouse/silver/merge_engine.py`), `HotStateProjector`, `ClickHouseBatchSink` | Natural-key deduplicated `silver.market_klines` and `silver.market_trades` Parquet tables, monotonic Redis hot cache (`BR-003`), and ClickHouse `ReplacingMergeTree` tables. |
| **Stage 7** | **Gold Layer Analytical Marts** | `GoldLayerMartEngine` (`src/lakehouse/gold/mart_engine.py`) | Curated ZSTD Parquet analytical marts: `gold.fct_daily_market_summary`, `gold.fct_realized_volatility`, and `gold.fct_orderbook_liquidity`. |
| **Stage 8** | **Automated Data Quality Gates** | `DataQualityGateEngine` (`src/lakehouse/quality/gates.py`) | Pre-promotion evaluation of `DQ-KLINE-001`..`005` and `DQ-TRADE-001`..`003` (OHLC invariants, non-negative volume, natural-key uniqueness, quote volume parity, positive timestamps/prices). |
| **Stage 9** | **Storage Optimization & Compaction** | `SilverLakehouseMergeEngine.compact_and_snapshot_iceberg_table` | Small-file Parquet compaction sorted by natural key and Apache Iceberg v2 snapshot metadata manifest (`metadata/v{snapshot_id}.metadata.json`). |
| **Stage 10** | **Data Serving & Consumption** | `HotProjectorMarketAdapter`, `ClickHouseSinkFallbackAdapter`, `ControlledToolGateway` | Sub-50ms hot price serving with automatic ClickHouse OLAP fallback (`AC-002`) and read-only Agent tool bindings (`BR-004`). |
| **Stage 11** | **Data Observability & SLIs** | `DataObservabilityMetricsCollector` (`src/shared/observability/metrics.py`) | OpenMetrics / Prometheus exposition (all 10 metrics: `fmdp_ingested_events_total`, `fmdp_dlq_events_total`, `fmdp_consumer_lag_records`, `fmdp_hot_out_of_order_dropped_total`, `fmdp_dq_validation_runs_total`, `fmdp_gold_mart_rows_total`, `fmdp_serving_requests_total`, `fmdp_stage_events_total`, `fmdp_stage_processing_duration_ms`, `fmdp_end_to_end_latency_ms`). |
| **Stage 12** | **Governance, Lineage & Retention** | `DataLineageGovernanceRegistry` (`src/lakehouse/catalog/lineage.py`) | End-to-end dataset catalog (12 canonical datasets) and directed lineage graph across all transformation stages. |

---

## 3. Domain Microservices Decomposition (`src/serving/api/services/` & `gateway/`)

| Service ID | Runtime Module | Internal Port | Bounded Contexts Owned | Primary Backing Stores | Target P95 SLA |
|---|---|---|---|---|---|
| **`svc-api-gateway`** | `src/serving/api/gateway/service.py` | `8000` | Edge Gateway, WAF, Rate Limiter, Service Registry | `SlidingWindowRateLimiter` (Redis target) | $\le 25\text{ ms}$ |
| **`svc-market-hot`** | `src/serving/api/services/market.py` | `8001` | `market` (`prices`, `snapshots`, `orderbook`; `/ws/v1/market/stream` `PLANNED`) | Redis Hot Cache + ClickHouse Fallback | $\le 50\text{ ms}$ |
| **`svc-historical-backfill`** | `src/serving/api/services/historical.py` | `8002` | `historical` (`klines`, `trades`, `backfill-jobs`) | ClickHouse OLAP + Watermark DB | $\le 500\text{ ms}$ |
| **`svc-analytics-quant`** | `src/serving/api/services/analytics.py` | `8003` | `analytics` (`statistics`, `correlations`, `anomalies`) | ClickHouse Materialized Rollups | $\le 400\text{ ms}$ |
| **`svc-catalog-governance`** | `src/serving/api/services/catalog.py` | `8004` | `catalog`, `platform_config` | PostgreSQL Metadata + MinIO/Iceberg | $\le 150\text{ ms}$ |
| **`svc-iam-security`** | `src/serving/api/services/iam.py` | `8005` | `iam` (`token`, `verify`, `revoke`, `cipher`) | PostgreSQL IAM + Redis Revocation Set | $\le 80\text{ ms}$ |
| **`svc-intelligence-agent`** | `src/serving/api/services/intelligence.py` | `8006` | `agent_api`, `reporting` | Controlled Tool Gateway + Report Store | $\le 2,500\text{ ms}$ |
| **`svc-data-plane-v01`** | `src/serving/api/services/data_plane.py` | `8007` | End-to-End Data Platform v0.1 (`Stages 1..12`) | Kafka + Bronze/Silver/Gold Lakehouse | $\le 1,000\text{ ms}$ |

---

## 4. Data Platform v0.1 & Microservices API Contracts

| Endpoint ID | Method & Path | Owning Microservice | Description |
|---|---|---|---|
| **`API-011`** | `POST /api/v1/data-platform/v01/run` | `svc-data-plane-v01` | Executes all 12 stages of Data Platform v0.1 end-to-end and returns `DataPlatformV01ExecutionReport`. |
| **`API-012`** | `GET /api/v1/data-platform/v01/gold/{mart_name}` | `svc-data-plane-v01` | Queries materialized Gold marts (`fct_daily_market_summary`, `fct_realized_volatility`, `fct_orderbook_liquidity`). |
| **`API-013`** | `POST /api/v1/data-platform/v01/compaction` | `svc-data-plane-v01` | Triggers Stage 9 small-file Parquet compaction and writes Apache Iceberg v2 snapshot metadata. |
| **`API-014`** | `GET /api/v1/data-platform/v01/lineage` | `svc-data-plane-v01` | Returns Stage 12 dataset ownership catalog and directed lineage graph. |
| **`API-015`** | `GET /api/v1/microservices/topology` | `svc-api-gateway` | Returns the 8-service topology manifest with AES-CTR+HMAC masked internal bindings. |

