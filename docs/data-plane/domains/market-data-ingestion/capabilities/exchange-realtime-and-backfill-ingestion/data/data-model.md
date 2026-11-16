---
doc_id: CAP-DP-ING-MOD-001
title: "Logical Data Model: Exchange Ingestion & Watermarks"
doc_type: specification
plane: data-plane
scope_level: capability
domain: market-data-ingestion
capability_id: CAP-DP-ING-001
status: IN_REVIEW
implementation_status: IMPLEMENTED
version: "2.0.0"
owner_role: database-architect
accountable_role: database-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/ingestion/domain/models.py"
    - "src/ingestion/infrastructure/watermark_store.py"
related_docs:
  - CAP-DP-ING-DB-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: database-architect
    summary: "Defined logical ingestion domain models (WatermarkRecord, DetectedStreamGap, ExchangeSymbolMetadata)."
---

# Logical Data Model: Exchange Ingestion & Watermarks

## 1. Domain Entities & Attributes `[REQUIRED]`

| Entity (`models.py`) | Logical Key | Key Attributes & Types | Invariants |
|---|---|---|---|
| `WatermarkRecord` | `(provider, symbol, interval)` | `provider: str`, `symbol: str`, `interval: str`, `last_open_time: datetime(UTC)`, `updated_at: datetime(UTC)`, `status: SYNCED | BACKFILLING | GAP_DETECTED` | Strictly monotonic progress per stream interval unless healing gap. |
| `ExchangeSymbolMetadata` | `(provider, symbol)` | `base_asset`, `quote_asset`, `tick_size: Decimal`, `step_size: Decimal`, `min_notional: Decimal`, `status` | All exchange filters stored as fixed-point `Decimal`. |
| `DetectedStreamGap` | Transient alert value object | `provider`, `symbol`, `interval`, `expected_open_time: datetime`, `observed_open_time: datetime`, `missing_from: datetime`, `missing_to: datetime` | `missing_from <= missing_to`. |

## 2. Persistence & Key Mapping

Only `WatermarkRecord` is persisted across calls; `ExchangeSymbolMetadata` and `DetectedStreamGap` remain transient runtime value objects.
