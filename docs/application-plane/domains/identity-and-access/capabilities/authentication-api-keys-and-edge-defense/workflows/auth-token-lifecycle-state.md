---
doc_id: DIAG-APP-IAM-STATE-001
title: "State Machine Diagram: JWT Token & API Key Lifecycle"
doc_type: diagram
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
  is_authoritative: false
  authoritative_source:
    - "docs/application-plane/domains/identity-and-access/capabilities/authentication-api-keys-and-edge-defense/requirements/capability-specification.md"
related_docs:
  - CAP-APP-IAM-REQ-001
  - CAP-APP-IAM-UC-002
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Rendered UML stateDiagram-v2 for HS256 JWT token lifecycle."
---

# State Machine Diagram: JWT Token & API Key Lifecycle

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-APP-IAM-STATE-001` |
| **Title & Purpose** | HS256 JWT Issuance, IP Verification, Expiration & In-Memory Revocation States |
| **Owner Role & Scope** | `security-architect / CAP-APP-IAM-001` |
| **Authoritative Source** | [capability-specification.md](../requirements/capability-specification.md) (`CAP-APP-IAM-REQ-001`) |
| **Notation** | `Mermaid stateDiagram-v2` (`UML 2.5.1`) |
| **Version & Status** | `2.0.0 — DRAFT` |

## 2. Diagram

```mermaid
stateDiagram-v2
    [*] --> IssuedActive : "POST /auth/token (IP-HMAC bound)"
    IssuedActive --> Verified : "POST /auth/verify [valid sig, same IP, not expired]"
    Verified --> IssuedActive : "Next request verification"
    IssuedActive --> Revoked : "POST /auth/revoke [in-memory hash set only]"
    IssuedActive --> Expired : "now > exp claim"
    IssuedActive --> IpRejected : "verify_token from changed IP"
    IssuedActive --> ProcessLost : "API restart clears _revoked_token_hashes"
    Revoked --> [*]
    Expired --> [*]
    ProcessLost --> [*]
```

## 3. Legend

- **In-Memory Gap**: `Revoked` state is lost upon process restart (`ProcessLost`), allowing non-expired tokens to verify again if signed with the same secret!
