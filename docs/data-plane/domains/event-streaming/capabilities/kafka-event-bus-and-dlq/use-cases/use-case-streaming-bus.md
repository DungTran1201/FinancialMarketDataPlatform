---
doc_id: CAP-DP-STR1-UC-001
title: "Use Case: Publish, Poll & Commit Consumer Offsets Safely"
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
related_docs:
  - CAP-DP-STR1-SPEC-001
requirement_ids:
  - UC-STR1-001
  - AC-STR1-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Authored publish/poll/commit/DLQ use case matching in-memory PartitionedEventStreamingBroker."
---

# Use Case: `UC-STR1-001` — Publish, Poll & Commit Consumer Offsets Safely

## 1. Identification & Traceability `[REQUIRED]`

- **Use Case ID**: `UC-STR1-001`
- **Primary Actor**: Data Plane Producer (`WebSocketStreamCollector`, `HistoricalRestBackfillWorker`, `StatisticalAnomalyDetector`) & Consumer Groups (`cg.*`)
- **Parent Requirements**: `FR-STR1-001`..`003` (`RULE-STR1-001`, `RULE-STR1-002`)

## 2. Trigger, Preconditions & Postconditions `[REQUIRED]`

- **Trigger**: Producer awaits `publish_event(topic, envelope)` or `publish_dlq(dlq)`, or consumer group polls & commits offsets.
- **Preconditions**: Broker initialized with 6 partitions.
- **Success Postconditions**: Envelope stored at partitioned offset; `get_topic_lag(topic, group)` equals `0` after `commit_offsets()`.
- **Failure Postconditions**: Deduplication drop increments `duplicate_drops_count` (`deduplicate_events=True`); failed downstream sink skips commit so lag preserves uncommitted offset.

## 3. Main Success & Alternative Flows `[REQUIRED]`

1. Producer calls `resolve_topic_for_event(ev)` and awaits `publish_event(topic, ev)`.
2. Consumer calls `poll_topic(topic, consumer_group)` receiving un-committed envelopes since group's last offset.
3. Downstream sink writes data; consumer calls `commit_offsets(topic, consumer_group, next_offset)` -> `get_topic_lag` returns `0`.

| Branch ID | Condition | Behavior | Result |
|---|---|---|---|
| `ALT-1` | Duplicate `event_id` with `deduplicate_events=True` | Increments `_duplicate_drops` and skips append (`kafka_broker.py:102-108`). | Deduplicated |
| `EXC-1` | Poison payload | Routed to `publish_dlq(dlq)` (`partition=0` of `market.dlq.v1`). | Isolated in DLQ |

- **Acceptance Criteria (`AC-STR1-001`)**: Publishing duplicate `event_id` increments `duplicate_drops_count == 1`; polling + committing drops group lag to `0` (`test_data_platform_v01_e2e.py`, `test_three_planes_framework.py`).
