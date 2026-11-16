---
doc_id: OVR-ARCH-XPL-001
title: "Cross-Plane Interactions & Canonical Contract Ownership"
doc_type: architecture
plane: platform
scope_level: platform
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: system-architect
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/infrastructure/runtime.py"
    - "src/serving/api/modules/"
    - "src/intelligence/tools/contracts.py"
related_docs:
  - OVR-ROOT-001
  - OVR-ARCH-3P-001
  - OVR-DIAG-XPL-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: system-architect
    summary: "Mapped every cross-plane interaction, provider/consumer contract owner, execution mechanism, and AS-IS vs TARGET difference."
---

# Cross-Plane Interactions & Canonical Contract Ownership

Derived sequence view: [cross-plane-interaction.md](diagrams/cross-plane-interaction.md) (`DIAG-OVR-XPL-001`).

## 1. Cross-Plane Contract Ownership & Dependency Matrix `[REQUIRED]`

Per Documentation V2 rules, consumers MUST reference provider-owned contracts rather than copying schemas.

| Flow ID | Interaction Description | Provider Plane | Consumer Plane | Authoritative Contract Path | `AS-IS` Execution Mechanism | Failure / Fallback Behavior (`AS-IS`) |
|---|---|---|---|---|---|---|
| `XPL-01` | Market quote, snapshot & orderbook query (`Hot Cache -> OLAP Fallback`) | Data Plane (`CAP-DP-STR-002`) | Application Plane (`CAP-APP-MKT-001`) | `src/shared/contracts/schemas/datasets.py` & `docs/application-plane/domains/market-experience-and-catalog/capabilities/market-and-analytics-query-portal/contracts/openapi.yaml` | In-process `GetLatestPriceQueryHandler` tries `HotStateProjector` dict, falling back transparently to `ClickHouseBatchSink` dict (`is_stale=True`); orderbook missing falls back to static bids/asks. | Returns `404` for unknown prices/snapshots; static dict for orderbook (`GAP`). |
| `XPL-02` | Historical candles, trades, quant math & manual ingestion/backfill triggers | Data Plane (`CAP-DP-ING-001`, `CAP-DP-STR-002`, `CAP-DP-LAK-001`) | Application Plane (`CAP-APP-MKT-001`, `CAP-APP-OPS-001`) | `docs/data-plane/shared-contracts/asyncapi.yaml` & `docs/data-plane/shared-contracts/data-contract.yaml` | In-process synchronous calls from FastAPI routers via `PlatformRuntimeContainer` into `ProductionExchangeHistoricalCollector` (ASGI sim), `ClickHouseBatchSink`, and `DataPlatformV01Pipeline`. | Invalid time window returns `422` (`ERR_INVALID_TIME_RANGE`); bad ingest routes to `market.dlq.v1`. |
| `XPL-03` | Observability telemetry, 10-timestamp trace stream (`t0..t9`), SSE/WS & Prometheus `/metrics` | Data Plane + Shared Observability | Application Plane (`CAP-APP-OPS-001`) -> Browser SPA | `src/shared/observability/{tracing,metrics}.py` & `docs/application-plane/domains/platform-operations-and-control/capabilities/observability-control-and-gateway/contracts/openapi.yaml` | In-process `PipelineTraceRegistry` (`asyncio.Queue`) streams snapshots/traces/heartbeats over SSE & WS; `DataObservabilityMetricsCollector` exports `/metrics`; TCP sockets probe infra ports. | Probe timeouts report `UNAVAILABLE` without crashing API; SSE reconnects every `3s` on client. |
| `XPL-04` | Agent investigation execution (`POST /agents/runs`) & SSE event replay | Application Plane (`CAP-APP-AGT-001`) -> Intelligence Plane (`CAP-INT-ORC-001`) | Application Plane (`AiWorkspaceModule`) | `docs/application-plane/domains/agent-experience-and-reporting/capabilities/agent-run-and-report-portal/contracts/openapi.yaml` & `src/intelligence/workflows/investigation.py` | Router calls `await runtime.execute_agent_investigation(...)` synchronously inside `202` request handler (idempotent via `Idempotency-Key` dict lookup). | Unmonitored symbol sets `status="FAILED"`; non-existent `run_id` returns `404`. |
| `XPL-05` | Agent read-only data tool calls & report persistence (`ControlledToolGateway`) | Data Plane (`CAP-DP-STR-002`) + App Runtime (`self.reports`) | Intelligence Plane (`CAP-INT-ORC-001`) | `src/intelligence/tools/contracts.py` & `docs/intelligence-plane/shared-contracts/tool-contracts.yaml` | `PlatformRuntimeContainer._register_all_ten_deterministic_tools()` injects Python closures into `ControlledToolGateway`, enforcing RBAC & row limits (`max_rows_or_periods`) over in-memory stores. | Non-whitelisted tool / missing permission raises `UnauthorizedToolAccessError`; oversized `limit` raises `ToolQueryLimitExceededError`; invalid citations raise `ReportProvenanceError`. |
| `XPL-06` | Anomaly detection event trigger (`market.anomalies.v1`) | Data Plane (`CAP-DP-STR-002` `AnomalyDetector`) | Intelligence Plane (`CAP-INT-ORC-001`) `[TARGET]` | `docs/data-plane/shared-contracts/asyncapi.yaml` (`market.anomalies.v1`) | `POST /api/v1/analytics/anomalies/evaluate` publishes `EventEnvelopeV1` to in-memory `market.anomalies.v1`; **automatic Kafka consumer loop triggering `agent-worker` is `NOT_IMPLEMENTED`** (`intelligence/main.py` is a stub). | `cooldown_seconds=900` prevents duplicate anomaly emissions. |

## 2. Building Block & Compatibility Policies `[REQUIRED]`

- Breaking changes to `EventEnvelopeV1` (`schema_version = "1.0.0"`) or topic schemas require a versioned topic suffix (`.v2`).
- Consumers MUST tolerate additive optional JSON fields (`related_docs` contracts use schema-verified optional keys).
- Security enforcement across all cross-plane HTTP ingress (`XPL-01`..`04`) currently has `BLOCKING` gap `SEC-AUDIT-003`.

## 3. Scope & Context Constraints `[REQUIRED]`

- Cross-plane state sharing (`runtime.monitored_instruments`, `runtime.agent_runs`, `runtime.reports`) works ONLY inside the single-process monolith (`main.py`); multi-container Compose execution (`--profile microservices`) lacks shared PostgreSQL/Redis wiring (`GAP-ARCH-001`).
