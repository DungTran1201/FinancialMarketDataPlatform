---
doc_id: CAP-APP-IAM-UC-002
title: "Use Case UC-IAM-002: Revoke JWT & Mint Scoped API Key"
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
    - "frontend/src/services/auth/auth.service.ts"
    - "frontend/src/modules/administration/AdministrationModule.ts"
related_docs:
  - CAP-APP-IAM-REQ-001
  - APP-ARCH-COMPAT-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Documented JWT revocation, API key generation, unauthenticated risk, and UI compatibility bugs."
---

# Use Case UC-IAM-002: Revoke JWT & Mint Scoped API Key

## 1. Trigger, Actors & Preconditions

- **Actor (`AS-IS`)**: Any network caller (`SECURITY GAP`: endpoints require neither `iam:admin` nor Bearer JWT!) or Operator via `#/administration`.
- **Flows Covered**: `POST /api/v1/auth/revoke` and `POST /api/v1/auth/api-keys`.

## 2. Main Flow & UI Compatibility Failures (`AS-IS`)

1. **JWT Revocation**: Caller submits `{ "token_or_sha256_hash": "..." }` to `POST /api/v1/auth/revoke`. Backend adds hash to in-memory `_revoked_token_hashes` set and returns `{"status": "revoked", "revoked_token_sha256_hash": ...}`. *(Lost upon server restart.)*
2. **API Key Minting**: Caller submits `{ "role": "service" }` to `POST /api/v1/auth/api-keys` (`HTTP 422` if invalid `UserRole`).
3. `CredentialHasher.generate_api_key(role)` produces raw `fmdp_live_*` token + SHA-256 hash + `key_id` + `key_prefix` and returns `api_key_once`.
4. **AS-IS Persistence & UI Failures**:
   - Backend discards the `record` immediately without inserting into DB.
   - `AdministrationModule.ts` calls `authService.createApiKey()` then discards `api_key_once` without displaying the secret to the user (`COMPAT-003`).
   - Subsequent table refresh calls `GET /api/v1/auth/api-keys` -> `405 Method Not Allowed`, silently caught to `[]` (`COMPAT-001`), and `DELETE /api/v1/auth/api-keys/{id}` fails (`COMPAT-002`).
