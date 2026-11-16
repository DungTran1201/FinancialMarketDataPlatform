---
doc_id: CAP-APP-OPS-TS-001
title: "Test Scenarios: Observability, Control & Gateway"
doc_type: specification
plane: application-plane
scope_level: capability
domain: platform-operations-and-control
capability_id: CAP-APP-OPS-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: qa-lead
accountable_role: devops-sre
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "tests/integration/test_realtime_observability_dashboard.py"
    - "tests/integration/test_three_planes_framework.py"
related_docs:
  - CAP-APP-OPS-DOC-001
  - CAP-APP-OPS-REQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: qa-lead
    summary: "Documented observability REST/SSE/WS and microservice gateway verification scenarios."
---

# Test Scenarios: Observability, Control & Gateway

## 1. Covered In-Process Backend Scenarios (`AS-IS`)

- **`TS-OPS-001`**: Execute `POST /observability/demo/emit` (`emit_batch`, `inject_dlq`, `flush_lakehouse`) -> query `/overview`, `/topology` (12 nodes, Kafka Broker 2 & 3 `UNAVAILABLE`), `/kafka`, `/storage` (6 DQ rules), `/latency`, and `/traces/{event_id}`.
- **`TS-OPS-002`**: Connect SSE (`/observability/stream?max_events=2`) and WebSocket (`/ws/v1/observability/stream`), verify initial `snapshot`, send `ping` -> receive `pong`.
- **`TS-OPS-003`**: Execute `POST /data-platform/v01/run`, `GET /gold/{mart_name}`, `/compaction`, `/lineage`, `/watermarks`, `/metrics`, and `/microservices/{topology,health,dispatch}`.

## 2. Uncovered Security & UI Gaps

- Negative RBAC tests (`401`/`403`) on mutating ops routes (`SEC-OPS-001`) are unimplemented; `#/dashboard` & `#/data-flow` frontend UI DOM tests do not exist.
