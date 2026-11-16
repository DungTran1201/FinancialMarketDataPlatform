---
doc_id: OVR-DIAG-CTX-001
title: "Diagram: FMDP System Context (C4 Level 1)"
doc_type: diagram
plane: platform
scope_level: platform
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: system-architect
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/overview/system-context.md"
related_docs:
  - OVR-CTX-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: system-architect
    summary: "Derived C4 Level 1 System Context diagram distinguishing live in-process paths from TARGET external feeds."
---

# Diagram: FMDP System Context (C4 Level 1)

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-OVR-CTX-001` |
| **Title & Purpose** | C4 Level 1 System Context showing FMDP boundary, human actors, API clients, and upstream/infrastructure systems |
| **C4 Level** | Level 1 — System Context |
| **Owner Role & Scope** | `system-architect / platform` |
| **Authoritative Source** | [system-context.md](../system-context.md) (`OVR-CTX-001`) |
| **Notation** | `Mermaid flowchart TB` (`C4 Model`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram `[REQUIRED]`

```mermaid
flowchart TB
    actor_user["Human User / Quant / Operator (Browser SPA)"]
    actor_bot["External Quant Bot / API Consumer"]
    ext_binance["Binance Spot API (REST & WS)"]
    ext_llm["External LLM API (TARGET - Mocked AS-IS)"]

    subgraph fmdp_sys["FinancialMarketDataPlatform Boundary (fmdp.local)"]
        sys_core["FMDP Platform (Edge Nginx + Vite/Nginx SPA + FastAPI Monolith + Pipelines + Agent)"]
    end

    actor_user -->|"HTTPS / WSS / SSE (Ports 80/443/3000/3001)"| sys_core
    actor_bot -->|"REST /api/v1/* (Port 8000 / 443)"| sys_core
    ext_binance -.->|"HTTPS /api/v3/klines (AS-IS: Embedded ASGI Sim Default)"| sys_core
    sys_core -.->|"TARGET LLM Inference (AS-IS: DeterministicMockLLMAdapter)"| ext_llm
```

## 3. Legend `[REQUIRED]`

- **Solid Arrow (`-->`)**: Active implemented HTTP/SSE/WS interface exposed by the running platform.
- **Dashed Arrow (`-.->`)**: External dependency that runs via in-process simulation (`AS-IS`) or remains `NOT_IMPLEMENTED` (`TARGET`).
- **Subgraph**: Complete FMDP runtime and declared infrastructure boundary (`docker-compose.yml`).
