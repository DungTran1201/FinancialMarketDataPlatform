---
doc_id: CAP-DP-ING-COMP-001
title: "Component Design: Exchange Ingestion & Backfill Subsystems"
doc_type: specification
plane: data-plane
scope_level: capability
domain: market-data-ingestion
capability_id: CAP-DP-ING-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: data-architect
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/ingestion/domain/ports.py"
    - "src/ingestion/providers/binance/normalizer.py"
    - "src/ingestion/providers/binance/rest_client.py"
    - "src/ingestion/application/ws_service.py"
    - "src/ingestion/application/backfill_service.py"
related_docs:
  - CAP-DP-ING-SPEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Mapped domain ports, adapters, HTTP retry loop, and worker stub gaps."
---

# Component Design: Exchange Ingestion & Backfill Subsystems

Derived DFD: [ingestion-dfd.md](ingestion-dfd.md) (`DIAG-DP-ING-DFD-001`).

## 1. Domain Ports & Clean Architecture Boundaries `[REQUIRED]`

| Port (`src/ingestion/domain/ports.py`) | Implementing Adapter | Known Interface Gap |
|---|---|---|
| `PayloadNormalizerPort` | `BinancePayloadNormalizer` (`providers/binance/normalizer.py`) | Supports `trade`, `kline`, `24hrTicker`/`ticker`, `depthUpdate`/`orderbook`/`depth20`. |
| `HistoricalCollectorPort` | `ProductionExchangeHistoricalCollector` (`providers/binance/rest_client.py`) | Defaults `use_embedded_asgi_transport=True`; omits `self.use_embedded_asgi_transport` attribute. |
| `EventPublisherPort` | `PartitionedEventStreamingBroker` (`streaming/infrastructure/kafka_broker.py`) | Port omits `resolve_topic_for_event` called by `backfill_service.py:49` and `ws_service.py:92`. |
| `WatermarkStorePort` | `IngestionWatermarkStore` (`infrastructure/watermark_store.py`) | Port declares `get_last_open_time`, whereas store implements `get_watermark` and `list_watermarks`. |

## 2. Entrypoint & Lifecycle Reality `[REQUIRED]`

- `WebSocketStreamCollector` (`ws_service.py`) processes injected dict frames (`process_ws_frame`) without owning any `websockets` connection loop (`ws_collector.py` exits after logging config).
- `HistoricalRestBackfillWorker` (`backfill_service.py`) paginates missing intervals (`max_page_size=500`) using `TokenBucketRateLimiter` (`1200 * 0.80 = 960` weight/min).
- `rest_backfill.py` exits immediately on startup; invocations execute inside `DataPlatformV01Pipeline` or HTTP `/api/v1/historical/backfill-jobs`.
