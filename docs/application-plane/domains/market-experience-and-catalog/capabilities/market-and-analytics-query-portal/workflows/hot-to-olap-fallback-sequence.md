---
doc_id: DIAG-APP-MKT-SEQ-001
title: "Sequence Diagram: Hot Redis -> ClickHouse OLAP Read Fallback & Eviction"
doc_type: diagram
plane: application-plane
scope_level: capability
domain: market-experience-and-catalog
capability_id: CAP-APP-MKT-001
status: IN_REVIEW
implementation_status: IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/application-plane/domains/market-experience-and-catalog/capabilities/market-and-analytics-query-portal/use-cases/uc-mkt-001-query-hot-market-and-orderbook.md"
related_docs:
  - CAP-APP-MKT-UC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Rendered hot cache hit vs OLAP fallback sequence for /market/prices and /snapshots."
---

# Sequence Diagram: Hot Redis -> ClickHouse OLAP Read Fallback & Eviction

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-APP-MKT-SEQ-001` |
| **Title & Purpose** | Cache Hit vs Evicted OLAP Fallback for `/market/snapshots/{symbol}` |
| **Owner Role & Scope** | `fullstack-engineer / CAP-APP-MKT-001` |
| **Authoritative Source** | [uc-mkt-001-query-hot-market-and-orderbook.md](../use-cases/uc-mkt-001-query-hot-market-and-orderbook.md) (`CAP-APP-MKT-UC-001`) |
| **Notation** | `Mermaid sequenceDiagram` (`UML 2.5.1`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram

```mermaid
sequenceDiagram
    autonumber
    participant UI as MarketAnalyticsModule
    participant API as Market Router
    participant REDIS as HotRedisProjector
    participant CH as ClickHouseBatchSink

    UI->>API: GET /api/v1/market/snapshots/BTCUSDT
    API->>REDIS: get_hot_snapshot("binance", "BTCUSDT")
    alt Hot Cache Hit
        REDIS-->>API: Snapshot DTO
        API-->>UI: 200 {data, meta: {source: "redis_hot_cache"}}
    else Cache Miss / After POST /evict
        API->>CH: compute_aggregated_statistics & get_latest_price_from_olap
        alt Found in OLAP
            CH-->>API: Aggregated stats + close prices
            API-->>UI: 200 {data, meta: {source: "clickhouse_fallback"}}
        else Absent Everywhere
            API-->>UI: 404 ERR_SNAPSHOT_NOT_FOUND
        end
    end
```

## 3. Legend

- **`meta.source`**: Explicitly reveals whether data came from `redis_hot_cache` or `clickhouse_fallback` (except `GET /orderbook/{symbol}` which always labels `"redis_hot_cache"` even on static fallback).
