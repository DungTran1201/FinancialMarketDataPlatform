---
doc_id: CAP-APP-IAM-SEC-001
title: "Security Requirements: Authentication, API Keys & Edge Defense"
doc_type: specification
plane: application-plane
scope_level: capability
domain: identity-and-access
capability_id: CAP-APP-IAM-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: security-architect
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/iam/presentation/router.py"
    - "src/serving/api/modules/iam/domain/ports.py"
related_docs:
  - CAP-APP-IAM-DOC-001
  - CAP-APP-IAM-TM-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Defined testable security controls mapping implemented edge defenses vs blocked auth/RBAC gaps."
---

# Security Requirements: Authentication, API Keys & Edge Defense

## 1. Security Requirements & Implementation Reality

| Sec Req ID | Control Requirement | `AS-IS` Status |
|---|---|---|
| `SEC-IAM-001` | `POST /auth/token` MUST authenticate against Postgres `users` PBKDF2 hashes and assign server-stored `role` (`is_active=TRUE`), rejecting caller-chosen roles. | `NOT_IMPLEMENTED` (`BLOCKED`) |
| `SEC-IAM-002` | Every protected endpoint MUST inject FastAPI `Depends` enforcing Bearer JWT / hashed API-key signature, expiry, revocation, IP binding, and `ROLE_CAPABILITIES`. | `NOT_IMPLEMENTED` (`BLOCKED`) |
| `SEC-IAM-003` | `UserRole.SERVICE` MUST define an explicit capability tuple in `ROLE_CAPABILITIES`. | `NOT_IMPLEMENTED` |
| `SEC-IAM-004` | Edge middleware MUST reject untrusted `Host` (`400`), WAF path/query regex threats (`403`), and rate-limit bursts (`429`) across gateway AND standalone services. | `PARTIALLY_IMPLEMENTED` (gateway + `iam` only) |
| `SEC-IAM-005` | Non-local deployments MUST fail startup when `JWT_SECRET_KEY` equals the codebase default literal and restrict `X-Forwarded-For` to trusted reverse proxies. | `NOT_IMPLEMENTED` |
| `SEC-IAM-006` | `auth.service.ts` MUST NOT auto-assign `quant_admin` for unauthenticated browser sessions. | `NOT_IMPLEMENTED` (`BLOCKED`) |

## 2. Authorization Matrix & Remediation Priority

Enforced RBAC targets are enumerated in [authorization-matrix.yaml](authorization-matrix.yaml). Remediation prioritizes closing `SEC-IAM-001` and `SEC-IAM-002` before removing `DRAFT` / `BLOCKED` gate flags.
