---
doc_id: CAP-DP-STR1-SPEC-001
title: "Capability Specification: Kafka Event Bus & DLQ"
doc_type: specification
plane: data-plane
scope_level: capability
domain: event-streaming
capability_id: CAP-DP-STR-001
status: IN_REVIEW
implementation_status: SIMULATED
version: "2.0.0"
owner_role: data-architect
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/streaming/contracts/topics.py"
    - "src/streaming/infrastructure/kafka_broker.py"
related_docs:
  - CAP-DP-STR-001-ROOT
requirement_ids:
  - FR-STR1-001
  - FR-STR1-002
  - FR-STR1-003
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Documented topic partitioning, manual consumer-group commit offsets, DLQ routing, and in-memory vs Confluent adapter status."
---

# Capability Specification: Kafka Event Bus & DLQ

## 1. Capability Scope & `AS-IS` Reality `[REQUIRED]`

Provides partitioned event streaming across the 6 canonical topics in [asyncapi.yaml](../../../../../shared-contracts/asyncapi.yaml) (`market.raw.{trades,klines,tickers,orderbook}.v1`, `market.anomalies.v1`, `market.dlq.v1`) and tracks offsets per consumer group. Executes `AS-IS` in memory via `PartitionedEventStreamingBroker`.

## 2. Functional Requirements `[REQUIRED]`

| Req ID | Requirement Statement | `AS-IS` Evidence | Target / Gap |
|---|---|---|---|
| `FR-STR1-001` | Broker MUST route `EventEnvelopeV1` events by `{provider}:{symbol}` partition key across `num_partitions=6` preserving per-symbol order. | `kafka_broker.py:87-131` (`IN_PROCESS_PARTITIONED_BROKER`) | Real KRaft cluster configured (`kafka:9092`), unused at runtime |
| `FR-STR1-002` | Broker MUST track per-consumer-group offsets manually (`poll_topic`, `commit_offsets`) only advancing after sink persistence succeeds. | `kafka_broker.py:151-193` | Zero `confluent_kafka.Consumer` loop wired |
| `FR-STR1-003` | Broker MUST isolate malformed events into `market.dlq.v1` and expose per-topic lag telemetry without dropping poison messages silently. | `kafka_broker.py:133-149, 211-370` | `publish_dlq` does not forward to `_confluent_adapter` |
