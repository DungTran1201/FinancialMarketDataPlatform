---
doc_id: "ARCH-ADR-002"
title: "ADR-0002: NATS JetStream as Persistent Event Log & Backpressure Bus"
version: "1.0.0"
status: "IN_REVIEW"
implementation_status: "PLANNED"
owner: "Distributed Systems Engineer & Streaming Data Engineer"
purpose: "Justifies selecting NATS JetStream over Kafka, Redis Streams, and in-memory queues for durable event delivery on 8 GB hardware."
scope: "Inter-process persistent messaging (`CAP-DP-STR`)."
dependencies:
  - "docs/architecture/technology-evaluation-matrix.md"
references:
  - "docs/testing-and-operations/phase-2-poc-benchmark-plan.md"
assumptions:
  - "Containerized NATS JetStream passes PoC connectivity, ACK/redelivery, restart persistence, and <=256 MB RAM checks."
open_issues:
  - "Confirm Windows Docker bind/named volume flush latency during WI-P2-003."
review_criteria:
  - "Supported by WI-P2-003 empirical throughput, latency, replay, and crash measurements"
---

# ADR-0002: NATS JetStream for Persistent Event Delivery

## Context

Section 3.4 requires a persistent messaging system with durable delivery, explicit consumer acknowledgement, replay, and slow-consumer recovery — while prohibiting bare in-memory pub/sub and discouraging heavyweight Kafka on 8 GB hardware.

## Options Considered

1. **Apache Kafka**: Rejected (§3.4 + multi-GB JVM/KRaft overhead).
2. **Redis Streams + AOF**: Fast, **rejected** because streams remain memory-resident, creating OOM risk when holding multi-hour replay logs on `8 GB` RAM.
3. **NATS JetStream FileStore (Selected Proposal)**: Single Go binary (~20 MB Docker image), configurable disk `max_bytes` retention, pull-based consumer backpressure (`max_ack_pending`), explicit `Ack`/`Nak`, `MaxDeliver` poison-message routing, built-in `Nats-Msg-Id` dedup window.

## Decision

Evaluate and adopt **NATS JetStream** inside a memory-capped container (`<= 256 MB`), running `BusPort` protocol adapters so business consumers remain transport-agnostic.

## Consequences

- **Positive**: Disk-backed durability & replay under `150 MB` RAM; native pull backpressure protects consumer processes.
- **Negative**: Requires explicit Docker volume persistence and poison-message DLQ bridge code on `MaxDeliver` exhaustion (verified in Phase 2 PoC).
