---
doc_id: DIAG-DP-STR1-TM-001
title: "Diagram: Kafka Event Bus Trust Boundaries"
doc_type: diagram
plane: data-plane
scope_level: capability
domain: event-streaming
capability_id: CAP-DP-STR-001
status: IN_REVIEW
implementation_status: SIMULATED
version: "2.0.0"
owner_role: security-architect
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/data-plane/domains/event-streaming/capabilities/kafka-event-bus-and-dlq/security/threat-model.md"
related_docs:
  - CAP-DP-STR1-TM-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Derived trust boundary diagram for Kafka Event Bus & DLQ."
---

# Diagram: Kafka Event Bus Trust Boundaries

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-DP-STR1-TM-001` |
| **Title & Purpose** | Shows trust boundaries around broker ingestion, in-memory topic lists, and target PLAINTEXT KRaft network |
| **Owner Role & Scope** | `security-architect / CAP-DP-STR-001` |
| **Authoritative Source** | [threat-model.md](threat-model.md) (`CAP-DP-STR1-TM-001`) |
| **Notation** | `Mermaid flowchart TB` (`Trust Boundary DFD`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram `[REQUIRED]`

```mermaid
flowchart TB
    api_ingest["POST /api/v1/market/ingest [GAP: SEC-AUDIT-003]"]

    subgraph tb_dp["Trust Boundary: data_plane_net / In-Memory Bus"]
        norm["Normalizer Validation Gate [SEC-STR1-001]"]
        bus["PartitionedEventStreamingBroker [In-Memory]"]
        kaf["TARGET Kafka :9092 [GAP: PLAINTEXT No SASL]"]
    end

    api_ingest -->|"THR-STR1-001: Flood Risk"| norm
    norm -->|"Validated Envelope / DLQ"| bus
    bus -.->|"THR-STR1-002: Payload Only"| kaf
```

## 3. Legend `[REQUIRED]`

- **Dashed Arrow (`-.->`)**: Uninstantiated Confluent producer bridge (`_confluent_adapter`).
