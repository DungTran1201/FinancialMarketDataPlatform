---
name: kafka-event-streaming
description: Versioned Kafka envelopes, partitioning, consumer offsets, backpressure, and DLQ routing.
---

# Skill: Kafka Event Streaming & Consumer Delivery (`SKILL-024`)

## 1. Description

Design and implement versioned Kafka event contracts (`EventEnvelopeV1`), topic partitioning, producer durability, commit-after-write consumer offset safety, backpressure, DLQ routing (`market.dlq.v1`), and replay.

## 2. Trigger Conditions

- Kafka topics, producers, consumer groups (`consumer-hot-redis`, `consumer-analytics-ch`, `consumer-lakehouse-bronze`), partitioning, serialization, retries, offset handling, DLQ routing, or streaming sink changes (`streaming-data-engineer`, `data-engineer`).

## 3. Authoritative Inputs

- `AGENTS.md`, target `README.md`, `src/shared/contracts/events/market_events.py` (`EventEnvelopeV1`), `src/streaming/contracts/topics.py`, `docs/architecture/08-data-flow-and-event-contracts.md`, `ADR-002`, `src/streaming/`, `docker-compose.yml`.

## 4. Preconditions

1. Target `README.md` read; delivery semantics per sink path, partition key (`{provider}:{symbol}`), consumer group, and sink commit boundary documented.

## 5. Execution Procedure

1. Define versioned topic name (`KafkaTopic`), event schema (`EventEnvelopeV1`), partition key, partition count, and schema compatibility policy.
2. Select partition key from required ordering scope (`{provider}:{symbol}` or `{provider}:{symbol}:{interval}`) and verify load distribution.
3. Configure producer acknowledgements (`acks=all`), idempotence, retries, and delivery timeouts.
4. Implement consumer poll lifecycle, bounded micro-batching, rebalance handling, and graceful shutdown (`src/streaming/consumers/`).
5. Persist to the external sink first and commit the Kafka offset only after confirmed durable write completion; design deterministic sink idempotency (`UUIDv5` event IDs, Lua monotonic checks, `ReplacingMergeTree`).
6. Route malformed or poison records to `market.dlq.v1` (`DeadLetterEnvelopeV1`) with sanitized failure metadata.
7. Add consumer lag, processing latency, retry, and DLQ telemetry, then run `tools/validators/run_all.py`.

## 6. Output Artifacts

- Topic/event contract specifications (`src/shared/contracts/events/market_events.py`, `src/streaming/contracts/topics.py`, `docs/specifications/data-contracts.md`), consumer implementations (`src/streaming/consumers/`), unit/contract tests (`tests/`), and replay runbooks.

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

