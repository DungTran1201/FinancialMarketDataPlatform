---
doc_id: "DIAG-DEP-001"
title: "Deployment Topology — Hybrid Windows PoC vs Linux Compose Target"
version: "1.0.0"
status: "IN_REVIEW"
implementation_status: "PLANNED"
owner: "SRE / DevOps Engineer"
purpose: "Contrasts the authorized Phase 2 Hybrid Native Windows + Containerized NATS topology against the future bounded 3-container Linux deployment path."
scope: "Single-node 8 GB workstation deployment (`DEC-P0-002`)."
dependencies:
  - "docs/phase-reports/phase-1-acceptance-and-decisions.md"
  - "docs/architecture/resource-budget.md"
references:
  - "docs/architecture/decisions/adr-0001-three-plane-hybrid-runtime.md"
assumptions:
  - "Docker Desktop runs a single memory-bounded Linux engine holding only NATS JetStream during Phase 2 PoC."
open_issues:
  - "Measure real Docker Desktop idle WSL2 VM RAM alongside Windows Python processes during WI-P2-003."
review_criteria:
  - "Shows exact loopback port binding and disk paths on Windows host"
---

# Deployment Topology (`Hybrid Phase 2 PoC` & `Future Linux Profile`)

```mermaid
flowchart TB
    subgraph WIN["Windows 10 Pro Host (7.85 GB RAM | i5-12400F | C: 15.54 GB free | E: 271.82 GB free)"]
        subgraph NATIVE_PY["Native Python 3.12 (.venv)"]
            P1["fmdp-realtime-api<br/>FastAPI :8000 + Collectors"]
            P2["fmdp-batch-quant-worker<br/>Parquet Writer + DuckDB + Quant"]
        end

        SPA["Vite / Static SPA (:5173 dev / :8000 static)"]

        subgraph DISK["Local SSD Volumes"]
            SSD_C["C: Active Workspace (<= 5 GB)<br/>data/sqlite/*.db (WAL)<br/>data/parquet/{bronze,silver,gold}/"]
            SSD_E["E: Optional Cold Archive (271 GB free)<br/>Multi-month historical Parquet"]
        end

        subgraph WSL2["Docker Desktop WSL2 (.wslconfig RAM capped)"]
            DOCKER_NATS["Container: nats:2.10-alpine<br/>mem_limit: 256m | --jetstream<br/>Bind: 127.0.0.1:4222 / :8222"]
            NATSVOL[("Named Docker Volume<br/>nats_jetstream_data (<= 1 GB)")]
        end
    end

    SPA -->|HTTP / WS 127.0.0.1:8000| P1
    P1 <-->|TCP 127.0.0.1:4222| DOCKER_NATS
    P2 <-->|TCP 127.0.0.1:4222| DOCKER_NATS
    DOCKER_NATS <--> NATSVOL
    P2 -->|Single Writer WAL & ZSTD Parquet| SSD_C
    P2 -.->|Optional TTL Offload| SSD_E
    P1 -.->|Startup Catalog Read| SSD_C
```

## Legend & Diagram Metadata

- **Solid Arrows (`-->`)**: Active Hybrid Native Windows + NATS Container runtime connections (`DEC-P0-002`).
- **Dashed Arrows (`-.->`)**: Optional cold-tier storage offloading onto `E:\` (`DEC-P0-003`) and startup metadata loading.
- **Authoritative Spec**: [resource-budget.md](../architecture/resource-budget.md), [adr-0001-three-plane-hybrid-runtime.md](../architecture/decisions/adr-0001-three-plane-hybrid-runtime.md).

