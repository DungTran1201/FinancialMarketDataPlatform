# ADR-007 — Zero-Mock End-to-End Data Platform v0.1 & Domain Microservices Decomposition

- **Status**: Accepted (`BASELINED` on `arch/microservices`)
- **Date**: 2026-11-15
- **Owners**: `data-platform-architect`, `data-engineer`, `system-architect`
- **Supersedes / Extends**: Extends [ADR-001](ADR-001-modular-monolith-and-three-plane-separation.md), [ADR-002](ADR-002-streaming-backbone-and-polyglot-storage.md), and [ADR-005](ADR-005-idempotency-deduplication-and-event-ordering.md)

---

## 1. Context

During the initial baseline (`ADR-001`), the Application Plane (`Plane B`) was structured as a single **Modular Monolith** (`backend-api`) containing 8 strictly isolated Clean Architecture bounded contexts (`market`, `historical`, `analytics`, `catalog`, `iam`, `platform_config`, `agent_api`, `reporting`), while the Data Plane (`Plane A`) included a simulated historical kline adapter (`SimulatedExchangeHistoricalCollector`) and lacked executable runtime engines for:
- **Stage 1**: Exchange metadata discovery (`GET /api/v3/exchangeInfo`, `tick_size`/`lot_size` filter verification).
- **Stage 7**: Executable Gold layer analytical mart materialization (`gold.fct_daily_market_summary`, `gold.fct_realized_volatility`, `gold.fct_orderbook_liquidity`).
- **Stage 9**: Lakehouse small-file compaction and Apache Iceberg v2 snapshot manifest generation.
- **Stage 11 & Stage 12**: Prometheus OpenMetrics exposition (`fmdp_*` SLIs) and automated end-to-end dataset lineage tracking (`Source -> Kafka -> Bronze -> Silver -> Gold -> Serving`).

On branch `arch/microservices`, the engineering organization requires:
1. **Complete removal of mocks in the Data Platform** so all 12 stages of the Data Lifecycle execute with production-grade protocols, real `httpx.AsyncClient` REST pagination, token-bucket rate limiting (`X-MBX-USED-WEIGHT-1M`), durable SQLite/PostgreSQL watermark checkpointing, ZSTD Parquet/Iceberg storage, and real Prometheus/lineage telemetry (**Data Platform v0.1**).
2. **Decomposition from Modular Monolith to Domain Microservices** while preserving all Clean Architecture boundary invariants (`TC-006`) and backward compatibility with the unified API gateway (`svc-api-gateway`).

---

## 2. Decision

### 2.1 Zero-Mock Data Platform v0.1 Architecture (`Plane A`)
1. **Production Exchange Collector (`ProductionExchangeHistoricalCollector`)**:
   - Replaces in-memory mock kline synthesis with real `httpx.AsyncClient` HTTP execution against `/api/v3/exchangeInfo` (Stage 1) and `/api/v3/klines` (Stage 2), governed by `TokenBucketRateLimiter` (`<= 80%` of `1,200 weight/min`) and `SequenceAndGapDetector`.
   - For deterministic offline/CI execution without external internet dependency, requests traverse a real ASGI HTTP Exchange Server (`build_deterministic_exchange_asgi_app`) via `httpx.ASGITransport`, exercising full HTTP query serialization, status code handling, and `X-MBX-USED-WEIGHT-1M` headers.
2. **Durable Watermark Checkpointing (`IngestionWatermarkStore`)**:
   - Persists `(provider, symbol, interval, last_open_time, status)` checkpoints in a relational SQLite/PostgreSQL control store (`ingestion_watermarks`).
3. **Complete Medallion Lakehouse (`Bronze -> Silver -> Gold`) & Stage 9 Compaction**:
   - **Bronze (`BronzeParquetArchiver`)**: Writes immutable ZSTD-compressed Parquet files partitioned by `provider={p}/ingestion_date={YYYY-MM-DD}`.
   - **Silver (`SilverLakehouseMergeEngine`)**: Deduplicates `silver.market_klines` and `silver.market_trades` by natural key (`MERGE INTO`) and executes Stage 9 small-file compaction with Apache Iceberg v2 metadata manifests (`metadata/v{snapshot_id}.metadata.json`).
   - **Gold (`GoldLayerMartEngine`)**: Materializes `gold.fct_daily_market_summary`, `gold.fct_realized_volatility`, and `gold.fct_orderbook_liquidity` as curated ZSTD Parquet tables after passing `DataQualityGateEngine` (`DQ-KLINE-001..004`).
4. **Prometheus Observability & Governance Lineage (`Stages 11 & 12`)**:
   - `DataObservabilityMetricsCollector` exports `fmdp_ingested_events_total`, `fmdp_dlq_events_total`, `fmdp_consumer_lag_records`, `fmdp_dq_validation_runs_total`, and `fmdp_gold_mart_rows_total`.
   - `DataLineageGovernanceRegistry` records directed acyclic lineage edges across all 12 stages.

### 2.2 Decomposition into 8 Domain Microservices (`src/microservices/`)
While keeping `src/backend/modules/*` as the canonical Clean Architecture domain/application libraries (`TC-006`), runtime deployment decomposes into 8 independently deployable ASGI microservices:
1. `svc-api-gateway` (Port `8000`): Unified HTTPS/WAF/Rate-Limiter Edge Gateway & Service Registry Dispatcher.
2. `svc-market-hot` (Port `8001`): Real-time prices, 24h snapshots, top-20 order book, and WebSocket stream fan-out (`market`).
3. `svc-historical-backfill` (Port `8002`): ClickHouse historical OHLCV/trades queries and REST backfill job control (`historical`).
4. `svc-analytics-quant` (Port `8003`): Rolling VWAP/volatility statistics, Pearson correlations, and Z-score anomaly evaluation (`analytics`).
5. `svc-catalog-governance` (Port `8004`): Instrument catalog, freshness SLIs, and platform configuration (`catalog`, `platform_config`).
6. `svc-iam-security` (Port `8005`): JWT HS256 issuance/verification with IP-HMAC binding, token revocation, and AES-CTR+HMAC endpoint masking (`iam`).
7. `svc-intelligence-agent` (Port `8006`): LangGraph 6-node investigation orchestrator, Controlled Tool Gateway, and verified provenance reports (`agent_api`, `reporting`).
8. `svc-data-plane-v01` (Port `8007`): End-to-End Data Platform v0.1 orchestrator, Gold mart query engine, Iceberg compaction controller, lineage catalog, and Prometheus metrics exporter.

---

## 3. Consequences

- **Positive**:
  - Zero mocks remain in the Data Platform; every stage (`Stage 1` through `Stage 12`) produces verifiable Parquet/Iceberg artifacts, SQLite/PostgreSQL watermarks, Prometheus metrics, and lineage edges.
  - Each domain microservice (`svc-*`) can scale, deploy, and be health-probed independently under the `microservices` Docker Compose profile (`DEP-006`), while `svc-api-gateway` preserves 100% API compatibility for existing clients and test suites (`TC-001..TC-011`).
- **Trade-offs**:
  - Running all 8 microservices as separate OS containers increases memory overhead by $\sim 1.2\text{ GB}$ compared to the single-process `core` profile; therefore, `docker-compose.yml` provides the opt-in `--profile microservices` topology alongside `--profile core`.

