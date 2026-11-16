---
doc_id: GOV-MIG-P2RISK-001
title: "Phase 2 Verified Security, Architecture, Integration & Testing Risk Register"
doc_type: migration-report
plane: governance
scope_level: platform
status: IN_REVIEW
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: security-architect
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/migration/phase-2-repository-audit.md"
related_docs:
  - GOV-MIG-P2AUD-001
  - GOV-MIG-P2LOG-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Consolidated confirmed security findings, architectural contradictions, runtime simulation gaps, and frontend/backend drifts on 7880c85."
---

# Phase 2 Verified Security, Architecture, Integration & Testing Risk Register

All items below were re-verified directly against source code and infrastructure configs on branch `docs-v2/phase-2-project-documentation` (`7880c85`). Per Phase 2 rules, application source code was **not** modified to fix these gaps during documentation authoring.

---

## 1. Security Findings Register (`SEC-AUDIT-*`)

| Finding ID | Severity | Affected Components & Exact Evidence | Current State & Impact | Production / Release Consequence | Recommended Target Remediation |
|---|---|---|---|---|---|
| `SEC-AUDIT-001` | **CRITICAL** | `src/serving/api/modules/iam/presentation/router.py:183-226` (`POST /api/v1/auth/token`) | Hashes supplied `password` via `CredentialHasher.hash_password(password)` and immediately verifies against that same hash (`L202-204`); accepts caller-supplied `role` (`admin`, `operator`, etc.) with zero user DB lookup. | **BLOCKS PRODUCTION**: Complete authentication bypass & arbitrary privilege escalation to `admin`. | Authenticate credentials against PostgreSQL `users` table (verifying `password_hash` and `is_active`); derive `role` strictly from stored user record. |
| `SEC-AUDIT-002` | **CRITICAL** | `src/serving/api/modules/iam/presentation/router.py:253-281` (`POST /api/v1/auth/api-keys`, `POST /api/v1/auth/revoke`), `iam/domain/security.py:90-93`, `iam/domain/ports.py:18-44` | Both routes require zero authentication/RBAC; issued API key hashes are discarded unpersisted; `verify_api_key` is dead code; `UserRole.SERVICE` has empty capability set (`[]`). | **BLOCKS PRODUCTION**: Anyone can mint nominal `admin` keys or revoke active JWTs via in-memory set (and revocation is unsynced across `svc-iam-security` vs gateway). | Require `admin` Bearer JWT on API key management; persist salted/hashed API keys & revocation blacklist in PostgreSQL/Redis with TTL; assign explicit least-privilege scopes to `SERVICE`. |
| `SEC-AUDIT-003` | **CRITICAL** | All 8 domain routers (`market`, `historical`, `analytics`, `catalog`, `platform_config`, `agent_api`, `reporting`, `iam`), `services/data_plane.py`, `gateway/{service,observability}.py`, `WS /ws/v1/observability/stream` | Zero FastAPI `Depends(...)` auth/RBAC checks exist on any endpoint or WebSocket route; standalone microservice apps (`services/*.py`, except `iam.py`) omit even the defense middleware. | **BLOCKS PRODUCTION**: All ingestion, backfill, lakehouse, microservice dispatch, catalog write, and AI run routes are publicly executable without credentials. | Enforce unified JWT / API-key dependency checking per-route capability requirements per Authorization Matrix across both monolith and microservice factories. |
| `SEC-AUDIT-004` | **HIGH** | `src/serving/api/modules/iam/presentation/router.py:28-34` (`_extract_client_ip`), `L81-96` (WAF), `src/shared/config/settings.py:33-35` | Unconditionally trusts `X-Forwarded-For`/`X-Real-IP`; missing `Host` defaults to `"localhost"`; WAF skips JSON bodies/headers; rate limiter uses isolated in-memory dicts; `jwt_secret_key` falls back to static `"change_me_generate_32_byte_random_hex_secret"`. | **BLOCKS PRODUCTION**: IP spoofing bypasses rate limits & IP-bound JWTs; default secret enables forged JWTs if env var is omitted. | Trust forwarded headers only from verified proxy CIDRs; fail fast at startup if default JWT secret is active outside unit tests; add Redis-backed rate limits. |
| `SEC-AUDIT-005` | **MEDIUM** | `src/serving/api/main.py:123-125` (`/health/ready`), `iam/presentation/router.py:283-307` (`/auth/domains`), `frontend/src/services/auth/auth.service.ts:18-27` | Unauthenticated readiness/domain endpoints expose masked internal bindings and TLS posture; frontend initializes unauthenticated UI sessions as hardcoded `quant_admin` (`ADMIN`). | Reconnaissance exposure and misleading browser RBAC posture. | Restrict `/auth/domains` and detailed readiness metadata to authenticated operators; require real login flow before rendering admin persona in frontend. |
| `SEC-AUDIT-006` | **MEDIUM** | `src/intelligence/tools/contracts.py:35,88-108`, `src/serving/infrastructure/runtime.py:489-542`, `src/intelligence/orchestrator/graph.py:159-160` | `GENERATE_ANALYSIS_REPORT` (`postgres_agent_rw`) and `DETECT_ANOMALIES` mutate in-memory state (`self.reports`, `self.detected_anomalies`) while `ToolGovernancePolicy.is_read_only_market_data` defaults to `True`; Node 5 executes outside budget check; `AGENT_RUN_TIMEOUT_SECONDS` un-enforced. | Misclassification of write-capable Agent tools bypasses stricter approval/side-effect gates; run-level timeout unguarded. | Explicitly tag `GENERATE_ANALYSIS_REPORT` and state-mutating tools `is_read_only_market_data=False`; enforce hard run timeout and Node 5 budget check. |

