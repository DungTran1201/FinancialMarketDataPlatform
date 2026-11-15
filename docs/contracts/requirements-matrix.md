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

All 10 Functional Requirements are baselined in `models/requirements/requirements.yaml` with explicit `implementation_status` and verified test references in `models/testing/testing.yaml`:

| ID | Title | Description | Implementation Status | Architectural Component(s) | Verified Test Case(s) |
|---|---|---|---|---|---|
| `FR-01` | Streaming WebSocket Ingestion | Collect real-time market events (Ticker, Trade, Kline, Order Book) from Binance WebSocket API | `PARTIALLY_IMPLEMENTED` | `COMP-001` (`collector-ws` stub / WS adapter), `COMP-009` (`DataPlatformV01Pipeline`) | `TC-009`, `TC-010`, `TC-011`, `TC-013` |
| `FR-02` | Historical REST Synchronization & Backfill | Collect and synchronize historical market data from Binance REST API with deterministic watermarks | `PARTIALLY_IMPLEMENTED` | `COMP-002` (`collector-rest` stub / REST adapter), `COMP-009` (`DataPlatformV01Pipeline`), `COMP-014` (`svc-historical-backfill`) | `TC-009`, `TC-010`, `TC-011`, `TC-013` |
| `FR-03` | Multi-Provider Canonical Normalization | Normalize incoming provider payloads into canonical `EventEnvelopeV1` contracts | `IMPLEMENTED` | `COMP-001`, `COMP-002`, `COMP-009` (`DataPlatformV01Pipeline`) | `TC-001`, `TC-009`, `TC-010`, `TC-011`, `TC-013`, `TC-014` |
| `FR-04` | Low-Latency Hot Data Serving | Serve latest prices and snapshots from Redis with automatic ClickHouse fallback | `IMPLEMENTED` | `COMP-003` (`consumer-hot-redis`), `COMP-013` (`svc-market-hot`), `COMP-017` (`frontend-experience-layer`) | `TC-003`, `TC-009`, `TC-010`, `TC-011`, `TC-015` |
| `FR-05` | Historical & Analytical OLAP Serving | Support bounded time-series queries over historical candles, trades, and statistics in ClickHouse | `IMPLEMENTED` | `COMP-004` (`consumer-analytics-ch`), `COMP-014` (`svc-historical-backfill`), `COMP-015` (`svc-analytics-quant`) | `TC-005`, `TC-009`, `TC-010`, `TC-011`, `TC-016` |
| `FR-06` | Lakehouse Medallion Storage | Persist Bronze, Silver, and Gold datasets in Parquet and Iceberg v2 manifests (targeting MinIO object storage) | `PARTIALLY_IMPLEMENTED` | `COMP-005` (`consumer-lakehouse-bronze` stub), `COMP-009` (`DataPlatformV01Pipeline`), `COMP-010` (`GoldLayerMartEngine`) | `TC-009`, `TC-010`, `TC-011`, `TC-014` |
| `FR-07` | Data Quality & Lineage Enforcement | Enforce schema validation, deterministic deduplication, and `Decimal` quality assertions via `DataQualityGateEngine` (`DQ-KLINE-001..005`, `DQ-TRADE-001..003`; external Great Expectations runtime `PLANNED`) | `PARTIALLY_IMPLEMENTED` | `COMP-009` (`DataPlatformV01Pipeline`), `COMP-011` (`DataLineageGovernanceRegistry`) | `TC-002`, `TC-009`, `TC-010`, `TC-011`, `TC-012` |
| `FR-08` | BI & Visualization Integration | Expose curated analytical datasets in ClickHouse to Apache Superset | `PARTIALLY_IMPLEMENTED` | `COMP-004` (`consumer-analytics-ch`), `COMP-015` (`svc-analytics-quant`) | `TC-009`, `TC-010`, `TC-011` |
| `FR-09` | Isolated Agentic Intelligence | Provide an isolated 5-node LangGraph orchestrator accessing data solely through `ControlledToolGateway` (`10` tools) | `PARTIALLY_IMPLEMENTED` | `COMP-007` (`agent-worker` stub), `COMP-008` (`ControlledToolGateway`), `COMP-020` (`svc-intelligence-agent`) | `TC-004`, `TC-006`, `TC-009`, `TC-011` |
| `FR-10` | Platform Control & Governance | Manage users, RBAC roles, monitored instruments, watermarks, observability telemetry, and audit logs across PostgreSQL and control-plane endpoints | `PARTIALLY_IMPLEMENTED` | `COMP-006` (`backend-api`), `COMP-012` (`svc-api-gateway`), `COMP-016` (`svc-data-plane-v01`), `COMP-018` (`svc-catalog-governance`), `COMP-019` (`svc-iam-security`) | `TC-007`, `TC-008`, `TC-009`, `TC-011`, `TC-015`, `TC-017` |

