---
doc_id: APP-DOM-OPS-SPEC-001
title: "Domain Specification: Platform Operations, Observability & Gateway Control"
doc_type: specification
plane: application-plane
scope_level: domain
domain: platform-operations-and-control
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: devops-sre
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/gateway/observability.py"
    - "src/serving/api/gateway/service.py"
    - "src/serving/api/services/data_plane.py"
    - "src/serving/infrastructure/runtime.py"
related_docs:
  - APP-DOM-OPS-001
  - CAP-APP-OPS-DOC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Documented observability REST/SSE/WS endpoints, internal ASGI dispatch, and unauthenticated mutation surface."
---

# Domain Specification: Platform Operations, Observability & Gateway Control

## 1. Domain Responsibilities (`AS-IS`)

1. **Observability & Telemetry (`/api/v1/observability`, `/ws/v1/observability/stream`)**: Serves platform KPIs, 12-node DAG topology, Kafka broker status (including explicit single-node KRaft reporting where Brokers 2 & 3 are `UNAVAILABLE`), storage/DQ stats, percentile latencies, per-event trace timelines, candlesticks, TCP infra probing (`/live/probe`), and pipeline simulation triggers (`/demo/emit`).
2. **Data Plane Control (`/api/v1/data-platform/v01`)**: Exposes full 12-stage orchestration (`/run`), `/status`, Gold marts (`/gold/{mart_name}`), Parquet/Iceberg `/compaction`, `/lineage`, `/watermarks`, `/metrics`, and `/telemetry`.
3. **Gateway & Platform Discovery (`/api/v1/microservices`, `/api/v1/platform`, `/health/*`, `/metrics`)**: Exposes service topology, live probes across `svc-*`, arbitrary internal ASGI routing (`/dispatch/{service_id}`), and `PlatformConfig`.
4. **Operational SPA Modules**: Powers `#/dashboard` (`DashboardModule.ts`), `#/data-flow` (`DataFlowModule.ts`), and system config tabs inside `#/administration` (`AdministrationModule.ts`).

## 2. Critical Security & Integrity Gaps

- All mutating ops endpoints (`/live/probe` external HTTPS egress trigger, `/demo/emit`, `/data-platform/v01/run`, `/compaction`, and arbitrary `/microservices/dispatch/{service_id}`) execute **without authentication or RBAC checks** (`SEC-AUDIT-003`).
- `historical_transport` inside `get_observability_overview()` references an absent `use_embedded_asgi_transport` attribute and always displays `"EMBEDDED_ASGI_SIMULATOR"` (`GAP`).
- Registry metadata cites nonexistent `/ui/data-flow` and unimplemented `/ws/v1/market` (`COMPAT-009`).
