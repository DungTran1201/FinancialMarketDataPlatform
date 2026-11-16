---
doc_id: APP-DOM-MKT-GLOSS-001
title: "Glossary: Market Experience & Data Catalog"
doc_type: glossary
plane: application-plane
scope_level: domain
domain: market-experience-and-catalog
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/market/presentation/router.py"
    - "src/serving/api/modules/catalog/presentation/router.py"
related_docs:
  - APP-DOM-MKT-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Defined terms for hot->OLAP snapshot fallback, bounded time ranges, staleness threshold, and instrument config."
---

# Glossary: Market Experience & Data Catalog

## 1. Domain Terms

- **Hot -> OLAP Fallback**: Read-path behavior in `latest_price_handler` and `GET /market/snapshots/{symbol}` that falls back to `ClickHouseBatchSink` when `HotRedisProjector` returns `None`.
- **`BoundedTimeRange`**: Value object (`src/shared/domain/primitives.py`) validating `start_time <= end_time` within `max_window_days * 86400` seconds before querying OLAP klines.
- **Staleness Threshold (`market_staleness_threshold_ms`)**: Platform config threshold (default `5000` ms) governing `is_stale` on `/market/prices` and `is_healthy` on `/catalog/freshness`.
- **Monitored Instrument Config (`MonitoredInstrumentConfig`)**: In-memory (`AS-IS`) vs Postgres `monitored_instruments` (`TARGET`) tuple specifying `provider`, `symbol`, `enabled_streams`, and `is_active`.
