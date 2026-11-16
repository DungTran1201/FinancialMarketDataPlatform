---
doc_id: CAP-DP-STR1-COMP-001
title: "Component Design: Kafka Event Broker & Confluent Adapter"
doc_type: specification
plane: data-plane
scope_level: capability
domain: event-streaming
capability_id: CAP-DP-STR-001
status: IN_REVIEW
implementation_status: SIMULATED
version: "2.0.0"
owner_role: data-architect
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/streaming/infrastructure/kafka_broker.py"
    - "src/streaming/contracts/topics.py"
related_docs:
  - CAP-DP-STR1-SPEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Documented PartitionedEventStreamingBroker, ConfluentKafkaStreamingAdapter, and StreamBrokerPort mismatch."
---

# Component Design: Kafka Event Broker & Confluent Adapter

Derived DFD: [streaming-dfd.md](streaming-dfd.md) (`DIAG-DP-STR1-DFD-001`).

## 1. Internal Structure & Adapters `[REQUIRED]`

- `PartitionedEventStreamingBroker` (`kafka_broker.py:64`): Stores topic payloads in `self._topics: dict[str, list[dict]]` and offsets in `self._committed_offsets`, optionally persisting offsets to JSON `state_path`.
- `ConfluentKafkaStreamingAdapter` (`kafka_broker.py:20`): Configures idempotent producer (`acks: "all"`, `enable.idempotence: True`, `retries: 5`) and manual consumer config (`enable.auto.commit: False`, `isolation.level: "read_committed"`). Never instantiated in runtime (`_confluent_adapter=None`).

## 2. Known Contract & Implementation Deficits `[REQUIRED]`

- `StreamBrokerPort` (`topics.py:24-37`) declares synchronous method names (`consume_for_group`, `commit_offset`, `topic_lag`) that diverge from `PartitionedEventStreamingBroker` async/renamed methods (`poll_topic`, `commit_offsets`, `get_topic_lag`).
- If `_confluent_adapter` is enabled, `publish_event` serializes only `event.payload` rather than the full `EventEnvelopeV1` envelope (`kafka_broker.py:124-130`), and `publish_dlq` never forwards to Kafka.
