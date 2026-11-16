---
doc_id: APP-OPS-SLO-001
title: "Application Plane Observability & SLIs/SLOs"
doc_type: specification
plane: application-plane
scope_level: plane
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: devops-sre
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/main.py"
    - "src/serving/api/gateway/observability.py"
    - "src/serving/infrastructure/runtime.py"
related_docs:
  - APP-ROOT-001
  - APP-OPS-RUN-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Documented emitted serving metrics, trace subscriptions, and unapproved target latency/availability SLOs."
---

# Application Plane Observability & SLIs/SLOs

## 1. Instrumented Telemetry (`AS-IS`)

- **Prometheus `/metrics`**: Emits HTTP serving counter increments from `runtime.observability_metrics.record_serving_request(...)` across `/api/v1/observability/*` handlers (`2xx` and `4xx`). Other module routers (`/market`, `/historical`, `/auth`, `/agents`) do not record per-route Prometheus histograms.
- **SSE & WS Heartbeat Telemetry**: `/api/v1/observability/stream` (2.5s timeout heartbeat) and `/ws/v1/observability/stream` (3.0s timeout heartbeat) push live `EventLifecycleTrace` deltas and overview snapshots.
- **Response Trace Headers**: `install_security_defense_middleware` injects `X-Request-ID`, `X-Client-IP-Token`, `X-RateLimit-Tier`, and `X-RateLimit-Remaining` on routes attached to `main.py` and `services/iam.py`.

## 2. Target SLO Status (`OPEN` — Unapproved)

- Numeric API availability targets, p95 REST response SLAs, and WebSocket fan-out capacity ceilings are explicitly marked **`OPEN`** pending load testing once synchronous `POST` endpoints are decoupled into background workers and Postgres persistence is active.
