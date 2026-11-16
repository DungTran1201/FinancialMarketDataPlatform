---
doc_id: APP-DOM-OPS-GLOSS-001
title: "Glossary: Platform Operations, Observability & Gateway Control"
doc_type: glossary
plane: application-plane
scope_level: domain
domain: platform-operations-and-control
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: devops-sre
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/gateway/observability.py"
    - "src/serving/infrastructure/runtime.py"
related_docs:
  - APP-DOM-OPS-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Defined terms for EventLifecycleTrace, LiveProbeRequest, DemoSimulationRequest, and MicroserviceRegistry."
---

# Glossary: Platform Operations, Observability & Gateway Control

## 1. Domain Terms

- **`EventLifecycleTrace`**: Per-event telemetry record tracking timestamps (`t0_collector_rx` through `t9_serving_ready`), serial vs parallel hot/OLAP/lakehouse branch durations, and final status (`SERVING_COMPLETE` / `DQ_BLOCKED`).
- **TCP Infrastructure Probe (`/live/probe`)**: Non-blocking socket check with 5-second cache TTL testing Kafka `:9092`, Redis, ClickHouse `:8123`, MinIO `:9000`, and PostgreSQL, optionally running HTTPS pull from `api.binance.com`.
- **`MicroserviceRegistry.dispatch_internal_request`**: Internal gateway helper invoking ASGI apps (`svc-market-hot`..`svc-data-plane-v01`) from `POST /api/v1/microservices/dispatch/{service_id}`.
- **`DemoSimulationRequest`**: Controlled trigger (`emit_batch`, `inject_dlq`, `flush_lakehouse`, `run_full_pipeline`) exercising end-to-end runtime pipelines.
