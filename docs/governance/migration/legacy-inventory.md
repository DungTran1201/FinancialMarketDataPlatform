---
doc_id: GOV-MIG-INV-001
title: "Documentation V1 Legacy Inventory & Implementation Reality Audit"
doc_type: migration-report
plane: governance
scope_level: platform
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "1.0.0"
owner_role: documentation-architect
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "Git backup tag docs-v1-legacy-2026-11-16 (commit f0329d3)"
related_docs:
  - DOC-ROOT-001
  - GOV-MIG-DISP-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Initial evidence-based audit of baseline commit f0329d3 before Documentation V2 Phase 1 migration."
revision_history:
  - version: "1.0.0"
    date: "2026-11-16"
    author_role: documentation-architect
    summary: "Completed repository-wide documentation inventory, architecture consistency audit, implementation reality audit, and security re-audit."
---

# Documentation V1 Legacy Inventory & Implementation Reality Audit

## 1. Audit Scope & Git Baseline

- **Repository**: `DungTran1201/FinancialMarketDataPlatform`
- **Audited Baseline Commit**: `f0329d3` (`main`, clean working tree prior to migration)
- **Immutable Backup Tag**: `docs-v1-legacy-2026-11-16`
- **Migration Working Branch**: `docs-v2/phase-1-foundation`
- **Audit Method**: Direct inspection of all files across `docs/`, `models/`, `work-items/`, `.agents/`, `tools/`, `src/`, `frontend/`, `deploy/`, `tests/`, `notebooks/`, `.github/workflows/`, `pyproject.toml`, `docker-compose.yml`, `.env.example`, `setup.bat`, and `run.bat`.

---

## 2. Complete Documentation & Governance Inventory

### 2.1 Quantitative Summary by Subsystem

| Location | Files | Nature | Authoritative in V1 | Code / CI / Script References | Recommended Disposition |
|---|---|---|---|---|---|
| `docs/` | 200 | Prose specs, ADRs, templates, diagrams, governance | Mixed (`BASELINED` & `DRAFT`) | `src/lakehouse/gold/mart_engine.py:3` docstring, `src/shared/security/primitives.py:31` docstring; `tools/validators/` | Retire active tree (`LEGACY_DOCUMENT` / `REPLACE_WITH_GOVERNANCE` / `REBUILD_IN_PHASE_2`) |
| `models/` | 52 | 38 YAML models/templates + 14 READMEs | Yes (V1 canonical YAML) | `deploy/kafka/topics-init.sh:2` comment; `tools/validators/` only (zero `src/`/`tests/` runtime reads) | `LEGACY_DOCUMENT` / `REBUILD_IN_PHASE_2` |
| `work-items/` | 71 | `_template/` + 6 V1 work items | Yes (V1 change tracking) | `tools/validators/validate_work_items.py` only | `LEGACY_DOCUMENT` (recoverable via Git tag) |
| `.agents/` | 109 | 19 roles, 22 rules, 25 skills, 7 configs, 3 catalogs, 3 root manifests | Yes (V1 Agent OS) | `tools/validators/validate_agent_config.py`; IDE skill discovery | `REPLACE_WITH_GOVERNANCE` (remove V1 rules/templates; keep concise V2 pointer + hooks) |
| `tools/` | 18 | 10 V1 validators + `run_all.py` + 4 hooks + 3 READMEs | Yes (V1 tooling) | `.github/workflows/ci.yml:33`, `run.bat:113`, `.agents/hooks.json` | `REPLACE_WITH_GOVERNANCE` (remove obsolete count-hardcoded V1 validators; keep `run_all.py` & hooks aligned to V2 validator) |
| `README.md` | 1 | Root project overview | Yes | `tools/validators/validate_docs.py` | `PRESERVE_PROJECT_DOCUMENT` (update links to Docs V2 without adding Phase 2 specs) |
| `AGENTS.md` | 1 | Root agent instructions | Yes | `tools/validators/validate_docs.py` | `REPLACE_WITH_GOVERNANCE` (update concisely to point to Docs V2) |
| `src/**/README.md` | 7 | Subsystem developer notes | Informative | None | `REVIEW_REQUIRED` (leave `src/` untouched in Phase 1; sync stale `src/serving/README.md` in Phase 2 or separate code task) |
| `frontend/README.md` | 1 | SPA developer notes | Informative | None | `REVIEW_REQUIRED` (leave `frontend/` untouched in Phase 1; note stale folders/ports) |
| `deploy/README.md` | 1 | Infra config notes | Informative | None | `PRESERVE_PROJECT_DOCUMENT` |
| `tests/README.md` | 1 | Test suite index | Informative | None | `PRESERVE_PROJECT_DOCUMENT` |
| `notebooks/` | 5 | Exploratory notebook, early WS workers, raw JSON snapshot | Prototype | None | `PRESERVE_RUNTIME_ASSET` (historical prototype reference; keep isolated from `src/`) |
| `pyproject.toml`, `docker-compose.yml`, `.env.example`, `.github/workflows/ci.yml`, `setup.bat`, `run.bat`, `deploy/**` | 21 | Build, runtime, CI/CD, DDL, infra configs | Yes (runtime/CI) | Directly executed / deployed | `PRESERVE_RUNTIME_ASSET` |

