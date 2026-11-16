---
doc_id: DIAG-DP-LAK-ERD-001
title: "Diagram: Silver & Gold Medallion Entity Relationships"
doc_type: diagram
plane: data-plane
scope_level: capability
domain: lakehouse-analytics
capability_id: CAP-DP-LAK-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: database-architect
accountable_role: database-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/data-plane/domains/lakehouse-analytics/capabilities/medallion-lakehouse-and-quality-gates/data/data-model.md"
related_docs:
  - CAP-DP-LAK-MOD-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: database-architect
    summary: "Derived ERD for Silver tables and derived Gold marts."
---

# Diagram: Silver & Gold Medallion Entity Relationships

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-DP-LAK-ERD-001` |
| **Title & Purpose** | Logical & physical key relationships across Silver market tables and Gold fact marts |
| **Model Level** | Logical / Parquet Physical (`AS-IS` Local Parquet) |
| **Owner Role & Scope** | `database-architect / CAP-DP-LAK-001` |
| **Authoritative Source** | [data-model.md](data-model.md) (`CAP-DP-LAK-MOD-001`) |
| **Notation** | `Mermaid erDiagram` (`Crow's Foot`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram `[REQUIRED]`

```mermaid
erDiagram
    SILVER_MARKET_KLINES ||--o{ GOLD_FCT_DAILY_MARKET_SUMMARY : "aggregates_daily"
    SILVER_MARKET_TRADES ||--o{ GOLD_FCT_REALIZED_VOLATILITY : "computes_returns"
    SILVER_ORDER_BOOK_SNAPSHOTS ||--o{ GOLD_FCT_ORDERBOOK_LIQUIDITY : "target_unmerged_AS_IS"

    SILVER_MARKET_KLINES {
        string provider PK "Partition/Key"
        string symbol PK "Natural Key"
        string interval PK "Natural Key"
        datetime open_time PK "Natural Key"
        decimal close_price "Decimal quantized 8dp"
    }
    GOLD_FCT_DAILY_MARKET_SUMMARY {
        string provider PK "Composite PK"
        string symbol PK "Composite PK"
        date trading_day PK "Composite PK"
        decimal daily_return_pct "Fixed-point Decimal"
    }
    SILVER_MARKET_TRADES {
        string provider PK "Natural Key"
        string symbol PK "Natural Key"
        int trade_id PK "Natural Key"
        decimal price "Decimal quantized 8dp"
    }
    GOLD_FCT_REALIZED_VOLATILITY {
        string provider PK "Composite PK"
        string symbol PK "Composite PK"
        datetime window_end PK "Composite PK"
        decimal realized_volatility "Annualized"
    }
    SILVER_ORDER_BOOK_SNAPSHOTS {
        string provider PK "Natural Key"
        string symbol PK "Natural Key"
        datetime exchange_event_time PK "Conflict: catalog.yaml uses last_update_id"
    }
    GOLD_FCT_ORDERBOOK_LIQUIDITY {
        string provider PK "Composite PK"
        string symbol PK "Composite PK"
        datetime window_end PK "Composite PK"
        decimal bid_ask_spread_bps "Fixed-point Decimal"
    }
```

## 3. Legend `[REQUIRED]`

- `||--o{`: Derived analytical lineage from Silver source dataset to Gold fact mart (`silver.order_book_snapshots` merge is `NOT_IMPLEMENTED` in `merge_engine.py`).
