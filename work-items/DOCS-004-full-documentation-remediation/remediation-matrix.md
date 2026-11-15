# Repository-Wide Remediation Matrix — `DOCS-004`

This matrix consolidates all cross-workstream defects (`Workstream A` through `Workstream D`) identified during `DOCS-004` discovery and tracks their resolution against verified repository sources (`models/`, `src/`, `frontend/`, `deploy/`, `docker-compose.yml`, and `tests/`).

See [remediation-matrix.csv](remediation-matrix.csv) for the machine-readable CSV register.

## 1. Workstream A — `DOCS-003` Completion & Technical Consistency

| ID | Domain | Verified Defect | Remediation Applied | Authoritative Source | Status |
|---|---|---|---|---|---|
| `REM-A01` | API & WebSocket Contracts | Phantom routes (`/health`, `/ws/market`, `/analytics/volatility`) & missing 33+ routes / wrong `kline` field names (`open` vs `open_price`) | Reconciled all `55` active HTTP/WS routes + `1` `PLANNED` (`API-003` `/ws/v1/market/stream`) in `models/api/api.yaml`, `api-specification.md`, `rest-contracts.md`, `ws-sse-contracts.md` | `src/serving/api/main.py` & domain routers | `FIXED_VERIFIED` |
| `REM-A02` | Events & Kafka Contracts | `EventEnvelopeV1` / `DeadLetterEnvelopeV1` examples, `EventType` enum, retention durations, and consumer group lists conflicted across models and docs | Synchronized 9-field `EventEnvelopeV1`, 7-field `DeadLetterEnvelopeV1`, 5 `EventType`s, 6 topics, and `4` active `CG_*` constants + `1` planned (`cg.agent.anomaly.v1`) | `src/shared/contracts/events/market_events.py`, `src/streaming/contracts/topics.py` | `FIXED_VERIFIED` |
| `REM-A03` | Requirements & Components | `FR-01..10` lacked `IMPLEMENTED`/`PARTIALLY_IMPLEMENTED` separation; `COMP-018..020` missing | Added runtime implementation evidence to `requirements.yaml` & `components.yaml` (`COMP-001..020`) | `src/serving/infrastructure/runtime.py`, `src/serving/api/services/` | `FIXED_VERIFIED` |
| `REM-A04` | UX & Security Reality | Stale API refs in `ux.yaml`, wrong screen route (`/ui/data-flow` vs `/data-flow`), Argon2id/RS256 claims, overstated domain RBAC | Updated `ux.yaml`, `screen-specifications.md`, `user-flows.md`, `10-security-and-governance.md` (`PBKDF2-HMAC-SHA256`, `HS256`, `PROP-APP-004`) | `frontend/src/app/router/router.ts`, `src/serving/api/modules/iam/domain/security.py` | `FIXED_VERIFIED` |
| `REM-A05` | Test Traceability & Evidence | `DOCS-003` fabricated Vitest/`App.test.tsx`; `TC-017` negative validator test missing | Reconciled `models/testing/testing.yaml` (`TC-001..017`), created `tests/unit/test_documentation_validators.py`, added `DOCS-003` addendum | `tests/**/*.py`, `frontend/package.json` (`node --test`) | `FIXED_VERIFIED` |
| `REM-A06` | Identifier Registry & Semantic Validators | `ADR-007..008` & `DIAG-COMP` missing from `identifier-registry.yaml`; validators lacked runtime/port/link semantic checks | Updated `identifier-registry.yaml`; upgraded `validate_{models,diagrams,identifiers,docs,traceability}.py` | `.agents/config/identifier-registry.yaml`, `tools/validators/` | `FIXED_VERIFIED` |

## 2. Workstream B — Architecture Baseline Reconciliation

