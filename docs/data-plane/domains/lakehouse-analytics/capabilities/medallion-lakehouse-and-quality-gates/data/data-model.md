---
doc_id: CAP-DP-LAK-MOD-001
title: "Logical Data Model: Bronze, Silver & Gold Medallion Tables"
doc_type: specification
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
  is_authoritative: true
  authoritative_source:
    - "src/shared/contracts/schemas/datasets.py"
    - "src/lakehouse/catalog/lineage.py"
related_docs:
  - CAP-DP-LAK-DB-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: database-architect
    summary: "Defined logical medallion datasets and 12-node lineage entity model."
---

# Logical Data Model: Bronze, Silver & Gold Medallion Tables

## 1. Dataset Contracts & Keys `[REQUIRED]`

Refer to canonical definitions in [data-contract.yaml](../../../../../shared-contracts/data-contract.yaml):
- `silver.market_klines`: natural key `(provider, symbol, interval, open_time)`
- `silver.market_trades`: natural key `(provider, symbol, trade_id)`
- `silver.order_book_snapshots`: natural key `(provider, symbol, exchange_event_time)` (*conflict*: `last_update_id` in `catalog-config.yaml`)
- Gold marts: `gold.fct_daily_market_summary` `(provider, symbol, trading_day)`, `gold.fct_realized_volatility` `(provider, symbol, window_end)`, `gold.fct_orderbook_liquidity` `(provider, symbol, window_end)`.

## 2. Lineage Graph Entities (`catalog/lineage.py`) `[REQUIRED]`

`DataLineageGovernanceRegistry` links 12 canonical `DatasetGovernanceNode`s (`source.binance.*`, `kafka.*`, `redis.*`, `clickhouse.*`, `bronze.*`, `silver.*`, `gold.*`) via directed `LineageEdge(from_dataset, to_dataset, transformation)`.
