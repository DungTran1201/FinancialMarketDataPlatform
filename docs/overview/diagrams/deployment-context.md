---
doc_id: OVR-DIAG-DEP-001
title: "Diagram: Compose Deployment Profiles & Network Zones"
doc_type: diagram
plane: platform
scope_level: platform
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: devops-sre
accountable_role: devops-sre
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/overview/platform-dependencies.md"
    - "docs/overview/architecture/architecture-overview.md"
related_docs:
  - OVR-DEP-001
  - OVR-ARCH-SYS-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Derived Compose topology diagram showing exact Docker network zones, host port bindings, and stub vs live status."
---

# Diagram: Compose Deployment Profiles & Network Zones

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-OVR-DEP-001` |
| **Title & Purpose** | Shows `docker-compose.yml` bridge networks (`frontend_net`, `app_control_net`, `data_plane_net`), ports, and profiles |
| **Owner Role & Scope** | `devops-sre / platform` |
| **Authoritative Source** | [architecture-overview.md](../architecture/architecture-overview.md) (`OVR-ARCH-SYS-001`) |
| **Notation** | `Mermaid flowchart TB` (`Deployment Topology`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram `[REQUIRED]`

```mermaid
flowchart TB
    ext["External Traffic (0.0.0.0:80 / 0.0.0.0:443)"]

    subgraph net_fe["frontend_net (bridge)"]
        nginx["edge-gateway (nginx:1.27 :80/:443)"]
        fe["frontend (nginx SPA :3000 -> 127.0.0.1:3001)"]
        api["backend-api (FastAPI :8000 -> 127.0.0.1:8000)"]
        graf["grafana (:3000) [profile: observability]"]
        sup["superset (:8088) [profile: bi]"]
    end

    subgraph net_ctrl["app_control_net (bridge)"]
        pg[("postgres:16 (:5432)")]
        prom["prometheus:v2.52.0 (:9090)"]
        svc_grp["Optional svc-* Wrappers (:8001..:8007) [profile: microservices]"]
    end

    subgraph net_dp["data_plane_net (bridge)"]
        kaf["kafka:3.7.0 KRaft (:9092)"]
        red[("redis:7.2 (:6379)")]
        ch[("clickhouse:24.3 (:8123/:9000)")]
        min[("minio (:9000/:9001) [profile: lakehouse]")]
        stubs["Stub Workers (collector-*, consumer-*, agent-worker) [exit immediately]"]
    end

    ext -->|"HTTPS / HTTP Redirect"| nginx
    nginx -->|"/"| fe
    nginx -->|"/api/* /ws/v1/*"| api
    nginx -->|"monitor.fmdp.local"| graf
    nginx -->|"bi.fmdp.local"| sup
    nginx -.->|"console.s3.fmdp.local"| min
    api --- pg
    api --- red
    api --- ch
    api --- kaf
    prom -->|"/metrics scrape :8000 / :8007"| api
    stubs -.->|"TARGET Kafka/Stores"| net_dp
```

## 3. Legend `[REQUIRED]`

- **Subgraph**: Docker bridge networks configured in `docker-compose.yml:565-571`.
- **Undirected Link (`---`)**: Declared Compose network/dependency connectivity (currently TCP-probed only by `backend-api`; workers exit cleanly without event loops).
- **Dashed Arrow (`-.->`)**: Optional profile services (`lakehouse`) or unimplemented worker paths.
