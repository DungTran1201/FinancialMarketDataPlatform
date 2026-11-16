---
doc_id: DIAG-DP-STR2-ERD-001
title: "Diagram: ClickHouse Analytical Schema & Redis Key Entities"
doc_type: diagram
plane: data-plane
scope_level: capability
domain: event-streaming
capability_id: CAP-DP-STR-002
status: IN_REVIEW
implementation_status: SIMULATED
version: "2.0.0"
owner_role: database-architect
accountable_role: database-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/data-plane/domains/event-streaming/capabilities/realtime-hot-state-and-olap-projection/data/database-design.md"
related_docs:
  - CAP-DP-STR2-DB-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: database-architect
    summary: "Derived ERD for ClickHouse market_data tables declared in 01_schema.sql."
---

# Diagram: ClickHouse Analytical Schema & Redis Key Entities

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-DP-STR2-ERD-001` |
| **Title & Purpose** | Physical ClickHouse tables (`market_trades`, `market_klines`, `market_tickers`) and logical Redis hot keys |
| **Model Level** | Physical (`TARGET` ClickHouse DDL; simulated in-memory `AS-IS`) |
| **Owner Role & Scope** | `database-architect / CAP-DP-STR-002` |
| **Authoritative Source** | [database-design.md](database-design.md) (`CAP-DP-STR2-DB-001`) |
| **Notation** | `Mermaid erDiagram` (`Crow's Foot`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram `[REQUIRED]`

```mermaid
erDiagram
    MARKET_TRADES {
        string provider PK "LowCardinality + ORDER BY"
        string symbol PK "LowCardinality + ORDER BY"
        uint64 trade_id PK "ORDER BY trade_id"
        decimal price "Decimal128(18)"
        decimal quantity "Decimal128(18)"
        datetime ingested_at "ReplacingMergeTree version"
    }
    MARKET_KLINES {
        string provider PK "ORDER BY"
        string symbol PK "ORDER BY"
        string interval PK "ORDER BY"
        datetime open_time PK "ORDER BY"
        decimal open_price "Decimal128(18)"
        decimal high_price "Decimal128(18)"
        decimal low_price "Decimal128(18)"
        decimal close_price "Decimal128(18)"
        datetime exchange_event_time "ReplacingMergeTree version"
    }
    MARKET_TICKERS {
        string provider PK "ORDER BY"
        string symbol PK "ORDER BY"
        datetime exchange_event_time PK "ReplacingMergeTree version"
        decimal last_price "Decimal128(18)"
        decimal vwap_24h "Decimal128(18)"
    }
```

## 3. Legend `[REQUIRED]`

- **Analytical Columns**: Columnar ClickHouse `ReplacingMergeTree` keys (`ORDER BY` tuple shown as composite sorting keys, not relational enforced constraints).
