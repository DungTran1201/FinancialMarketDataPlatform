# Diagram 15: Local & Resource-Constrained Deployment Architecture (Docker Compose Profiles) (`DIAG-DEP-015`)

| Diagram Metadata | Value |
|---|---|
| **Diagram ID** | `DIAG-DEP-015` |
| **Title** | Docker Compose Profile Deployment & Network Topology |
| **Diagram Category** | `docs/diagrams/deployment/` |
| **Notation / Mermaid Type** | `Mermaid (flowchart TB)` |
| **Status** | `IMPLEMENTED` (`docker-compose.yml` 7 profiles) / `PLANNED` (Phase 2 Spark/Airflow/dbt/GE batch containers) |
| **Version** | `1.1.0` |
| **Authoritative Document Reference** | `docs/architecture/12-deployment-architecture.md`, `docs/operations/deployment-guide.md` |
| **Canonical Model Reference** | `models/deployment/deployment.yaml` |
| **Related Artifact IDs** | `DEP-001`..`DEP-008`, `PROP-APP-002` |

## Architectural Explanation

In compliance with Objective O7 (Resource Efficiency) and Section 9.11 (no Kubernetes initially), the entire platform is packaged in `docker-compose.yml` using **7 modular activation profiles** (`core`, `frontend`, `lakehouse`, `intelligence`, `observability`, `bi`, `microservices`) and 3 isolated virtual networks (`frontend_net`, `app_control_net`, `data_plane_net`):
- **Profile `core`**: `postgres`, `redis`, `kafka` (1-node KRaft), `clickhouse`, `collector-ws`, `collector-rest`, `consumer-hot-redis`, `consumer-analytics-ch`, `backend-api` (`:8000`), `frontend` (`127.0.0.1:3001->3000`), `edge-gateway` (`:80/:443`).
- **Profile `frontend`**: Runs `frontend` SPA standalone (`127.0.0.1:3001->3000`).
- **Profile `lakehouse`**: Adds `minio` (`127.0.0.1:9010->9000` API, `127.0.0.1:9001->9001` Console) and `consumer-lakehouse-bronze` (note: `spark-worker`, `dbt-runner`, `great-expectations`, and `airflow` are `[PLANNED]` Phase 2 additions — not yet in `docker-compose.yml`).
- **Profile `intelligence`**: Adds `agent-worker`.
- **Profiles `observability` & `bi`**: Add `prometheus` (`:9090`, scraping `localhost:9090`, `backend-api:8000/metrics`, `svc-data-plane-v01:8007/api/v1/data-platform/v01/metrics`), `grafana` (`:3000`), and `superset` (`:8088`).
- **Profile `microservices`**: Launches 7 domain containers `svc-market-hot..svc-data-plane-v01` (`:8001`..`:8007`) on `app_control_net` + `data_plane_net`.

```mermaid
flowchart TB
    subgraph HostEnvironment["Single Host / Developer Workstation (Docker Compose v2 — 7 Profiles)"]
        subgraph EdgeNet["Network: frontend_net"]
            Edge["edge-gateway (:80/:443)<br/>[Profile: core]"]
            Frontend["frontend (:3001->:3000)<br/>[Profiles: core, frontend]"]
            FastAPI["backend-api (:8000)<br/>[Profile: core]"]
            Grafana["grafana (:3000)<br/>[Profile: observability]"]
            Superset["superset (:8088)<br/>[Profile: bi]"]
        end

        subgraph AppNet["Network: app_control_net"]
            Postgres[("postgres (:5432)<br/>[core, lakehouse, intelligence, bi]")]
            AgentWorker["agent-worker<br/>[Profile: intelligence]"]
            Prometheus["prometheus (:9090)<br/>[Profile: observability]"]
            SvcGroup["svc-* Microservices (:8001..:8007)<br/>[Profile: microservices]"]
        end

        subgraph DataNet["Network: data_plane_net"]
            WSCol["collector-ws<br/>[Profile: core]"]
            RESTCol["collector-rest<br/>[Profile: core]"]
            Kafka[("kafka 1-Node KRaft (:9092)<br/>[core, lakehouse, intelligence]")]
            HotCons["consumer-hot-redis<br/>[Profile: core]"]
            CHCons["consumer-analytics-ch<br/>[Profile: core]"]
            BrzCons["consumer-lakehouse-bronze<br/>[Profile: lakehouse]"]
            Redis[("redis (:6379)<br/>[core, intelligence]")]
            ClickHouse[("clickhouse (:8123/:9000)<br/>[core, lakehouse, intelligence, bi]")]
            MinIO[("minio (:9010->:9000, :9001)<br/>[Profile: lakehouse]")]
            PlannedBatch["Phase 2 Batch: airflow, spark, dbt, ge<br/>[PLANNED — Not in Compose Yet]"]
        end
    end

    Edge --> Frontend & FastAPI
    FastAPI --> Postgres & Redis & ClickHouse
    Superset --> ClickHouse & Postgres
    Grafana --> Prometheus

    WSCol & RESTCol --> Kafka
    Kafka --> HotCons --> Redis
    Kafka --> CHCons --> ClickHouse
    Kafka --> BrzCons --> MinIO
    PlannedBatch -.->|"Target Phase 2"| MinIO & ClickHouse & Postgres

    AgentWorker --> Postgres & Redis & ClickHouse
    Prometheus -->|"Scrape /metrics"| FastAPI
    Prometheus -->|"Scrape :8007 metrics"| SvcGroup
```

