---
doc_id: DP-ARCH-SEC-001
title: "Data Plane Security & Trust Boundaries"
doc_type: specification
plane: data-plane
scope_level: plane
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: security-architect
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/ingestion/providers/binance/normalizer.py"
    - "docker-compose.yml"
    - ".env.example"
    - "src/serving/api/services/data_plane.py"
related_docs:
  - DP-ARCH-001
  - GOV-MIG-P2RISK-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Identified Data Plane external exchange validation, least-privilege DB target roles, and HTTP trigger RBAC gaps."
---

# Data Plane Security & Trust Boundaries

## 1. Trust Boundaries

1. **External Exchange Boundary (`Binance -> Normalizer`)**: Public market data only (no user PII; `BINANCE_API_KEY`/`SECRET` empty). All untrusted frames MUST pass `BinancePayloadNormalizer` validation (`Decimal > 0`, bounded OHLC relationships, non-empty symbols, UTC timestamps); malformed payloads are isolated into `DeadLetterEnvelopeV1`.
2. **Compose Storage Role Separation (`TARGET`)**: `.env.example` separates `CLICKHOUSE_INGEST_USER` (`fmdp_ingest_writer`), `CLICKHOUSE_API_READER_USER` (`fmdp_api_reader`), and `CLICKHOUSE_AGENT_RO_USER` (`fmdp_agent_ro`), and separates `POSTGRES_ADMIN_USER`, `POSTGRES_APP_USER`, and `POSTGRES_AGENT_USER`. **Gap**: Python runtime currently runs in-process without DB credentials active (`GAP-DATA-001`).
3. **HTTP Data Plane Control Surface (`SEC-AUDIT-003`)**: `POST /api/v1/market/ingest`, `POST /api/v1/historical/backfill-jobs`, `POST /api/v1/catalog/lakehouse/pipeline`, and `POST /api/v1/data-platform/v01/{run,compaction}` expose **zero** authentication or `OPERATOR`/`ADMIN` RBAC checks (`BLOCKED`).

## 2. Configuration & Credential Hygiene Gaps

- `.env.example` contains placeholder local credentials (`change_me_local_*`) wired into `docker-compose.yml` defaults. Production secrets injection/rotation is `OPEN`.
- `docker-compose.yml` injects `MINIO_ENDPOINT=http://minio:9000` while `PlatformConfig` reads `MINIO_ENDPOINT_URL` (`http://localhost:9000` default).
- Kafka internal listener uses unencrypted `PLAINTEXT` on `data_plane_net`.
