---
doc_id: CAP-DP-STR1-SEC-001
title: "Security Requirements: Kafka Event Bus & DLQ"
doc_type: specification
plane: data-plane
scope_level: capability
domain: event-streaming
capability_id: CAP-DP-STR-001
status: DRAFT
implementation_status: SIMULATED
version: "2.0.0"
owner_role: security-architect
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/streaming/infrastructure/kafka_broker.py"
    - "docker-compose.yml"
related_docs:
  - CAP-DP-STR1-TM-001
requirement_ids:
  - SEC-STR1-001
  - SEC-STR1-002
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Defined event integrity and target Kafka SASL/TLS requirements."
---

# Security Requirements: Kafka Event Bus & DLQ

## 1. Security Controls `[REQUIRED]`

| Control ID | Security Requirement | Current Reality | Target Verification |
|---|---|---|---|
| `SEC-STR1-001` | Event producers MUST emit validated `EventEnvelopeV1` or isolate malformed messages to `market.dlq.v1` without executing deserialized code (`json.loads` only). | `IMPLEMENTED` in `normalizer.py` + `kafka_broker.py` | Verified in `test_three_planes_framework.py` |
| `SEC-STR1-002` | Production Kafka brokers outside single-host Docker bridge MUST enforce SASL/SCRAM + TLS and producer/consumer topic ACLs. | `NOT_IMPLEMENTED` (`PLAINTEXT` in `docker-compose.yml:76-81`) | `[OPEN]` Infrastructure security milestone |

## 2. API Exposure Dependency

All HTTP endpoints producing directly to `PartitionedEventStreamingBroker` depend on `CAP-APP-IAM-001` remediation (`SEC-AUDIT-003`).
