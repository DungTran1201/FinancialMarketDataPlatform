---
doc_id: CAP-DP-ING-UC-001
title: "Use Case: Normalize Market Stream, Detect Gap & Execute Backfill Recovery"
doc_type: specification
plane: data-plane
scope_level: capability
domain: market-data-ingestion
capability_id: CAP-DP-ING-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: business-analyst
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/ingestion/application/ws_service.py"
    - "src/ingestion/application/backfill_service.py"
related_docs:
  - CAP-DP-ING-SPEC-001
requirement_ids:
  - UC-ING-001
  - AC-ING-001
  - AC-ING-002
  - AC-ING-003
  - AC-ING-004
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Authored ingestion & gap-healing use case tracing exact method calls and error handling."
---

# Use Case: `UC-ING-001` — Normalize Market Stream, Detect Gap & Execute Backfill Recovery

## 1. Identification & Traceability `[REQUIRED]`

- **Use Case ID**: `UC-ING-001`
- **Primary Actor**: Exchange Feed / Pipeline Caller (`DataPlatformV01Pipeline` or HTTP Backfill API)
- **Secondary Actors**: `PartitionedEventStreamingBroker`, `IngestionWatermarkStore`, Binance REST / ASGI Simulator
- **Parent Requirements**: `FR-ING-001`..`FR-ING-004`
- **Applied Business Rules**: `RULE-ING-001`..`RULE-ING-003`

## 2. Trigger, Preconditions & Postconditions `[REQUIRED]`

- **Trigger**: Caller submits raw exchange dict frame to `WebSocketStreamCollector.process_ws_frame()` or backfill range to `HistoricalRestBackfillWorker.execute_backfill()`.
- **Preconditions**: Broker and SQLite `IngestionWatermarkStore` initialized cleanly; symbol string non-empty.
- **Success Postconditions**: `EventEnvelopeV1` published to partitioned topic; watermark updated to `SYNCED`.
- **Failure Postconditions**: Invalid payload quarantined as `DeadLetterEnvelopeV1` on `market.dlq.v1`; failed REST calls leave watermark at `BACKFILLING`/`GAP_DETECTED` and raise exception to caller.

## 3. Main Success Flow `[REQUIRED]`

1. Collector passes raw frame to `BinancePayloadNormalizer.normalize_or_route_dlq(raw_frame, source_topic, ingested_at)`.
2. Normalizer validates schema, `Decimal` positivity, and UTC timestamps (`RULE-ING-001`), generating deterministic UUIDv5 `event_id`.
3. If `event_type == EventType.KLINE`, `SequenceAndGapDetector.observe_kline()` checks delta against expected interval (`1m`/`5m`/`60m`).
4. On contiguous step, `WebSocketStreamCollector` resolves topic (`market.raw.klines.v1`) and awaits `broker.publish_event(topic, envelope)`.

## 4. Alternative & Exception Flows `[REQUIRED]`

| Branch ID | Condition / Error Trigger | System Behavior | Outcome / Error Code |
|---|---|---|---|
| `ALT-1` | Closed kline gap detected (`RULE-ING-003`) | Upsert watermark `GAP_DETECTED` -> invoke `HistoricalRestBackfillWorker.execute_backfill()` -> upsert `BACKFILLING` -> paginate REST `500`/page -> publish missing bars -> upsert `SYNCED` -> publish current kline. | Gap healed (`auto_backfilled_events > 0`) |
| `EXC-1` | Negative/NaN price, invalid OHLC, or missing `s` | `normalize_or_route_dlq()` returns `(None, DeadLetterEnvelopeV1)`; calls `broker.publish_dlq(dlq)`. | Quarantined in `market.dlq.v1` |
| `EXC-2` | Exchange HTTP `429` / `418` / `5xx` | `_request_with_retry()` honors `Retry-After` (`<= 1.0s`) or backoff (`0.02 * 2^attempt`) up to `max_retries=3`. | Raises `RuntimeError` / `HTTPStatusError` if exhausted |
| `EXC-3` | Unknown interval in `SequenceAndGapDetector` | Falls back to default step `3600s` (`rate_limiter.py:67-68`). | `[GAP]` Intervals other than `1m`/`5m`/`1h` (e.g. `15m`) use `60m` step! |

## 5. Acceptance Criteria (`AC-ING-001`..`004`)

- `AC-ING-001`: Invalid trade frame with `p: "-42.50"` routes 1 `DeadLetterEnvelopeV1` to `market.dlq.v1` without halting subsequent valid frames.
- `AC-ING-002`: Requested range exceeding `max_page_size` splits into sequential paginated `/api/v3/klines` requests without exceeding safety weight limit `960/min`.
- `AC-ING-003`: Skipping 3 minutes on `1m` closed klines yields `auto_backfilled_events == 3` and final watermark status `SYNCED`.
- `AC-ING-004`: Re-upserting `(provider, symbol, interval)` updates existing SQLite row cleanly with zero duplicates.
