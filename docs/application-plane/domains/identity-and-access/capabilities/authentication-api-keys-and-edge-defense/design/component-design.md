---
doc_id: CAP-APP-IAM-COMP-001
title: "Component & Screen Design: IAM Router, Middleware & Auth SPA"
doc_type: specification
plane: application-plane
scope_level: capability
domain: identity-and-access
capability_id: CAP-APP-IAM-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/iam/presentation/router.py"
    - "src/serving/api/modules/iam/domain/security.py"
    - "frontend/src/services/auth/auth.service.ts"
    - "frontend/src/modules/administration/AdministrationModule.ts"
related_docs:
  - CAP-APP-IAM-REQ-001
  - APP-ARCH-COMPAT-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Documented backend IAM components and AdministrationModule Auth/Key UI panel design and defects."
---

# Component & Screen Design: IAM Router, Middleware & Auth SPA

## 1. Backend Components (`src/serving/api/modules/iam/` & `services/iam.py`)

| Component | Responsibility | `AS-IS` Constraint / Gap |
|---|---|---|
| `install_security_defense_middleware` | Host header filter, path/query regex WAF, IP rate limit (`AUTH`/`AGENT_TRIGGER`/`HEAVY_ANALYTICS`/`MARKET_READ`), HSTS/CSP response headers. | Trusts any `X-Forwarded-For` header; omits request JSON body WAF check; isolated inside `main.py` and `services/iam.py`. |
| `CredentialHasher` | PBKDF2-HMAC-SHA256 (`210,000` iterations) hashing + verification; `fmdp_live_*` key generation. | Invoked transiently on request password instead of verifying stored Postgres `users.password_hash`. |
| `JwtSecurityService` | Signs/verifies HS256 JWTs with `jti`, SHA-256 token hash, `bound_ip_hash`, and in-memory `_revoked_token_hashes`. | `services/iam.py` creates isolated instances; revocation set lost on restart; `settings.jwt_secret_key` defaults to hardcoded literal. |
| `DomainHttpsEndpointPolicy` & `IPAndEndpointCipher` | Exposes TLS domain origins and masks container host/ports in `GET /auth/domains`. | Safe display helper; route itself lacks admin JWT guard. |

## 2. Frontend Components (`auth.service.ts` & `AdministrationModule.ts` Screen Panel)

- **Session State**: `auth.service.ts` reads `localStorage['fmdp_user_profile']` or silently synthesizes `{ username: 'quant_admin', role: 'admin' }`. Zero login modal or `auth.store.ts` exists.
- **API Key Management UI (`AdministrationModule.ts`)**:
  - Attempts `GET /api/v1/auth/api-keys` (returns HTTP `405`, caught to empty `[]`).
  - Submits `POST /api/v1/auth/api-keys` with selected role, then discards `data.api_key_once` without displaying the secret (`COMPAT-003`).
  - Attempts `DELETE /api/v1/auth/api-keys/{key_id}` (returns `404/405`).
- **Domain Topology Panel**: Consumes `GET /api/v1/auth/domains` and renders public HTTPS/WSS origins and masked container bindings cleanly.
