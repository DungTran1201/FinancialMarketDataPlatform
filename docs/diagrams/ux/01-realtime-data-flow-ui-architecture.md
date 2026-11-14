# Diagram UX-001 — Real-Time Data Flow UI & Telemetry Architecture (`DIAG-UX-001`)

## 1. Purpose

Illustrates the frontend UX/UI component hierarchy (`SCR-001`), real-time telemetry loop (`API-016`), and stage-by-stage latency calculation from **Stage 1/2 (Ingestion)** to **Stage 11/12 (Monitoring & Lineage)**.

- **Authoritative Sources**: [models/ux/ux.yaml](../../../models/ux/ux.yaml), [screen-specifications.md](../../product/11-ux/screen-specifications.md)

---

## 2. Mermaid UX & Real-Time Telemetry Flowchart (`DIAG-UX-001`)

```mermaid
flowchart TD
    subgraph UI["Frontend Observatory UI (SCR-001: /ui/data-flow)"]
        HDR["Header & Polling Controller<br/>(500ms / 1000ms / 2000ms + Full Run Trigger)"]
        KPI["4 Real-Time KPI Cards<br/>(T_ingest_to_monitor, Source Lag, E2E Lag, SLA %)"]
        TBL["Live Exchange Feed Table<br/>(BTCUSDT, ETHUSDT, SOLUSDT, BNBUSDT, XRPUSDT)"]
        GRID["12-Stage Visual Data Flow & Latency Waterfall<br/>(Processing ms, Cumulative ms, Progress %)"]
    end

    subgraph API["Plane A / B Telemetry & Control Endpoints"]
        TEL["GET /api/v1/data-platform/v01/telemetry (API-016)<br/>(step_realtime_tick_and_collect_telemetry)"]
        RUN["POST /api/v1/data-platform/v01/run (API-011)<br/>(run_end_to_end_pipeline)"]
    end

    subgraph Engine["12-Stage Real-Time Pipeline Timing (perf_counter_ns)"]
        S1_4["Stages 1-4: Discovery -> Ingestion -> Validation -> Kafka"]
        S5_8["Stages 5-8: MinIO Bronze -> Silver/Redis/CH -> Gold -> DQ Gate"]
        S9_12["Stages 9-12: Iceberg Compaction -> Serving -> Monitoring -> Lineage"]
        CALC["Latency Aggregator:<br/>T_ingest_to_monitor = Sum(S01..S11)<br/>T_E2E = Source_Lag + T_ingest_to_monitor"]
    end

    HDR -- "Poll Every 500..2000ms" --> TEL
    HDR -- "Click Run Full Pipeline" --> RUN
    TEL --> Engine
    S1_4 --> S5_8 --> S9_12 --> CALC
    CALC --> KPI
    CALC --> TBL
    CALC --> GRID
```