### 2.2 Detailed `docs/` Inventory (200 Legacy Files)

| Path Pattern | Count | Document Type | Claimed Scope | Owner (V1) | Authoritative | Duplicates / Conflicts | Code / CI Refs | Disposition |
|---|---|---|---|---|---|---|---|---|
| `docs/README.md` | 1 | Master Doc Index | Entire `docs/` hierarchy | `documentation-architect` | Yes | References obsolete 22 diagrams / 38 models | None | `REPLACE_WITH_GOVERNANCE` |
| `docs/overview/*` (`README.md`, `system-overview.md`, `technology-stack.md`) | 3 | Orientation & Stack | Platform overview & tech versions | `documentation-architect` | Yes | Conflicts with `src/` (6-node vs 5-node LangGraph, DuckDB, CoinGecko) and `docker-compose.yml` image versions | None | `REBUILD_IN_PHASE_2` |
| `docs/architecture/00..14*.md` + `README.md` | 16 | Architecture Specs | C4 L1–L3, Data Platform, Backend, Agent, Storage, Contracts, API, Security, Observability, Deployment, Perf, v0.1 | `architecture-modeler` / `data-platform-architect` | Yes (`BASELINED`) | `README.md` cites `00..13` + `Qdrant`/`RAG` (missing in files); `05` vs `14` conflict on monolith vs 8 microservices | `mart_engine.py:3` docstring (`04-*`) | `REBUILD_IN_PHASE_2` |
| `docs/architecture/adr/ADR-001..008*.md` + `README.md` | 9 | Architecture Decisions | Plane separation, event streaming, storage, monolith, caching, agent, v0.1, modular restructure | `architecture-modeler` | Yes (`Accepted` / `APPROVED`) | `ADR-004` rejects 8 microservices; `ADR-007` adopts 8 microservices; `ADR-007` vs `06` disagree on 6 vs 5 LangGraph nodes | `validate_identifiers.py`, `validate_docs.py` | `REBUILD_IN_PHASE_2` |
| `docs/specifications/*` (6 files) | 6 | Platform Specifications | Data reqs, dictionary, contracts, API spec, NFRs | `requirements-engineer` / `api-architect` | Yes (`BASELINED`) | `non-functional-requirements.md` specifies `allkeys-lru` vs `ADR-005`/`docker-compose.yml` `volatile-lru`; duplicates `docs/contracts/` | `primitives.py:31` docstring (`api-specification.md`) | `REBUILD_IN_PHASE_2` |
| `docs/contracts/*` (3 files) | 3 | Contract Portal | API contracts & requirements matrix | `api-architect` | Yes (`APPROVED`) | `api-contracts.md` route paths conflict with `api-specification.md` & `src/serving/api/`; `requirements-matrix.md` `BR-003` conflicts with `models/requirements/business-rules.yaml` | None | `REBUILD_IN_PHASE_2` |
| `docs/operations/*` (3 files) | 3 | Operations & Runbooks | Compose deployment guide & SRE runbooks `RB-001..003` | `dataops-engineer` | Yes (`APPROVED`) | Ports (`frontend:3000`, `grafana:3001`) conflict with `docker-compose.yml` (`frontend:3001`, `grafana:3000`); runbook calls non-existent `/api/v1/historical/backfill/pause` | None | `REBUILD_IN_PHASE_2` |
| `docs/development/*` (3 files) | 3 | Developer Guides | Quickstart & codebase map | `documentation-architect` | Yes (`APPROVED`) | `README.md` references non-existent `component-specification.template.md`; `codebase-map.md` claims 6-node LangGraph; `developer-quickstart.md` cites Vite `:5173` vs `vite.config.ts` `:3000` | None | `REBUILD_IN_PHASE_2` |
| `docs/diagrams/**` (53 files) | 53 | Derived Mermaid Diagrams & Templates | 22 instantiated diagrams across 8 dirs + 12 diagram templates + 19 READMEs | `architecture-modeler` / `ux-modeler` | Derived only | `backend/08..09` collide with `data-platform/08..09`; `ux/01` still shows decommissioned `/ui/data-flow`; 10 empty template-only categories | `validate_diagrams.py` | `REBUILD_IN_PHASE_2` (22 diagrams) / `REPLACE_WITH_GOVERNANCE` (12 templates + READMEs) |
| `docs/product/README.md` + `docs/product/00..10`, `12` (15 READMEs) | 15 | Product Lifecycle Index & Stubs | Lifecycle index & unpopulated phase directories | `documentation-architect` | Stub | Empty phase directories (`README.md` only) | `document-map.yaml` | `LEGACY_DOCUMENT` |
| `docs/product/11-ux/*` (3 files) | 3 | UX Specs | `SCR-001` & `UX-001` | `ux-modeler` | Mixed (`SCR-001` lacks status) | `user-flows.md` uses deleted `/ui/data-flow` & `API-016` while `screen-specifications.md` uses `/data-flow` | None | `REBUILD_IN_PHASE_2` |
| `docs/product/13-operations/*` (2 files) | 2 | Monitoring Spec | `OPS-MON-001` (`monitoring.md`) | `dataops-engineer` | `DRAFT` | Unapproved draft; notes `/ui/*` decommissioned and honestly lists unavailable brokers/containers | None | `REBUILD_IN_PHASE_2` |
| `docs/product/14-governance/*` (8 files) | 8 | Governance Reports | Baseline, status, DoD, decision log, RCM, open questions, validation report | `documentation-auditor` | Stale (`2026-11-12`) | Frozen at `DOCS-001` (`11` roles, `107` READMEs, `16` diagrams, `29` models) | None | `REPLACE_WITH_GOVERNANCE` |
| `docs/features/README.md` | 1 | Feature Package Index | Empty feature directory contract | `documentation-architect` | Stub | No features populated | None | `LEGACY_DOCUMENT` |
| `docs/templates/**` (72 files) | 72 | Document Templates | 57 `.template.md` + 15 READMEs across 14 categories | `documentation-architect` | `TEMPLATE` | `templates/README.md` states `56` templates while `57` exist; enforces bloated multi-phase product docs | `validate_templates.py` | `REPLACE_WITH_GOVERNANCE` |
| `docs/archive/*` (2 files) | 2 | Legacy Archive | Superseded v0.0 & migration notes | `documentation-architect` | `ARCHIVED` | Active `docs/archive/` folder prohibited under Documentation V2 | None | `LEGACY_DOCUMENT` |

