---
doc_id: APP-DOM-IAM-001
title: "Domain: Identity, Access & Edge Security"
doc_type: index
plane: application-plane
scope_level: domain
domain: identity-and-access
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
    - "src/serving/api/modules/iam/domain/security.py"
related_docs:
  - APP-ROOT-001
  - APP-DOM-IAM-SPEC-001
  - APP-DOM-IAM-GLOSS-001
  - CAP-APP-IAM-DOC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Created Identity, Access & Edge Security domain root under Application Plane."
---

# Domain: Identity, Access & Edge Security

Owns JWT issuance/verification/revocation, API key generation, RBAC capability definitions, HTTPS/WSS endpoint masking, and HTTP edge defense middleware (`Host`, WAF path/query inspection, sliding-window rate limiting, and security headers).

## 1. Domain Documentation

- [domain-specification.md](domain-specification.md) (`APP-DOM-IAM-SPEC-001`)
- [glossary.md](glossary.md) (`APP-DOM-IAM-GLOSS-001`)

## 2. Capabilities

- [CAP-APP-IAM-001 — Authentication, API Keys & Edge Defense](capabilities/authentication-api-keys-and-edge-defense/README.md) (`DRAFT` / `HIGH_CRITICAL`)
