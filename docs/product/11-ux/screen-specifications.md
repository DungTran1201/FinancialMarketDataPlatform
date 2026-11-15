# Phase 11 — Screen Specifications (`SCR-001`..`SCR-007`)

> **Canonical Model**: [models/ux/ux.yaml](../../../models/ux/ux.yaml) (`MODEL-UX-001`, Navigation Group `NAV-001`)  
> **Frontend Runtime**: TypeScript + Vite SPA ([frontend/package.json](../../../frontend/package.json)) served at `http://localhost:3001` (`FRONTEND_PORT=3001` -> container `:3000`) and proxied via `https://fmdp.local/`.  
> **Endpoint Drift Note**: Frontend client calls flagged under `PROP-APP-001` reflect unaligned SPA client paths documented separately in [docs/product/14-governance/unresolved-issues.md](../14-governance/unresolved-issues.md); runtime business logic in `frontend/` is unmodified under `DOCS-004`.

---

## 1. Screen Inventory Summary (`SCR-001`..`SCR-007`)

| Screen ID | Route | Module / Implementation File | Status | Bound Backend APIs (`API-###`) | Notes / Known Drifts |
|---|---|---|---|---|---|
| `SCR-001` | `/ui/data-flow` (decommissioned) | `src/serving/api/gateway/ui.py` (deleted) | `DEPRECATED` | `[]` (historical: `API-011`, `API-012`, `API-014`..`API-022`) | Superseded by `SCR-003` in `FEAT-002` `frontend/` SPA |
| `SCR-002` | `/dashboard` | [DashboardModule.ts](../../../frontend/src/modules/dashboard/DashboardModule.ts) | `IMPLEMENTED` | `API-017`..`API-022`, `API-053`..`API-056` | `PROP-APP-001`: `observability.service.ts` also calls unimplemented `POST /observability/stream/control` |
| `SCR-003` | `/data-flow` | [DataFlowModule.ts](../../../frontend/src/modules/data-flow/DataFlowModule.ts) | `IMPLEMENTED` | `API-017`..`API-022`, `API-051`..`API-056` | Primary Parallel-Branch Observatory (see Section 2) |
| `SCR-004` | `/market-analytics` | [MarketAnalyticsModule.ts](../../../frontend/src/modules/market-analytics/MarketAnalyticsModule.ts) | `PARTIALLY_IMPLEMENTED` | `API-001`, `API-032`, `API-004`, `API-007`, `API-036`, `API-037` | `PROP-APP-001`: `market.service.ts` & `analytics.service.ts` path/query drifts vs OpenAPI routes |
| `SCR-005` | `/data-management` | [DataManagementModule.ts](../../../frontend/src/modules/data-management/DataManagementModule.ts) | `PARTIALLY_IMPLEMENTED` | `API-039`, `API-041`, `API-042`, `API-014`, `API-046` | `PROP-APP-001`: `catalog.service.ts` calls unimplemented `/catalog/{datasets,lineage,data-quality}` |
| `SCR-006` | `/ai-workspace` | [AiWorkspaceModule.ts](../../../frontend/src/modules/ai-workspace/AiWorkspaceModule.ts) | `PARTIALLY_IMPLEMENTED` | `API-008`, `API-009`, `API-043`, `API-044`, `API-045` | `PROP-APP-001`: `agent.service.ts` `listRuns` calls unimplemented `GET /api/v1/agents/runs` |
| `SCR-007` | `/administration` | [AdministrationModule.ts](../../../frontend/src/modules/administration/AdministrationModule.ts) | `PARTIALLY_IMPLEMENTED` | `API-026`, `API-029` | `PROP-APP-001`: `auth.service.ts` calls unimplemented `GET /auth/api-keys` and `DELETE /auth/api-keys/{id}` |

---

## 2. Primary Observatory Screen (`SCR-003`: `/data-flow`) Visual Layout

- **Derived Diagram**: [Diagram UX-001: Real-Time Data Flow UI Architecture](../../diagrams/ux/01-realtime-data-flow-ui-architecture.md)

