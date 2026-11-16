---
doc_id: CAP-APP-OPS-REQ-001
title: "Capability Specification: Observability, Control & Gateway"
doc_type: specification
plane: application-plane
scope_level: capability
domain: platform-operations-and-control
capability_id: CAP-APP-OPS-001
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
    - "frontend/src/modules/dashboard/DashboardModule.ts"
    - "frontend/src/modules/data-flow/DataFlowModule.ts"
related_docs:
  - CAP-APP-OPS-DOC-001
  - CAP-APP-OPS-TM-001
  - APP-ARCH-COMPAT-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Authored atomic functional requirements and verified frontend/backend gaps for platform observability & control."
---

# Capability Specification: Observability, Control & Gateway

## 1. Capability Scope & `AS-IS` Reality

Provides live telemetry snapshots, SSE/WS streams, 12-stage DAG inspection, single-node Kafka KRaft broker reporting, TCP/Binance probing, simulation controls, DataPlatformV01 pipeline triggers, Gold mart queries, and internal microservice dispatch across `#/dashboard`, `#/data-flow`, and `#/administration`.

## 2. Functional Requirements

| Req ID | Requirement Statement | `AS-IS` Evidence | Target / Gap |
|---|---|---|---|
| `FR-OPS-001` | System MUST report honest platform KPIs, 12-node topology, Kafka single-node KRaft status (`Broker 2/3 UNAVAILABLE`), storage/DQ stats, percentile latencies, and per-event traces. | `gateway/observability.py`, `runtime.py:710-1405` | `historical_transport` hardcodes `"EMBEDDED_ASGI_SIMULATOR"` due to missing attr check. |
| `FR-OPS-002` | System MUST stream live telemetry via SSE (`/observability/stream`) and bidirectional WebSocket (`/ws/v1/observability/stream`) supporting `snapshot`, `trace`, `heartbeat`, and `ping`/`pong`. | `gateway/observability.py:177-280` | `observability.service.setStreamControl()` targets unimplemented `/stream/control` (`404`, `COMPAT-004`). |
| `FR-OPS-003` | Operators MUST be able to trigger TCP infra/Binance probes (`/live/probe`), controlled simulations (`/demo/emit`), 12-stage `/data-platform/v01/{run,compaction}`, and microservice dispatch (`/microservices/dispatch/{id}`). | `observability.py:159-175`, `services/data_plane.py`, `gateway/service.py` | **CRITICAL GAP (`SEC-AUDIT-003`)**: Zero auth/RBAC guards on mutating/probing/dispatch endpoints. |
| `FR-OPS-004` | Gateway MUST accurately advertise live service topology (`/microservices/topology`), live microservice health, platform config (`/platform/config`), `/health/*`, and `/metrics`. | `gateway/service.py`, `main.py` | Registry lists nonexistent `/ui/data-flow` and unimplemented `/ws/v1/market`; `/health/ready` never checks live DBs. |
| `FR-OPS-005` | `#/dashboard` & `#/data-flow` UI views MUST bind KPIs and DAG node metrics exclusively to live backend telemetry without hardcoded status strings. | `DashboardModule.ts`, `PipelineDag.ts` | `DashboardModule` hardcodes `"5/5 Connected"` card (`COMPAT-005`) and `PipelineDag.ts` contains static SVG node labels (`COMPAT-006`). |
