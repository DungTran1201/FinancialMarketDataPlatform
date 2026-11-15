# Phase 11 — Screen Specifications (`SCR-001`: Real-Time Data Flow & Latency Observatory)

## 1. Screen Overview

- **Screen ID**: `SCR-001`
- **Title**: Real-Time Data Flow Observatory & Parallel-Branch Telemetry UI
- **Route**: `GET /data-flow` ([frontend/src/modules/data-flow/DataFlowModule.ts](../../../frontend/src/modules/data-flow/DataFlowModule.ts)) + `GET /api/v1/observability/data-flow` ([src/serving/api/gateway/observability.py](../../../src/serving/api/gateway/observability.py))
- **Backing Telemetry APIs**: `/api/v1/observability/*` (`API-017`..`API-022`), SSE `/api/v1/observability/stream`, WS `/ws/v1/observability/stream`, plus backward-compatible `API-011`, `API-016`
- **Derived Diagram**: [Diagram UX-001: Real-Time Data Flow UI Architecture](../../diagrams/ux/01-realtime-data-flow-ui-architecture.md)

---

## 2. Visual Layout & Component Hierarchy (Dark Technical Observatory)

1. **Top Control Bar, Mode Isolation & Filter Strip**:
   - Displays live SSE status badge, execution context (`LIVE DATA ACTIVE` vs `DEMO TRACES PRESENT` vs `IDLE`), and honest live TCP probe pills (`Kafka B1..B3`, `Redis`, `ClickHouse`, `MinIO`).
   - Time window selector (`1m`, `5m`, `15m`, `1h`, `24h`, `All`), symbol filter, mode filter (`ALL`, `LIVE`, `DEMO`), explicit `Probe Live Infra` / `Pull Live Binance REST` actions, and explicit `DEMO` actions (`Emit 5 Events`, `Inject DLQ`, `Flush Bronze -> Gold`, `Run 12-Stage Pipeline`).
2. **Global KPI Strip (Always Visible)**:
   - `Events Ingested`, `Events Processed`, `Failed / DLQ`, `Kafka Consumer Lag`, `Critical E2E P50 Latency` (broken down by Hot / OLAP / Lakehouse), and `Data Freshness`.
3. **6 Engineering Workspace Tabs**:
   - **Tab 1 — Interactive Parallel Data Flow DAG**: Zoomable/pannable SVG topology separating parallel branches (`Redis Hot || ClickHouse OLAP || Bronze->Silver->Gold`) with real-event animated pulse orbs and click-to-inspect Node Drawer.
   - **Tab 2 — Kafka Cluster & Partitions**: Broker 1..3 truth (`1-node KRaft`), 6 canonical topics, Partition boxes (`P0..P5`), Consumer Group lag progress bars, Publish/Consume rate chart, and DLQ viewer.
   - **Tab 3 — Lakehouse & Data Warehouse Explorer**: Data Lake vs Data Lakehouse vs Data Warehouse comparison table grounded in `.local_lakehouse/`, Bronze Parquet stats, Silver Apache Iceberg v2 snapshots (`v*.metadata.json`), Gold marts, DQ rules (`DQ-KLINE-001..005`), and ClickHouse/Redis buffer stats.
   - **Tab 4 — Real-Time Candlestick Chart**: Canvas OHLCV + Volume chart supporting `1m/5m/15m/1h/4h/1d` `Decimal` rollups, crosshair OHLCV tooltip, and explicit zero-fake-candle policy.
   - **Tab 5 — Processing & Parallel-Branch E2E Latency Dashboard**: Non-summed branch comparison, latency histogram, clickable time-bucket series, stage percentiles (`min/avg/P50/P95/P99/max`), and slow/failed event jump table.
   - **Tab 6 — Event Trace Inspector (`event_id`)**: Filterable event list, 10-timestamp UTC audit table, stage waterfall bars, and DLQ/DQ error details.
