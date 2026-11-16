---
doc_id: CAP-DP-ING-ERR-001
title: "Error Catalog: Exchange Ingestion & Backfill"
doc_type: specification
plane: data-plane
scope_level: capability
domain: market-data-ingestion
capability_id: CAP-DP-ING-001
status: IN_REVIEW
implementation_status: IMPLEMENTED
version: "2.0.0"
owner_role: data-architect
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/ingestion/providers/binance/normalizer.py"
    - "src/ingestion/providers/binance/rest_client.py"
related_docs:
  - CAP-DP-ING-SPEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Cataloged ingestion exception types, DLQ error routing, and HTTP retry semantics."
---

# Error Catalog: Exchange Ingestion & Backfill

## 1. Error Classification Matrix `[REQUIRED]`

| Error / Exception | Trigger Condition | Handling / Destination | Retryable |
|---|---|---|---|
| `NormalizationError` | Unsupported Binance event type `"e"` or missing required `s` symbol (`normalizer.py:42-44,198`). | Caught by `normalize_or_route_dlq`; emits `DeadLetterEnvelopeV1` to `market.dlq.v1`. | No (poison message) |
| `ValueError` (`Decimal` / OHLC bounds) | Negative/zero trade price or quantity, or `high < low` (`market_events.py:67-100`). | Caught by `normalize_or_route_dlq`; emits `DeadLetterEnvelopeV1`. | No |
| HTTP `429` / `418` / `>=500` | Upstream Binance weight limit or transient server failure (`rest_client.py:136-139`). | Retries up to `max_retries=3` obeying capped `Retry-After`. | Yes |
| `RuntimeError` / `httpx.HTTPStatusError` | Exhausted REST retries or unhandled `4xx` response (`rest_client.py:155-158`). | Raised to worker/caller; watermark remains `BACKFILLING`/`GAP_DETECTED`. | Manual re-trigger |

## 2. Diagnostic & Monitoring Notes

All poison-message normalizer rejections increment `fmdp_dlq_events_total` and surface in `GET /api/v1/observability/traces?only_errors=true`.
