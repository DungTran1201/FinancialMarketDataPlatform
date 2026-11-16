---
doc_id: GOV-MIG-P2AUD-001
title: "Documentation V2 — Phase 2 Repository Re-Audit (Baseline 7880c85)"
doc_type: migration-report
plane: governance
scope_level: platform
status: IN_REVIEW
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: system-architect
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/migration/phase-2-implementation-inventory.yaml"
    - "pyproject.toml"
    - "docker-compose.yml"
related_docs:
  - GOV-MIG-P1-001
  - GOV-MIG-P2LOG-001
  - GOV-MIG-P2RISK-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: system-architect
    summary: "Completed evidence-only Phase 2 repository re-audit across src/, frontend/, deploy/, notebooks/, tests/, and CI/configs on 7880c85."
---

# Documentation V2 — Phase 2 Repository Re-Audit (Baseline `7880c85`)

This audit verifies every source file, infrastructure descriptor, frontend route/service, intelligence tool, and test suite on branch `docs-v2/phase-2-project-documentation` (branched from `docs-v2/phase-1-foundation` commit `7880c85`). Companion machine-readable inventory lives in [phase-2-implementation-inventory.yaml](phase-2-implementation-inventory.yaml).

---

## 1. Source Code & Architectural Boundary Audit

- **Package Topology & DAG Enforcement**: `src/` comprises 6 top-level packages: `src/shared/` (17 files), `src/ingestion/` (17 files), `src/streaming/` (6 files), `src/lakehouse/` (17 Python/README/SQL/dbt files + dbt build artifacts), `src/serving/` (domain modules, gateway, 7 microservice wrappers, infrastructure runtime), and `src/intelligence/` (11 files). AST boundary tests in `tests/architecture/test_clean_architecture_boundaries.py` verify strict domain purity and acyclic imports across packages, with composition roots at `src/lakehouse/orchestration/pipeline.py` and `src/serving/infrastructure/runtime.py`.
- **Important Symbol Verification (Data Plane)**: Actual classes in `src/ingestion/` are `BinancePayloadNormalizer` (`normalizer.py:25`), `ProductionExchangeHistoricalCollector` (`rest_client.py:102`), `HistoricalRestBackfillWorker` (`backfill_service.py:12`), `WebSocketStreamCollector` (`ws_service.py:27`), and `IngestionWatermarkStore` (`watermark_store.py:12`). No continuous Exchange WebSocket loop exists in `src/`; `ws_collector.py`, `rest_backfill.py`, `hot_redis.py:main()`, `analytics_ch.py:main()`, `bronze/consumer.py:main()`, and `intelligence/main.py` all log config parameters and exit immediately.
- **Standalone Prototypes (`notebooks/`)**: `notebooks/` contains 5 prototype files (`ingestion.ipynb`, `docker-compose.yml`, `workers/{binance_worker,coinbase_worker}.py`, and sample JSON metadata). Zero imports reference `notebooks/` from `src/` or `tests/`.

---

## 2. Serving APIs (`src/serving/`) & Security Re-Audit

### 2.1 Process Model & Microservice Registry
- `src/serving/api/main.py` creates the unified FastAPI monolith (`create_app()`) sharing one `PlatformRuntimeContainer` (`rt`) on `app.state.runtime`, mounts `lifespan` (`finally: rt.close()` closing SQLite `watermark_store`), installs `defense_in_depth_middleware`, mounts gateway + observability + all 8 domain routers, and registers `svc-api-gateway` plus all 7 domain ASGI sub-apps in `MicroserviceRegistry` (`src/serving/api/gateway/registry.py`).
- **Gateway vs. Real Routes Gap**: `CANONICAL_MICROSERVICES` (`registry.py:49`) lists `"/ws/v1/market"` on `svc-market-hot`, which is **not implemented** anywhere in `src/`. Conversely, `src/serving/README.md:11` still cites deleted `gateway/ui.py` (`/ui/data-flow`).
- **Standalone Microservices State Split**: Six `create_*_microservice_app(runtime=None)` wrappers share `rt` when mounted in-process (`runtime.py:189-218`), whereas `create_iam_microservice_app(config)` (`services/iam.py:17`) creates isolated in-memory `JwtSecurityService` and `SlidingWindowRateLimiter` instances even in-process. When run as separate containers via `docker-compose.yml --profile microservices`, each factory instantiates an isolated in-memory `PlatformRuntimeContainer()`.
- **Synchronous `HTTP 202` Execution**: `POST /api/v1/market/ingest`, `POST /api/v1/historical/backfill-jobs` (which hardcodes `"transport_mode": "MOCKED_SIMULATED_EXCHANGE_REST"` at `router.py:150`), and `POST /api/v1/agents/runs` execute synchronously via `await` before returning HTTP `202`. `GET /api/v1/market/orderbook/{symbol}` returns hardcoded static bids/asks when `get_hot_orderbook()` returns `None`.

