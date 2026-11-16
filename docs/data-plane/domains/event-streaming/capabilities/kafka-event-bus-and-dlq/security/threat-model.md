---
doc_id: CAP-DP-STR1-TM-001
title: "Threat Model: Kafka Event Bus & DLQ"
doc_type: specification
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
  is_authoritative: true
  authoritative_source:
    - "src/streaming/infrastructure/kafka_broker.py"
    - "docker-compose.yml"
related_docs:
  - CAP-DP-STR1-SEC-001
  - DIAG-DP-STR1-TM-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Analyzed PLAINTEXT broker transport, unauthenticated poison injection via API, and offset/memory exhaustion."
---

# Threat Model: Kafka Event Bus & DLQ

Derived threat diagram: [threat-model-diagram.md](threat-model-diagram.md) (`DIAG-DP-STR1-TM-001`).

## 1. Assets, Actors & Trust Boundaries `[REQUIRED]`

- **Assets**: Ordered raw event log, `market.dlq.v1`, consumer group commit state.
- **Trust Boundaries**: Internal bridge `data_plane_net` (`docker-compose.yml:565`) and FastAPI `POST /market/ingest` (`SEC-AUDIT-003`).

## 2. Threat Scenarios, Mitigations & Residual Risks `[REQUIRED]`

| Threat ID | Scenario & Entry Point | Severity | Current Mitigations / Gaps | Residual Risk |
|---|---|---|---|---|
| `THR-STR1-001` | Unauthenticated caller floods `POST /market/ingest` exhausting in-memory `_topics` RAM. | `HIGH` | Rate limiter limits `120r/m` per IP (bypassable via `SEC-AUDIT-004`); zero endpoint auth (`SEC-AUDIT-003`). | `HIGH` (`BLOCKED`) |
| `THR-STR1-002` | Plaintext Kafka listener (`PLAINTEXT://:9092`) without SASL/TLS on `data_plane_net`. | `MEDIUM` | Docker bridge network isolates host (`127.0.0.1:9092`); zero SASL/ACL in Compose. | `MEDIUM` (`OPEN` for multi-host deployment) |
| `THR-STR1-003` | Poison messages halt streaming consumers. | `LOW` | `DeadLetterEnvelopeV1` routes invalid records to `market.dlq.v1`. | `LOW` (`test_gap_recovery_and_dlq.py`) |
