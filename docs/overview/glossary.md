---
doc_id: OVR-GLOSS-001
title: "Platform Ubiquitous Glossary"
doc_type: glossary
plane: platform
scope_level: platform
status: IN_REVIEW
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: business-analyst
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/shared/contracts/events/market_events.py"
    - "src/shared/domain/primitives.py"
    - "src/shared/observability/tracing.py"
related_docs:
  - OVR-ROOT-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Defined canonical platform domain and technical terms aligned directly with verified code identifiers."
---

# Platform Ubiquitous Glossary

## 1. Domain & Engineering Terms `[REQUIRED]`

| Term | Canonical Code Symbol / Identifier | Precise Meaning | Owning Scope | Disallowed Synonyms |
|---|---|---|---|---|
| **EventEnvelopeV1** | `EventEnvelopeV1` (`market_events.py:103`) | Immutable canonical event wrapper containing deterministic UUIDv5 `event_id`, `schema_version="1.0.0"`, `event_type`, `provider`, lowercase/uppercase validated `symbol`, `partition_key`, `exchange_event_time` (UTC), `ingested_at` (UTC), `natural_key`, and typed `payload`. | Data Plane (`CAP-DP-STR-001`) | Raw trade blob, untyped dict |
| **InstrumentKey** | `InstrumentKey` (`primitives.py:22`) | Normalized provider + trading pair identifier enforcing lowercase `provider` and uppercase alphanumeric `symbol` (`provider:symbol`). | Platform (`src/shared/`) | Free-text pair, mixed-case ticker |
| **DecimalPrice** | `DecimalPrice` (`primitives.py:60`) | Fixed-point finite non-negative `Decimal` wrapper preventing binary floating-point rounding drift in prices/quantities. | Platform (`src/shared/`) | `float` price |
| **Hot Cache / Hot Path** | `HotStateProjector` (`hot_redis.py:61`) | Monotonic low-latency serving state for latest price, 24h snapshot, and top-20 orderbook (`AS-IS`: in-memory dicts; `TARGET`: Redis Lua upsert + TTL). | Data Plane (`CAP-DP-STR-002`) | OLAP warehouse, Bronze Parquet |
| **OLAP Analytical Path** | `ClickHouseBatchSink` (`analytics_ch.py:43`) | Deduplicated analytical store supporting historical candle rollups, trade scans, and VWAP/volatility aggregations (`AS-IS`: in-memory dicts; `TARGET`: ClickHouse `ReplacingMergeTree`). | Data Plane (`CAP-DP-STR-002`) | Transactional DB |
| **Medallion Tiers (Bronze / Silver / Gold)** | `Archiver` / `MergeEngine` / `MartEngine` (`src/lakehouse/`) | **Bronze**: immutable raw event ZSTD Parquet archive; **Silver**: natural-key deduplicated + DQ-gated Parquet & Iceberg manifests; **Gold**: business-ready `fct_*` summary, volatility & liquidity marts. | Data Plane (`CAP-DP-LAK-001`) | Raw dump |
| **Dead-Letter Queue (DLQ)** | `DeadLetterEnvelopeV1` / `market.dlq.v1` | Quarantine topic holding malformed payloads with deterministic `dlq_id`, `error_type`, `error_message`, `raw_payload`, and `source_topic`. | Data Plane (`CAP-DP-STR-001`) | Dropped packet, error log only |
| **Watermark** | `WatermarkRecord` (`watermark_store.py`) | Last synced exchange `open_time` per `(provider, symbol, interval)` (`AS-IS`: SQLite `SYNCED | BACKFILLING | GAP_DETECTED`; `TARGET`: Postgres DDL `IDLE | RUNNING | FAILED | COMPLETED`). | Data Plane (`CAP-DP-ING-001`) | Consumer offset only |
| **10-Timestamp Event Trace (`t0`–`t9`)** | `EventLifecycleTrace` (`tracing.py:187`) | End-to-end observability timeline from exchange event generation (`t0`) and ingestion (`t1`) through Kafka (`t3`), parallel hot/OLAP/Bronze sinks (`t4`–`t7`), Silver/Gold (`t8`), and Serving (`t9`), separating serial spine from parallel branch latencies. | Application / Data (`CAP-APP-OPS-001`) | Raw server log |
| **ControlledToolGateway** | `ControlledToolGateway` (`gateway.py:27`) | Whitelist, RBAC permission, bounded `limit`, and asyncio timeout enforcer wrapping the 10 approved deterministic Agent tools and attaching UUID `ToolProvenanceMetadata`. | Intelligence Plane (`CAP-INT-ORC-001`) | Unbounded LLM tool call |
| **Provenance Citation** | `ProvenanceCitation` (`reporting/ports.py`) | Auditable link (`invocation_id`, `tool_name`, `source_store`, `symbol`, window, `row_count`) validated by `ReportValidator` against actual tool calls. | Intelligence Plane (`CAP-INT-ORC-001`) | Uncited LLM claim |
| **Execution Mode (`LIVE` vs `DEMO`)** | `execution_mode` (`tracing.py`) | Distinguishes traces produced via `trigger_demo_action()` / embedded ASGI simulator (`DEMO`) from live ingestion paths (`LIVE`). | Platform Observability | Test environment |
