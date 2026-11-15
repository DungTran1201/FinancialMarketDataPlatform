# Deployment & Infrastructure Configs (`deploy/`)

Stores declarative container definitions, database initialization DDL, topic/bucket/catalog bootstraps, observability alerts, and edge TLS proxy configs synchronized with `docker-compose.yml` (`models/deployment/deployment.yaml`).

## Directory Structure

| Directory | Responsibility | Key Artifacts |
|---|---|---|
| `docker/` | Python service container build image (`Dockerfile.python`) shared by core workers and ASGI services | Multi-stage runtime installing `pyproject.toml`. |
| `kafka/` | Declarative Kafka topic creation & retention script (`topics-init.sh`) aligned with `models/data-platform/topics.yaml` | 6 canonical topics + retention policies. |
| `postgres/` | Control-plane OLTP DDL (`init/01_schema.sql`: monitored instruments, ingestion watermarks, agent runs, audit tables) | Auto-mounted by `postgres` service. |
| `clickhouse/` | OLAP analytical DDL (`init/01_schema.sql`: `ReplacingMergeTree` trades/klines/tickers & materialized rollups) | Auto-mounted by `clickhouse` service. |
| `object-storage/` | MinIO S3 bucket initialization (`init-buckets.sh`) for Bronze, Silver, Gold, and checkpoints | Idempotent `mc mb` bootstrap. |
| `iceberg/` | Apache Iceberg v2 catalog defaults & table properties (`catalog-config.yaml`) | ZSTD, merge-on-read, snapshot retention rules. |
| `observability/` | Unified telemetry: Prometheus scrape config (`prometheus/prometheus.yml`), SLI alerts (`prometheus/alerts.yml`), Grafana datasource provisioning (`grafana/datasources/prometheus.yml`) | Mounted by `--profile observability` (`DEP-004`). |
| `nginx/` & `tls/` | Edge TLS termination reverse proxy (`nginx.conf`) & mTLS/HTTPS dev cert generator (`generate_tls_certs.py`, `certs/`) | Retained separately from data-store configs for `ZONE-2` (`edge-gateway`) security isolation. |

