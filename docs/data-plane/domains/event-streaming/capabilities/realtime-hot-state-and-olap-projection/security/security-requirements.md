---
doc_id: CAP-DP-STR2-SEC-001
title: "Security Requirements: Hot Cache & OLAP Consumers"
doc_type: specification
plane: data-plane
scope_level: capability
domain: event-streaming
capability_id: CAP-DP-STR-002
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
    - ".env.example"
    - "src/serving/api/modules/analytics/presentation/router.py"
related_docs:
  - CAP-DP-STR2-TM-001
requirement_ids:
  - SEC-STR2-001
  - SEC-STR2-002
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Defined ClickHouse least-privilege DB role segregation and HTTP eviction/anomaly RBAC requirements."
---

# Security Requirements: Hot Cache & OLAP Consumers

## 1. Security Controls (`SEC-STR2-*`) `[REQUIRED]`

| Control ID | Security Requirement | Current State | Verification Target |
|---|---|---|---|
| `SEC-STR2-001` | Target ClickHouse queries from Application & Intelligence Planes MUST bind to read-only credentials (`CLICKHOUSE_API_READER_USER`, `CLICKHOUSE_AGENT_RO_USER`) separate from `CLICKHOUSE_INGEST_USER`. | Configured in `.env.example:48-54` only; unused in code | Container integration check (`OPEN`) |
| `SEC-STR2-002` | `POST /market/evict/{symbol}` and `POST /analytics/anomalies/evaluate` MUST require `OPERATOR`/`ADMIN` RBAC verification. | **FAILING (`SEC-AUDIT-003`)** | Blocked pending IAM auth enforcement |

## 2. Input & Lua Integrity Note

`_sync_record_to_live_redis` MUST NOT invoke `eval` with synthetic `last_price="0"` when an `ORDER_BOOK` event omits price fields.
