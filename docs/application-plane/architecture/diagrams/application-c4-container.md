---
doc_id: DIAG-APP-C4-001
title: "Application Plane C4 Container Diagram"
doc_type: diagram
plane: application-plane
scope_level: plane
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/application-plane/architecture/application-architecture.md"
related_docs:
  - APP-ARCH-001
  - APP-ARCH-ROOT-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Rendered Application Plane C4 Container diagram separating SPA, Proxy, FastAPI Gateway/Routers, and Data/Intelligence dependencies."
---

# Application Plane C4 Container Diagram

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-APP-C4-001` |
| **Title & Purpose** | Application Plane Container Topology (`AS-IS` Modular Monolith + Target Postgres) |
| **Owner Role & Scope** | `fullstack-engineer / application-plane` |
| **Authoritative Source** | [application-architecture.md](../application-architecture.md) (`APP-ARCH-001`) |
| **Notation** | `Mermaid flowchart LR` (`C4 Container`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram

```mermaid
flowchart LR
    user["Operator / Quant Analyst / External Client"]
    spa["TypeScript Hash SPA (Vite 3000 / Nginx 80)"]
    api["FastAPI Serving Gateway (src/serving/api/main.py :8000)"]
    mw["Defense Middleware (Host, WAF Path/Query, RateLimit)"]
    rt["PlatformRuntimeContainer (In-Process Memory + SQLite)"]
    dp["Data Plane Stores (Kafka, Redis, CH, Lakehouse)"]
    ip["Intelligence Plane (MarketInvestigationWorkflow)"]
    pg["PostgreSQL 16 (01_schema.sql - UNWIRED TARGET)"]

    user -->|"HTTP / Hash Routes"| spa
    spa -->|"/api/* & /ws/* Proxy"| mw
    mw --> api
    api --> rt
    rt --> dp
    rt --> ip
    api -.->|"Target ORM/SQL (NOT_IMPLEMENTED)"| pg
```

## 3. Legend

- **Solid Edges (`-->`)**: Active `AS-IS` synchronous/SSE/WS runtime execution paths.
- **Dashed Edges (`-.->`)**: `TARGET` PostgreSQL persistence declared in `01_schema.sql` with zero runtime SQL driver calls today.
