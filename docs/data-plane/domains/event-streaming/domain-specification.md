---
doc_id: DP-DOM-STR-SPEC-001
title: "Domain Specification: Event Streaming"
doc_type: specification
plane: data-plane
scope_level: domain
domain: event-streaming
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
    - "src/streaming/consumers/"
related_docs:
  - DP-DOM-STR-001
  - DP-CTR-ROOT-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Defined event-streaming domain ownership separating broker log mechanics from downstream projection/anomaly consumers."
---

# Domain Specification: Event Streaming

## 1. Bounded Context & Owned Assets `[REQUIRED]`

Manages the 6 canonical topics (`ALL_CANONICAL_TOPICS`) and 4 consumer groups (`CG_HOT_REDIS`, `CG_ANALYTICS_CH`, `CG_LAKEHOUSE_BRONZE`, `CG_ANOMALY_DETECTOR`) bridging ingestion and real-time serving / analytical consumers. Canonical schemas live in [asyncapi.yaml](../../shared-contracts/asyncapi.yaml) and [data-contract.yaml](../../shared-contracts/data-contract.yaml).

## 2. Capability Split Rationale

- `CAP-DP-STR-001` isolates topic routing, partitioning (`hash(partition_key) % 6`), offset commit state, and DLQ handling.
- `CAP-DP-STR-002` isolates stateful projections (`HotStateProjector`, `ClickHouseBatchSink`) and statistical z-score detection (`StatisticalAnomalyDetector`), whose backing stores (`redis`, `clickhouse`) require distinct storage models.
