# Data Rule — Kafka Delivery, Consumer and Sink Semantics (`DATA-RULE-005`)

| Metadata | Value |
|---|---|
| **Rule ID** | `DATA-RULE-005` |
| **Rule Slug** | `kafka-consumer-delivery` |
| **Trigger Scope** | Kafka producers, consumer groups, topic partitioning, sinks, retry, DLQ, and replay |
| **Activation Mode** | `Always Active` |
| **Status** | `BASELINED` |
| **Updated Date** | `2026-11-12` |

---

## 1. Purpose & Scope

Governs Kafka producer durability, partition ordering, consumer offset commit boundaries, idempotent sink writes, and dead-letter routing across `consumer-hot-redis`, `consumer-analytics-ch`, and `consumer-lakehouse-bronze`.

## 2. Mandatory Directives

1. **Explicit Delivery Semantics**: State producer durability (`acks=all`, idempotence) and consumer delivery semantics (at-least-once + idempotent sink deduplication) for every path.
2. **Partition Ordering**: Use `compute_partition_key` (`{provider}:{symbol}` or `{provider}:{symbol}:{interval}`) aligned to the required ordering boundary.
3. **Commit-After-Write**: Persist to the external sink (Redis Lua monotonic check, ClickHouse micro-batch insert, or MinIO Parquet flush) before committing the corresponding Kafka offset.
4. **Poison Message & Backpressure Handling**: Implement bounded retries, dead-letter routing (`market.dlq.v1`), consumer lag telemetry, and replay procedures.

## 3. Prohibited Actions

- Do not claim platform-wide end-to-end exactly-once delivery based on Kafka broker settings alone.
- Do not auto-commit or manually commit offsets on message receipt before sink persistence succeeds.
- Do not silently discard failed records without routing to `market.dlq.v1` or quarantine.

## 4. Verification Mechanism

- Failure-injection and contract tests around sink writes, offset commits, duplicate delivery, and DLQ routing, plus `tools/validators/run_all.py`.

