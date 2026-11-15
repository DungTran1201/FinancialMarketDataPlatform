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

| Service Name | Container Name | Profile(s) | Host Port(s) | Compose Health Check / Verification Probe |
|---|---|---|---|---|
| **`edge-gateway`** | `fmdp-edge-gateway` | `core` | `80`, `443` | HTTP `80` redirects to HTTPS `443` (`nginx.conf`; no `/health` route) |
| **`frontend`** | `fmdp-frontend` | `core`, `frontend` | `3001` (mapped to `3000`) | `http://localhost:3001/` (no Compose `healthcheck` defined) |
| **`kafka`** | `fmdp-kafka` | `core`, `lakehouse`, `intelligence` | `9092` | `/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list` |
| **`redis`** | `fmdp-redis` | `core`, `intelligence` | `6379` | `redis-cli -a $REDIS_PASSWORD ping` |
| **`postgres`** | `fmdp-postgres` | `core`, `lakehouse`, `intelligence`, `bi` | `5432` | `pg_isready -U ${POSTGRES_ADMIN_USER:-fmdp_pg_admin} -d ${POSTGRES_DB:-fmdp_control}` |
| **`clickhouse`** | `fmdp-clickhouse` | `core`, `lakehouse`, `intelligence`, `bi` | `8123`, `9000` | `http://localhost:8123/ping` |
| **`minio`** | `fmdp-minio` | `lakehouse` | `9010` (`9000`), `9001` | `http://localhost:9010/minio/health/live` (host) / `http://localhost:9000/minio/health/live` (container) |
| **`prometheus`** | `fmdp-prometheus` | `observability` | `9090` | `http://localhost:9090/-/healthy` (no Compose `healthcheck` defined) |
| **`grafana`** | `fmdp-grafana` | `observability` | `3000` | `http://localhost:3000/api/health` (no Compose `healthcheck` defined) |
| **`superset`** | `fmdp-superset` | `bi` | `8088` | `http://localhost:8088/health` (no Compose `healthcheck` defined) |
| **`backend-api`** | `fmdp-backend-api` | `core` | `8000` | `http://localhost:8000/api/v1/health/live` and `/api/v1/health/ready` |
| **`collector-ws`** | `fmdp-collector-ws` | `core` | *(Internal)* | Config-logging startup stub (`PROP-APP-002` `PARTIALLY_IMPLEMENTED`) |
| **`collector-rest`** | `fmdp-collector-rest` | `core` | *(Internal)* | Config-logging startup stub (`PROP-APP-002` `PARTIALLY_IMPLEMENTED`) |
| **`consumer-hot-redis`** | `fmdp-consumer-hot-redis` | `core` | *(Internal)* | Kafka consumer loop (`consumer-hot-redis`) |
| **`consumer-analytics-ch`** | `fmdp-consumer-analytics-ch` | `core` | *(Internal)* | Kafka consumer micro-batch flusher (`consumer-analytics-ch`) |
| **`consumer-lakehouse-bronze`** | `fmdp-consumer-lakehouse-bronze` | `lakehouse` | *(Internal)* | Config-logging startup stub (`PROP-APP-002` `PARTIALLY_IMPLEMENTED`) |
| **`agent-worker`** | `fmdp-agent-worker` | `intelligence` | *(Internal)* | Config-logging startup stub (`PROP-APP-002` `PARTIALLY_IMPLEMENTED`) |
| **`svc-market-hot`** | `fmdp-svc-market-hot` | `microservices` | `8001` | `http://127.0.0.1:8001/api/v1/health/live` |
| **`svc-historical-backfill`** | `fmdp-svc-historical-backfill` | `microservices` | `8002` | `http://127.0.0.1:8002/api/v1/health/live` |
| **`svc-analytics-quant`** | `fmdp-svc-analytics-quant` | `microservices` | `8003` | `http://127.0.0.1:8003/api/v1/health/live` |
| **`svc-catalog-governance`** | `fmdp-svc-catalog-governance` | `microservices` | `8004` | `http://127.0.0.1:8004/api/v1/health/live` |
| **`svc-iam-security`** | `fmdp-svc-iam-security` | `microservices` | `8005` | `http://127.0.0.1:8005/api/v1/health/live` |
| **`svc-intelligence-agent`** | `fmdp-svc-intelligence-agent` | `microservices` | `8006` | `http://127.0.0.1:8006/api/v1/health/live` |
| **`svc-data-plane-v01`** | `fmdp-svc-data-plane-v01` | `microservices` | `8007` | `http://127.0.0.1:8007/api/v1/health/live` |

---

## 2. Deployment Commands

### 2.1. Option A: Core Profile (Recommended for Development & Testing)
Runs all backing infrastructure, Nginx edge gateway, TypeScript/Vite frontend (`3001`), and the unified `backend-api` (`8000`):
```powershell
docker compose --profile core up -d
```

### 2.2. Option B: Core + Microservices Profile (Isolated Domain Containers)
Runs core infrastructure alongside all 7 isolated domain microservice containers (`8001..8007`):
```powershell
docker compose --profile core --profile microservices up -d
```

> [!NOTE]
> `docker compose config --quiet` validates all 7 profiles (`core`, `lakehouse`, `intelligence`, `observability`, `bi`, `microservices`, `frontend`) with zero host port collisions (`clickhouse` uses `9000`, `minio` API uses `9010`). Live multi-container runtime bring-up depends on host Docker daemon availability (`NOT_RUN` in offline static CI).

### 2.3. Verifying Container Status & Health
```powershell
docker compose ps
```
Containers with configured Docker healthchecks should report `healthy`; services without explicit Compose `healthcheck` entries should report `running`.

---

## 3. Environment Variables Configuration

Copy `.env.example` to `.env` before launching:
```powershell
Copy-Item .env.example .env
```
Key configuration parameters in `.env.example`:
- `KAFKA_BOOTSTRAP_SERVERS`: `localhost:9092` (host) / `kafka:9092` (inside Docker Compose)
- `REDIS_HOST` / `REDIS_PORT` / `REDIS_PASSWORD`: `localhost` (`redis` in Compose) / `6379`
- `CLICKHOUSE_HOST` / `CLICKHOUSE_HTTP_PORT` / `CLICKHOUSE_NATIVE_PORT`: `localhost` (`clickhouse` in Compose) / `8123` / `9000`
- `MINIO_API_PORT` / `MINIO_CONSOLE_PORT` / `MINIO_ENDPOINT_URL`: `9010` / `9001` / `http://localhost:9010`
- `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD`: `fmdp_minio_admin` / `change_me_local_minio_password`
- `FRONTEND_PORT`: `3001` (maps host `3001` -> container `3000`)
- `JWT_SECRET_KEY`: Secure random `HS256` secret key (`>= 32` chars for non-local environments)

