# Impact Analysis & Old -> New Mapping — `ARCH-001`

## 1. Old -> New Source Mapping (`src/`)

| Old Path | New Path | Architectural Rationale |
|---|---|---|
| `src/shared/config.py` | `src/shared/config/settings.py` | Centralize configuration package under `shared/config/` |
| `src/shared/contracts/events.py` | `src/shared/contracts/events/market_events.py` | Separate event envelope contracts from dataset schema specs |
| *(extracted/formalized)* | `src/shared/contracts/schemas/datasets.py` | Shared immutable Bronze/Silver/Gold/Hot dataset schema descriptors |
| `src/shared/domain/primitives.py` | `src/shared/domain/primitives.py` | Retained in `shared/domain/` |
| *(extracted from `agent/tools/gateway.py`)* | `src/shared/domain/quant.py` | Pure Decimal/float quant functions shared by `serving` and `intelligence` without Plane B -> Plane C coupling |
| *(extracted from `quality/lineage_and_observability.py`)* | `src/shared/observability/metrics.py` | Shared OpenMetrics collector across all planes |
| *(extracted from `backend/modules/iam/domain/security.py`)* | `src/shared/security/primitives.py` | Shared AES-GCM cipher, JWT HS256, WAF, rate limiter, HTTPS policy primitives |
| `src/collectors/ports.py` | `src/ingestion/domain/ports.py` | Ingestion domain ports (`PayloadNormalizerPort`, `EventPublisherPort`, `HistoricalCollectorPort`, `WatermarkStorePort`) |
| *(extracted from `collectors/publisher.py` & `main_rest.py`)* | `src/ingestion/domain/models.py` | Pure domain value objects (`ExchangeSymbolMetadata`, `DetectedStreamGap`, `WatermarkRecord`) |
| `src/collectors/publisher.py` *(rate limiter + gap detector)* | `src/ingestion/application/rate_limiter.py` | Token bucket weight limiter and sequence gap detector |
| `src/collectors/main_ws.py` *(worker logic)* | `src/ingestion/application/ws_service.py` | WebSocket collection loop & reconnect backoff |
| `src/collectors/main_rest.py` *(worker logic)* | `src/ingestion/application/backfill_service.py` | Historical REST backfill orchestration |
| `src/collectors/main_rest.py` *(watermark SQLite/PG store)* | `src/ingestion/infrastructure/watermark_store.py` | Watermark persistence adapter |
| `src/collectors/normalizer.py` | `src/ingestion/providers/binance/normalizer.py` | Binance payload normalization isolated per provider |
| `src/collectors/publisher.py` *(HTTP/ASGI exchange client)* | `src/ingestion/providers/binance/rest_client.py` | `ProductionExchangeHistoricalCollector` + deterministic exchange ASGI app |
| `src/collectors/main_ws.py` *(CLI entrypoint)* | `src/ingestion/entrypoints/ws_collector.py` | Container entrypoint for `collector-ws` |
| `src/collectors/main_rest.py` *(CLI entrypoint)* | `src/ingestion/entrypoints/rest_backfill.py` | Container entrypoint for `collector-rest` |
| `src/collectors/publisher.py` *(Kafka broker & adapter)* | `src/streaming/infrastructure/kafka_broker.py` | Partitioned streaming broker and Confluent Kafka adapter |
| *(extracted Kafka routing/DLQ contracts)* | `src/streaming/contracts/topics.py` | Consumer group identifiers, DLQ routing helper, stream sink ports |
| `src/consumers/anomaly_detector.py` | `src/streaming/consumers/anomaly_detector.py` | Streaming statistical anomaly detector |
| `src/consumers/hot_redis/main.py` | `src/streaming/consumers/hot_redis.py` | Redis Lua monotonic hot state projector |
| `src/consumers/analytics_ch/main.py` | `src/streaming/consumers/analytics_ch.py` | ClickHouse micro-batch OLAP sink |
| `src/consumers/lakehouse_bronze/main.py` *(archive engine)* | `src/lakehouse/bronze/archiver.py` | Bronze Parquet ZSTD writer & partition path builder |
| `src/consumers/lakehouse_bronze/main.py` *(consumer loop/main)* | `src/lakehouse/bronze/consumer.py` | Container entrypoint for `consumer-lakehouse-bronze` (depends on `shared` + `lakehouse.bronze`) |
| `src/processing/spark/bronze_to_silver.py` | `src/lakehouse/silver/merge_engine.py` | Silver deduplicated MERGE + Stage 9 Parquet compaction & Iceberg v2 snapshot manifests |
| `src/processing/gold_marts.py` | `src/lakehouse/gold/mart_engine.py` | Gold Parquet analytical mart materialization |
| `src/transformation/dbt/` *(sources only)* | `src/lakehouse/gold/dbt/` | ClickHouse dbt project & SQL marts (transient `logs/` and `target/` removed) |
| `src/quality/expectations/suite_definitions.py` | `src/lakehouse/quality/gates.py` | Pre-Gold blocking data quality engine |
| `src/quality/lineage_and_observability.py` *(catalog & lineage)* | `src/lakehouse/catalog/lineage.py` | Dataset governance catalog & directed lineage graph |
| `src/processing/pipeline_v01.py` | `src/lakehouse/orchestration/pipeline.py` | End-to-end 12-stage Data Platform v0.1 pipeline composition root |
| `src/backend/main.py` | `src/serving/api/main.py` | FastAPI Modular Monolith ASGI entrypoint |
| `src/backend/modules/*` | `src/serving/api/modules/*` | 8 Clean Architecture bounded contexts |
| `src/microservices/registry.py` | `src/serving/api/gateway/registry.py` | Encrypted microservice topology registry |
| `src/microservices/gateway_service.py` | `src/serving/api/gateway/service.py` | Unified Edge Gateway (`svc-api-gateway`) |
| `src/frontend/data_flow_ui.py` | `src/serving/api/gateway/ui.py` | Real-Time Data Flow Observatory UI router |
| `src/microservices/*_service.py` (7 domain services) | `src/serving/api/services/*.py` | Optional split domain ASGI service entrypoints (`--profile microservices`) |
| `src/backend/runtime.py` | `src/serving/infrastructure/runtime.py` | Serving dependency injection container (`PlatformRuntimeContainer`) |
| `src/agent/main.py` | `src/intelligence/main.py` | Intelligence worker entrypoint (`agent-worker`) |
| `src/agent/orchestrator/graph.py` *(graph orchestration)* | `src/intelligence/orchestrator/graph.py` | Compiled `MarketIntelligenceGraph` & `DeterministicMockLLMAdapter` |
| `src/agent/orchestrator/graph.py` *(workflow nodes & state)* | `src/intelligence/workflows/investigation.py` | `WORKFLOW_NODES`, `AgentWorkflowState`, investigation node handlers |
| `src/agent/orchestrator/graph.py` *(provenance validation)* | `src/intelligence/reporting/validator.py` | `ReportProvenanceError`, `ReportValidator` |
| `src/agent/tools/contracts.py` | `src/intelligence/tools/contracts.py` | Tool governance policies & provenance envelopes |
| `src/agent/tools/gateway.py` | `src/intelligence/tools/gateway.py` | `ControlledToolGateway` (consumes quant helpers from `src/shared/domain/quant.py`) |

