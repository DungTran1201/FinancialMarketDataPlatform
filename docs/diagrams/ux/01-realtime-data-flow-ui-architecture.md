# Diagram UX-001 — Real-Time Data Flow UI & Telemetry Architecture (`DIAG-UX-001`)

| Diagram Metadata | Value |
|---|---|
| **Diagram ID** | `DIAG-UX-001` |
| **Title** | Real-Time Data Flow UI & Telemetry Architecture |
| **Diagram Category** | `docs/diagrams/ux/` |
| **Notation / Mermaid Type** | `Mermaid (flowchart TD)` |
| **Status** | `IMPLEMENTED` |
| **Version** | `2.0.0` |
| **Authoritative Document Reference** | `docs/product/11-ux/screen-specifications.md`, `docs/product/11-ux/user-flows.md` |
| **Canonical Model Reference** | `models/ux/ux.yaml` |
| **Related Artifact IDs** | `SCR-003`, `SCR-001 (DEPRECATED)`, `UX-001`, `API-017`..`API-022`, `API-051`..`API-056`, `AC-004` |

## 1. Purpose

Illustrates the TypeScript + Vite Experience Layer Observatory module (`SCR-003` at `/data-flow` in `frontend/src/modules/data-flow/DataFlowModule.ts`, served via `frontend` host port `3001` -> `:3000` and proxied by `edge-gateway` — superseding decommissioned `SCR-001` `/ui/data-flow` & deleted `src/serving/api/gateway/ui.py`), live SSE/WebSocket push, non-mutating `/api/v1/observability/*` REST endpoints (`API-017`..`API-022`, `API-051`..`API-056`), and parallel-branch trace correlation via `PipelineTraceRegistry`.

- **Authoritative Sources**: [models/ux/ux.yaml](../../../models/ux/ux.yaml), [screen-specifications.md](../../product/11-ux/screen-specifications.md), [monitoring.md](../../product/13-operations/monitoring.md)

---

## 2. Mermaid UX & Real-Time Telemetry Flowchart (`DIAG-UX-001`)

```mermaid
flowchart TD
    subgraph UI["Frontend Experience SPA (SCR-003: /data-flow via frontend:3000 / host :3001)"]
        HDR["Top Bar: SSE Badge, LIVE/DEMO Filter, Infra Probe & Actions"]
        KPI["KPI Strip: Ingested, Processed, DLQ, Lag, E2E P50, Freshness"]
        DAG["Tab 1: Zoom/Pan Parallel SVG DAG + Node Drawer + Pulse Animation"]
        KFK["Tab 2: Kafka Cluster B1..B3 Probe, Partitions & CG Lag"]
        STG["Tab 3: Lakehouse Parquet/Iceberg v2 & ClickHouse/Redis"]
        CND["Tab 4: Real OHLCV Candlestick Chart + Decimal Rollups"]
        LAT["Tab 5: Parallel Branch Percentiles, Histogram & Clickable Buckets"]
        TRC["Tab 6: 10-Timestamp Event Trace Inspector"]
    end

    subgraph API["Observability Gateway (src/serving/api/gateway/observability.py)"]
        SSE["SSE /api/v1/observability/stream (API-055) & WS /ws/v1/observability/stream (API-056)"]
        REST["REST /api/v1/observability/{overview,topology,kafka,storage,latency,traces,candles}"]
        ACT["Actions /api/v1/observability/{live/probe,demo/emit} & API-016 /telemetry"]
    end

    subgraph Core["Shared Observability & Runtime Facade"]
        REG["PipelineTraceRegistry (10 Timestamps, Parallel Critical Path, Ring Buffer)"]
        MET["DataObservabilityMetricsCollector (10 fmdp_* Prometheus Metrics)"]
        FS["Disk & Memory Inspectors (.local_lakehouse Iceberg v2, Broker, CH, Redis, TCP Probe)"]
    end

    HDR --> ACT
    SSE --> DAG
    REST --> KPI
    REST --> KFK
    REST --> STG
    REST --> CND
    REST --> LAT
    REST --> TRC
    ACT --> REG
    REG --> SSE
    REG --> REST
    REG --> MET
    FS --> REST
```
