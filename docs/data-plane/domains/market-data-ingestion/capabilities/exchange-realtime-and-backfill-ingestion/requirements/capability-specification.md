---
doc_id: CAP-DP-ING-SPEC-001
title: "Capability Specification: Exchange Realtime & Backfill Ingestion"
doc_type: specification
plane: data-plane
scope_level: capability
domain: market-data-ingestion
capability_id: CAP-DP-ING-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
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
    - "src/ingestion/application/ws_service.py"
    - "src/ingestion/application/backfill_service.py"
    - "src/ingestion/infrastructure/watermark_store.py"
related_docs:
  - CAP-DP-ING-ROOT
  - CAP-DP-ING-RULE-001
requirement_ids:
  - FR-ING-001
  - FR-ING-002
  - FR-ING-003
  - FR-ING-004
  - FR-ING-005
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Specified exact AS-IS vs TARGET ingestion behavior for normalizer, REST paginator, gap healing, and SQLite watermarks."
---

# Capability Specification: Exchange Realtime & Backfill Ingestion

## 1. Capability Scope & `AS-IS` Reality `[REQUIRED]`

Acquires and normalizes spot market events (`trade`, `kline`, `24hrTicker`, `depth20`) from Binance into canonical `EventEnvelopeV1` streams, quarantines invalid inputs to `market.dlq.v1`, executes paginated historical kline backfill with HTTP weight throttling, detects sequence gaps, and updates watermarks.

- **`AS-IS` Evidence**: Normalization, REST pagination (defaulting to embedded ASGI simulator `use_embedded_asgi_transport=True`), gap healing (`process_ws_frame`), and SQLite WAL watermarks are implemented and tested in-process. Continuous WS socket loops (`ws_collector.py`) and PostgreSQL watermark persistence (`deploy/postgres/init/01_schema.sql`) remain `NOT_IMPLEMENTED`.

## 2. Functional Requirements `[REQUIRED]`

| Req ID | Requirement Statement | `AS-IS` Code Reference | Acceptance Criteria |
|---|---|---|---|
| `FR-ING-001` | Normalizer MUST validate incoming Binance `trade`, `kline`, `24hrTicker`, and `depth20` payloads into `EventEnvelopeV1` with `Decimal` precision and UTC timestamps, routing invalid payloads to `DeadLetterEnvelopeV1`. | `normalizer.py:32-221` (`IMPLEMENTED`) | `AC-ING-001` (`test_gap_recovery_and_dlq.py:102`) |
| `FR-ING-002` | Historical REST collector MUST paginate `/api/v3/klines` in bounded slices (`max_page_size=500`), parse `X-MBX-USED-WEIGHT-1M`, respect safety ratio `0.80 * 1200`, and retry `429`/`418`/`>=500` up to `max_retries=3`. | `rest_client.py:102-256`, `rate_limiter.py:11-44` (`PARTIAL`: ASGI sim default) | `AC-ING-002` (`test_data_platform_v01_e2e.py:275`) |
| `FR-ING-003` | Stream processor MUST detect skipped interval steps on closed klines via `SequenceAndGapDetector`, record `GAP_DETECTED` watermark, and trigger automatic REST backfill (`auto_backfilled_events`). | `ws_service.py:48-95`, `rate_limiter.py:47-83` (`IMPLEMENTED` for injected frames; continuous WS loop missing) | `AC-ING-003` (`test_gap_recovery_and_dlq.py:29`) |
| `FR-ING-004` | Watermark store MUST persist `(provider, symbol, interval) -> last_open_time, status` idempotently via upsert across `SYNCED`, `BACKFILLING`, and `GAP_DETECTED`. | `watermark_store.py:12-124` (SQLite WAL; Postgres DDL mismatches schema) | `AC-ING-004` (`test_domain_and_quant.py:65`) |
| `FR-ING-005` | Continuous WS collector worker MUST connect to `BINANCE_WS_BASE_URL` and reconnect with bounded exponential backoff (`compute_reconnect_backoff_seconds`). | `ws_collector.py` (`NOT_IMPLEMENTED` — logs and exits); `ws_service.py:20-24` (formula only) | `OPEN-ING-001` |

## 3. Open Questions & Code Defects

- **Interface Mismatch**: `WatermarkStorePort.get_last_open_time` (`ports.py:48`) is not implemented on `IngestionWatermarkStore`, and `EventPublisherPort` (`ports.py:24-29`) omits `resolve_topic_for_event`.
- **Attribute Bug**: `ProductionExchangeHistoricalCollector.__init__` does not store `self.use_embedded_asgi_transport`, causing runtime telemetry checks (`runtime.py:1168`) to always read default `True`.
