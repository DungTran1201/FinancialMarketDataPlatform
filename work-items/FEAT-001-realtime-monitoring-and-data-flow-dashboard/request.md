# Work Item Request — FEAT-001

| Metadata | Value |
|---|---|
| **Work Item ID** | `FEAT-001` |
| **Title** | `Real-Time Data Platform Observatory, Pipeline Flow Visualizer & Event Lifecycle Tracing` |
| **Change Type** | `FEAT` |
| **Risk Tier** | `R2` |
| **Status** | `ACTIVE` |
| **Requested By** | `Principal Data Platform Architect / User` |
| **Created Date** | `2026-11-15` |
| **Updated Date** | `2026-11-15` |

---

## 1. Change Summary & Intent

Design and implement an interactive, browser-verified **Data Platform Real-Time Monitoring & Data Flow Visualization Observatory** on branch `arch/microservices` providing deep engineering visibility into:

`Exchange -> Ingestion -> Kafka Cluster -> Parallel Consumers (Redis Hot State / ClickHouse OLAP / Bronze Iceberg) -> Silver -> Gold -> Serving -> API / Dashboard / Agent`.

## 2. In-Scope Objectives

- Fix UI Content-Security-Policy delivery on `/ui/*` while preserving strict security controls on JSON endpoints (`/api/**`).
- Add unified `EventLifecycleTrace` correlation (`event_id`, `correlation_id`) across ingestion, Kafka broker publish/consume, Redis projection, ClickHouse sink/rollup, Bronze Parquet archive, Silver Iceberg v2 merge, Gold mart refresh, DLQ, and Serving readiness.
- Enforce parallel-branch latency mathematics (compute per-branch latency for Redis, ClickHouse, and Lakehouse independently; never sum parallel sink branches into serving E2E latency).
- Expose bounded-cardinality Prometheus stage/E2E histograms (`fmdp_stage_processing_duration_ms`, `fmdp_end_to_end_latency_ms`) without putting `event_id` or high-cardinality keys in metric labels.
- Serve non-mutating `/api/v1/observability/*` REST endpoints and `/api/v1/observability/stream` (SSE) + `/ws/v1/observability/stream` (WebSocket), keeping existing `/api/v1/data-platform/v01/telemetry` backward-compatible (`TC-011`).
- Render dark technical Observatory UI (`/ui/data-flow`) featuring Overview KPIs, interactive zoom/pan SVG Data Flow DAG with node inspector drawer, Kafka Cluster/Topic/Partition/Consumer Lag inspector, Lakehouse (Bronze/Silver/Gold/Iceberg manifests) vs ClickHouse DWH explorer, real-data OHLCV Candlestick chart (with `Decimal` rollups), Pipeline Latency dashboard (clickable time buckets), and Event Trace Inspector.
- Strictly separate passive AS-IS telemetry, explicit `LIVE` external probes/Binance REST pulls, and explicit `DEMO` synthetic stress/fault injection.

## 3. Out-of-Scope Boundaries

- Deploying managed multi-broker Kafka clusters beyond existing `docker-compose.yml` single-node KRaft topology (missing Broker 2 & Broker 3 must be reported as `UNAVAILABLE`).
- Bypassing Clean Architecture boundaries in `src/serving/api/**`.
- Fabricating synthetic candles, offsets, or storage row counts in `LIVE` mode.

## 4. Constraints & Non-Negotiables

- Zero mock data presented as real data.
- Preserve existing security headers, WAF/rate-limiting, and `tests/architecture/test_clean_architecture_boundaries.py`.
- Synchronize `models/`, `docs/`, `docs/diagrams/`, and pass `tools/validators/run_all.py`.

