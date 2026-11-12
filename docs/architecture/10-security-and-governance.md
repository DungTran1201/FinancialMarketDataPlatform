# 10 — Security and Governance Architecture

## 1. Security-by-Design Principles

Security and data governance are built into the platform's network, credential, database, API, and Agent boundaries from Day 1.

See also: [Diagram 16: Security and Trust Boundary Diagram](../diagrams/security/16-security-trust-boundaries.md).

---

## 2. Authentication & Role-Based Access Control (RBAC)

### 2.1. Authentication Mechanisms
1. **Interactive Users**: Authenticate via `POST /api/v1/auth/token` (Argon2id password verification) to receive short-lived signed JWT access tokens (`15m` expiry, `HS256`/`RS256`) and rotating refresh tokens.
2. **External Services / CLI**: Authenticate via scoped `X-API-Key` headers. Only the SHA-256 hash and prefix (`fmdp_live_...`) of the API key are stored in PostgreSQL `api_keys`.
3. **Service-to-Service**: Internal containers authenticate to PostgreSQL, ClickHouse, Redis, Kafka, and MinIO using dedicated service accounts injected strictly via environment variables / Docker secrets.

### 2.2. RBAC Permission Matrix

| Capability / Endpoint Group | `viewer` | `analyst` | `operator` | `admin` | `agent_service` (Internal) |
|---|---|---|---|---|---|
| Read Hot Market Prices & Snapshots (`/api/v1/market/*`) | Allowed | Allowed | Allowed | Allowed | Allowed (via Tool Gateway) |
| Read Historical Candles & Trades (`/api/v1/historical/*`) | Allowed | Allowed | Allowed | Allowed | Allowed (Bounded $\le 500$ rows) |
| Read Analytical Statistics & Reports (`/api/v1/analytics/*`, `/reports`) | Allowed | Allowed | Allowed | Allowed | Allowed (via Tool Gateway) |
| Trigger On-Demand Agent Analysis (`POST /api/v1/agents/runs`) | Denied | **Allowed** | **Allowed** | **Allowed** | Allowed (Event-Triggered) |
| Trigger Historical Backfill (`POST /api/v1/historical/backfill-jobs`) | Denied | Denied | **Allowed** | **Allowed** | **Denied** |
| Modify Monitored Symbols & Thresholds (`/api/v1/catalog/instruments`) | Denied | Denied | **Allowed** | **Allowed** | **Denied** |
| Manage Users, Roles & API Keys (`/api/v1/users`, `/api/v1/auth/keys`) | Denied | Denied | Denied | **Allowed** | **Denied** |

---

## 3. Least-Privilege Database & Storage Access Policies

Credentials are strictly segregated by service responsibility so a compromise or bug in one plane cannot corrupt another:

| Storage System | Credential / Role Name | Assigned To | Granted Permissions |
|---|---|---|---|
| **PostgreSQL** | `fmdp_app_rw` | `backend-api`, `collector-rest` | `SELECT, INSERT, UPDATE` on control tables (`users`, `monitored_instruments`, `ingestion_watermarks`, `agent_runs`). No `DROP`/`TRUNCATE`. |
| **PostgreSQL** | `fmdp_agent_rw` | `agent-worker` | `SELECT, INSERT, UPDATE` restricted strictly to `agent_runs` and `agent_tool_invocations`. Zero access to `users` or `api_keys`. |
| **ClickHouse** | `fmdp_ingest_writer` | `consumer-analytics-ch`, `spark-worker`, `dbt-runner` | `INSERT, SELECT, CREATE VIEW` on `market_data.*` and `analytics.*`. |
| **ClickHouse** | `fmdp_api_reader` | `backend-api`, `superset` | `SELECT` only (`readonly=1`, `max_execution_time=8`, `max_rows_to_read=2000000`). |
| **ClickHouse** | `fmdp_agent_ro` | `agent-worker` (Tool Gateway) | `SELECT` only (`readonly=1`, `max_execution_time=5`, `max_rows_to_read=500000`). |
| **MinIO (S3)** | `bronze-writer-policy` | `consumer-lakehouse-bronze`, `collector-rest` | `s3:PutObject`, `s3:GetObject` on `s3://market-data/bronze/*` only. |
| **MinIO (S3)** | `lakehouse-etl-policy` | `spark-worker`, `airflow` | Read Bronze; Read/Write `s3://market-data/silver/*` and `gold/*`. |

---

## 4. Secret Management & Environment Isolation

1. **Zero Secrets in Source Control**:
   - `.gitignore` blocks `.env`, `*.pem`, `*.key`, and credential files.
   - `.env.example` provides documented placeholder variables without real keys.
2. **Separate Secret Domains**:
   - Application JWT signing secret (`JWT_SECRET_KEY`)
   - PostgreSQL credentials (`POSTGRES_*`)
   - ClickHouse credentials (`CLICKHOUSE_*`)
   - Redis password (`REDIS_PASSWORD`)
   - MinIO S3 keys (`MINIO_ROOT_USER` / service access keys)
   - External Exchange API keys (`BINANCE_API_KEY`, optional for public streams)
   - External LLM Provider API key (`LLM_API_KEY`, mounted **only** into `agent-worker`, never into `backend-api` or collectors).

---

## 5. Data Governance, Classification, Audit & Lineage

### 5.1. Data Classification

| Classification Tier | Datasets | Handling & Retention Rules |
|---|---|---|
| **Tier 1 — Confidential / Security Critical** | `users.password_hash`, `api_keys.key_hash`, JWT secrets, LLM API keys | Encrypted at rest/transit; redacted in all logs; never accessible to Agent tools or BI dashboards. |
| **Tier 2 — Internal Operational & Audit** | `audit_logs`, `agent_runs`, `agent_tool_invocations`, `ingestion_watermarks` | Retained 1+ year in PostgreSQL; immutable append-only audit trail for all config changes and Agent tool calls. |
| **Tier 3 — Market & Analytical Data** | Trades, Klines, Tickers, Order Books, Silver/Gold Iceberg tables, Analytical Marts | Public exchange source data normalized and enriched by platform; governed by schema contracts and provenance tracking. |

### 5.2. End-to-End Data Lineage
Every analytical record and Agent report can be traced back to its exact origin:
- **Ingestion $\rightarrow$ Bronze/ClickHouse**: Tracked via `event_id` (deterministic UUIDv5), `provider`, `exchange_event_time`, and `ingested_at`.
- **Bronze $\rightarrow$ Silver $\rightarrow$ Gold**: Tracked via Apache Iceberg snapshot IDs and dbt model DAG lineage (`manifest.json`).
- **Storage $\rightarrow$ Agent Report**: Tracked via `agent_tool_invocations` (`invocation_id`, `tool_name`, `input_params`, `source_table`, `time_range`, `row_count`, `sha256_evidence_hash`).

