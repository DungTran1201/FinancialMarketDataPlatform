---
doc_id: CAP-DP-STR1-ERR-001
title: "Error Catalog: Kafka Event Bus & DLQ"
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
    - "src/streaming/infrastructure/kafka_broker.py"
related_docs:
  - CAP-DP-STR1-SPEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Cataloged Confluent adapter fallback, duplicate event drop, and DLQ handling."
---

# Error Catalog: Kafka Event Bus & DLQ

## 1. Error & Failure Semantics `[REQUIRED]`

| Condition | Code Path | Runtime Behavior | Remediation |
|---|---|---|---|
| **Live Kafka Unavailable (`publish_serialized`)** | `kafka_broker.py:47-61` | Returns `False` without raising; in-memory broker list still retains event. | Wire retry/alert metric when live Kafka becomes mandatory. |
| **Duplicate `event_id`** | `kafka_broker.py:102-108` | Increments `_duplicate_drops` cleanly when `deduplicate_events=True`. | Safe idempotent drop. |

## 2. Monitoring Integration

DLQ growth increments `fmdp_dlq_events_total`, triggering `FMDPDeadLetterQueueSpike` in `alerts.yml`.
