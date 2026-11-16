---
doc_id: DP-DOM-STR-001
title: "Domain: Event Streaming"
doc_type: index
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
    - "src/streaming/"
related_docs:
  - DP-ROOT-001
  - DP-DOM-STR-SPEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Registered event-streaming Data Plane domain and capabilities CAP-DP-STR-001 and CAP-DP-STR-002."
---

# Domain: Event Streaming

Owns the canonical Kafka topic bus, `{provider}:{symbol}` partitioning, DLQ routing, monotonic hot cache projection, ClickHouse batch micro-aggregation, and statistical anomaly alert emission (`src/streaming/`).

- [domain-specification.md](domain-specification.md) (`DP-DOM-STR-SPEC-001`)
- Capabilities:
  - `CAP-DP-STR-001`: [kafka-event-bus-and-dlq](capabilities/kafka-event-bus-and-dlq/README.md) (`SIMULATED` — In-process `PartitionedEventStreamingBroker`)
  - `CAP-DP-STR-002`: [realtime-hot-state-and-olap-projection](capabilities/realtime-hot-state-and-olap-projection/README.md) (`SIMULATED` — In-memory dicts; live Redis/CH unused)