---

## 3. Architecture Consistency Audit

Inspection across `docs/`, `models/`, `docker-compose.yml`, `frontend/`, and `src/` confirmed the following contradictions and ambiguities:

1. **Modular Monolith vs. Microservices Contradiction**:
   - `ADR-001` and `ADR-004` explicitly reject splitting the 8 backend bounded contexts into independent HTTP microservices.
   - `ADR-007` and `docs/architecture/14-*` later introduce 8 ASGI microservices (`svc-api-gateway` `:8000` plus `svc-market-hot` `:8001` through `svc-data-plane-v01` `:8007`) under `--profile microservices` (`docker-compose.yml:400-563`).
   - In actual code (`src/serving/api/services/*.py`), each microservice factory (`create_*_microservice_app`) instantiates a separate `PlatformRuntimeContainer()` with its own **in-memory** dicts when run as an independent container process, meaning separate containers would not share hot state, watermarks, or traces without real Redis/Postgres/Kafka backing.
2. **LangGraph Node Count Mismatch**:
   - `docs/architecture/06-*`, `ADR-006`, `docs/diagrams/agent/12-*`, `frontend/src/modules/ai-workspace/AiWorkspaceModule.ts`, and `src/intelligence/workflows/investigation.py` (`WORKFLOW_NODES`) implement/specify **5 nodes**.
   - `docs/overview/system-overview.md`, `docs/development/codebase-map.md`, `docs/architecture/05-*` §5, and `ADR-007` claim a **6-node** LangGraph workflow.
