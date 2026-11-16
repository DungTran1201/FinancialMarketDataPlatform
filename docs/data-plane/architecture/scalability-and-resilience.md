---
doc_id: DP-ARCH-RES-001
title: "Data Plane Scalability, Reliability & Resilience Architecture"
doc_type: specification
plane: data-plane
scope_level: plane
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: devops-sre
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/ingestion/application/ws_service.py"
    - "src/ingestion/application/rate_limiter.py"
    - "src/streaming/infrastructure/kafka_broker.py"
    - "src/streaming/consumers/anomaly_detector.py"
related_docs:
  - DP-ARCH-001
  - OVR-ARCH-QA-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Documented implemented fault-handling mechanics alongside SPOFs and unresolved scalability/SLO targets."
---

# Data Plane Scalability, Reliability & Resilience

## 1. Delivery Semantics (Zero Overclaiming)

- **`AS-IS` Delivery**: **At-least-once in-process polling + idempotent natural-key sinks**. Offsets commit manually after `hot_redis`, `clickhouse`, and `bronze_archiver` complete writes (`DataPlatformV01Pipeline` L270–303). Optional broker `event_id` drop activates only if `deduplicate_events=True`.
- **Exactly-Once Statement**: Distributed end-to-end Kafka-to-ClickHouse/Iceberg exactly-once semantics are **NOT implemented** (`enable.idempotence: True` on unused producer adapter only).

## 2. Implemented Fault & Flow-Control Mechanisms

1. **Malformed Frames (Poison Messages)**: `BinancePayloadNormalizer.normalize_or_route_dlq()` isolates errors to `market.dlq.v1` (partition `0` in memory) without crashing callers (`normalizer.py:200-221`).
2. **Stream Sequence Gaps**: `SequenceAndGapDetector` inspects consecutive closed klines (`1m`/`5m` -> exact step, else `60m`), emits `DetectedStreamGap`, marks SQLite watermark `GAP_DETECTED`, and invokes `HistoricalRestBackfillWorker` to heal missing bars (`ws_service.py:72-90`).
3. **Out-of-Order Hot Cache Protection**: `HotStateProjector` and `REDIS_MONOTONIC_UPSERT_LUA` reject stale updates (`incoming_ts < current_ts`) and increment `dropped_out_of_order_count`.
4. **Upstream Rate Limits**: `TokenBucketRateLimiter` caps Binance REST weight at `80% * 1200 = 960/min`; `_request_with_retry` retries HTTP `429`/`418`/`>=500` up to 3 times (`Retry-After` capped at `1.0s`, exponential backoff `0.02 * 2^attempt`).
5. **Anomaly Alert Storms**: `StatisticalAnomalyDetector` enforces `900s` per-key cooldown (`agent:cooldown:{provider}:{symbol}:{detector}`).
6. **Atomic Local Parquet Writes**: Bronze, Silver, and Gold writers write `.tmp` siblings and atomically `replace()`.

## 3. Single Points of Failure & Open Scaling Questions

| Risk / Failure Scenario | Current Blast Radius (`AS-IS`) | Open Target / Gap |
|---|---|---|
| **Single Kafka Broker & Monolith Process** | Compose runs single KRaft node (`KAFKA_NODE_ID=1`); Broker 2 & 3 `UNAVAILABLE`. In-process dicts vanish if `backend-api` restarts without JSON snapshots. | Multi-broker KRaft & Redis/ClickHouse cluster sizing `[OPEN]`. |
| **Unbounded In-Memory Growth** | `PartitionedEventStreamingBroker._topics` appends indefinitely without log compaction or retention pruning; `ClickHouseBatchSink._trades_table` has no TTL sweep. | Live Kafka retention (`72h`/`7d`/`30d` conflict) and ClickHouse TTL. |
| **Backpressure & Queue Saturation** | No backpressure bound exists on `POST /market/ingest` or synchronous pipeline trigger; Compose defines zero container memory limits (`deploy.resources`). | Resource limits & throughput caps `[OPEN]`. |
