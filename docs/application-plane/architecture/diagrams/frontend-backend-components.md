---
doc_id: DIAG-APP-COMP-001
title: "Application Plane Frontend-to-Backend Component Diagram"
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
    - "docs/application-plane/architecture/frontend-architecture.md"
    - "docs/application-plane/architecture/backend-architecture.md"
related_docs:
  - APP-ARCH-FE-001
  - APP-ARCH-BE-001
  - APP-ARCH-COMPAT-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Rendered mapping from the 6 SPA modules and frontend services to FastAPI presentation routers."
---

# Application Plane Frontend-to-Backend Component Diagram

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-APP-COMP-001` |
| **Title & Purpose** | Frontend SPA Modules to Backend FastAPI Router Decomposition |
| **Owner Role & Scope** | `fullstack-engineer / application-plane` |
| **Authoritative Source** | [frontend-architecture.md](../frontend-architecture.md) (`APP-ARCH-FE-001`) |
| **Notation** | `Mermaid flowchart LR` (`C4 Component`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram

```mermaid
flowchart LR
    subgraph fe["Frontend SPA (frontend/src)"]
        m_dash["DashboardModule (#/dashboard)"]
        m_flow["DataFlowModule (#/data-flow)"]
        m_mkt["MarketAnalyticsModule (#/market-analytics)"]
        m_cat["DataManagementModule (#/data-management)"]
        m_ai["AiWorkspaceModule (#/ai-workspace)"]
        m_adm["AdministrationModule (#/administration)"]
        s_ws["ws-client.ts & sse.ts"]
        s_http["api/client.ts & auth.service.ts"]
    end

    subgraph be["Backend FastAPI Routers (src/serving/api)"]
        r_obs["/api/v1/observability & /ws/v1/observability/stream"]
        r_dp["/api/v1/data-platform/v01"]
        r_mkt["/api/v1/market & /historical & /analytics"]
        r_cat["/api/v1/catalog"]
        r_ai["/api/v1/agents & /reports"]
        r_iam["/api/v1/auth & /platform & /microservices"]
    end

    m_dash --> s_ws --> r_obs
    m_flow --> s_http --> r_obs
    m_flow --> s_http --> r_dp
    m_mkt --> s_http --> r_mkt
    m_cat --> s_http --> r_cat
    m_cat --> s_http --> r_dp
    m_ai --> s_http --> r_ai
    m_adm --> s_http --> r_iam
```

## 3. Legend

- **Frontend Modules**: Top-level lazy/hash views under `frontend/src/modules/`.
- **Backend Routers**: Domain presentation routers in `src/serving/api/` sharing `PlatformRuntimeContainer`.
