# Requirements, Business Rules & Acceptance Traceability Matrix

| Metadata | Value |
|---|---|
| **Document ID** | `DOC-CONTRACTS-REQ-MATRIX` |
| **Title** | End-to-End Requirements Traceability Matrix |
| **Category** | Technical Governance & Traceability |
| **Status** | `APPROVED` |
| **Updated Date** | `2026-11-15` |
| **Authoring Role** | `requirements-engineer` & `documentation-architect` |

---

## 1. Functional Requirements Register (`FR-01` through `FR-10`)

All 10 Functional Requirements are baselined in `models/requirements/requirements.yaml` and verified by `tools/validators/validate_traceability.py`:

| ID | Title | Description | Architectural Component(s) | Verified Test Case(s) |
|---|---|---|---|---|
| `FR-01` | Streaming WebSocket Ingestion | Collect real-time market events (Ticker, Trade, Kline, Order Book) from Binance WebSocket API | `COMP-001` (`collector-ws`), `COMP-009` (`DataPlatformV01Pipeline`) | `TC-009`, `TC-010` |
| `FR-02` | Historical REST Synchronization & Backfill | Collect and synchronize historical market data from Binance REST API with deterministic watermarks | `COMP-002` (`collector-rest`), `COMP-009` (`DataPlatformV01Pipeline`) | `TC-009`, `TC-011` |
| `FR-03` | Multi-Provider Canonical Normalization | Normalize incoming provider payloads into canonical `EventEnvelopeV1` contracts | `COMP-001` (`collector-ws`), `COMP-002` (`collector-rest`), `COMP-009` (`DataPlatformV01Pipeline`) | `TC-001`, `TC-009` |
| `FR-04` | Low-Latency Hot Data Serving | Serve latest prices and snapshots from Redis with automatic ClickHouse fallback | `COMP-003` (`consumer-hot-redis`), `COMP-013` (`svc-market-hot`) | `TC-003`, `TC-009` |
| `FR-05` | Historical & Analytical OLAP Serving | Support bounded time-series queries over historical candles, trades, and statistics in ClickHouse | `COMP-004` (`consumer-analytics-ch`), `COMP-015` (`svc-analytics-quant`) | `TC-005`, `TC-009` |
| `FR-06` | Lakehouse Medallion Storage | Persist Bronze, Silver, and Gold datasets in Apache Iceberg + Parquet over MinIO | `COMP-005` (`consumer-lakehouse-bronze`), `COMP-010` (`GoldLayerMartEngine`) | `TC-009`, `TC-012` |
| `FR-07` | Data Quality & Lineage Enforcement | Enforce schema validation at ingestion, deterministic deduplication, and Great Expectations assertions | `COMP-009` (`DataPlatformV01Pipeline`), `COMP-011` (`DataLineageGovernanceRegistry`) | `TC-002`, `TC-009`, `TC-014` |
| `FR-08` | BI & Visualization Integration | Expose curated analytical datasets in ClickHouse to Apache Superset | `COMP-004` (`consumer-analytics-ch`), `COMP-015` (`svc-analytics-quant`) | `TC-009` |
| `FR-09` | Isolated Agentic Intelligence | Provide an isolated LangGraph service accessing data solely through the Controlled Tool Gateway | `COMP-007` (`agent-worker`), `COMP-008` (`ControlledToolGateway`) | `TC-004`, `TC-006`, `TC-009` |
| `FR-10` | Platform Control & Governance | Manage users, RBAC roles, monitored instruments, watermarks, and audit logs in PostgreSQL | `COMP-006` (`backend-api`), `COMP-012` (`svc-api-gateway`), `COMP-016` (`svc-data-plane-v01`) | `TC-007`, `TC-008`, `TC-009` |

---

## 2. Business Rules Register (`BR-001` through `BR-003`)

Authoritative source: `models/requirements/business-rules.yaml`.

| Rule ID | Name | Constraint & Invariant Description | Enforcement Point |
|---|---|---|---|
| `BR-001` | Exact Financial Precision | All monetary values, quantities, spreads, and VWAPs must be computed using fixed-point `Decimal` arithmetic (`0.00000001`). Floating-point arithmetic is strictly prohibited. | `src/shared/domain/quant.py`, Lakehouse engines |
| `BR-002` | Ingestion Rate Limiting | Outbound HTTP requests to exchanges must not exceed 80% of published IP rate limits (e.g. `<= 960 weight/min` on Binance). | `src/ingestion/application/rate_limiter.py` |
| `BR-003` | Mandatory DQ Promotion Gate | Lakehouse batches with failing critical data quality rules (`DQ-KLINE-001..005`) must be blocked from Gold layer promotion and routed to DLQ. | `src/lakehouse/quality/` |

---

## 3. Acceptance Criteria (`AC-01` through `AC-04`)

Authoritative source: `models/requirements/acceptance-criteria.yaml`.

| Criteria ID | Requirement Link | Criterion Statement | Verification Command |
|---|---|---|---|
| `AC-01` | `FR-01`, `FR-02` | End-to-end event latency from ingestion to serving must be sub-second (`< 1000ms`) for 95% of events. | `pytest tests/e2e/` |
| `AC-02` | `FR-03`, `BR-001` | Lakehouse Silver merge deduplicates events by natural key with zero floating-point precision loss. | `pytest tests/data_quality/` |
| `AC-03` | `FR-04`, `FR-09` | Edge API Gateway rejects unauthorized requests with HTTP 401/403 and limits anomalous IP burst rates. | `pytest tests/unit/test_security_and_defense.py` |
| `AC-04` | `FR-10` | Prometheus `/metrics` endpoint exposes `fmdp_*` counters, histograms, and consumer lag gauges. | `pytest tests/integration/` |

