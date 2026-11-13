---
name: kafka-event-streaming
description: "Design and implement versioned Kafka event contracts, topic partitioning, producer durability, consumer offset safety, backpressure, DLQ and replay."
---

# Skill: Kafka Event Streaming & Consumer Delivery (`SKILL-024`)

## 1. Description

Design and implement versioned Kafka event contracts, topic partitioning, producer durability, consumer offset safety, backpressure, DLQ routing, and replay.

## 2. Trigger Conditions

- Use for Kafka topics (`KafkaTopic`), producers, consumer groups (`consumer-hot-redis`, `consumer-analytics-ch`, `consumer-lakehouse-bronze`), partitioning, serialization, retries, offset handling, dead-letter routing (`market.dlq.v1`), or streaming sink changes.
- Invoked by Agent roles `streaming-data-engineer` and `data-engineer`.

## 3. Authoritative Inputs

- `AGENTS.md` and target directory `README.md`
- `src/shared/contracts/events.py` (`EventEnvelopeV1`, `DeadLetterEnvelopeV1`, `KafkaTopic`)
- `docs/architecture/08-data-flow-and-event-contracts.md` and `docs/architecture/adr/ADR-002-event-driven-data-platform.md`
- `src/consumers/` and `docker-compose.yml`

## 4. Preconditions

1. Target directory `README.md` has been read in full.
2. Delivery semantics per sink path, partition key (`compute_partition_key`), consumer group, and sink commit boundary have been documented.

## 5. Execution Procedure

1. Define versioned topic name (`KafkaTopic`), event schema (`EventEnvelopeV1`), partition key, partition count, and schema compatibility policy.
2. Select partition key from required ordering scope (`{provider}:{symbol}` or `{provider}:{symbol}:{interval}`) and verify load distribution.
3. Configure producer acknowledgements (`acks=all`), idempotence, retries, and delivery timeouts.
4. Implement consumer poll lifecycle, bounded micro-batching, rebalance handling, and graceful shutdown (`src/consumers/`).
5. Persist to the external sink first and commit the Kafka offset only after confirmed durable write completion; design deterministic sink idempotency (`UUIDv5` event IDs, Lua monotonic checks, `ReplacingMergeTree`).
6. Route malformed or poison records to `market.dlq.v1` (`DeadLetterEnvelopeV1`) with sanitized failure metadata.
7. Add consumer lag, processing latency, retry, and DLQ telemetry, then run `tools/validators/run_all.py`.

## 6. Output Artifacts

- Topic/event contract specifications (`src/shared/contracts/events.py`, `docs/specifications/data-contracts.md`), consumer implementations (`src/consumers/`), unit/contract tests (`tests/`), and replay runbooks.

## 7. Validation

```powershell
python tools/validators/run_all.py
python -m unittest discover -s tests -v
```

## 8. Failure Handling

- Pause or apply backpressure to consumers when sinks are degraded, retain source offsets, quarantine poison messages to `market.dlq.v1`, and never silently skip failed records.

## 9. Restrictions

- Do not claim end-to-end exactly-once semantics based on Kafka broker configuration alone.
- Do not place unbounded values in Prometheus metric labels.
- Do not mix incompatible schema versions on the same topic version.

## 10. Related Skills

- `financial-market-data-ingestion`
- `lakehouse-medallion`
- `dataops-observability`
- `data-platform-testing-recovery`

