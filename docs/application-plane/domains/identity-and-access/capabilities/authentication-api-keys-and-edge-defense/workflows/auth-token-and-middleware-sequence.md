---
doc_id: DIAG-APP-IAM-SEQ-001
title: "Sequence Diagram: Edge Middleware, JWT Issuance & Verification"
doc_type: diagram
plane: application-plane
scope_level: capability
domain: identity-and-access
capability_id: CAP-APP-IAM-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: security-architect
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/application-plane/domains/identity-and-access/capabilities/authentication-api-keys-and-edge-defense/use-cases/uc-iam-001-issue-and-verify-jwt.md"
related_docs:
  - CAP-APP-IAM-UC-001
  - CAP-APP-IAM-TM-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Rendered UML sequence diagram for HTTP middleware filtering, AS-IS self-hash JWT issue, and target Postgres verification."
---

# Sequence Diagram: Edge Middleware, JWT Issuance & Verification

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-APP-IAM-SEQ-001` |
| **Title & Purpose** | Edge Middleware, `POST /auth/token` & `POST /auth/verify` Sequence |
| **Owner Role & Scope** | `security-architect / CAP-APP-IAM-001` |
| **Authoritative Source** | [uc-iam-001-issue-and-verify-jwt.md](../use-cases/uc-iam-001-issue-and-verify-jwt.md) (`CAP-APP-IAM-UC-001`) |
| **Notation** | `Mermaid sequenceDiagram` (`UML 2.5.1`) |
| **Version & Status** | `2.0.0 — DRAFT` |

## 2. Diagram

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant MW as Defense Middleware
    participant IAM as IAM Router
    participant JWT as JwtSecurityService
    participant PG as Postgres users (TARGET UNWIRED)

    C->>MW: POST /api/v1/auth/token (username, password, role)
    MW->>MW: Host check, WAF path/query regex, SlidingWindow (10 req/min)
    alt Host/WAF/Rate Violation
        MW-->>C: 400 / 403 / 429 JSON error + X-Request-ID
    else Passed Middleware
        MW->>IAM: Forward with request.state.client_ip
        note over IAM,PG: GAP (SEC-AUDIT-001): Skips Postgres users lookup! Self-hashes input password instead.
        IAM->>JWT: issue_token(subject, caller_role, client_ip)
        JWT-->>C: 200 {access_token, jti, bound_ip_hash} + HSTS/CSP headers
    end

    C->>MW: POST /api/v1/auth/verify (access_token)
    MW->>IAM: Forward
    IAM->>JWT: verify_token(access_token, client_ip)
    alt Invalid Sig / Expired / Revoked / IP Mismatch
        JWT-->>C: 401 Unauthorized
    else Valid Claims
        JWT-->>C: 200 {valid: true, role, capabilities}
    end
```

## 3. Legend

- **Lifelines & Boxes**: `MW` and `IAM` reflect exact runtime sequence in `router.py`; `PG` note marks `SEC-AUDIT-001` DB lookup omission.
