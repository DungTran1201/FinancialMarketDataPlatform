---
doc_id: CAP-APP-OPS-COMP-001
title: "Component & Screen Design: Observability, Gateway & Operational Screens"
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
    - "frontend/src/modules/administration/AdministrationModule.ts"
related_docs:
  - CAP-APP-OPS-REQ-001
  - APP-ARCH-COMPAT-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Documented backend telemetry/dispatch gateways and screen designs/defects for Dashboard, DataFlow, and Administration."
---

# Component & Screen Design: Observability, Gateway & Operational Screens

## 1. Backend Gateway & Runtime Telemetry Components

- **`gateway/observability.py`**: Exposes `/api/v1/observability/*` and `/ws/v1/observability/stream` delegating to `PlatformRuntimeContainer` (`probe_external_infrastructure`, `trace_registry`, `get_observability_topology`, `trigger_demo_action`).
- **`gateway/service.py` & `registry.py`**: Exposes `/api/v1/microservices/{topology,health,dispatch/{service_id}}`. Registry cites unimplemented `/ws/v1/market` and removed `/ui/data-flow` (`COMPAT-009`).
- **`services/data_plane.py`**: Exposes `/api/v1/data-platform/v01/{run,status,gold/{mart},compaction,lineage,watermarks,metrics,telemetry}`.

## 2. Frontend Screen Specifications (`#/dashboard`, `#/data-flow`, `#/administration`)

- **`DashboardModule.ts` (`#/dashboard`)**: Displays KPI tiles (`events_ingested`, latency percentiles, freshness), `LatencyHistogram.ts`, live WebSocket feed, and Core Stores health card. *Defect (`COMPAT-005`)*: Hardcodes `"5/5 Connected"` & `"min/Isolated"` independently of `/live/probe`.
- **`DataFlowModule.ts` (`#/data-flow`)**: Renders 12-node DAG (`PipelineDag.ts`), Kafka partition lag table, trace table + drawer timeline (`t0..t9`), and Demo simulation buttons (`emit_batch`, `inject_dlq`, `flush_lakehouse`, `run_full_pipeline`). *Defects*: `PipelineDag.ts` embeds static SVG badges (`COMPAT-006`); `setStreamControl()` hits unimplemented `/stream/control` (`404`, `COMPAT-004`).
- **`AdministrationModule.ts` (`#/administration`)**: Renders Platform Config, Microservice Topology/Health checks, Domain origins, and API keys (`CAP-APP-IAM-001` defects `COMPAT-001..003`).
