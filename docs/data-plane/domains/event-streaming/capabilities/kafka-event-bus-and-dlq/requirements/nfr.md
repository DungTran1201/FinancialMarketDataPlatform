---
doc_id: CAP-DP-STR1-NFR-001
title: "Non-Functional Requirements: Kafka Event Bus"
doc_type: specification
plane: data-plane
scope_level: capability
domain: event-streaming
capability_id: CAP-DP-STR-001
status: DRAFT
implementation_status: SIMULATED
version: "2.0.0"
owner_role: devops-sre
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/streaming/infrastructure/kafka_broker.py"
    - "docker-compose.yml"
related_docs:
  - CAP-DP-STR1-SPEC-001
requirement_ids:
  - NFR-STR1-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Documented single-node Compose broker constraint and OPEN replication/latency targets."
---

# Non-Functional Requirements: Kafka Event Bus

## 1. Streaming Reliability & Capacity `[REQUIRED]`

| NFR ID | Attribute | Current Reality (`AS-IS`) | Target Status |
|---|---|---|---|
| `NFR-STR1-001` | Replication & Lag Alerting | Compose runs 1 KRaft broker (`replication_factor=1`, Broker 2/3 unavailable); `alerts.yml` fires critical lag alert at `fmdp_consumer_lag_records > 5000` for `2m`. | `[OPEN]` Multi-broker HA RF=3 and throughput msg/s SLA unapproved. |

## 2. Volatility Disclosure

In-memory `_topics` lists do not replicate or bound RAM usage on long runs (`GAP`).
