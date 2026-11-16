---
doc_id: CAP-DP-ING-RULE-001
title: "Business Rules: Exchange Ingestion Precision, Weight & Gap Rules"
doc_type: specification
plane: data-plane
scope_level: capability
domain: market-data-ingestion
capability_id: CAP-DP-ING-001
status: IN_REVIEW
implementation_status: IMPLEMENTED
version: "2.0.0"
owner_role: business-analyst
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/ingestion/providers/binance/normalizer.py"
    - "src/ingestion/application/rate_limiter.py"
    - "src/shared/contracts/events/market_events.py"
related_docs:
  - CAP-DP-ING-SPEC-001
requirement_ids:
  - RULE-ING-001
  - RULE-ING-002
  - RULE-ING-003
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Documented deterministic ingestion invariants and violation actions from verified source code."
---

# Business Rules: Exchange Ingestion Precision, Weight & Gap Rules

## 1. Domain Business Rules `[REQUIRED]`

| Rule ID | Condition / Formula | Context | Violation Consequence | Related FR |
|---|---|---|---|---|
| `RULE-ING-001` | Prices (`p`, `o`, `h`, `l`, `c`), quantities (`q`, `v`), `bid`/`ask` levels MUST be finite positive/non-negative `Decimal` strings (`high >= low`, `open/close in [low, high]`); `ingested_at` MUST be timezone-aware UTC; `s` MUST be non-empty. | `normalizer.py:32-198`, `market_events.py:55-126` | Raises `NormalizationError` / `ValueError`; `normalize_or_route_dlq` emits `DeadLetterEnvelopeV1` to `market.dlq.v1`. | `FR-ING-001` |
| `RULE-ING-002` | Exchange REST request weight MUST stay under `max_weight_per_minute * safety_ratio` (`1200 * 0.80 = 960` weight/min). HTTP `429`/`418`/`>=500` MUST obey `Retry-After` (capped at `1.0s` in client loop) up to `max_retries=3`. | `rate_limiter.py:11-44`, `rest_client.py:125-158` | Client pauses (`asyncio.sleep(min(0.05, delay))`) or exhausts retries and raises `RuntimeError` / `httpx.HTTPStatusError`. | `FR-ING-002` |
| `RULE-ING-003` | Closed consecutive klines (`is_closed == True`) whose `(current_open - prev_open)` exceeds step (`60s` for `1m`, `300s` for `5m`, else `3600s`) MUST emit `DetectedStreamGap` and backfill `[prev_open + step, current_open - step]`. | `rate_limiter.py:54-79`, `ws_service.py:70-90` | Watermark transitions to `GAP_DETECTED` -> `BACKFILLING` -> `SYNCED` upon healed candle publish. | `FR-ING-003`, `FR-ING-004` |

## 2. Known Interval Step Caveat

`SequenceAndGapDetector` maps `1m -> 60s`, `5m -> 300s`, and falls back to `3600s` (`1h`) for all other intervals (meaning `15m`/`4h`/`1d` intervals are not accurately step-checked yet).
