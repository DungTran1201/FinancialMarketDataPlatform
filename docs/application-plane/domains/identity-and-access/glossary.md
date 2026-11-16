---
doc_id: APP-DOM-IAM-GLOSS-001
title: "Glossary: Identity, Access & Edge Security"
doc_type: glossary
plane: application-plane
scope_level: domain
domain: identity-and-access
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: security-architect
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/iam/domain/ports.py"
    - "src/serving/api/modules/iam/domain/security.py"
related_docs:
  - APP-DOM-IAM-001
  - CAP-APP-IAM-DOC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Defined IAM domain terms for roles, capability scopes, IP HMAC tokens, and API key hashes."
---

# Glossary: Identity, Access & Edge Security

## 1. Canonical IAM Terms

- **`ROLE_CAPABILITIES`**: Static RBAC dictionary (`src/serving/api/modules/iam/domain/ports.py`) mapping `UserRole` (`viewer`, `analyst`, `operator`, `admin`) to capability strings (`market:read`, `agent:trigger`, `iam:admin`, etc.). `UserRole.SERVICE` currently lacks an entry.
- **Bound IP Hash (`ip_hash`)**: HMAC-SHA256 digest produced by `IPAndEndpointCipher.hash_ip(raw_ip)` embedded in JWT claims to bind tokens to client IP (`X-Forwarded-For` trusted blindly `AS-IS`).
- **One-Time API Key (`api_key_once`)**: Prefixed raw credential (`fmdp_live_...`) returned only upon `POST /api/v1/auth/api-keys`; only its SHA-256 hash is meant for storage (`AS-IS`: unpersisted).
- **`WAF_THREAT_DETECTED`**: HTTP `403` error raised by `inspect_request_for_waf_threats` when URL path or query string matches regex SQLi, XSS, or path-traversal signatures.
