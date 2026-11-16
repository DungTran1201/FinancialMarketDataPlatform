---
doc_id: CAP-APP-IAM-ERR-001
title: "Error Catalog: IAM & Edge Defense"
doc_type: specification
plane: application-plane
scope_level: capability
domain: identity-and-access
capability_id: CAP-APP-IAM-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: security-architect
accountable_role: fullstack-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/iam/presentation/router.py"
related_docs:
  - APP-ERR-SHARED-001
  - CAP-APP-IAM-REQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Enumerated IAM router string-detail errors and middleware HTTP blocks."
---

# Error Catalog: IAM & Edge Defense

## 1. Edge Defense Middleware Errors (`{ "error": { ... } }`)

| HTTP | Error Code | Trigger |
|---|---|---|
| `400` | `UNTRUSTED_HOST_HEADER` | `Host` header outside `DomainHttpsEndpointPolicy.allowed_hosts`. |
| `403` | `WAF_THREAT_DETECTED` | URL path or query string matches regex SQLi/XSS/traversal signatures. |
| `429` | `RATE_LIMIT_EXCEEDED` | Exceeded sliding-window IP quota (`AUTH=10`, `AGENT_TRIGGER=5`, `HEAVY_ANALYTICS=30`, `MARKET_READ=120`). |

## 2. IAM Endpoint Errors (`{ "detail": "<string>" }`)

| HTTP | Detail Message | Endpoint |
|---|---|---|
| `422` | `"Username (>=3 chars) and password (>=8 chars) are required."` / `"Invalid role: ..."` | `POST /token`, `POST /api-keys` |
| `401` | `"Credential verification failed."` or `SecurityViolationError` string (expired/revoked/IP mismatch/invalid sig) | `POST /token`, `POST /verify` |
| `405` | Method Not Allowed | Frontend calls `GET /api/v1/auth/api-keys` or `DELETE /api/v1/auth/api-keys/{id}` (unimplemented) |
