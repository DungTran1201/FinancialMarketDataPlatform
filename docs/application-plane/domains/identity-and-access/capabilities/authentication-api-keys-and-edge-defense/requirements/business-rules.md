---
doc_id: CAP-APP-IAM-RULE-001
title: "Business Rules: Authentication, API Keys & Edge Defense"
doc_type: specification
plane: application-plane
scope_level: capability
domain: identity-and-access
capability_id: CAP-APP-IAM-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: security-architect
accountable_role: business-analyst
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/iam/domain/ports.py"
    - "src/serving/api/modules/iam/presentation/router.py"
    - "src/shared/security/primitives.py"
related_docs:
  - CAP-APP-IAM-DOC-001
  - CAP-APP-IAM-REQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Documented deterministic IAM business rules and code enforcement gaps."
---

# Business Rules: Authentication, API Keys & Edge Defense

## 1. Enforced Validation & Cryptographic Rules (`AS-IS`)

| Rule ID | Business Rule | `AS-IS` Code Enforcement | Gap / Note |
|---|---|---|---|
| `RULE-IAM-001` | Credentials require `username >= 3` chars and `password >= 8` chars; `role` must belong to `UserRole`. | `iam/presentation/router.py:191-199` | Caller `role` override is accepted instead of querying stored role (`OPEN`). |
| `RULE-IAM-002` | Password hashes MUST use `PBKDF2-HMAC-SHA256` with `210,000` iterations; API keys expose plaintext `api_key_once` only at creation and hash via `SHA-256`. | `iam/domain/security.py` | Key record is discarded immediately after `POST /api-keys` response. |
| `RULE-IAM-003` | Rate limits apply per hashed client IP across tiers: `AUTH=10`, `AGENT_TRIGGER=5`, `HEAVY_ANALYTICS=30`, `MARKET_READ=120` req/min. | `SlidingWindowRateLimiter` in `primitives.py` | Isolated per worker process and per `services/iam.py` app instance. |

## 2. Target Governance Rules (Not Yet Enforced)

| Rule ID | Target Rule | Current Status |
|---|---|---|
| `RULE-IAM-004` | `UserRole.SERVICE` MUST define an explicit least-privilege capability set in `ROLE_CAPABILITIES`. | **GAP**: `UserRole.SERVICE` omitted from `ROLE_CAPABILITIES` (`iam/domain/ports.py:18-44`). |
| `RULE-IAM-005` | Production startup MUST reject default `jwt_secret_key` (`settings.py:34`) when `APP_ENV != local`. | **GAP**: Hardcoded literal allowed silently. |