### 1.1. Non-Functional Requirements (`NFR-001` through `NFR-003`)

| ID | Title | Target | Verification Status | Linked Test Case(s) |
|---|---|---|---|---|
| `NFR-001` | Hot Latest Price Latency | `P50 <= 5ms, P95 <= 15ms, P99 <= 30ms` | `UNVERIFIED_UNDER_PRODUCTION_LOAD` (in-process/sim verified) | `TC-010`, `TC-011`, `TC-015` |
| `NFR-002` | Historical Candles Query Latency | `P50 <= 25ms, P95 <= 80ms, P99 <= 200ms` | `UNVERIFIED_UNDER_PRODUCTION_LOAD` (`BoundedTimeRange` & DDL verified) | `TC-010`, `TC-011` |
| `NFR-003` | Plane Isolation & Graceful Degradation | `100%` Data Plane uptime on Intelligence/Redis outage | `PARTIALLY_VERIFIED_IN_PROCESS` | `TC-003`, `TC-006`, `TC-010`, `TC-011` |

---

## 2. Business Rules Register (`BR-001` through `BR-004`)

Authoritative source: `models/requirements/business-rules.yaml`.

| Rule ID | Name | Expression & Invariant Description | Related Requirements | Enforcement Point / Test Ref |
|---|---|---|---|---|
| `BR-001` | Exact Decimal Financial Precision | All monetary prices and quantities must use `Decimal(38, 18)` and never IEEE-754 floats. | `FR-03`, `FR-07` | `src/shared/contracts/events/market_events.py`, Lakehouse engines / `TC-002`, `TC-012`, `TC-016` |
| `BR-002` | OHLCV Candle Invariant | `high_price >= low_price AND high_price >= open_price AND high_price >= close_price AND base_volume >= 0` | `FR-07` | `MarketKlinePayloadV1`, `DataQualityGateEngine` (`DQ-KLINE-001..005`) / `TC-002`, `TC-012`, `TC-016` |
| `BR-003` | Monotonic Hot State Timestamp Guard | Redis hot state updates only apply when `incoming.exchange_event_time_ms >= stored.exchange_event_time_ms`. | `FR-04` | `HotStateProjector` / `TC-009`, `TC-010`, `TC-013` |
| `BR-004` | Deterministic Agent Quantitative Execution | LLMs must never compute financial arithmetic or execute raw SQL; all metrics come from `ControlledToolGateway`. | `FR-09` | `ControlledToolGateway` / `TC-004`, `TC-009`, `TC-011` |

---

## 3. Acceptance Criteria (`AC-001` through `AC-004`)

Authoritative source: `models/requirements/acceptance-criteria.yaml`.

| Criteria ID | Requirement Link | Criterion (`Given / When / Then`) | Linked Test Case(s) |
|---|---|---|---|
| `AC-001` | `FR-03` | Raw trade/kline event normalized & validated -> deterministic UUIDv5 `event_id` and `provider:symbol` partition key generated. | `TC-001`, `TC-002`, `TC-009`, `TC-010`, `TC-011`, `TC-012`, `TC-013`, `TC-014` |
| `AC-002` | `FR-04` | Redis hot cache misses or unreachable during `GET /api/v1/market/prices/{symbol}` -> transparent fallback to ClickHouse returning `source=clickhouse_fallback`. | `TC-003`, `TC-009`, `TC-010`, `TC-011`, `TC-013` |
| `AC-003` | `FR-09` | Agent attempts unwhitelisted SQL tool or exceeds row limits -> `ControlledToolGateway` rejects invocation before touching any database. | `TC-004`, `TC-009`, `TC-011` |
| `AC-004` | `FR-04` | Event flows through Ingestion, Kafka, parallel sinks, and Serving -> `/api/v1/observability/*` and `/ws/v1/observability/stream` correlate reached timestamps without summing parallel sink branches or fabricating unavailable nodes. | `TC-015` |