| ID | Domain | Verified Defect | Remediation Applied | Authoritative Source | Status |
|---|---|---|---|---|---|
| `REM-B01` | Implemented vs Planned Separation | Distributed `Airflow`, `Spark`, `dbt-runner`, `GE`, and `Qdrant` containers & 6 LangGraph nodes described as active runtime | Reconciled `docs/architecture/00..14` & `models/architecture/architecture.yaml`: clearly separated `IMPLEMENTED` in-process Python engines/monolith from `PLANNED` external stack & documented 5 active vs 6 target LangGraph nodes | `src/lakehouse/`, `src/intelligence/`, `docker-compose.yml` | `FIXED_VERIFIED` |
| `REM-B02` | Service Decomposition & ADRs | Logical modules conflated with independent services; worker CLI stubs undisclosed | Updated `ADR-004`, `ADR-007`, `ADR-008`, `01-system-context.md`, `05-backend-architecture.md` with Modular Monolith + 7 opt-in `svc-*` wrappers + `gateway/service.py` + `PROP-APP-002` | `src/serving/api/main.py`, `src/serving/api/services/`, `src/ingestion/entrypoints/` | `FIXED_VERIFIED` |
| `REM-B03` | Derived Diagram Synchronization | All 22 active diagrams lacked standard `Diagram ID` + `Status` tables, showed old Prometheus targets (`backend-api:8000` only) and wrong paths (`gateway/ui.py`, `frontend/src` vs `src/`) | Synchronized `docs/diagrams/README.md` (`22` active + `12` templates = `34`) and all 22 active diagrams under `docs/diagrams/` | `models/**/*.yaml`, `deploy/observability/prometheus/prometheus.yml` | `FIXED_VERIFIED` |

## 3. Workstream C — Operations & Deployment Verification (`OPS`)

| ID | Domain | Verified Defect | Remediation Applied | Authoritative Source | Status |
|---|---|---|---|---|---|
| `REM-C01` | Compose Ports & Profiles | Host port `9000` collided between `clickhouse` and `minio` under `--profile lakehouse`; `.env.example` incomplete | Updated `docker-compose.yml` (`127.0.0.1:${MINIO_API_PORT:-9010}:9000`), synced `.env.example`, `deployment.yaml`, `12-deployment-architecture.md`, `deployment-guide.md` | `docker-compose.yml`, `.env.example` | `FIXED_VERIFIED` |
| `REM-C02` | Observability & Runbooks | Runbooks cited 11 invented metrics, 6 invented alerts, and nonexistent `/health`; `prometheus.yml` omitted `svc-data-plane-v01` | Aligned `operational-runbooks.md`, `monitoring-and-alerting.md`, `docs/product/13-operations/monitoring.md` with 10 `fmdp_*` metrics, 2 alerts, and added `svc-data-plane-v01:8007` scrape job | `src/shared/observability/metrics.py`, `deploy/observability/prometheus/alerts.yml` | `FIXED_VERIFIED` |
| `REM-C03` | Storage & Kafka Init Parity | `s3://market-data/` conflicted with `lakehouse-{bronze,silver,gold,checkpoints}` | Reconciled bucket names across storage/ops docs and logged `LAKEHOUSE_BUCKET` normalization as `PROP-APP-003` | `deploy/object-storage/init-buckets.sh`, `deploy/kafka/topics-init.sh` | `FIXED_VERIFIED` |

## 4. Workstream D — Documentation Governance & Consolidation

| ID | Domain | Verified Defect | Remediation Applied | Authoritative Source | Status |
|---|---|---|---|---|---|
| `REM-D01` | Path Integrity & Governance Counts | 18 broken internal paths and stale role (`11` vs `19`), template (`56` vs `57`), ADR (`6` vs `8`), and README (`119` vs `120`) counts | Fixed all broken refs across `docs/` and `.agents/`, synchronized governance docs (`documentation-baseline.md`, `artifact-status.md`, `decision-log.md`, `readme-coverage-matrix.md`, `unresolved-issues.md`, `validation-report.md`) | Repository filesystem & `.agents/config/` | `FIXED_VERIFIED` |
| `REM-D02` | Consolidation & Historical Audit Addenda | Conflicting authority guidance and inaccurate legacy claims in `DOCS-002` & `DOCS-003` reports; malformed literal `\n` in `DOCS-003/remediation-matrix.md` | Consolidated single portal hierarchy across `README.md`, `docs/README.md`, `docs/overview/*`; appended non-destructive correction addenda to `DOCS-002` & `DOCS-003` | `AGENTS.md`, `docs/README.md`, `work-items/` | `FIXED_VERIFIED` |
| `REM-D03` | Out-of-Scope Runtime Code Drifts | Application & frontend runtime defects require separate PRs under `Rule 1.4` | Logged `PROP-APP-001`..`PROP-APP-005` in `discovery.md` and `docs/product/14-governance/unresolved-issues.md` without modifying runtime code | Inspected `src/` & `frontend/src/` | `LOGGED_PROPOSALS` |

