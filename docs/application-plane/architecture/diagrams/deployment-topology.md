---
doc_id: DIAG-APP-DEP-001
title: "Application Plane Deployment Topology Diagram"
doc_type: diagram
plane: application-plane
scope_level: plane
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: devops-sre
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/application-plane/architecture/deployment-architecture.md"
related_docs:
  - APP-ARCH-DEP-001
  - APP-OPS-RUN-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Rendered Compose serving profile vs microservices profile port allocation and SPA proxy."
---

# Application Plane Deployment Topology Diagram

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-APP-DEP-001` |
| **Title & Purpose** | Compose Monolith Serving vs Microservices Profile & Vite/Nginx Frontend |
| **Owner Role & Scope** | `devops-sre / application-plane` |
| **Authoritative Source** | [deployment-architecture.md](../deployment-architecture.md) (`APP-ARCH-DEP-001`) |
| **Notation** | `Mermaid flowchart TD` (`Deployment View`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram

```mermaid
flowchart TD
    client["Client Browser (:3000 dev / :80 prod)"]
    proxy["Vite / Nginx Reverse Proxy"]
    gw["serving-api or svc-api-gateway (:8000 + Middleware)"]
    subgraph ms["--profile microservices (Isolated Memory Containers :8001..8007)"]
        s1["svc-market-hot (:8001)"]
        s2["svc-historical-backfill (:8002)"]
        s3["svc-analytics-quant (:8003)"]
        s4["svc-catalog-governance (:8004)"]
        s5["svc-iam-security (:8005 + Middleware)"]
        s6["svc-intelligence-agent (:8006)"]
        s7["svc-data-plane-v01 (:8007)"]
    end

    client --> proxy
    proxy -->|"/api/* & /ws/*"| gw
    gw -.->|"ASGI/HTTP (Empty isolated state when standalone)"| s1
    gw -.->|"ASGI/HTTP"| s5
    gw -.->|"ASGI/HTTP"| s7
```

## 3. Legend

- **Port `8000` (`main.py`)**: Default unified FastAPI process serving all routers with shared memory.
- **Ports `8001..8007`**: Standalone microservice FastAPI apps under `docker compose --profile microservices` (all except `8005` lack `install_security_defense_middleware`).
