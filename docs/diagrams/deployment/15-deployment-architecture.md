# Diagram 15: Local & Resource-Constrained Deployment Architecture (Docker Compose Profiles)

## Architectural Explanation

In compliance with Objective O7 (Resource Efficiency) and Section 9.11 (Deployment Limitations — no Kubernetes initially), the entire platform is packaged for **Docker Compose** using **modular activation profiles** and isolated virtual networks:
- **Profile `core` (Default — Lightweight Streaming & API, $\sim 4-6\text{ GB}$ RAM)**:
  - Runs `postgres`, `redis`, `kafka` (KRaft mode — no ZooKeeper overhead), `clickhouse`, `collector-ws`, `collector-rest`, `consumer-hot-redis`, `consumer-analytics-ch`, and `backend-api`.
- **Profile `lakehouse` (Batch Storage & Medallion Processing)**:
  - Adds `minio`, `consumer-lakehouse-bronze`, `spark-worker`, `dbt-runner`, `great-expectations`, and `airflow`.
- **Profile `intelligence` (Agentic Analytics)**:
  - Adds `agent-worker` (LangGraph service).
- **Profile `observability` & `bi`**:
  - Adds `prometheus`, `grafana`, and `superset`.

```mermaid
flowchart TB
    subgraph HostEnvironment["Single Host / Developer Workstation (Docker Engine & Compose v2)"]
        subgraph EdgeNet["Network: frontend_net (Exposed Host Ports)"]
            FastAPI["backend-api (:8000)<br/>[Profile: core]"]
            Superset["superset (:8088)<br/>[Profile: bi]"]
            Grafana["grafana (:3000)<br/>[Profile: observability]"]
            AirflowUI["airflow-webserver (:8080)<br/>[Profile: lakehouse]"]
        end

        subgraph AppNet["Network: app_control_net (Internal Control & Intelligence)"]
            Postgres[("postgres (:5432)<br/>[Profile: core]")]
            AgentWorker["agent-worker<br/>[Profile: intelligence]"]
            Prometheus["prometheus (:9090)<br/>[Profile: observability]"]
        end

        subgraph DataNet["Network: data_plane_net (Internal High-Throughput Streaming & Storage)"]
            WSCol["collector-ws<br/>[Profile: core]"]
            RESTCol["collector-rest<br/>[Profile: core]"]
            Kafka[("kafka KRaft (:9092)<br/>[Profile: core]")]
            HotCons["consumer-hot-redis<br/>[Profile: core]"]
            CHCons["consumer-analytics-ch<br/>[Profile: core]"]
            BrzCons["consumer-lakehouse-bronze<br/>[Profile: lakehouse]"]
            Redis[("redis (:6379)<br/>[Profile: core]")]
            ClickHouse[("clickhouse (:8123/:9000)<br/>[Profile: core]")]
            MinIO[("minio (:9000/:9001)<br/>[Profile: lakehouse]")]
            Spark["spark-batch / dbt / ge<br/>[Profile: lakehouse]"]
        end
    end

    FastAPI --> Postgres & Redis & ClickHouse
    Superset --> ClickHouse & Postgres
    Grafana --> Prometheus
    AirflowUI --> Postgres & Spark & RESTCol

    WSCol & RESTCol --> Kafka
    Kafka --> HotCons --> Redis
    Kafka --> CHCons --> ClickHouse
    Kafka --> BrzCons --> MinIO
    Spark --> MinIO & ClickHouse

    AgentWorker --> Postgres & Redis & ClickHouse
    Prometheus --> FastAPI & WSCol & HotCons & CHCons & AgentWorker
```

