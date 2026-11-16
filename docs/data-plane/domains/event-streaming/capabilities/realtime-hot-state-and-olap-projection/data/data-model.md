---
doc_id: CAP-DP-STR2-MOD-001
title: "Logical Data Model: Hot State & ClickHouse OLAP Entities"
doc_type: specification
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
  is_authoritative: true
  authoritative_source:
    - "src/streaming/consumers/hot_redis.py"
    - "src/streaming/consumers/analytics_ch.py"
related_docs:
  - CAP-DP-STR2-DB-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: database-architect
    summary: "Defined logical entities for hot prices/orderbooks and analytical klines/trades/tickers."
---

# Logical Data Model: Hot State & ClickHouse OLAP Entities

## 1. Hot State Entities `[REQUIRED]`

| Logical Entity | Natural Key | Core Attributes | TTL / Monotonicity |
|---|---|---|---|
| `HotPriceRecord` | `market:v1:price:{provider}:{symbol}` | `last_price: Decimal`, `exchange_event_time: UTC`, `ingested_at: UTC` | `300s` target TTL; monotonic timestamp |
| `HotSnapshotRecord` | `market:v1:snapshot:{provider}:{symbol}` | `last_price`, `high_24h`, `low_24h`, `vwap_24h`, `base_volume_24h` | `300s` target TTL |
| `HotOrderBookRecord` | `market:v1:orderbook:{provider}:{symbol}` | `bids: [[price, qty], ...]`, `asks: [[price, qty], ...]`, top 20 levels | `120s` target TTL |

## 2. Analytical OLAP Entities `[REQUIRED]`

| Logical Entity | Natural Key | Decimal Precision & Ordering |
|---|---|---|
| `MarketTradeFact` | `(provider, symbol, trade_id)` | `Decimal128(18)` price/qty; versioned by `ingested_at` |
| `MarketKlineFact` | `(provider, symbol, interval, open_time)` | `Decimal128(18)` OHLCV; versioned by `exchange_event_time` |
| `MarketTickerFact` | `(provider, symbol, exchange_event_time)` | `Decimal128(18)` prices, `Decimal64(6)` change% |
