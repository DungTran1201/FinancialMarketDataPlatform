# 12 — Deployment Architecture

## 1. Deployment Philosophy: Resource-Efficient Profiled Docker Compose

In accordance with Objective **O7** and Section **9.11**, the platform does **not** introduce Kubernetes, service meshes, or multi-region clusters in its initial architecture. Instead, it uses a single, clean **Docker Compose** orchestration specification (`docker-compose.yml`) divided into functional **Compose Profiles** so developers and operators can run the exact subset of planes needed for their workload.

See also: [Diagram 15: Deployment Architecture](../diagrams/deployment/15-deployment-architecture.md).

---

## 2. Docker Compose Profile Matrix

| Profile Name | Command to Start | Included Services | Approx. RAM Footprint | Target Use Case |
|---|---|---|---|---|
| **`core`** *(Default)* | `docker compose --profile core up -d` | `postgres`, `redis`, `kafka` (KRaft), `clickhouse`, `collector-ws`, `collector-rest`, `consumer-hot-redis`, `consumer-analytics-ch`, `backend-api` | $\sim 4.0 - 5.5\text{ GB}$ | Real-time ingestion, hot cache, ClickHouse OLAP, and FastAPI backend development/testing. |
| **`intelligence`** | `docker compose --profile core --profile intelligence up -d` | Adds `agent-worker` (LangGraph Orchestrator & Tool Gateway) | $+ 0.5\text{ GB}$ | Developing and testing on-demand and anomaly-triggered AI Agent workflows. |
| **`lakehouse`** | `docker compose --profile core --profile lakehouse up -d` | Adds `minio`, `consumer-lakehouse-bronze`, `spark-worker`, `dbt-runner`, `great-expectations`, `airflow` | $+ 4.5 - 6.0\text{ GB}$ | Running Bronze–Silver–Gold Lakehouse pipelines, historical backfills, and data quality suites. |
| **`observability`** | `docker compose --profile core --profile observability up -d` | Adds `prometheus`, `grafana` | $+ 0.6\text{ GB}$ | Monitoring ingestion lag, API P50/P95/P99 latency, and alerting dashboards. |
| **`bi`** | `docker compose --profile core --profile bi up -d` | Adds `superset` | $+ 1.2\text{ GB}$ | Interactive BI visualization and market surveillance dashboards. |

### Why Apache Kafka Runs in KRaft Mode
- Running Apache Kafka in **KRaft (Kafka Raft Metadata) mode** eliminates the separate Apache ZooKeeper container, saving $\sim 512\text{ MB}-1\text{ GB}$ of JVM heap and reducing local container startup time by $50\%$.

---

## 3. Network Segmentation & Port Exposure

To enforce Trust Boundaries (`Diagram 16`), containers are attached to three internal bridge networks:
1. `frontend_net`: Connects externally exposed UI/API containers (`backend-api:8000`, `grafana:3000`, `superset:8088`, `airflow:8080`).
2. `app_control_net`: Connects `backend-api`, `agent-worker`, `airflow`, `postgres`, and `prometheus`.
3. `data_plane_net`: Connects `collector-ws`, `collector-rest`, `kafka`, `consumer-*`, `redis`, `clickhouse`, `minio`, and `spark-worker`.

---

## 4. Environment Progression: Development vs. Staging vs. Production

While the codebase and container images remain identical across environments, operational parameters scale cleanly via environment configuration:

| Dimension | Local Development (`docker-compose.yml`) | Staging (Single VM / Compose) | Production (Multi-Node / Managed Infra Ready) |
|---|---|---|---|
| **Monitored Symbols** | 5–10 Spot Pairs (`BTCUSDT`, `ETHUSDT`, etc.) | 25–50 Spot Pairs | 200+ Spot & Derivatives Pairs |
| **Kafka Topology** | 1 Broker (KRaft), `replication.factor=1`, 6 partitions/topic | 1–3 Brokers, `replication.factor=1..3`, 6 partitions | 3+ Brokers, `replication.factor=3`, `min.insync.replicas=2`, 12–24 partitions |
| **ClickHouse** | 1 Node, local Docker volume | 1 Node with daily S3 backup to MinIO | 2+ Replicas (`ReplicatedReplacingMergeTree`) over NVMe + S3 tiered storage |
| **Redis** | 1 Instance (`256MB`, `volatile-lru`) | 1 Instance (`1GB`) | Redis Sentinel / Cluster (`4GB+`) |
| **PostgreSQL** | 1 Instance (`postgres:16-alpine`) | 1 Instance + Automated WAL backups | Primary + Standby Replica + PgBouncer connection pooling |
| **Object Storage** | Local MinIO container | Dedicated MinIO / Cloud S3 bucket | Multi-AZ MinIO or AWS S3 / GCS (`S3_ENDPOINT_URL` config switch) |
| **Secret Delivery** | Local `.env` file (untracked in Git) | CI/CD injected encrypted secrets | Vault / Cloud Secret Manager mounted into container runtime |
| **LLM Provider** | `mock` (Deterministic offline) or developer API key | Rate-limited staging API key | Dedicated production API key with strict daily token quota |

