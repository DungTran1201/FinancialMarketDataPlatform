---
doc_id: APP-ERR-SHARED-001
title: "Application Plane Shared HTTP & Middleware Error Catalog"
doc_type: specification
plane: application-plane
scope_level: plane
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/iam/presentation/router.py"
    - "src/serving/api/modules/market/presentation/router.py"
    - "src/serving/api/modules/historical/presentation/router.py"
    - "src/serving/api/modules/analytics/presentation/router.py"
    - "src/serving/api/modules/agent_api/presentation/router.py"
    - "src/serving/api/modules/reporting/presentation/router.py"
related_docs:
  - APP-ROOT-001
  - APP-ARCH-API-001
  - CAP-APP-IAM-DOC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Cataloged middleware JSON error envelopes and FastAPI HTTPException detail formats observed in Application Plane routers."
---

# Application Plane Shared HTTP & Middleware Error Catalog

## 1. Error Envelope Divergence (`AS-IS`)

1. **Middleware Envelope** (`install_security_defense_middleware`): `{ "error": { "code", "message", "request_id", "timestamp", ... } }` on HTTP `400`, `403`, `429`.
2. **Structured FastAPI Detail**: `{ "detail": { "code": "ERR_*", "message": "..." } }` returned by `market`, `historical` (`422`/`404`), `analytics` (`404`), `agents` (`404`), and `reports` (`404`).
3. **Plain String FastAPI Detail**: `{ "detail": "<string>" }` returned by `iam` (`422`/`401`), `observability` (`404`), `microservices` (`404`), and `data-platform/v01` (`404`).

## 2. Shared Plane Error Codes

| HTTP Status | Code / Detail | Trigger Condition | Source (`AS-IS`) |
|---|---|---|---|
| `400` | `UNTRUSTED_HOST_HEADER` | `Host` header not in `DomainHttpsEndpointPolicy.allowed_hosts` / subdomain. | `iam/presentation/router.py:67-79` |
| `401` | String `detail` | Invalid password or failed `JwtSecurityService.verify_token` / expired / IP mismatch / revoked. | `iam/presentation/router.py:204,238` |
| `403` | `WAF_THREAT_DETECTED` | URL path or query string matches regex WAF SQLi/XSS/traversal pattern. | `iam/presentation/router.py:83-96` |
| `404` | `ERR_SYMBOL_NOT_FOUND` / `ERR_SNAPSHOT_NOT_FOUND` / `ERR_ANALYTICS_NOT_FOUND` / `ERR_JOB_NOT_FOUND` / `ERR_AGENT_RUN_NOT_FOUND` / `ERR_REPORT_NOT_FOUND` | Lookup key missing from in-memory runtime stores. | Module routers |
| `422` | `ERR_INVALID_TIME_RANGE` / FastAPI Validation | `BoundedTimeRange` violation or Pydantic field constraint failure. | `historical/presentation/router.py:47-51` |
| `429` | `RATE_LIMIT_EXCEEDED` | Sliding-window request threshold exceeded per hashed IP and tier. | `iam/presentation/router.py:101-127` |
| `500` | Unhandled Python Exception | Uncaught `ValueError` in `datetime.fromisoformat()` (`historical/router.py:39-40`, `market/router.py:143`) when invalid ISO string is supplied! | `CAP-APP-MKT-001` gap |