3. **Conflicting API Contracts & Frontend Integration Drift**:
   - `docs/contracts/api-contracts.md` documents endpoints (`/api/v1/market/ticker/24h`, `/api/v1/historical/klines`, `POST /api/v1/historical/backfill`, `/api/v1/analytics/volatility`, `/api/v1/observability/data-flow`, `/api/v1/observability/stream/events`, `WS /ws/market`) that do not match `docs/specifications/api-specification.md` or `src/serving/api/`.
   - Even `frontend/src/services/` calls non-existent backend routes (`GET /api/v1/auth/api-keys`, `DELETE /api/v1/auth/api-keys/{keyId}`, `GET /api/v1/catalog/{datasets,lineage,data-quality}`, `GET /api/v1/agents/runs`, `POST /api/v1/observability/stream/control`) and uses mismatched query/path shapes (`/market/price?symbol=...` vs `/market/prices/{symbol}`, `/historical/klines?symbol=...` vs `/historical/klines/{symbol}`, `/analytics/volatility` vs `/analytics/statistics/{symbol}`, `/analytics/correlation` vs `/analytics/correlations`).
4. **Canonical Model Cross-Contradictions (`models/`)**:
   - `models/api/integrations.yaml` lists topic retentions (`72h`, `24h`, `168h`, `336h`) and kline partition key `{provider}:{symbol}:{interval}`, while `models/data-platform/topics.yaml` lists `7d` (`604800000ms`) for raw topics and `30d` (`2592000000ms`) for anomalies/DLQ, and `models/data-platform/events.yaml` lists `{provider}:{symbol}`.
   - `models/ux/ux.yaml` binds `SCR-005..007` to `API-007..012` (analytics/agent/health/v01-run in `models/api/api.yaml`), and `UX-001` references decommissioned `SCR-001` (`/ui/data-flow`).
   - `models/deployment/deployment.yaml` (`DEP-006`) declares `svc-catalog-governance`, `svc-iam-security`, and `svc-intelligence-agent`, which have no `COMP-###` entries in `models/architecture/components.yaml`.
5. **Decommissioned UI References & Ghost Technologies**:
   - `src/serving/api/gateway/ui.py` (`/ui/data-flow`) was decommissioned in `FEAT-001`, yet `src/serving/README.md`, `docs/product/11-ux/user-flows.md`, and `docs/diagrams/ux/01-realtime-data-flow-ui-architecture.md` still document it as active.
   - `docs/architecture/README.md` references `Qdrant` and `RAG` (absent everywhere in repo); `docs/overview/system-overview.md` references `CoinGecko` and `DuckDB` (absent in `src/`); `docs/overview/technology-stack.md` cites newer container versions (`Kafka 3.8+`, `Redis 7.4+`, `ClickHouse 24.8+`, `Grafana 11.2+`) than `docker-compose.yml` (`3.7.0`, `7.2`, `24.3`, `11.0.0`).
   - `docs/specifications/non-functional-requirements.md` states Redis eviction policy `allkeys-lru`, contradicting `ADR-005` and `docker-compose.yml` (`volatile-lru`).
