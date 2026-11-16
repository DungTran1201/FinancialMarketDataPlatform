---
doc_id: DP-OPS-RB-001
title: "Data Plane Operational Runbook"
doc_type: specification
plane: data-plane
scope_level: plane
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: devops-sre
accountable_role: devops-sre
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/gateway/observability.py"
    - "src/serving/api/services/data_plane.py"
    - "deploy/kafka/topics-init.sh"
    - "deploy/object-storage/init-buckets.sh"
related_docs:
  - DP-ROOT-001
  - DP-OPS-REC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Authored verified operational procedures matching real endpoints and highlighting missing compose init automation."
---

# Data Plane Operational Runbook

## 1. Pipeline Inspection & Trigger Procedures (`AS-IS`)

1. **Check Pipeline Status & Watermarks**: Query `GET /api/v1/data-platform/v01/status` and `GET /api/v1/data-platform/v01/watermarks` (reads `.local_storage/control_watermarks.db` SQLite).
2. **Execute Manual 12-Stage Pipeline Run (Simulated Exchange + Local Parquet)**: Call `POST /api/v1/data-platform/v01/run` with `{"symbols": ["BTCUSDT"], "interval": "1m", "backfill_minutes": 6}`.
3. **Trigger Silver Compaction**: Call `POST /api/v1/data-platform/v01/compaction` with `{"layer": "silver", "table_name": "market_klines"}` to compact local Parquet files into `compacted_silver_market_klines.parquet` and append Iceberg v2 JSON metadata (`version-hint.text`).
4. **Inspect Kafka Consumer Lag & DLQ**: Query `GET /api/v1/observability/kafka?topic=market.raw.trades.v1&window=5m` and `GET /api/v1/observability/traces?only_errors=true`. Note Broker 2 and 3 always appear `UNAVAILABLE` on single-node KRaft Compose.
5. **Infrastructure Port Probe**: Call `POST /api/v1/observability/live/probe` (`{"symbol": "BTCUSDT", "interval": "1m", "fetch_binance": false}`) to test TCP reachability against Postgres, Redis, ClickHouse, and Kafka.

## 2. Container Infrastructure Initialization Notes (`TARGET` / Gaps)

- `deploy/kafka/topics-init.sh` and `deploy/object-storage/init-buckets.sh` are **not** run automatically by `docker-compose.yml` startup; operators provisioning live containers MUST execute them manually against running `kafka:9092` and `minio:9000` (and resolve `LAKEHOUSE_BUCKET=market-data` vs `lakehouse-*` bucket naming conflict).
- Standalone worker containers (`collector-ws`, `collector-rest`, `consumer-*`) exit with code `0` immediately (`NOT_IMPLEMENTED` runtime loops).
