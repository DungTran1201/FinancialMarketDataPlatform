# ADR-002: Event-Driven Data Platform & Streaming vs. Batch Processing Boundaries

- **Status**: Accepted
- **Date**: 2026-11-12
- **Deciders**: Data Platform Architecture Team

---

## 1. Decision Title

Use **Apache Kafka** as the central event streaming backbone with **at-least-once delivery + idempotent consumers**, lightweight Python streaming consumers for hot/analytical ingestion, **PySpark** strictly for batch Lakehouse processing, **dbt Core** for SQL data modeling, and **Apache Airflow** strictly for batch workflow orchestration.

---

## 2. Context

Financial market data arrives both as continuous high-frequency WebSocket streams (trades, tickers, klines, order book updates) and as bounded historical datasets via REST APIs. Downstream consumers have vastly different latency and compute profiles:
- Redis needs immediate state updates ($<500\text{ ms}$).
- ClickHouse needs micro-batched columnar inserts ($1-5\text{ s}$).
- MinIO/Iceberg needs larger compacted Parquet files ($5-15\text{ m}$ or hourly/daily batches).
- Curated analytical models require reproducible SQL transformations and data quality validation.

---

## 3. Problem Statement

How do we ingest, distribute, and process real-time and historical market events without coupling producers to consumers, without routing every streaming event through heavy batch engines (Spark/Airflow), and without duplicating transformation logic across Python, Spark, and dbt?

---

## 4. Selected Option

1. **Event Streaming Backbone (Apache Kafka)**:
   - Collectors normalize Binance payloads into canonical `EventEnvelopeV1` contracts and publish to topic-per-entity streams (`market.raw.trades.v1`, `market.raw.klines.v1`, `market.raw.tickers.v1`, `market.raw.orderbook.v1`) partitioned by `{provider}:{symbol}`.
2. **Delivery Guarantee (At-Least-Once + Idempotency)**:
   - Producers use `acks=all` and `enable.idempotence=true`.
   - Consumers commit offsets manually **only after** target storage acknowledgement and implement deterministic deduplication (`event_id` / `exchange_event_time`).
3. **Strict Processing Engine Separation**:
   - **Lightweight Python Async Consumers**: Handle low-latency `Kafka -> Redis` (Hot Path) and micro-batched `Kafka -> ClickHouse` (Analytics Path).
   - **Apache Spark (PySpark)**: Restricted to batch/micro-batch Lakehouse operations: `Bronze -> Silver` deduplication, schema enforcement, historical backfill merging, and Iceberg table compaction. Never invoked per streaming event or per synchronous API request.
   - **dbt Core**: Owns SQL-based analytical transformations (`Silver -> Gold` business models and ClickHouse analytical marts).
   - **Apache Airflow**: Orchestrates scheduled batch pipelines (REST historical backfills, PySpark Bronze-to-Silver jobs, dbt runs, Great Expectations suites, and Iceberg maintenance). Never used to process individual streaming events.

---

## 5. Alternative Options Considered

### Alternative A: Spark Structured Streaming for All Real-Time Paths (Including Redis & ClickHouse)
- **Description**: Route all Kafka topics through long-running PySpark Structured Streaming jobs to update Redis and ClickHouse.
- **Rejection Reason**: Violates Constraint 8 ("Spark must not become the default processing path for every incoming real-time event") and Section 9.5. JVM/Spark micro-batch overhead adds unnecessary latency ($2-10\text{ s}$) to the Hot Path and consumes excessive memory ($4-8\text{ GB}$ minimum) for simple state projections that lightweight Python consumers handle in $<100\text{ MB}$.

### Alternative B: Deploy Both Apache Flink and Apache Spark
- **Description**: Use Apache Flink for stateful stream processing and Apache Spark for batch Lakehouse processing.
- **Rejection Reason**: Violates Constraint 2 ("Do not deploy both Spark and Flink in the initial architecture"). Operating two heavy JVM distributed compute frameworks simultaneously in Docker Compose creates severe operational and memory overhead without a demonstrated stateful multi-stream join requirement that ClickHouse Materialized Views and Python consumers cannot satisfy.

### Alternative C: End-to-End Distributed Exactly-Once Transactions Across Kafka, Redis, ClickHouse, and MinIO
- **Description**: Attempt two-phase commit or transactional coordination across all sinks.
- **Rejection Reason**: Violates Section 9.2. Neither Redis, ClickHouse, nor object storage participates in Kafka's internal transactional coordinator cleanly without extreme latency penalties. At-least-once delivery combined with monotonic timestamp checks (Redis), `ReplacingMergeTree` (ClickHouse), and Iceberg `MERGE INTO` (Silver) provides deterministic correctness with far lower complexity.

---

## 6. Decision Rationale

Each engine is used strictly where its architecture excels:
- **Kafka** provides durable buffered fan-out, replayability, and partition-level ordering per symbol.
- **Python consumers** provide sub-50ms event handling for Redis and efficient 1-second micro-batching for ClickHouse.
- **PySpark** handles large-volume columnar Parquet/Iceberg rewrites and backfills where distributed DataFrame operations shine.
- **dbt Core** centralizes business metric SQL definitions under version control with built-in lineage and tests.

---

## 7. Benefits

- **No Transformation Duplication**:
  - Normalization happens once in Collectors (`Raw Exchange -> Canonical Envelope`).
  - Deduplication/Standardization happens once in Silver (`PySpark` for Lakehouse; `ReplacingMergeTree` for ClickHouse).
  - Business aggregations happen in SQL (`ClickHouse Materialized Views` for real-time; `dbt` for curated Gold marts).
- **Replay & Recovery**: Kafka retention (24h–72h) and Bronze Lakehouse archives allow rebuilding Redis or ClickHouse projections from scratch without re-querying Binance APIs.

---

## 8. Drawbacks

- Requires managing Kafka consumer group offsets, dead-letter queues (`market.dlq.v1`), and schema compatibility discipline.
- Eventual consistency delay ($1-5\text{ s}$) between Redis hot cache and ClickHouse analytical tables.

---

## 9. Architectural Limitations

- Ordering is guaranteed **only within a single Kafka partition** (`{provider}:{symbol}`). Cross-symbol global ordering is not guaranteed by Kafka partition offsets and must rely on normalized `exchange_event_time` timestamps.
- Duplicate events will occur during collector reconnects or consumer rebalances; every downstream sink must tolerate duplicates.

---

## 10. Operational Implications

- Consumer lag (`kafka_consumer_group_lag`) must be scraped by Prometheus and alerted on when lag exceeds threshold windows.
- ClickHouse consumers must buffer events in memory up to `max_batch_size=5000` or `flush_interval_ms=1000` before issuing a single bulk `INSERT` to prevent ClickHouse `Too many parts` errors.

---

## 11. Consequences

- Collectors and Consumers share a single canonical Pydantic contract package (`src/shared/contracts/`) so schema validation is identical at producer and consumer boundaries.
- Airflow DAGs trigger containerized jobs (`PySpark`, `dbt`, `Great Expectations`) rather than executing heavy data processing inside the Airflow scheduler/worker process itself.

---

## 12. Conditions That Could Invalidate This Decision

1. If sub-second complex stateful stream joins across dozens of symbols with sliding event-time watermarks become a primary requirement, a dedicated stateful stream processor would need to be evaluated via a superseding ADR.
2. If symbol count exceeds several thousand pairs with full L2 order book ticks on a single node, Python collector/consumer serialization may require Rust/Go collectors or partitioned worker sharding.

