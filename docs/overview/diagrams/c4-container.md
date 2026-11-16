---
doc_id: OVR-DIAG-CONT-001
title: "Diagram: FMDP C4 Container Architecture (AS-IS vs TARGET)"
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
    - "docs/overview/architecture/architecture-overview.md"
related_docs:
  - OVR-ARCH-SYS-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: system-architect
    summary: "Derived C4 Level 2 Container diagram accurately separating active in-process engines from TARGET Docker stores/workers."
---

# Diagram: FMDP C4 Container Architecture

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-OVR-CONT-001` |
| **Title & Purpose** | C4 Level 2 Container view of active web/API monolith, local persistence, and declared Docker containers |
| **C4 Level** | Level 2 — Container |
| **Owner Role & Scope** | `system-architect / platform` |
| **Authoritative Source** | [architecture-overview.md](../architecture/architecture-overview.md) (`OVR-ARCH-SYS-001`) |
| **Notation** | `Mermaid flowchart TB` (`C4 Model`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram `[REQUIRED]`

```mermaid
flowchart TB
    browser["Browser Client"]
    edge["Edge Gateway (nginx:1.27-alpine :80/:443)"]
    spa["Frontend SPA (Vite / nginx :3000/:3001)"]

    subgraph runtime_proc["backend-api Container / Process (:8000) — Active In-Process Composition"]
        api["FastAPI Gateway & 8 Routers (main.py)"]
        dp_eng["Data Plane Engines (Normalizer, In-Memory Kafka, Hot Dicts, CH Dicts, Lakehouse, 12-Stage Pipeline)"]
        int_eng["Intelligence Engine (5-Node MarketIntelligenceGraph + ControlledToolGateway + Mock LLM)"]
    end

    store_local[("Local Host Storage (.local_storage SQLite WAL + .local_lakehouse Parquet)")]

    subgraph target_infra["Declared Docker Infra & Stub Workers (docker-compose.yml — NOT WIRED AT RUNTIME)"]
        infra_bus["Kafka KRaft (:9092) + Stub Ingestion/Consumer Workers"]
        infra_stores[("Postgres (:5432), Redis (:6379), ClickHouse (:8123/:9000), MinIO (:9000)")]
        infra_obs["Prometheus (:9090), Grafana (:3000), Superset (:8088)"]
    end

    browser -->|"HTTPS / WSS"| edge
    edge -->|"/"| spa
    edge -->|"/api/* & /ws/v1/*"| api
    api -->|"Direct Python Calls"| dp_eng
    api -->|"Await Orchestration"| int_eng
    int_eng -->|"ControlledToolGateway"| dp_eng
    dp_eng -->|"Local Disk IO"| store_local
    api -.->|"TCP Port Probe Only (:5432/:6379/:8123/:9092)"| infra_stores
    infra_obs -.->|"Scrape /metrics (TARGET Dashboard)"| api
    infra_bus -.->|"TARGET Async Topics"| infra_stores
```

## 3. Legend `[REQUIRED]`

- **Solid Arrows (`-->`)**: Verified active in-process or local-disk runtime paths on `7880c85`.
- **Dashed Arrows (`-.->`)**: Declared container infrastructure / TCP probes / stub workers not yet wired for end-to-end persistence.
