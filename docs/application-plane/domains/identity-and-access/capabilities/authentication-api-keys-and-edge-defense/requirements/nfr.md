---
doc_id: CAP-APP-IAM-NFR-001
title: "Non-Functional Requirements: Authentication, API Keys & Edge Defense"
doc_type: specification
plane: application-plane
scope_level: capability
domain: identity-and-access
capability_id: CAP-APP-IAM-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: security-architect
accountable_role: devops-sre
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/iam/domain/security.py"
    - "src/shared/security/primitives.py"
related_docs:
  - CAP-APP-IAM-REQ-001
  - APP-OPS-SLO-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Documented IAM cryptography strengths and unestablished scalability/latency SLOs."
---

# Non-Functional Requirements: Authentication, API Keys & Edge Defense

## 1. Security & Cryptographic Non-Functional Characteristics

- **Password Work Factor**: `PBKDF2-HMAC-SHA256` fixed at `210,000` iterations (`iam/domain/security.py`) provides brute-force resistance per OWASP baseline.
- **Zero-Plaintext Storage Policy**: Token hashes, bound IPs, and masked container addresses use SHA-256 / HMAC (`IPAndEndpointCipher`) rather than plaintext persistence in API logs/responses.
- **Horizontal State Requirement (`BLOCKED`)**: In-memory `_revoked_token_hashes` and `SlidingWindowRateLimiter` prevent stateless multi-worker or multi-replica scaling until backed by Redis/Postgres.

## 2. Performance & Availability Targets (`OPEN`)

- Maximum p99 auth latency under 210k PBKDF2 iterations and distributed rate-limiter failover behavior remain **`OPEN`** pending benchmark profiling (`[ASSUMPTION: Auth traffic burst profile needed from SRE]`).