1. **Top Control Bar, Mode Isolation & Filter Strip**:
   - Displays live SSE status badge (`API-055` `/api/v1/observability/stream`), fallback WebSocket (`API-056` `/ws/v1/observability/stream`), execution context (`LIVE DATA ACTIVE` vs `DEMO TRACES PRESENT` vs `IDLE`), and live TCP probe pills (`Kafka B1..B3`, `Redis`, `ClickHouse`, `MinIO`).
   - Time window selector (`1m`, `5m`, `15m`, `1h`, `24h`, `All`), symbol filter, mode filter (`ALL`, `LIVE`, `DEMO`), `Probe Live Infra` / `Pull Live Binance REST` actions, and explicit `DEMO` actions (`Emit 5 Events`, `Inject DLQ`, `Flush Bronze -> Gold`, `Run 12-Stage Pipeline`).
2. **Global KPI Strip (Always Visible)**:
   - `Events Ingested`, `Events Processed`, `Failed / DLQ`, `Kafka Consumer Lag`, `Critical E2E P50 Latency` (broken down by Hot / OLAP / Lakehouse), and `Data Freshness`.
3. **6 Engineering Workspace Tabs**:
   - **Tab 1 — Interactive Parallel Data Flow DAG**: Zoomable/pannable SVG topology separating parallel branches (`Redis Hot || ClickHouse OLAP || Bronze->Silver->Gold`) with real-event animated pulse orbs and click-to-inspect Node Drawer.
   - **Tab 2 — Kafka Cluster & Partitions**: Broker 1..3 truth (`1-node KRaft` active vs Brokers 2 & 3 `UNAVAILABLE`), 6 canonical topics, Partition boxes (`P0..P5`), Consumer Group lag progress bars, Publish/Consume rate chart, and DLQ viewer.
   - **Tab 3 — Lakehouse & Data Warehouse Explorer**: Data Lake vs Data Lakehouse vs Data Warehouse comparison grounded in `.local_lakehouse/`, Bronze Parquet stats, Silver Apache Iceberg v2 snapshots (`v*.metadata.json`), Gold marts, DQ rules (`DQ-KLINE-001..005`, `DQ-TRADE-001..003`), and ClickHouse/Redis buffer stats.
   - **Tab 4 — Real-Time Candlestick Chart**: Canvas OHLCV + Volume chart supporting `1m/5m/15m/1h/4h/1d` `Decimal` rollups, crosshair OHLCV tooltip, and explicit zero-fake-candle policy.
   - **Tab 5 — Processing & Parallel-Branch E2E Latency Dashboard**: Non-summed branch comparison (`AC-004`), latency histogram, clickable time-bucket series, stage percentiles (`min/avg/P50/P95/P99/max`), and slow/failed event jump table.
   - **Tab 6 — Event Trace Inspector (`event_id`)**: Filterable event list, 10-timestamp UTC audit table, stage waterfall bars, and DLQ/DQ error details.

---

## 3. Secondary SPA Modules (`SCR-002`, `SCR-004`..`SCR-007`)

- **`SCR-002` Overview Dashboard (`/dashboard`)**: Platform summary KPIs, service health cards, and live observability ticker (`API-017`..`API-022`, `API-053`..`API-056`).
- **`SCR-004` Market Analytics (`/market-analytics`)**: Live symbol quotes, klines, anomaly & correlation inspection (`PARTIALLY_IMPLEMENTED` — frontend service query/path drifts logged in `PROP-APP-001`).
- **`SCR-005` Data Management (`/data-management`)**: Backfill jobs, instrument catalog, and lineage inspection (`PARTIALLY_IMPLEMENTED` — `/catalog/{datasets,lineage,data-quality}` drifts logged in `PROP-APP-001`).
- **`SCR-006` AI Workspace (`/ai-workspace`)**: Market Intelligence copilot query, session history, and execution trace drawer (`PARTIALLY_IMPLEMENTED` — `listRuns` drift logged in `PROP-APP-001`).
- **`SCR-007` Administration (`/administration`)**: Operator sign-in (`POST /api/v1/auth/token`) and API key issuance (`POST /api/v1/auth/api-keys`) (`PARTIALLY_IMPLEMENTED` — list/delete API-key routes unimplemented per `PROP-APP-001`).
