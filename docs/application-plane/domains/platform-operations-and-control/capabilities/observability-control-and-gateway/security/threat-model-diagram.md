---
doc_id: DIAG-APP-OPS-TM-001
title: "Threat Model Diagram: Unauthenticated Ops Control & Dispatch Surface"
doc_type: diagram
plane: application-plane
scope_level: capability
domain: platform-operations-and-control
capability_id: CAP-APP-OPS-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: security-architect
accountable_role: devops-sre
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/application-plane/domains/platform-operations-and-control/capabilities/observability-control-and-gateway/security/threat-model.md"
related_docs:
  - CAP-APP-OPS-TM-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Rendered threat attack vectors targeting unauthenticated demo/v01 triggers, live probe, and microservice dispatch."
---

# Threat Model Diagram: Unauthenticated Ops Control & Dispatch Surface

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-APP-OPS-TM-001` |
| **Title & Purpose** | Attack Surface on Unauthenticated Pipeline Triggers & Internal ASGI Dispatch |
| **Owner Role & Scope** | `security-architect / CAP-APP-OPS-001` |
| **Authoritative Source** | [threat-model.md](threat-model.md) (`CAP-APP-OPS-TM-001`) |
| **Notation** | `Mermaid flowchart LR` (`Threat Model`) |
| **Version & Status** | `2.0.0 — DRAFT` |

## 2. Diagram

```mermaid
flowchart LR
    atk["Unauthenticated Client"]
    gw["Gateway :8000 (No Bearer Guard AS-IS)"]
    v01["/data-platform/v01/run & /demo/emit"]
    disp["/microservices/dispatch/{service_id}"]
    ext["api.binance.com (via /live/probe)"]

    atk -.->|"THR-OPS-001 Compute/Disk Loop"| gw --> v01
    atk -.->|"THR-OPS-002 Internal Mesh Pivot"| gw --> disp
    atk -.->|"THR-OPS-003 External HTTPS Probe"| gw --> ext
```

## 3. Legend

- **Dashed Arrows (`-.->`)**: Unauthenticated routes exposed `AS-IS` without `Depends` authorization enforcement.