---

## 2. Architecture, Runtime & Integration Gaps (`GAP-*`)

| Gap ID | Severity | Area | Confirmed Evidence | Impact / Open Action |
|---|---|---|---|---|
| `GAP-ARCH-001` | **HIGH** | Monolith vs. Microservices Split | `create_*_microservice_app(runtime=None)` (`src/serving/api/services/*.py`) instantiates isolated in-memory `PlatformRuntimeContainer()` per container process (`docker-compose.yml:400-563`), whereas `gateway/registry.py` lists unimplemented `/ws/v1/market` on `svc-market-hot`. | Separate microservice containers cannot share ingested quotes, watermarks, agent runs, or rate limits until Redis/Postgres/Kafka persistence is wired. Requires explicit ADR decision & persistence wiring before microservices deployment. |
| `GAP-DATA-001` | **HIGH** | Control Store & Ingestion Stubs | `ws_collector.py`, `rest_backfill.py`, `hot_redis.py`, `analytics_ch.py`, `bronze/consumer.py`, `intelligence/main.py` exit on `main()`; `IngestionWatermarkStore` uses SQLite schema incompatible with `deploy/postgres/init/01_schema.sql`; `ProductionExchangeHistoricalCollector` defaults to embedded ASGI simulator and omits `.use_embedded_asgi_transport` attribute. | Docker worker containers exit immediately (`Exited (0)`); real Binance WS, PostgreSQL, Redis, ClickHouse, MinIO, Iceberg REST (`iceberg-rest:8181` missing from Compose), and live `dbt` pipelines are not executed at runtime. |
| `GAP-DATA-002` | **MEDIUM** | Broker/Sink Persistence & Metric Consistency | `HotStateProjector._sync_record_to_live_redis` skips snapshot/orderbook keys and writes `last_price="0"` on price-less orderbooks; `ClickHouseBatchSink` JSON persistence omits trades/tickers and `get_storage_snapshot()` checks `_table` instead of `event_type`; `DeadLetterEnvelopeV1.failed_at` uses static import-time timestamp; `deploy/clickhouse/init/01_schema.sql` defines 0 MVs. | Live external adapters would diverge or drop state without remediation before production cutover. |
| `GAP-FE-001` | **HIGH** | Remaining Frontend/Backend Drift | `AuthService.getApiKeys()` calls nonexistent `GET /api/v1/auth/api-keys` (405 swallowed -> `[]`), `revokeApiKey()` calls nonexistent `DELETE /api/v1/auth/api-keys/{id}`; `AdministrationModule` discards `raw_key`; `ObservabilityService.setStreamControl()` hits missing `/stream/control`; `MarketAnalyticsModule` `|| 0.45` masks `0`; `MainLayout` ignores LIVE/DEMO & notifications; multiple UI views render static health/DAG/badge strings. | Administration API key lifecycle does not persist or reveal keys; analytics `0` values misrender; live-vs-demo mode toggle has zero effect. |
| `GAP-OPS-001` | **MEDIUM** | Deployment Config & Env Drift | `docker-compose.yml` sets `MINIO_ENDPOINT` while `settings.py` ignores it; `init-buckets.sh` creates `lakehouse-*` buckets while `.env.example` sets `LAKEHOUSE_BUCKET=market-data`; `grafana` lacks volume mount for `deploy/observability/grafana/datasources/prometheus.yml` and has 0 dashboards; zero Compose `resources.limits`; `topics-init.sh` not wired into Compose startup. | Container stack lacks automated topic/bucket init, Grafana datasource mounting, and memory bounds. |
| `GAP-QA-001` | **MEDIUM** | Verification & Frontend Testing Scope | All 51 Python tests use in-memory/local-disk/embedded-ASGI doubles (zero live Docker service tests); `frontend/tests/*.test.js` test inline copies/static arrays with zero `frontend/src/` imports. | Live external integration and frontend module regressions remain unverified automatically. |
