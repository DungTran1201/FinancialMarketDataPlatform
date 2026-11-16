---
doc_id: DP-DOM-ING-SPEC-001
title: "Domain Specification: Market Data Ingestion"
doc_type: specification
plane: data-plane
scope_level: domain
domain: market-data-ingestion
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
    - "src/ingestion/domain/models.py"
    - "src/ingestion/domain/ports.py"
related_docs:
  - DP-DOM-ING-001
  - CAP-DP-ING-SPEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Defined bounded context and provider-isolated ports for market data ingestion."
---

# Domain Specification: Market Data Ingestion

## 1. Bounded Context & Responsibilities `[REQUIRED]`

Translates external exchange wire formats into canonical `EventEnvelopeV1` messages while isolating provider quirks (`binance` currently) behind `PayloadNormalizerPort` and `HistoricalCollectorPort`. Excludes Kafka broker cluster operations, hot cache projection, and lakehouse compaction.

## 2. Owned Entities & Capabilities

- Domain models (`src/ingestion/domain/models.py`): `ExchangeSymbolMetadata`, `DetectedStreamGap`, `WatermarkRecord`.
- Single cohesive capability: `CAP-DP-ING-001` (`exchange-realtime-and-backfill-ingestion`).
- Open provider question `OPEN-PROD-001`: Whether non-Binance exchanges (`notebooks/workers/coinbase_worker.py`, Kraken) are in target scope.
