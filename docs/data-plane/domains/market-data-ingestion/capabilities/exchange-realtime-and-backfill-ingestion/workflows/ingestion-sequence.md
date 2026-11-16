---
doc_id: DIAG-DP-ING-SEQ-001
title: "Diagram: Ingestion Sequence, Gap Detection & Backfill Recovery"
doc_type: diagram
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
  is_authoritative: false
  authoritative_source:
    - "docs/data-plane/domains/market-data-ingestion/capabilities/exchange-realtime-and-backfill-ingestion/use-cases/use-case-ingestion-and-gap-heal.md"
related_docs:
  - CAP-DP-ING-UC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Derived ingestion normalizer, DLQ, gap-heal, and watermark SQLite sequence diagram."
---

# Diagram: Ingestion Sequence, Gap Detection & Backfill Recovery

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-DP-ING-SEQ-001` |
| **Title & Purpose** | Chronological flow across normalizer, gap detector, REST pagination, watermark SQLite store, and Kafka broker |
| **Owner Role & Scope** | `data-architect / CAP-DP-ING-001` |
| **Authoritative Source** | [use-case-ingestion-and-gap-heal.md](../use-cases/use-case-ingestion-and-gap-heal.md) (`CAP-DP-ING-UC-001`) |
| **Notation** | `Mermaid sequenceDiagram` (`UML 2.5.1`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram `[REQUIRED]`

```mermaid
sequenceDiagram
    autonumber
    participant Caller as "WS Frame Caller / Worker"
    participant WS as "WebSocketStreamCollector"
    participant Norm as "BinancePayloadNormalizer"
    participant Gap as "SequenceAndGapDetector"
    participant Back as "HistoricalRestBackfillWorker"
    participant REST as "Binance REST / ASGI Simulator"
    participant WM as "IngestionWatermarkStore (SQLite)"
    participant Bus as "PartitionedEventStreamingBroker"

    Caller->>+WS: "process_ws_frame(raw_frame)"
    WS->>+Norm: "normalize_or_route_dlq(raw_frame)"
    alt "Invalid Schema / Negative Price"
        Norm-->>WS: "(None, DeadLetterEnvelopeV1)"
        WS->>Bus: "publish_dlq(dlq)"
    else "Valid EventEnvelopeV1"
        Norm-->>-WS: "(envelope, None)"
        WS->>Gap: "observe_kline(envelope)"
        alt "Sequence Gap Detected"
            WS->>WM: "upsert_watermark(status=GAP_DETECTED)"
            WS->>+Back: "execute_backfill(missing_from, missing_to)"
            Back->>WM: "upsert_watermark(status=BACKFILLING)"
            Back->>REST: "GET /api/v3/klines (Retry + Weight Limit)"
            REST-->>Back: "OHLCV Pages (<=500 rows/page)"
            Back->>Bus: "publish_event('market.raw.klines.v1', ev)"
            Back->>WM: "upsert_watermark(status=SYNCED)"
            Back-->>-WS: "backfill complete"
        end
        WS->>Bus: "publish_event(topic, envelope)"
    end
```

## 3. Legend `[REQUIRED]`

- **Solid Arrow (`->>`)**: Synchronous/async Python call or HTTP request.
- **Dashed Arrow (`-->>`)**: Return value or response payload.
- **`alt` / `else`**: Error quarantine (`market.dlq.v1`) and automatic gap backfill paths.
