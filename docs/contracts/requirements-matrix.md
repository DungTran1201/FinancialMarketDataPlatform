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

| ID | Title | Description | Architectural Component | Verified Test Case |
|---|---|---|---|---|
| `FR-01` | Market Data Ingestion | Real-time WebSocket and HTTP REST ingestion from external exchanges | `COMP-001` (Ingestion Engine) | `TC-001` |
| `FR-02` | Event Streaming Backbone | At-least-once partitioned Kafka messaging with ordering guarantees | `COMP-002` (Event Streaming Broker) | `TC-002` |
| `FR-03` | Medallion Lakehouse Storage | Multi-layer lakehouse (Bronze, Silver, Gold) with ZSTD Parquet | `COMP-003` (Lakehouse Storage Engine) | `TC-003` |
| `FR-04` | Market Data Serving APIs | Low-latency REST, WebSocket, and SSE endpoints for market data | `COMP-004` (Serving API Gateway) | `TC-004` |
| `FR-05` | Real-time Anomaly Detection | Continuous Z-score and volume anomaly detection on streaming data | `COMP-005` (Anomaly Detection Engine) | `TC-005` |
| `FR-06` | Clean Architecture Boundaries | Strict isolation between Domain, Application, and Infrastructure layers | `COMP-006` (Clean Architecture Guard) | `TC-006` |
| `FR-07` | Agentic Autonomous Investigation | Multi-turn agent investigation workflow powered by LangGraph | `COMP-007` (Agentic Intelligence Engine) | `TC-007` |
| `FR-08` | Polyglot Storage Tiering | Automated routing to Redis, ClickHouse, and MinIO based on temperature | `COMP-008` (Storage Routing Engine) | `TC-008` |
| `FR-09` | Security Defense-in-Depth | JWT, IP-HMAC binding, NIST AES-256-GCM masking, and role access control | `COMP-009` (Security Defense Subsystem) | `TC-009` |
| `FR-10` | Observability & Telemetry | Prometheus metrics exposition, healthchecks, and structured audit logs | `COMP-010` (Observability Subsystem) | `TC-010` |

---

## 2. Business Rules Register (`BR-001` through `BR-003`)

Authoritative source: `models/requirements/business-rules.yaml`.

| Rule ID | Name | Constraint & Invariant Description | Enforcement Point |
|---|---|---|---|
| `BR-001` | Exact Financial Precision | All monetary values, quantities, spreads, and VWAPs must be computed using fixed-point `Decimal` arithmetic (`0.00000001`). Floating-point arithmetic is strictly prohibited. | `src/shared/domain/quant.py`, Lakehouse engines |
| `BR-002` | Ingestion Rate Limiting | Outbound HTTP requests to exchanges must not exceed 80% of published IP rate limits (e.g. `<= 960 weight/min` on Binance). | `src/ingestion/infrastructure/rate_limiter.py` |
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

