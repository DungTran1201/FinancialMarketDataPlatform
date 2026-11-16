---
doc_id: CAP-APP-OPS-ERR-001
title: "Error Catalog: Observability, Control & Gateway"
doc_type: specification
plane: application-plane
scope_level: capability
domain: platform-operations-and-control
capability_id: CAP-APP-OPS-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: devops-sre
accountable_role: fullstack-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/gateway/observability.py"
    - "src/serving/api/gateway/service.py"
    - "src/serving/api/services/data_plane.py"
related_docs:
  - APP-ERR-SHARED-001
  - CAP-APP-OPS-REQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Documented string-detail 404/422 errors and unimplemented UI stream control routes."
---

# Error Catalog: Observability, Control & Gateway

## 1. Ops Endpoint Errors (`{ "detail": "<string>" }`)

| HTTP | Condition | Route |
|---|---|---|
| `404` | `Trace not found for event_id=...` | `GET /api/v1/observability/traces/{event_id}` |
| `404` | `Unknown Gold mart '...'` | `GET /api/v1/data-platform/v01/gold/{mart_name}` |
| `404` | Unknown `service_id` (`KeyError` from `MicroserviceRegistry`) | `POST /api/v1/microservices/dispatch/{service_id}` |
| `422` | Pydantic regex/range failure (`window`, `interval`, `action`, `count`) | `/observability/*`, `/data-platform/v01/*` |
| `404` | Frontend calls `/api/v1/observability/stream/control` (`COMPAT-004`) | Unimplemented backend route |

## 2. Gateway Edge & Standalone Middleware Caveats

- Edge blocks (`400`/`403`/`429`) apply via `main.py` (`8000`) per [shared error catalog](../../../../../shared-contracts/error-catalog.md), but do not protect direct calls to standalone `svc-data-plane-v01` (`8007`).