6. **Stale Governance & Diagram Numbering Collisions**:
   - `docs/product/14-governance/` remained frozen at `2026-11-12`.
   - `docs/diagrams/backend/08-*` and `09-*` collide numerically with `docs/diagrams/data-platform/08-*` and `09-*`; legacy diagrams `01`..`16` lack in-file `DIAG-*` headers.
7. **Dependency Boundary Enforcement**:
   - `tests/architecture/test_clean_architecture_boundaries.py` verifies AST DAG isolation across `src/{shared,ingestion,streaming,lakehouse,serving,intelligence}`. This separation holds in code, with `src/lakehouse/orchestration/pipeline.py` and `src/serving/infrastructure/runtime.py` acting as the two composition roots.

---

## 4. Implementation Reality & Security Audit

### 4.1 Implementation Status Classification (`AS-IS`)

| Capability / Component | Implementation Status | Evidence (`src/`, `frontend/`, `deploy/`, `tests/`) | Gap Summary vs. Legacy Target Docs |
|---|---|---|---|
| Shared contracts (`EventEnvelopeV1`, `Decimal`, UUIDv5, `BoundedTimeRange`, quant math) | `IMPLEMENTED` | `src/shared/contracts/events/market_events.py`, `src/shared/domain/{primitives,quant}.py`, `tests/contract/test_contracts_and_guardrails.py` | Enforced in-process and verified by unit/contract tests. |
| Binance WS & REST payload normalization & DLQ wrapping | `IMPLEMENTED` | `src/ingestion/providers/binance/normalizer.py`, `tests/resilience/test_gap_recovery_and_dlq.py` | Normalizer logic is implemented; live exchange WS streaming in `src/` is not wired. |
| Exchange REST historical backfill & rate limiter | `PARTIALLY_IMPLEMENTED` | `src/ingestion/providers/binance/rest_client.py`, `src/ingestion/application/backfill_service.py` | `ProductionExchangeHistoricalCollector` defaults to `use_embedded_asgi_transport=True` (embedded simulated FastAPI exchange). Real HTTP exists only when toggled `False` or via `PlatformRuntimeContainer.fetch_live_binance_market_data()`. `historical/presentation/router.py:150` hardcodes `"transport_mode": "MOCKED_SIMULATED_EXCHANGE_REST"`. |
| Exchange WebSocket collector worker (`collector-ws`, `collector-rest`) | `NOT_IMPLEMENTED` (entrypoints) / `SIMULATED` (frame handler) | `src/ingestion/entrypoints/{ws_collector,rest_backfill}.py` (log-and-exit stubs); `src/ingestion/application/ws_service.py` | No `websockets` client or continuous loop exists in `src/` (only in legacy `notebooks/workers/*`). |
| Kafka Event Streaming (`PartitionedEventStreamingBroker`) | `SIMULATED` (default) / `PARTIALLY_IMPLEMENTED` | `src/streaming/infrastructure/kafka_broker.py` | In-process `defaultdict(list)` broker used by runtime and all tests. `ConfluentKafkaStreamingAdapter` has lazy `produce()` only if explicitly injected (default `None`); no `confluent_kafka.Consumer` loop exists. `docker-compose.yml` runs 1 KRaft node (`Broker 2/3` unavailable). |
| Hot State Cache (`HotStateProjector` -> Redis) | `SIMULATED` (default) / `PARTIALLY_IMPLEMENTED` | `src/streaming/consumers/hot_redis.py` | In-memory Python `dict`s (`_price_store`, `_snapshot_store`, `_orderbook_store`) + optional JSON file. `redis_client=None` in runtime; `hot_redis.py:main()` is a stub; `redis` package is never imported in `src/`. |
| OLAP Store (`ClickHouseBatchSink` -> ClickHouse) | `SIMULATED` | `src/streaming/consumers/analytics_ch.py`, `deploy/clickhouse/init/01_schema.sql` | In-memory dict simulation (`IN_PROCESS_REPLACING_MERGE_TREE_SIMULATION`). `_clickhouse_client` is stored and never called; `clickhouse-connect` never imported in `src/`; `analytics_ch.py:main()` is a stub. |
| Lakehouse Bronze / Silver / Gold & Quality Gates | `PARTIALLY_IMPLEMENTED` | `src/lakehouse/{bronze,silver,gold,quality,catalog,orchestration}/*.py`, `src/lakehouse/gold/dbt/` | Real ZSTD Parquet & Iceberg v2 JSON manifests written to **local disk** (`.local_lakehouse/`) via `pyarrow` and pure-Python `Decimal` math. `MinIO`/`S3`, `pyiceberg`, `pyspark`, `great-expectations`, and runtime `dbt` invocation are **not** implemented in `src/`. `bronze/consumer.py:main()` is a stub. |
| Control Store Watermarks (`IngestionWatermarkStore`) | `PARTIALLY_IMPLEMENTED` | `src/ingestion/infrastructure/watermark_store.py`, `deploy/postgres/init/01_schema.sql` | Uses local `sqlite3` WAL (`.local_storage/control_watermarks.db`). PostgreSQL (`asyncpg`/`sqlalchemy`) is never imported in `src/`; runtime instruments/jobs/agent_runs/reports live in memory dicts. |
| FastAPI Modular Monolith & 7 Microservice Wrappers | `PARTIALLY_IMPLEMENTED` | `src/serving/api/main.py`, `src/serving/api/modules/*`, `src/serving/api/services/*`, `src/serving/api/gateway/*` | Routes and Clean Architecture layers work in-process (`TestClient`/ASGI). Async `202` routes (`/agents/runs`, `/historical/backfill-jobs`) execute synchronously via `await`. Orderbook route returns hardcoded static bids/asks when missing. |
| Observability Tracing, Prometheus Metrics & TCP Infra Probe | `IMPLEMENTED` (in-process + TCP probe) | `src/shared/observability/{tracing,metrics}.py`, `src/serving/api/gateway/observability.py`, `src/serving/infrastructure/runtime.py:679` | 10-timestamp tracing, SSE/WS broadcast, `/metrics` Prometheus exposition, and real async TCP probes to container ports work. |
| Intelligence Plane (`MarketIntelligenceGraph`, `ControlledToolGateway`) | `SIMULATED` (LLM) / `IMPLEMENTED` (Gateway) | `src/intelligence/{orchestrator/graph.py,tools/gateway.py,reporting/validator.py}`, `src/intelligence/main.py` | 10-tool whitelist, RBAC check, row bounds, timeout, and citation validator work. Orchestrator uses `DeterministicMockLLMAdapter`; `langgraph` and real LLM APIs are not imported; `src/intelligence/main.py` is a stub. |
| Frontend SPA (`frontend/`) | `PARTIALLY_IMPLEMENTED` | `frontend/src/**/*`, `frontend/tests/*.test.js` | Built SPA with 6 modules exists, but multiple service endpoints/payload shapes diverge from FastAPI routes, and `frontend/tests/` only tests local inline functions rather than `frontend/src/`. |
| End-to-End Test Suite (`tests/`) | `SIMULATED` (in-process only) | `tests/{architecture,unit,contract,data_quality,integration,e2e,resilience,performance}/*` | 50 tests pass in-process (`pytest`), but zero tests exercise live Kafka, Redis, ClickHouse, PostgreSQL, MinIO, or real Binance WS/REST. |

