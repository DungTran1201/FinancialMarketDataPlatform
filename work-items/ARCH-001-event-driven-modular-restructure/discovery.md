# Discovery Register — `ARCH-001`

## 1. Verified Facts (`FACT`)

- `FACT-ARCH-001`: Legacy `src/` grouped components primarily by technical type (`src/collectors/`, `src/consumers/`, `src/processing/`, `src/quality/`, `src/transformation/`, `src/backend/`, `src/microservices/`, `src/agent/`, `src/frontend/`, `src/shared/`).
- `FACT-ARCH-002`: `src/collectors/publisher.py` mixed Ingestion concerns (`TokenBucketRateLimiter`, `SequenceAndGapDetector`, `ProductionExchangeHistoricalCollector`) with Streaming infrastructure (`PartitionedEventStreamingBroker`, `ConfluentKafkaStreamingAdapter`).
- `FACT-ARCH-003`: `src/quality/lineage_and_observability.py` mixed cross-cutting OpenMetrics telemetry (`DataObservabilityMetricsCollector`) with Lakehouse dataset governance & lineage (`DataLineageGovernanceRegistry`).
- `FACT-ARCH-004`: `src/backend/modules/analytics/presentation/router.py` and `src/backend/runtime.py` imported quantitative math helpers (`compute_deterministic_*`) directly from `src/agent/tools/gateway.py` (Intelligence Plane), creating a Plane B -> Plane C dependency.
- `FACT-ARCH-005`: `src/backend/modules/iam/domain/security.py` contained cryptographic/WAF/rate-limit primitives shared by `src/microservices/gateway_service.py` and `src/microservices/registry.py`.
- `FACT-ARCH-006`: `src/transformation/dbt/` contained committed/generated `target/` and `logs/` build artifacts alongside dbt SQL models.
- `FACT-ARCH-007`: `deploy/` had `docker/`, `postgres/`, `clickhouse/`, `prometheus/`, `nginx/`, and `tls/`, while lacking declarative artifacts for `kafka/`, `object-storage/`, `iceberg/`, and unified `observability/`.
- `FACT-ARCH-008`: `models/` lacked a `models/data-platform/` category for canonical datasets, events, topics, quality rules, lineage, and retention metadata.
- `FACT-ARCH-009`: `tests/` placed unit, contract, integration, end-to-end (`TC-011`), resilience, and performance (`TC-010`) tests together under `tests/unit/`.
- `FACT-ARCH-010`: `notebooks/` (`docker-compose.yml`, `workers/binance_worker.py`, `workers/coinbase_worker.py`, `ingestion.ipynb`, `datalake/`) is standalone exploratory lab material and does not import `src.*`.

## 2. Recorded Architectural Decisions (`DECISION`)

- `DEC-ARCH-001` (`ADR-008`): Restructure `src/` into 6 modular boundary packages (`shared`, `ingestion`, `streaming`, `lakehouse`, `serving`, `intelligence`), relocate pure quantitative math to `src/shared/domain/quant.py`, isolate shared security primitives in `src/shared/security/primitives.py`, keep `deploy/nginx/` and `deploy/tls/` alongside the 7 target `deploy/` areas, and enforce inter-module boundaries via `tests/architecture/test_clean_architecture_boundaries.py`.

