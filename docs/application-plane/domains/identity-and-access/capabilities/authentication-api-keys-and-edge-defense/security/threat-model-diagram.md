---
doc_id: DIAG-APP-IAM-TM-001
title: "Threat Model Diagram: Auth Bypass & Edge Defense Boundaries"
doc_type: diagram
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
  is_authoritative: false
  authoritative_source:
    - "docs/application-plane/domains/identity-and-access/capabilities/authentication-api-keys-and-edge-defense/security/threat-model.md"
related_docs:
  - CAP-APP-IAM-TM-001
  - CAP-APP-IAM-SEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Rendered attacker threat paths targeting unauthenticated routes, self-hashed login, XFF spoofing, and SPA quant_admin fallback."
---

# Threat Model Diagram: Auth Bypass & Edge Defense Boundaries

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-APP-IAM-TM-001` |
| **Title & Purpose** | Attack Paths Exploiting Unauthenticated Routes & Self-Hash Token Issuance |
| **Owner Role & Scope** | `security-architect / CAP-APP-IAM-001` |
| **Authoritative Source** | [threat-model.md](threat-model.md) (`CAP-APP-IAM-TM-001`) |
| **Notation** | `Mermaid flowchart LR` (`Threat Model`) |
| **Version & Status** | `2.0.0 — DRAFT` |

## 2. Diagram

```mermaid
flowchart LR
    atk["Untrusted Caller / Attacker"]
    xff["Spoofed X-Forwarded-For / Role=admin"]
    mw["Edge Middleware (8000 / 8005 only)"]
    iam["/api/v1/auth (Zero DB Check)"]
    ms["Standalone Ports 8001..8004, 8006, 8007"]
    biz["Business / Admin Routers (Zero Depends Guard)"]

    atk -->|"THR-IAM-004 Spoof IP"| xff --> mw
    mw -->|"THR-IAM-001 Forge Admin JWT"| iam
    mw -.->|"THR-IAM-002 Unauthenticated Bypass"| biz
    atk -.->|"Bypass Middleware Completely"| ms --> biz
```

## 3. Legend

- **Solid Edges (`-->`)**: Traffic filtered by Host/WAF path+query/rate-limit middleware (`main.py` & `services/iam.py`).
- **Dashed Edges (`-.->`)**: Critical bypass vectors where authentication, RBAC guards, or standalone middleware are absent `AS-IS`.
