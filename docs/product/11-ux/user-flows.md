# Phase 11 — User Flows (`UX-001`: Real-Time Data Flow & Latency Monitoring)

## 1. User Flow Identification

- **Flow ID**: `UX-001`
- **Primary Actor**: Data Engineer / Site Reliability Operator / Quantitative Analyst
- **Entry Screen**: `SCR-001` (`/ui/data-flow`)
- **Canonical Model**: [models/ux/ux.yaml](../../../models/ux/ux.yaml)

---

## 2. Step-by-Step Interaction Flow

1. **Step 1 — Open Observatory (`/ui/data-flow`)**: User navigates to `/ui/data-flow`; the browser initializes the real-time telemetry loop polling `GET /api/v1/data-platform/v01/telemetry` (`API-016`).
2. **Step 2 — Verify Live Source Feeds & Network Lag**: User inspects the live exchange stream table (`BTCUSDT`, `ETHUSDT`, `SOLUSDT`, `BNBUSDT`, `XRPUSDT`) to confirm real-time price updates and verify `source_lag_ms`.
3. **Step 3 — Audit 12-Stage Processing & Cumulative Waterfall**: User inspects each of the 12 stages (`Discovery` $\rightarrow$ `Ingestion` $\rightarrow$ `Validation` $\rightarrow$ `Kafka` $\rightarrow$ `MinIO Bronze` $\rightarrow$ `Silver + Redis/ClickHouse` $\rightarrow$ `Gold Marts` $\rightarrow$ `DQ Gate` $\rightarrow$ `Iceberg Compaction` $\rightarrow$ `Serving` $\rightarrow$ `Monitoring` $\rightarrow$ `Lineage`) to identify per-stage `processing_ms` and `cumulative_elapsed_ms`.
4. **Step 4 — Evaluate Total Ingestion-to-Monitoring Latency**: User reviews the KPI card computing $\mathcal{T}_{\text{ingest}\to\text{monitor}} = \sum_{i=1}^{11} \mathcal{T}_{\text{stage}, i}$ and verifies SLA utilization remains within the $\le 200\text{ ms}$ budget.
5. **Step 5 — Trigger On-Demand Full Pipeline Re-Run**: User clicks `Chạy lại Full 12-Stage Pipeline` (`POST /api/v1/data-platform/v01/run`) or adjusts the polling interval (`500ms` / `1000ms` / `2000ms`) to stress-test real-time responsiveness.

