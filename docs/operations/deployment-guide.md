# Production & Microservices Deployment Guide

| Metadata | Value |
|---|---|
| **Document ID** | `DOC-OPS-DEPLOYMENT` |
| **Title** | Production Container Deployment & Multi-Profile Guide |
| **Category** | Operations & Deployment |
| **Status** | `APPROVED` |
| **Updated Date** | `2026-11-15` |
| **Authoring Role** | `dataops-engineer` |

---

## 1. Deployment Topology & Port Allocations

The platform defines multi-profile container topologies in [docker-compose.yml](../../docker-compose.yml):

| Service Name | Container Name | Profile(s) | Host Port(s) | Health Check Endpoint |
|---|---|---|---|---|
| **`edge-gateway`** | `fmdp-edge-gateway` | `core` | `80`, `443` | `http://localhost:80/health` |
| **`frontend`** | `fmdp-frontend` | `core`, `frontend` | `3001` (mapped to 3000) | `http://localhost:3000/` |
| **`kafka`** | `fmdp-kafka` | `core`, `lakehouse`, `intelligence` | `9092` | KRaft Cluster ID check |
| **`redis`** | `fmdp-redis` | `core`, `intelligence` | `6379` | `redis-cli ping` |
| **`postgres`** | `fmdp-postgres` | `core`, `lakehouse`, `intelligence`, `bi` | `5432` | `pg_isready -U postgres` |
| **`clickhouse`** | `fmdp-clickhouse` | `core`, `lakehouse`, `intelligence`, `bi` | `8123`, `9000` | `http://localhost:8123/ping` |
| **`minio`** | `fmdp-minio` | `lakehouse` | `9000`, `9001` | `http://localhost:9000/minio/health/live` |
| **`prometheus`** | `fmdp-prometheus` | `observability` | `9090` | `http://localhost:9090/-/healthy` |
| **`grafana`** | `fmdp-grafana` | `observability` | `3000` | `http://localhost:3000/api/health` |
| **`superset`** | `fmdp-superset` | `bi` | `8088` | `http://localhost:8088/health` |
| **`backend-api`** | `fmdp-backend-api` | `core` | `8000` | `http://localhost:8000/health` |
| **`collector-ws`** | `fmdp-collector-ws` | `core` | *(Internal)* | Daemon event loop status |
| **`collector-rest`** | `fmdp-collector-rest` | `core` | *(Internal)* | Watermark checkpoint loop |
| **`consumer-hot-redis`** | `fmdp-consumer-hot-redis` | `core` | *(Internal)* | Kafka consumer offset lag |
| **`consumer-analytics-ch`** | `fmdp-consumer-analytics-ch` | `core` | *(Internal)* | Batch buffer flusher |
| **`consumer-lakehouse-bronze`** | `fmdp-consumer-lakehouse-bronze` | `lakehouse` | *(Internal)* | Parquet writer flush loop |
| **`agent-worker`** | `fmdp-agent-worker` | `intelligence` | *(Internal)* | LangGraph orchestrator loop |
| **`svc-market-hot`** | `fmdp-svc-market-hot` | `microservices` | `8001` | `http://localhost:8001/health` |
| **`svc-historical-backfill`** | `fmdp-svc-historical-backfill` | `microservices` | `8002` | `http://localhost:8002/health` |
| **`svc-analytics-quant`** | `fmdp-svc-analytics-quant` | `microservices` | `8003` | `http://localhost:8003/health` |
| **`svc-catalog-governance`** | `fmdp-svc-catalog-governance` | `microservices` | `8004` | `http://localhost:8004/health` |
| **`svc-iam-security`** | `fmdp-svc-iam-security` | `microservices` | `8005` | `http://localhost:8005/health` |
| **`svc-intelligence-agent`** | `fmdp-svc-intelligence-agent` | `microservices` | `8006` | `http://localhost:8006/health` |
| **`svc-data-plane-v01`** | `fmdp-svc-data-plane-v01` | `microservices` | `8007` | `http://localhost:8007/health` |

---

## 2. Deployment Commands

### 2.1. Option A: Core Profile (Recommended for Development & Testing)
Runs all backing infrastructure and the unified `backend-api` single-process gateway:
```powershell
docker compose --profile core up -d
```

### 2.2. Option B: Microservices Profile (Production Isolation)
Runs all backing infrastructure, the Edge Gateway, and all 7 isolated domain microservice containers:
```powershell
docker compose --profile microservices up -d
```

### 2.3. Verifying Container Status & Health
```powershell
docker compose ps
```
All containers should display state `healthy` or `running`.

---

## 3. Environment Variables Configuration

Copy `.env.example` to `.env` before launching:
```powershell
Copy-Item .env.example .env
```
Key configuration parameters:
- `KAFKA_BOOTSTRAP_SERVERS`: `kafka:9092`
- `REDIS_URL`: `redis://redis:6379/0`
- `CLICKHOUSE_HOST`: `clickhouse`
- `CLICKHOUSE_HTTP_PORT`: `8123`
- `MINIO_ENDPOINT`: `minio:9000`
- `MINIO_ROOT_USER`: `minioadmin`
- `MINIO_ROOT_PASSWORD`: `minioadmin`
- `JWT_SECRET`: Secure random HS256 secret key

