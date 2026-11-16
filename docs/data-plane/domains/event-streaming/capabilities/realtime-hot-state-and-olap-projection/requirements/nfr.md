---
doc_id: CAP-DP-STR2-NFR-001
title: "Non-Functional Requirements: Hot State & OLAP Projections"
doc_type: specification
plane: data-plane
scope_level: capability
domain: event-streaming
capability_id: CAP-DP-STR-002
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
    - "docker-compose.yml"
    - ".env.example"
    - "src/streaming/consumers/analytics_ch.py"
related_docs:
  - CAP-DP-STR2-SPEC-001
requirement_ids:
  - NFR-STR2-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Recorded configured TTL/eviction/batch constants vs unimplemented timers and OPEN latency SLAs."
---

# Non-Functional Requirements: Hot State & OLAP Projections

## 1. Configured Thresholds vs. Runtime Reality `[REQUIRED]`

| NFR ID | Attribute | Configured Settings (`docker-compose.yml` / `.env.example`) | `AS-IS` Reality & Open Targets |
|---|---|---|---|
| `NFR-STR2-001` | Cache Eviction & Batch Bounds | Redis `256mb`, `volatile-lru`, TTLs `300s`/`120s`; CH micro-batch `max_rows=5000`, `flush_interval_ms=1000`. | Timer `flush_interval_ms` is NOT implemented (`analytics_ch.py:137` checks row count only). Hot/OLAP read p95 SLOs remain `[OPEN]`. |

## 2. Volatility & Restart Risk

Without live Redis/ClickHouse backing (and with `ClickHouseBatchSink` persisting only klines to JSON), trades/tickers/hot prices in memory are lost on worker restart.