### 2.2 Security Re-Audit (`SEC-AUDIT-001`..`005`) — Confirmed Present on `7880c85`
1. `SEC-AUDIT-001` (**CRITICAL**): `POST /api/v1/auth/token` (`src/serving/api/modules/iam/presentation/router.py:183-226`) hashes client password and verifies it against the freshly computed hash (`L202-204`) without querying `deploy/postgres/init/01_schema.sql` `users` or any credential store. Any caller can mint a signed HS256 `admin` JWT.
2. `SEC-AUDIT-002` (**CRITICAL**): `POST /api/v1/auth/api-keys` (`L264-281`) and `POST /api/v1/auth/revoke` (`L253-262`) have zero authentication/RBAC checks; minted API key hashes are discarded unpersisted, and `CredentialHasher.verify_api_key` (`domain/security.py:90-93`) is unused by any endpoint. Additionally, `UserRole.SERVICE` is omitted from `ROLE_CAPABILITIES` (`domain/ports.py:18-44`).
3. `SEC-AUDIT-003` (**CRITICAL**): **Zero** endpoints across all 8 domain routers, `data_plane.py`, `gateway/service.py`, `gateway/observability.py`, or `WS /ws/v1/observability/stream` declare FastAPI `Depends(...)` authentication or RBAC checks. Middleware checks only Host header (`localhost` default if omitted), path/query regex WAF (body uninspected), and in-memory per-IP rate limits.
4. `SEC-AUDIT-004` (**HIGH**): `_extract_client_ip` (`iam/presentation/router.py:28-34`) unconditionally trusts `X-Forwarded-For` / `X-Real-IP` headers without trusted proxy validation, and `PlatformConfig.jwt_secret_key` (`src/shared/config/settings.py:33-35`) defaults to static `"change_me_generate_32_byte_random_hex_secret"`.
5. `SEC-AUDIT-005` (**MEDIUM**): Unauthenticated `GET /api/v1/auth/domains` and `GET /api/v1/health/ready` disclose encrypted internal infrastructure topology (`6379`/`8123`/`5432`/`9092`), and `frontend/src/services/auth/auth.service.ts:18-27` defaults unauthenticated browser sessions to a client-side `quant_admin` (`ADMIN`) profile.

---

## 3. Frontend SPA & API Contract Reconciliation (`frontend/`)

- **Active Routes (`frontend/src/app/router/router.ts:26-34`)**: Hash SPA with 7 routes across 6 modules (`DashboardModule`, `DataFlowModule`, `MarketAnalyticsModule`, `DataManagementModule`, `AiWorkspaceModule`, `AdministrationModule`). No `auth.store.ts` or login/logout modal exists; `frontend/README.md` cites nonexistent `public/icons/`, `src/app/providers/`, `src/hooks/`, while `StateView.ts` is unused.
- **Reconciled Routes (`7880c85`)**: `market.service.ts`, `analytics.service.ts`, `catalog.service.ts`, `agent.service.ts`, `observability.service.ts`, `sse.ts`, and `vite.config.ts` were updated in `7880c85` to align with FastAPI route paths and response envelopes (plus `GET /api/v1/agents/runs` added to backend).
- **Remaining Frontend vs. Backend & UI Reality Gaps**:
  - `AuthService.getApiKeys()` calls `GET /api/v1/auth/api-keys` (backend only exposes `POST /api/v1/auth/api-keys`, returning `405` silently swallowed into `[]`), and `AuthService.revokeApiKey()` calls `DELETE /api/v1/auth/api-keys/{id}` (backend exposes `POST /api/v1/auth/revoke`). `AdministrationModule` calls `createApiKey()` then discards the returned `raw_key` without showing it.
  - `ObservabilityService.setStreamControl()` (`POST /api/v1/observability/stream/control`) is unimplemented on backend (unused in UI).
  - Header LIVE/DEMO mode switch (`MainLayout.ts:139-142`) is ignored by modules; `DashboardModule` Core Stores Health card, `DataFlowModule` DAG SVG labels & Kafka badge, `CatalogService.getLineage()` empty fallbacks, `AgentService.getRuns()` node latencies, and `AdministrationModule` Defense-in-Depth badges contain hardcoded display values; `MarketAnalyticsModule` `|| 0.45`/`|| 0.012`/`|| 1440` masks legitimate `0` backend values.
  - `frontend/tests/{formatters,router}.test.js` do not import or execute `frontend/src/` code (`node_test` on inline copies/arrays only).

---

## 4. Persistence, Streaming, Infrastructure & Intelligence Reality