## 2. Old -> New Infrastructure & Model Mapping

- `deploy/prometheus/prometheus.yml` -> `deploy/observability/prometheus/prometheus.yml` (plus `alerts.yml` & `grafana/datasources/prometheus.yml`).
- Added `deploy/kafka/topics-init.sh`, `deploy/object-storage/init-buckets.sh`, `deploy/iceberg/catalog-config.yaml`.
- Retained `deploy/docker/`, `deploy/postgres/`, `deploy/clickhouse/`, `deploy/nginx/`, `deploy/tls/`.
- Added `models/data-platform/{README.md,datasets.yaml,events.yaml,topics.yaml,quality-rules.yaml,lineage.yaml,retention.yaml}`.
- Reorganized `tests/` into `architecture/`, `unit/`, `contract/`, `data_quality/`, `integration/`, `e2e/`, `resilience/`, `performance/`.

## 3. Risks & Mitigations

1. **Risk**: Broken Docker Compose commands, batch scripts (`setup.bat`, `run.bat`), or CI checks referencing old module names.
   - **Mitigation**: Update every reference atomically and verify with module import checks, `pytest`, `unittest discover`, `dbt parse`, and `docker-compose.yml` verification.
2. **Risk**: Validator failures due to moved `test_path`s, unindexed `models/data-platform/`, missing 12-section `README.md`s, or stale `DATA-001/artifact-plan.yaml` file assertions.
   - **Mitigation**: Update `models/testing/testing.yaml`, `models/architecture/components.yaml`, `models/domain/domain.yaml`, mark relocated `DATA-001` code paths as `DEPRECATED` with relocation pointer, add 12-section `README.md` for `models/data-platform/`, and pass `tools/validators/run_all.py` with 0 errors.
