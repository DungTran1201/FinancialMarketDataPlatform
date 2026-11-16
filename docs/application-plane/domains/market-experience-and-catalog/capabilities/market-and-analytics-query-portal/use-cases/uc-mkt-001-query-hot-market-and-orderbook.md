---
doc_id: CAP-APP-MKT-UC-001
title: "Use Case UC-MKT-001: Query Latest Quotes, Snapshots, Orderbook & Hot Eviction"
doc_type: specification
plane: application-plane
scope_level: use-case
domain: market-experience-and-catalog
capability_id: CAP-APP-MKT-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: business-analyst
accountable_role: fullstack-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/market/presentation/router.py"
    - "frontend/src/modules/market-analytics/MarketAnalyticsModule.ts"
related_docs:
  - CAP-APP-MKT-REQ-001
  - DIAG-APP-MKT-SEQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Detailed UC-MKT-001 quote, snapshot, depth, ingest, and cache eviction flows."
---

# Use Case UC-MKT-001: Query Latest Quotes, Snapshots, Orderbook & Hot Eviction

## 1. Use Case Scope & Actors

- **Actors**: Quant Analyst (`#/market-analytics`), API Consumer, Operator (`POST /evict`, `POST /ingest`).
- **Preconditions**: (`TARGET`) Valid JWT with `market:read` or `backfill:trigger`; (`AS-IS`) unauthenticated.

## 2. Flows & Verified Anomalies

1. **Single/Batch Quote Query**: Caller calls `GET /api/v1/market/prices/{symbol}` or `GET /api/v1/market/prices?symbols=...`. Handler reads hot price store first, falling back to `ClickHouseBatchSink`, returning Decimal strings and `age_ms`/`is_stale` (`404 ERR_SYMBOL_NOT_FOUND` on single miss; omitted on batch miss).
2. **24h Snapshot Query**: `GET /api/v1/market/snapshots/{symbol}` reads `hot_redis_projector` (`meta.source="redis_hot_cache"`), falling back to `clickhouse_sink` statistics (`meta.source="clickhouse_fallback"`), or raises `404 ERR_SNAPSHOT_NOT_FOUND`.
3. **L2 Orderbook Depth**: `GET /api/v1/market/orderbook/{symbol}?depth=20`. *Anomaly*: If hot cache has no orderbook entry, router returns hardcoded static bids/asks (`"89500.00"` etc.) mislabeled `"redis_hot_cache"`.
4. **Raw Event Push (`POST /market/ingest`)**: Normalizes frame (`BinancePayloadNormalizer`); routes invalid payload to `market.dlq.v1` (`ROUTED_TO_DLQ`) or publishes to Kafka, Redis hot state, and ClickHouse OLAP synchronously (`INGESTED`) before returning `202`.
5. **Hot Eviction (`POST /market/evict/{symbol}`)**: Removes hot keys from memory so subsequent reads exercise OLAP fallback (`SEC-AUDIT-003`: currently unauthenticated).
