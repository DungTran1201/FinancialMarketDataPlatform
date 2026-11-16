---
doc_id: DIAG-DP-ING-DFD-001
title: "Diagram: Ingestion Normalization, Watermark & DLQ Data Flow"
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
    - "docs/data-plane/domains/market-data-ingestion/capabilities/exchange-realtime-and-backfill-ingestion/design/component-design.md"
related_docs:
  - CAP-DP-ING-COMP-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Derived capability DFD covering WS frames, Binance REST simulator/HTTP, SQLite watermarks, and Kafka topics."
---

# Diagram: Ingestion Normalization, Watermark & DLQ Data Flow

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-DP-ING-DFD-001` |
| **Title & Purpose** | Ingestion data flow from Binance REST / injected WS frames into EventEnvelopeV1, SQLite watermarks, and DLQ |
| **Owner Role & Scope** | `data-architect / CAP-DP-ING-001` |
| **Authoritative Source** | [component-design.md](component-design.md) (`CAP-DP-ING-COMP-001`) |
| **Notation** | `Mermaid flowchart LR` (`DFD`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram `[REQUIRED]`

```mermaid
flowchart LR
    ext_ws["Live Binance WSS (TARGET)"]
    ext_rest["Binance REST / ASGI Simulator"]
    proc_ws["WebSocketStreamCollector.process_ws_frame()"]
    proc_norm["BinancePayloadNormalizer"]
    gate_val{"Valid Decimal & Schema?"}
    proc_gap["SequenceAndGapDetector + BackfillWorker"]
    store_wm[("SQLite ingestion_watermarks (.local_storage)")]
    out_dlq[("market.dlq.v1")]
    out_raw[("market.raw.{trades,klines,tickers,orderbook}.v1")]

    ext_ws -.->|"WSS JSON (NOT IMPLEMENTED)"| proc_ws
    ext_rest -->|"HTTPS / ASGI JSON"| proc_gap
    proc_ws -->|"Raw Dict"| proc_norm
    proc_norm -->|"Candidate"| gate_val
    gate_val -->|"Pass"| proc_gap
    gate_val -.->|"Fail (DeadLetterEnvelopeV1)"| out_dlq
    proc_gap -->|"Upsert SYNCED/BACKFILLING/GAP_DETECTED"| store_wm
    proc_gap -->|"Publish EventEnvelopeV1"| out_raw
```

## 3. Legend `[REQUIRED]`

- **Solid Arrows (`-->`)**: Active Python data flow executed by `ws_service.py` / `backfill_service.py`.
- **Dashed Arrows (`-.->`)**: `TARGET` unimplemented WSS socket loop and DLQ quarantine path.
