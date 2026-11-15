# 12 — Deployment Architecture

## 1. Deployment Philosophy: Resource-Efficient Profiled Docker Compose

In accordance with Objective **O7** and Section **9.11**, the platform does **not** introduce Kubernetes, service meshes, or multi-region clusters in its initial architecture. Instead, it uses a single, clean **Docker Compose** orchestration specification (`docker-compose.yml`) divided into functional **Compose Profiles** so developers and operators can run the exact subset of planes needed for their workload.

See also: [Diagram 15: Deployment Architecture](../diagrams/deployment/15-deployment-architecture.md).

---

## 2. Docker Compose Profile Matrix

| Profile Name | Command to Start | Included Services (`docker-compose.yml`) | Approx. RAM Footprint | Target Use Case |
|---|---|---|---|---|
| **`core`** *(Default)* | `docker compose --profile core up -d` | `postgres`, `redis`, `kafka` (KRaft), `clickhouse`, `backend-api` (`8000`), `frontend` (`3001->3000`), `edge-gateway` (`80`/`443`), `collector-ws`, `collector-rest`, `consumer-hot-redis`, `consumer-analytics-ch` | $\sim 4.0 - 5.5\text{ GB}$ | Real-time infrastructure, FastAPI backend, Nginx gateway, and TypeScript/Vite frontend. *(Note: standalone daemon workers `collector-*` run config-logging stubs unless wired; see `PROP-APP-002`.)* |
| **`intelligence`** | `docker compose --profile core --profile intelligence up -d` | Adds `agent-worker` (also pulls `postgres`, `redis`, `kafka`, `clickhouse` via profile membership) | $+ 0.5\text{ GB}$ | Developing and testing LangGraph AI Agent workflows (`agent-worker` daemon stub in v0.1). |
| **`lakehouse`** | `docker compose --profile core --profile lakehouse up -d` | Adds `minio` (API `9010->9000`, Console `9001->9001`) and `consumer-lakehouse-bronze` (plus `postgres`, `kafka`, `clickhouse`) | $+ 1.5 - 2.5\text{ GB}$ | Provisioning MinIO S3 buckets (`lakehouse-*`) and Bronze lakehouse ingestion target. |
| **`observability`** | `docker compose --profile core --profile observability up -d` | Adds `prometheus` (`9090`), `grafana` (`3000`) | $+ 0.6\text{ GB}$ | Scraping `/metrics`, consumer lag tracking, alert rules (`alerts.yml`), and Grafana dashboards. |
| **`bi`** | `docker compose --profile core --profile bi up -d` | Adds `superset` (`8088`) (plus `postgres`, `clickhouse`) | $+ 1.2\text{ GB}$ | Interactive BI visualization and market surveillance dashboards. |
| **`microservices`** | `docker compose --profile core --profile microservices up -d` | Adds `svc-market-hot` (`8001`), `svc-historical-backfill` (`8002`), `svc-analytics-quant` (`8003`), `svc-catalog-governance` (`8004`), `svc-iam-security` (`8005`), `svc-intelligence-agent` (`8006`), `svc-data-plane-v01` (`8007`) | $+ 1.2\text{ GB}$ | Running decomposed domain microservices (`ADR-007`) alongside `backend-api:8000`. |
| **`frontend`** | `docker compose --profile frontend up -d` | Starts `frontend` (`3001->3000`) independently against a locally running `backend-api` | $+ 0.3\text{ GB}$ | Standalone TypeScript/Vite dashboard development. |

> [!NOTE]
> **Planned Phase 2 Containers (`PLANNED` — Not Yet Defined in `docker-compose.yml`)**: `spark-worker`, `dbt-runner`, `great-expectations`, and `airflow` are architectural Phase 2 targets (`ADR-002`). Currently, Stages 1–12 execute inside `backend-api` and `svc-data-plane-v01` (`DataPlatformV01Pipeline`).

### Why Apache Kafka Runs in KRaft Mode
- Running Apache Kafka in **KRaft (Kafka Raft Metadata) mode** eliminates the separate Apache ZooKeeper container, saving $\sim 512\text{ MB}-1\text{ GB}$ of JVM heap and reducing local container startup time by $50\%$.

---

## 3. Network Segmentation & Port Exposure

To enforce Trust Boundaries (`Diagram 16`), containers are attached to three internal bridge networks (`docker-compose.yml`):
1. `frontend_net`: Connects externally exposed UI/API containers (`backend-api:8000`, `frontend:3001->3000`, `edge-gateway:80/443`, `grafana:3000`, `superset:8088`).
2. `app_control_net`: Connects `postgres:5432`, `redis:6379`, `clickhouse:8123/9000`, `backend-api`, `collector-ws`, `collector-rest`, `agent-worker`, `prometheus:9090`, `grafana`, `superset`, and `svc-market-hot`..`svc-data-plane-v01` (`8001..8007`).
3. `data_plane_net`: Connects `redis`, `kafka:9092`, `clickhouse`, `minio:9010/9001`, `backend-api`, `collector-ws`, `collector-rest`, `consumer-hot-redis`, `consumer-analytics-ch`, `consumer-lakehouse-bronze`, `agent-worker`, `prometheus`, and `svc-market-hot`..`svc-data-plane-v01`.

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