| Infrastructure / Component | Config / DDL Reality (`deploy/`) | Actual Code Behavior (`src/`) | Execution Classification |
|---|---|---|---|
| **Kafka** | `apache/kafka:3.7.0` 1 KRaft broker (`docker-compose.yml:67-94`); 6 topics in `topics-init.sh` (not auto-run) | `PartitionedEventStreamingBroker` uses in-memory `dict[str, list]`; `ConfluentKafkaStreamingAdapter` lazy producer only (unused); zero `Consumer` loops | `SIMULATED` (`IN_PROCESS_PARTITIONED_BROKER`) |
| **Redis** | `redis:7.2-alpine`, `--maxmemory 256mb --maxmemory-policy volatile-lru` (`docker-compose.yml:47`) | `HotStateProjector` reads/writes Python dicts; `_sync_record_to_live_redis` (unused `_redis_client=None`) only writes `price_key`, omitting snapshot/orderbook keys; `ORDER_BOOK` without price writes `last_price="0"` | `SIMULATED` (dicts) / `PARTIALLY_IMPLEMENTED` (Lua) |
| **ClickHouse** | `clickhouse/clickhouse-server:24.3-alpine`, 3 `ReplacingMergeTree` tables (`market_trades`, `market_klines`, `market_tickers`), **0 Materialized Views** in `01_schema.sql` | `ClickHouseBatchSink` simulates deduplication in Python dicts (`market_trades_raw`, `market_klines_1m`, `market_tickers_latest` in snapshot); `_clickhouse_client` unused; JSON state saves klines only | `SIMULATED` |
| **PostgreSQL** | `postgres:16-alpine`, 5 tables (`users`, `monitored_instruments`, `ingestion_watermarks`, `agent_runs`, `agent_tool_invocations`) | Never imported/called in `src/`. Watermarks use SQLite `.local_storage/control_watermarks.db` with a different schema & status enum; instruments, agent runs, and reports live in memory | `NOT_IMPLEMENTED` (`postgres`) / `IMPLEMENTED` (`sqlite` watermarks) |
| **Lakehouse / MinIO / Iceberg / dbt** | `minio/minio:latest`, 4 buckets in `init-buckets.sh` vs `LAKEHOUSE_BUCKET=market-data` in `.env.example`; `catalog-config.yaml` cites absent `iceberg-rest:8181`; `MINIO_ENDPOINT` vs `MINIO_ENDPOINT_URL` mismatch | Local filesystem ZSTD Parquet (atomic `.tmp` + `replace()`) + hand-rolled Iceberg v2 JSON manifests + `Decimal` DQ & Gold marts; `pyiceberg`/`pyspark`/`great_expectations`/`MinIO` unused; dbt has 1 offline SQL model (`fct_daily_market_summary`) | `PARTIALLY_IMPLEMENTED` (local Parquet/DQ) / `NOT_IMPLEMENTED` (S3/Iceberg REST/Spark/live dbt) |
| **Intelligence Plane (`src/intelligence/`)** | `.env.example`: `LLM_PROVIDER=mock`, `AGENT_RUN_TIMEOUT_SECONDS=90` (unwired in `PlatformConfig`) | 5-node Python async loop (`MarketIntelligenceGraph`, `langgraph` not imported) + `DeterministicMockLLMAdapter`; `ControlledToolGateway` enforces 10-tool RBAC/bounds; `GENERATE_ANALYSIS_REPORT` & `DETECT_ANOMALIES` have write side effects despite default `is_read_only_market_data=True`; `ReportValidator` checks non-empty `invocation_id` membership | `IMPLEMENTED` (Gateway/Validator) / `SIMULATED` (Mock LLM / in-memory store) |
| **Observability (`deploy/observability/`)** | Prometheus `15s` scrape & 2 alert rules; Grafana datasource YAML not mounted in `docker-compose.yml:367-377`; Superset unconfigured | Prometheus text `/metrics`, 10-timestamp `PipelineTraceRegistry`, SSE/WS streams & TCP socket probes execute in-process | `IMPLEMENTED` (Metrics/Traces) / `PARTIALLY_IMPLEMENTED` (Grafana/Superset unmounted) |

---

## 5. Verification Baseline on `7880c85`

- **Python Suite**: `tests/` contains 51 platform tests (`architecture`, `unit`, `contract`, `data_quality`, `integration`, `e2e`, `resilience`, `performance`) plus 8 `tests/docs/` tests — all executing purely **in-process / local disk / SQLite / embedded ASGI** with **0** live Docker container integration tests.
- **Note on `src/shared/contracts/events/market_events.py:139`**: `DeadLetterEnvelopeV1.failed_at` uses default `datetime.now(UTC)` (evaluated once at import time) rather than `field(default_factory=...)` when omitted.
