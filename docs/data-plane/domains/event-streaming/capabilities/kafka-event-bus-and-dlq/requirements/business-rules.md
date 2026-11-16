---
doc_id: CAP-DP-STR1-RULE-001
title: "Business Rules: Partitioning, Offsets & DLQ Retention"
doc_type: specification
plane: data-plane
scope_level: capability
domain: event-streaming
capability_id: CAP-DP-STR-001
status: IN_REVIEW
implementation_status: SIMULATED
version: "2.0.0"
owner_role: business-analyst
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/streaming/infrastructure/kafka_broker.py"
    - "deploy/kafka/topics-init.sh"
related_docs:
  - CAP-DP-STR1-SPEC-001
requirement_ids:
  - RULE-STR1-001
  - RULE-STR1-002
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Defined partitioning and retention rules across Kafka broker and topics-init.sh."
---

# Business Rules: Partitioning, Offsets & DLQ Retention

## 1. Domain Rules `[REQUIRED]`

| Rule ID | Condition / Formula | Consequence | Related FR |
|---|---|---|---|
| `RULE-STR1-001` | Partition index = `hash(f"{provider.lower()}:{symbol.upper()}") % 6`; all trades and klines for one symbol route deterministically to one partition in-process. | Note: Python `hash()` randomizes across OS restarts; live Confluent producer relies on Kafka string key hashing. | `FR-STR1-001` |
| `RULE-STR1-002` | Offset commits MUST remain manual (`enable.auto.commit: False` in `ConfluentKafkaStreamingAdapter`); DLQ events target `market.dlq.v1`. | Prevents silent message loss on downstream sink crash. | `FR-STR1-002`, `FR-STR1-003` |

## 2. Configured Topic Retention (`topics-init.sh`)

- Raw market topics (`market.raw.*.v1`): `6` partitions, `604800000 ms` (`7d`). Anomaly & DLQ topics: `3` partitions, `2592000000 ms` (`30d`).