### 4.2 Security Re-Audit Findings (Critical & High Risks)

> [!CAUTION]
> **Security Disclosure**: Independent audit of `src/serving/api/` confirms that the current authentication and authorization implementation is **NOT secure** and MUST NOT be described as production-ready or approved security behavior in Phase 2 without remediation. Per Phase 1 scope rules, application code was **not** modified during this documentation audit.

| Finding ID | Severity | Vulnerability & Confirmed Evidence | Impact |
|---|---|---|---|
| `SEC-AUDIT-001` | **CRITICAL** | **Self-Verified Authentication Bypass & Arbitrary Privilege Escalation (`POST /api/v1/auth/token`)**: `src/serving/api/modules/iam/presentation/router.py:183-211` reads `username`, `password`, and `role` from the unauthenticated JSON body, computes `password_hash = CredentialHasher.hash_password(password)` (line 202), and immediately checks `CredentialHasher.verify_password(password, password_hash)` (line 203) without querying any user store (`users` table in `deploy/postgres/init/01_schema.sql` is unused). Any caller can mint a valid `admin` HS256 JWT with any arbitrary `username` (>=3 chars) and `password` (>=8 chars). | Complete authentication bypass and immediate privilege escalation to `admin`. |
| `SEC-AUDIT-002` | **CRITICAL** | **Unauthenticated Admin API Key Minting & Token Revocation (`POST /api/v1/auth/api-keys`, `POST /api/v1/auth/revoke`)**: `src/serving/api/modules/iam/presentation/router.py:253-281` requires no Bearer JWT, API key, or `iam:admin` permission. Any caller can generate an `admin` API key (not persisted) or revoke arbitrary JWT hashes in an ephemeral in-memory `set[str]`. | Unauthenticated privilege minting and denial-of-service against valid tokens. |
| `SEC-AUDIT-003` | **CRITICAL** | **Missing Authentication & RBAC Enforcement on All Protected Endpoints**: None of the 8 module routers (`market`, `historical`, `analytics`, `catalog`, `platform_config`, `agent_api`, `reporting`, `iam`), `data_plane.py`, `gateway/service.py`, or `gateway/observability.py` use FastAPI authentication or capability dependencies (`Depends(...)`). `install_security_defense_middleware` (`iam/presentation/router.py:37-163`) checks Host header, regex WAF, and rate limits only — never JWTs or API keys. | All mutating/admin routes (`/market/ingest`, `/historical/backfill-jobs`, `/catalog/instruments/*`, `/agents/runs`, `/data-platform/v01/run`, `/data-platform/v01/compaction`, `/observability/demo/emit`, `/microservices/dispatch/*`) are publicly callable without credentials. |
| `SEC-AUDIT-004` | **HIGH** | **Client IP Spoofing & Rate-Limit / IP-Binding Bypass**: `_extract_client_ip` (`iam/presentation/router.py:28-34`) unconditionally trusts `X-Forwarded-For` / `X-Real-IP` headers from any caller (also echoed back via `X-Encrypted-Client-IP` / `X-Client-IP-Token` headers). Additionally, `PlatformConfig.jwt_secret_key` (`src/shared/config/settings.py:34`) defaults to a hardcoded string (`change_me_generate_32_byte_random_hex_secret`). | Callers connecting outside Nginx can spoof client IPs to bypass per-IP sliding-window rate limits and IP-bound JWT validation; default JWT secret allows token forgery if unset. |
| `SEC-AUDIT-005` | **MEDIUM** | **Endpoint Information Disclosure & Static Client-Side Dev Persona**: `GET /api/v1/auth/domains` and `/api/v1/health/ready` require no auth and disclose infrastructure topology/encrypted bindings; `frontend/src/services/auth/auth.service.ts:18-27` defaults unauthenticated browser sessions to a hardcoded `quant_admin` (`ADMIN`) profile. | Unnecessary reconnaissance disclosure and misleading client-side admin UI state. |

---

## 5. Audit Limitations

1. **No Live Container Execution**: Docker infrastructure containers (`postgres`, `redis`, `kafka`, `clickhouse`, `minio`, `prometheus`, `grafana`, `superset`, `edge-gateway`) were not started during this audit; container initialization SQL/shell scripts were verified by static inspection only.
2. **No Local Node.js Toolchain**: `node` and `npm` were unavailable on the host shell (`node -v` returned command not found), so frontend TypeScript compilation (`tsc && vite build`) and `node --test` execution were not run in this session.
3. **Host Python Baseline**: On commit `f0329d3`, `pytest tests/ -q` (`50 passed`), `ruff check src tests` (`All checks passed!`), and legacy `tools/validators/run_all.py` (`10/10` V1 checks passed) were verified directly before beginning Documentation V2 changes.
