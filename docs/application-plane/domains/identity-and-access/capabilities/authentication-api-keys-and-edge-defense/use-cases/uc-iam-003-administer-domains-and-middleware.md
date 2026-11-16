---
doc_id: CAP-APP-IAM-UC-003
title: "Use Case UC-IAM-003: Inspect Encrypted Domain Topology & Enforce Edge Defense"
doc_type: specification
plane: application-plane
scope_level: use-case
domain: identity-and-access
capability_id: CAP-APP-IAM-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: business-analyst
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/iam/presentation/router.py"
    - "src/shared/security/primitives.py"
related_docs:
  - CAP-APP-IAM-REQ-001
  - DIAG-APP-IAM-FLOW-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Documented GET /auth/domains encrypted topology inspection and defense_in_depth_middleware checks."
---

# Use Case UC-IAM-003: Inspect Encrypted Domain Topology & Enforce Edge Defense

## 1. Domain Topology Retrieval (`GET /api/v1/auth/domains`)

- **Actor**: Operator via `#/administration` or API client.
- **Behavior**: Returns configured `root_domain`, `tls_min_version`, HTTPS public origins (`api.`, `wss://`, `bi.`, `monitor.`, `console.s3.`), and `IPAndEndpointCipher.mask_service_endpoint(...)` masked bindings for `postgres`, `redis`, `clickhouse`, and `kafka`.

## 2. Edge Defense Middleware Intercepts (Every Gateway HTTP Request)

1. Extract IP (`X-Forwarded-For` / `X-Real-IP` / peer host) and generate HMAC digest + AES/Fernet-style masked token.
2. Validate `Host` header against `DomainHttpsEndpointPolicy.allowed_hosts` -> reject invalid Host with HTTP `400 UNTRUSTED_HOST_HEADER`.
3. Inspect URL path + query string via regex WAF -> reject SQLi/XSS/traversal with HTTP `403 WAF_THREAT_DETECTED`.
4. Evaluate `SlidingWindowRateLimiter` for path tier (`AUTH=10`, `AGENT_TRIGGER=5`, `HEAVY_ANALYTICS=30`, `MARKET_READ=120`) -> reject excess with HTTP `429 RATE_LIMIT_EXCEEDED`.
5. On downstream response, inject `Strict-Transport-Security`, `Content-Security-Policy`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `X-Request-ID`, `X-Client-IP-Token`, and `X-RateLimit-*`.
- **Exception Note**: Standalone microservices (`8001..8004, 8006, 8007`) do not install this middleware.
