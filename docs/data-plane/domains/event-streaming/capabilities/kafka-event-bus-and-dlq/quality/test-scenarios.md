---
doc_id: CAP-DP-STR1-TS-001
title: "Test Scenarios: Kafka Event Bus & DLQ"
doc_type: specification
plane: data-plane
scope_level: capability
domain: event-streaming
capability_id: CAP-DP-STR-001
status: IN_REVIEW
implementation_status: SIMULATED
version: "2.0.0"
owner_role: qa-lead
accountable_role: qa-lead
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "tests/contract/test_topic_and_dataset_contracts.py"
    - "tests/integration/test_three_planes_framework.py"
    - "tests/e2e/test_data_platform_v01_e2e.py"
related_docs:
  - CAP-DP-STR1-SPEC-001
requirement_ids:
  - TS-STR1-001
  - TS-STR1-002
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: qa-lead
    summary: "Recorded topic partition, commit lag, duplicate drop, and DLQ test scenarios."
---

# Test Scenarios: Kafka Event Bus & DLQ

## 1. Test Scenario Matrix `[REQUIRED]`

| Scenario ID | Linked FR | Preconditions | Test Action | Expected Outcome | Environment |
|---|---|---|---|---|---|
| `TS-STR1-001` | `FR-STR1-001`, `FR-STR1-002` | Clean `PartitionedEventStreamingBroker` | Publish trade events -> poll for `cg.hot.redis.v1` -> commit offsets. | Same `{provider}:{symbol}` maps to deterministic partition; `get_topic_lag == 0` post-commit. | In-memory (`test_three_planes_framework.py`) |
| `TS-STR1-002` | `FR-STR1-001`, `FR-STR1-003` | `deduplicate_events=True` | Publish duplicate `event_id` and invalid trade (`publish_dlq`). | `duplicate_drops_count == 1`; `dlq_events` captures malformed payload. | In-memory (`test_data_platform_v01_e2e.py`, `test_topic_and_dataset_contracts.py`) |

## 2. Environment Disclosure

Tests verify Python `PartitionedEventStreamingBroker` semantics only; live `confluent_kafka` broker integration has zero test coverage (`GAP-QA-001`).
