# Discovery Evidence & Runtime Defect Register — `DOCS-004`

## 1. Verified Facts (`FACT`)

### 1.1 Runtime Architecture & Implementation Classification Reality
- **FACT-01**: `PlatformRuntimeContainer` (`src/serving/infrastructure/runtime.py`) and `DataPlatformV01Pipeline` (`src/lakehouse/orchestration/pipeline.py`) execute all 12 data platform stages **in-process / locally** via embedded ASGI exchange simulation (`use_embedded_asgi_transport=True`), in-memory `PartitionedEventStreamingBroker` (plus optional Confluent adapter), in-memory/dict `HotStateProjector` & `ClickHouseBatchSink` (with optional live Redis Lua eval), disk-backed PyArrow ZSTD Parquet + Iceberg v2 JSON manifests under `.local_lakehouse/`, custom Python `Decimal` `DataQualityGateEngine` (`DQ-KLINE-001..005`, `DQ-TRADE-001..003`), SQLite WAL `IngestionWatermarkStore`, and `DeterministicMockLLMAdapter` inside the **5-node** `MarketIntelligenceGraph` (`WORKFLOW_NODES`).
- **FACT-02**: Container worker entrypoints `src/ingestion/entrypoints/ws_collector.py`, `src/ingestion/entrypoints/rest_backfill.py`, `src/streaming/consumers/hot_redis.py:main()`, `src/streaming/consumers/analytics_ch.py:main()`, `src/lakehouse/bronze/consumer.py`, and `src/intelligence/main.py` only initialize `PlatformConfig` and log readiness (`PARTIALLY_IMPLEMENTED` — no live continuous Kafka/WS daemon loops are wired).
- **FACT-03**: `airflow`, `spark-worker`, `dbt-runner`, `great-expectations`, and `qdrant` do NOT exist in `docker-compose.yml` or runtime Python execution paths (`PLANNED`). `src/lakehouse/gold/dbt/` contains a valid dbt project (`fct_daily_market_summary.sql`), but gold mart generation in the API/pipeline executes in Python (`GoldLayerMartEngine`). `prometheus`, `grafana`, and `superset` ARE defined as optional Compose profiles (`observability`, `bi`).

### 1.2 API & WebSocket Route Parity Discrepancies
- **FACT-04**: `src/serving/api/main.py` registers **55 routes** (`54` HTTP + `1` WebSocket `WS /ws/v1/observability/stream`), while the 7 standalone apps under `src/serving/api/services/` expose subset endpoints.
- **FACT-05**: Docs and models cite non-existent routes (`/health`, `/api/v1/market/ticker/24h`, `/api/v1/analytics/volatility`, `/ws/market`, `/ws/v1/market/stream`, `/api/v1/observability/data-flow`, `/api/v1/analytics/jobs`, `/api/v1/historical/backfill/pause`, `/api/v1/users`, `/ui/data-flow`), omit 33+ active routes (`/api/v1/auth/{verify,revoke,domains}`, `/api/v1/market/{ingest,evict/{symbol},orderbook/{symbol}}`, `POST /api/v1/analytics/anomalies/evaluate`, `PUT /api/v1/catalog/instruments/{symbol}`, `POST /api/v1/catalog/lakehouse/pipeline`, `/api/v1/platform/config`, `/api/v1/agents/runs*`, `/api/v1/reports*`, `/api/v1/microservices/*`, `/api/v1/data-platform/v01/{status,watermarks,metrics,telemetry}`, `/api/v1/observability/*`), and misstate kline fields (`open`/`high`/`low`/`close`/`volume`/`trades_count` instead of `open_price`/`high_price`/`low_price`/`close_price`/`base_volume`/`trade_count`).

### 1.3 Kafka, Metrics, Security, Storage & Compose Defects
- **FACT-06**: `src/streaming/contracts/topics.py` registers 6 canonical topics (`market.raw.trades.v1`, `market.raw.klines.v1`, `market.raw.tickers.v1`, `market.raw.orderbook.v1`, `market.anomalies.v1`, `market.dlq.v1`) and 4 Kafka consumer groups (`cg.hot.redis.v1`, `cg.analytics.clickhouse.v1`, `cg.lakehouse.bronze.v1`, `cg.anomaly.detector.v1`), while `cg.dlq.inspector.v1` is a trace-registry label on DLQ failure and `cg.agent.anomaly.v1` is `PLANNED` (not running in `src/intelligence/`). Topic retention in `deploy/kafka/topics-init.sh` vs `topics.py` / `integrations.yaml` drifted (`168h` vs `72h`/`336h`/`720h`).
- **FACT-07**: Real Prometheus metrics (`src/shared/observability/metrics.py`) use the `fmdp_*` namespace (`10` metrics); `deploy/observability/prometheus/alerts.yml` defines only `FMDPDeadLetterQueueSpike` and `FMDPConsumerLagHigh`. Docs/runbooks invented 11 non-existent metric names and 6 non-existent alerts.
- **FACT-08**: `CredentialHasher` uses `PBKDF2-HMAC-SHA256` (`pbkdf2_sha256$...`) and `JwtSecurityService` uses `HS256` with IP-HMAC binding — NOT Argon2id or RS256.
- **FACT-09**: `deploy/object-storage/init-buckets.sh` creates `lakehouse-bronze`, `lakehouse-silver`, `lakehouse-gold`, `lakehouse-checkpoints` — whereas docs cited `s3://market-data/` (`LAKEHOUSE_BUCKET=market-data` in `.env.example`).
- **FACT-10**: `docker-compose.yml` has a verified host port `9000` collision between `clickhouse` (`127.0.0.1:${CLICKHOUSE_NATIVE_PORT:-9000}:9000`) and `minio` (`127.0.0.1:9000:9000`) when `--profile lakehouse` runs; `frontend` maps host `3001:3000` while `grafana` maps `3000:3000`; `prometheus.yml` scrapes only `backend-api:8000`; `.env.example` omits Compose variables and uses wrong `9000` for MinIO alongside ClickHouse.

