---
doc_id: CAP-DP-ING-NFR-001
title: "Non-Functional Requirements: Exchange Ingestion"
doc_type: specification
plane: data-plane
scope_level: capability
domain: market-data-ingestion
capability_id: CAP-DP-ING-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: devops-sre
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/ingestion/application/ws_service.py"
    - "src/ingestion/providers/binance/rest_client.py"
related_docs:
  - CAP-DP-ING-SPEC-001
requirement_ids:
  - NFR-ING-001
  - NFR-ING-002
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Documented bounded reconnect/HTTP timeout constants vs OPEN live throughput SLA targets."
---

# Non-Functional Requirements: Exchange Ingestion

## 1. Ingestion Quality Targets `[REQUIRED]`

| NFR ID | Attribute | Metric / Formula (`AS-IS`) | Target Status |
|---|---|---|---|
| `NFR-ING-001` | Reconnect & HTTP Resilience | `compute_reconnect_backoff_seconds`: `min(60, 1 * 2^attempt) + jitter`; REST `timeout=10.0s`, `max_retries=3`, weight cap `80%`. | Implemented formulas (`OPEN`: continuous 24/7 uptime % & MTTR targets). |
| `NFR-ING-002` | Backfill Chunking & Live Latency | Pagination chunk capped at `max_page_size=500` bars/request. | `[OPEN]` Max acceptable backfill duration & live WS ingest-to-Kafka p95 latency unapproved. |

## 2. Measurement Conditions

Current checks execute against the embedded ASGI exchange simulator rather than live Binance public endpoints.
