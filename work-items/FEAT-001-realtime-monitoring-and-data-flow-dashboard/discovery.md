# Discovery & Evidence Register — FEAT-001

| Metadata | Value |
|---|---|
| **Work Item ID** | `FEAT-001` |
| **Authoring Role** | `discovery-analyst` |
| **Status** | `COMPLETED` |
| **Created Date** | `2026-11-15` |
| **Updated Date** | `2026-11-15` |

---

## 1. Sources Inspected

- `src/serving/api/modules/iam/presentation/router.py`
- `src/serving/api/main.py`
- `src/serving/api/gateway/ui.py`
- `src/serving/infrastructure/runtime.py`
- `src/streaming/infrastructure/kafka_broker.py`
- `src/streaming/consumers/hot_redis.py`
- `src/streaming/consumers/analytics_ch.py`
- `src/lakehouse/{bronze/archiver.py,silver/merge_engine.py,gold/mart_engine.py,quality/gates.py,catalog/lineage.py,orchestration/pipeline.py}`
- `src/shared/observability/metrics.py`
- `src/ingestion/providers/binance/rest_client.py`
- `docker-compose.yml` & `deploy/{clickhouse/init/01_schema.sql,kafka/topics-init.sh,iceberg/catalog-config.yaml,observability/}`

## 2. Verified Facts (`FACT`)

- **FACT-01 (Browser CSP Blocker)**: `src/serving/api/modules/iam/presentation/router.py` (L138-148) applied `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'; base-uri 'none'` to `/ui/data-flow`, blocking scripts, CSS, and fetch/SSE calls in browsers.
- **FACT-02 (Single-Node Kafka Compose vs In-Process Broker)**: `docker-compose.yml` defines a single Kafka KRaft node (`KAFKA_NODE_ID: 1`); Broker 2 and Broker 3 do not exist (`UNAVAILABLE`). Runtime uses in-process 6-partition `PartitionedEventStreamingBroker` with manual consumer group offsets and DLQ (`ConfluentKafkaStreamingAdapter` exists but is not auto-wired into `PlatformRuntimeContainer`).
- **FACT-03 (AS-IS Storage Reality)**: `HotStateProjector` (`hot_redis.py`) and `ClickHouseBatchSink` (`analytics_ch.py`) execute in-process with bounded buffers/tables (ClickHouse DDL lives in `deploy/clickhouse/init/01_schema.sql`; live container connectivity requires TCP `:8123` / `:6379`). Lakehouse Bronze Parquet, Silver dedup Parquet + Apache Iceberg v2 manifests (`v*.metadata.json`), and Gold Parquet marts are actively written to `.local_lakehouse/`.
- **FACT-04 (Synthetic Tick Behavior on Legacy Endpoint)**: `DataPlatformV01Pipeline.step_realtime_tick_and_collect_telemetry()` (API-016) injects a synthetic oscillating price tick and fills fallback timings on GET `/api/v1/data-platform/v01/telemetry` (asserted by `tests/e2e/test_data_platform_v01_e2e.py`).
- **FACT-05 (Clean Architecture Constraint)**: `tests/architecture/test_clean_architecture_boundaries.py` forbids `src/serving/api/**` from importing `src.ingestion`, `src.streaming`, `src.lakehouse`, or `src.intelligence`.
- **FACT-06 (Metrics Cardinality Gap)**: `DataObservabilityMetricsCollector` (`src/shared/observability/metrics.py`) currently exports 6 gauges/counters without per-stage duration histograms or high-resolution event trace correlation.

## 3. Explicit Assumptions (`ASSUMPTION — REQUIRES VALIDATION`)

- **ASSUMP-01**: Live external Docker containers (`kafka:9092`, `redis:6379`, `clickhouse:8123`, `minio:9000`, `postgres:5432`) may be offline during local workstation runs unless `docker compose up` is executed; fast non-blocking TCP probes (5s TTL cache, `<=100ms` timeout) safely classify them as `LIVE_CONTAINER` vs `UNAVAILABLE` without stalling API latency. `[ASSUMPTION — REQUIRES VALIDATION]`

## 4. Architectural / Business Decisions (`DECISION`)

- **DEC-01**: Place `EventLifecycleTrace`, `PipelineTraceRegistry`, and bounded-label stage/E2E Prometheus histograms inside `src/shared/observability/` so every architectural plane (`ingestion`, `streaming`, `lakehouse`, `serving/infrastructure`) can share tracing primitives cleanly without violating `TC-006`.
- **DEC-02**: Keep `GET /api/v1/data-platform/v01/telemetry` backward-compatible for `TC-011`, and introduce dedicated non-mutating `/api/v1/observability/*` REST + SSE/WS routes separating passive AS-IS reads, `LIVE` external probes/Binance REST pulls, and explicit `DEMO` injections.
- **DEC-03**: Compute parallel-branch latencies independently (`hot_branch_ms`, `olap_branch_ms`, `lakehouse_branch_ms`) and compute `end_to_end_serving_ms` strictly along the critical path to Serving without summing parallel sink branches.

## 5. Open Questions & Blockers (`OPEN QUESTION`)

- **OQ-01**: `[OPEN QUESTION]` External `api.binance.com` internet reachability depends on host firewall/network policy; air-gapped environments will observe `UNAVAILABLE` or explicit fallback when clicking `LIVE Binance Probe`.