### 1.4 Governance, Validator & Test Evidence Gaps
- **FACT-11**: `DOCS-003/remediation-validation-report.md` falsely reported frontend tests as Vitest / `App.test.tsx`; actual `frontend/package.json` runs `node --test tests/**/*.test.js` (`2` files, `3` unit tests on local JS helpers).
- **FACT-12**: `18` broken historical internal path references existed across `docs/`, `.agents/agents/`, and `.agents/skills/` prior to remediation (including nonexistent `models/api/api-contracts.yaml`, `models/context/context.yaml`, `models/security/security.yaml`, `models/security/threats.yaml`, `component-specification.template.md`).
- **FACT-13**: `identifier-registry.yaml` omits `ADR-007` and `ADR-008`, `models/architecture/components.yaml` omits `svc-catalog-governance`, `svc-iam-security`, `svc-intelligence-agent`, `models/ux/ux.yaml` maps incorrect `API-*` IDs, and legacy validators perform zero semantic checks against FastAPI routes, Compose ports, metric names, or consumer groups.

---

## 2. Separately Tracked Runtime & Frontend Engineering Proposals (Out of `DOCS-004` Code Mutation Scope)

Because `Rule 1.4` prohibits mutating `src/` or `frontend/` runtime business logic during `DOCS-004`, the following verified code defects are logged here for future application/frontend engineering work items (`APP` / `FEAT`):

1. **PROP-APP-001 (Frontend-Backend API Path Drift)**:
   - `frontend/src/services/api/market.service.ts` calls `/market/price` (`API` provides `/api/v1/market/prices/{symbol}`), `/market/klines` (API provides `/api/v1/historical/klines/{symbol}`), `/market/ticker/24h` (API provides `/api/v1/market/prices`), `/market/orderbook` (API provides `/api/v1/market/orderbook/{symbol}`), and `/market/symbols` (API provides `/api/v1/catalog/instruments`).
   - `frontend/src/services/api/analytics.service.ts` calls `/analytics/volatility`, `/analytics/returns` (not registered in `analytics/presentation/router.py`), and `frontend/src/services/api/catalog.service.ts` calls `/catalog/datasets`, `/catalog/lineage`, `/catalog/quality-gates` (API mounts lakehouse lineage under `/api/v1/data-platform/v01/lineage`).
   - `frontend/src/services/auth/auth.service.ts` calls `GET /auth/api-keys`, whereas backend router exposes only `POST /api/v1/auth/api-keys`.
2. **PROP-APP-002 (Worker Container Daemon Loops)**:
   - `ws_collector.py`, `rest_backfill.py`, `hot_redis.py:main`, `analytics_ch.py:main`, `bronze/consumer.py`, and `src/intelligence/main.py` require full async Kafka/WebSocket loop wiring to operate as live standalone Docker Compose daemons beyond `PlatformRuntimeContainer` in-process simulation.
3. **PROP-APP-003 (Lakehouse Bucket Env Normalization)**:
   - Legacy `LAKEHOUSE_BUCKET=market-data` env var in `.env.example` coexists with the 4 medallion buckets (`lakehouse-bronze`, `lakehouse-silver`, `lakehouse-gold`, `lakehouse-checkpoints`) provisioned by `deploy/object-storage/init-buckets.sh`.
4. **PROP-APP-004 (Non-IAM Route Auth/RBAC Enforcement)**:
   - `/api/v1/auth/*` and `ControlledToolGateway` enforce IAM/tool security, whereas non-IAM domain routers (`/api/v1/market`, `/historical`, `/analytics`, `/catalog`, `/platform`, `/agents/runs`, `/reports`, `/data-platform/v01`, `/observability`) lack FastAPI route-level JWT/RBAC `Depends(...)` guards (`runtime_rbac_enforced: false`).
5. **PROP-APP-005 (Agent Node & Stream Subscription Sync)**:
   - Either align `MarketIntelligenceGraph` to 6 nodes if `ADR-007` target requires 6, or formally keep 5 nodes (`ADR-006`) and wire `cg.agent.anomaly.v1` consumer in `src/intelligence/main.py`. Also decide whether to add `/ws/v1/market/stream` or formalize `/ws/v1/observability/stream` as the unified WebSocket channel.

---

## 3. Assumptions (`ASSUMPTION`) & Open Questions (`OPEN QUESTION`)

- **ASSUMP-01**: `[ASSUMPTION — REQUIRES VALIDATION]` External Kubernetes/Helm manifests (if introduced later) will preserve container-internal ports (`clickhouse:9000`, `minio:9000`) while isolating host port mappings (`minio` API exposed on host `${MINIO_API_PORT:-9010}` when co-located with ClickHouse locally).
- **OQ-01**: `[OPEN QUESTION]` Should `frontend/src/services/api/*` be updated in a follow-up `FEAT` work item to point directly to `/api/v1/...`, or should compatibility alias routes be added in `backend-api`?
- **OQ-02**: `[OPEN QUESTION]` Should `LAKEHOUSE_BUCKET=market-data` in `.env.example` be deprecated in favor of `LAKEHOUSE_BRONZE_BUCKET=lakehouse-bronze` (matching `deploy/object-storage/init-buckets.sh`)?
