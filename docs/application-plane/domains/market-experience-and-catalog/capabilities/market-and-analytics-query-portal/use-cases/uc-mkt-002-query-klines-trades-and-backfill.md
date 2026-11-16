---
doc_id: CAP-APP-MKT-UC-002
title: "Use Case UC-MKT-002: Query Historical Klines/Trades & Trigger Backfill"
doc_type: specification
plane: application-plane
scope_level: use-case
domain: market-experience-and-catalog
capability_id: CAP-APP-MKT-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: business-analyst
accountable_role: fullstack-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/historical/presentation/router.py"
    - "src/serving/api/gateway/observability.py"
related_docs:
  - CAP-APP-MKT-REQ-001
  - DIAG-APP-MKT-STATE-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Documented historical OHLCV query, trade scan, and backfill job execution/status polling."
---

# Use Case UC-MKT-002: Query Historical Klines/Trades & Trigger Backfill

## 1. Use Case Scope & Actors

- **Actors**: Quant Analyst (`GET /klines`, `/trades`, `/observability/candles`), Operator (`POST /backfill-jobs`).

## 2. Main Flows & Exceptions

1. **Historical Klines Query**: Caller invokes `GET /api/v1/historical/klines/{symbol}` (`interval`, `start_time`, `end_time`, `max_window_days`, `limit`). `BoundedTimeRange` rejects excessive windows with `422 ERR_INVALID_TIME_RANGE`. (*Bug*: Malformed `start_time`/`end_time` string triggers `500 ValueError` at `L39-40`.)
2. **Chart Candles Feed (`MarketAnalyticsModule`)**: Calls `GET /api/v1/observability/candles`, returning deduplicated/rolled-up bars (`no_fake_candles_policy: true`) with both floats (`open`, `high`, `low`, `close`) and exact Decimal strings (`*_str`) plus `statistics`.
3. **Trigger Backfill Job (`POST /historical/backfill-jobs`)**: Fetches candles via `historical_collector`, writes Kafka/Redis/ClickHouse/Bronze inline during the HTTP `202` call, updates `ingestion_watermarks`, and records `status="COMPLETED"` in `runtime.backfill_jobs` (hardcoding `"transport_mode": "MOCKED_SIMULATED_EXCHANGE_REST"` at `L150`).
4. **Poll Job (`GET /historical/backfill-jobs/{job_id}`)**: Returns `job_record` or `404 ERR_JOB_NOT_FOUND`.
