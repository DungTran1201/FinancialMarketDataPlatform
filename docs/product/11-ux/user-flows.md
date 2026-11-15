# Phase 11 — User Flows (`UX-001`, `UX-002`)

## 1. User Flow Catalog

- **Canonical Model**: [models/ux/ux.yaml](../../../models/ux/ux.yaml) (`MODEL-UX-001`)

---

## 2. `UX-001`: Real-Time Parallel Data Flow, Kafka Partition, Lakehouse & Event Trace Telemetry

- **Flow ID**: `UX-001`
- **Primary Actor**: Data Engineer / Operator / Quant Analyst
- **Entry Screen**: `SCR-003` (`/data-flow` in `frontend/` SPA; supersedes retired `SCR-001` `/ui/data-flow`)

1. **Step 1 — Subscribe to Real-Time Telemetry**: User opens `/data-flow` (`SCR-003`); the SPA connects to SSE `GET /api/v1/observability/stream` (`API-055`) or WebSocket `WS /ws/v1/observability/stream` (`API-056`) and hydrates topology/latency snapshots (`API-017`..`API-022`).
2. **Step 2 — Inspect Parallel Post-Kafka Topology (`API-018`)**: User inspects the zoomable SVG DAG separating post-Kafka parallel fan-out branches (`Redis Hot State || ClickHouse OLAP || Bronze -> Silver -> Gold`) and clicks individual stage nodes for live metrics.
3. **Step 3 — Audit Kafka Cluster & Partitions (`API-019`)**: User inspects honest broker probe status (`1-node KRaft` active vs Brokers 2 & 3 `UNAVAILABLE`), topic partitions (`P0..P5`), consumer group lag bars, and DLQ envelopes.
4. **Step 4 — Explore Lakehouse & OLAP State (`API-020`)**: User inspects `.local_lakehouse` Bronze Parquet files, Silver Iceberg v2 manifests (`v*.metadata.json`), Gold marts, DQ gate rules (`DQ-KLINE-001..005`, `DQ-TRADE-001..003`), and ClickHouse/Redis buffer stats.
5. **Step 5 — Analyze Non-Summed Parallel-Branch Latency & Event Traces (`AC-004`)**: User compares independent branch E2E percentiles (`API-021` — strictly non-summed parallel branches per `AC-004`), `Decimal` OHLCV candlesticks (`API-052`), and 10-timestamp per-event traces (`API-022`, `API-051`).

---

## 3. `UX-002`: Multi-Module Vite/TypeScript SPA Navigation Workflow

- **Flow ID**: `UX-002`
- **Primary Actor**: Viewer / Analyst / Operator / Admin
- **Entry Screen**: `SCR-002` (`/dashboard`)

1. **Step 1 — Open Overview Dashboard (`/dashboard`, `SCR-002`)**: User lands on `/dashboard` for platform KPIs and telemetry summary.
2. **Step 2 — Navigate via `MainLayout` Sidebar**: User navigates across `Data Flow` (`SCR-003` `/data-flow`), `Market Analytics` (`SCR-004` `/market-analytics`), `Data Management` (`SCR-005` `/data-management`), `AI Workspace` (`SCR-006` `/ai-workspace`), and `Administration` (`SCR-007` `/administration`). Note: unaligned frontend client paths in `SCR-002`/`004`..`007` are tracked under `PROP-APP-001`.

