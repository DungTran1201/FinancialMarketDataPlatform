# Phase 11 — Screen Specifications (`SCR-001`: Real-Time Data Flow & Latency Observatory)

## 1. Screen Overview

- **Screen ID**: `SCR-001`
- **Title**: Real-Time 12-Stage Data Flow & End-to-End Latency Observatory
- **Route**: `GET /ui/data-flow` ([src/serving/api/gateway/ui.py](../../../src/serving/api/gateway/ui.py))
- **Backing Telemetry API**: `GET /api/v1/data-platform/v01/telemetry` (`API-016`) and `POST /api/v1/data-platform/v01/run` (`API-011`)
- **Derived Diagram**: [Diagram UX-001: Real-Time Data Flow UI Architecture](../../diagrams/ux/01-realtime-data-flow-ui-architecture.md)

---

## 2. Visual Layout & Component Hierarchy

1. **Header & Real-Time Polling Controller**:
   - Displays live connection pulse (`LIVE REAL-TIME TELEMETRY STREAM`), polling frequency selector (`500ms`, `1000ms`, `2000ms`), and one-click execution trigger (`Chạy lại Full 12-Stage Pipeline`).
2. **4 Core KPI Summary Cards**:
   - **Card 1 — Tổng thời gian xử lý (`Ingestion -> Monitoring`)**: Displays $\mathcal{T}_{\text{ingest}\to\text{monitor}} = \sum_{i=1}^{11} \mathcal{T}_{\text{stage}, i}$ in `ms` alongside total 12-stage time (including Stage 12 Lineage).
   - **Card 2 — Độ trễ Nguồn Thực tế (`Exchange -> Ingestion`)**: Displays live $\mathcal{L}_{\text{source}} = t_{\text{ingested}} - t_{\text{exchange}}$ (`ms`) and total End-to-End lag $\mathcal{L}_{\text{E2E}} = \mathcal{L}_{\text{source}} + \mathcal{T}_{\text{ingest}\to\text{monitor}}$.
   - **Card 3 — Ngân sách SLA (`<= 200 ms`)**: Displays percentage of SLA budget consumed with dynamic progress bar.
   - **Card 4 — Tiến trình Pipeline & Kiểm soát Chất lượng**: Displays `100% (12/12)` stage completion, Hot Redis updates count, and DLQ routed count.
3. **Live Exchange Source Streams Table**:
   - Real-time table updating `BTCUSDT`, `ETHUSDT`, `SOLUSDT`, `BNBUSDT`, and `XRPUSDT` with live `last_price`, `exchange_event_time`, `source_lag_ms`, and `LIVE_STREAMING` status badge.
4. **12-Stage Visual Data Flow & Latency Waterfall Grid**:
   - Renders 12 interactive cards (`Stage 1: Exchange Discovery` $\rightarrow$ `Stage 2: WS & REST Ingestion` $\rightarrow$ `Stage 3: Validation & DLQ` $\rightarrow$ `Stage 4: Kafka Partitioned Stream` $\rightarrow$ `Stage 5: MinIO Bronze Archival` $\rightarrow$ `Stage 6: Silver Merge & Hot/OLAP Sinks` $\rightarrow$ `Stage 7: Gold Analytical Marts` $\rightarrow$ `Stage 8: Great Expectations DQ Gate` $\rightarrow$ `Stage 9: Iceberg Storage Compaction` $\rightarrow$ `Stage 10: Low-Latency Data Serving` $\rightarrow$ `Stage 11: Prometheus Monitoring` $\rightarrow$ `Stage 12: Data Governance & Lineage`).
   - Each card displays: stage status badge, underlying technology, output artifact, stage processing duration (`processing_ms`), cumulative elapsed time (`cumulative_elapsed_ms`), stage source lag (`source_lag_ms`), records processed, and progress bar (`0–100%`).

