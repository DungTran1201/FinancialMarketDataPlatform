# Change Request — `DOCS-004`

- **Work Item ID**: `DOCS-004`
- **Title**: Full Repository Documentation Remediation, Architecture Reconciliation, Operational Verification & Governance Consolidation
- **Type**: `DOCS` (Consolidated Master Remediation covering Workstreams A–D: `DOCS-003` completion, Architecture Baseline Reconciliation, Operations Verification, and Documentation Governance)
- **Risk Tier**: `R2` (Cross-Subsystem Architecture, Models, Contracts, Operations, Diagrams & Validator Tooling)
- **Requested Date**: `2026-11-15`
- **Predecessor Work Items Preserved**: `DOCS-001`, `DATA-001`, `ARCH-001`, `FEAT-001`, `FEAT-002`, `DOCS-002` (superseded/corrected via addendum), `DOCS-003` (completed/superseded via addendum)

## Problem Statement

An independent audit of `FinancialMarketDataPlatform` on branch `docs/DOCS-003-consistency-remediation` (baseline commit `c954d32f33dcc6b4200804662b4bdae2b3a3ddbd`) established that while `DOCS-002` and `DOCS-003` claimed completion, substantial structural and semantic inconsistencies remain across the documentation system:
1. Planned technologies (Spark, dbt orchestrator containers, Great Expectations, Airflow daemon, live LLM SDK calls, `WS /ws/v1/market/stream`) are presented in architecture docs, specifications, and diagrams as live runtime containers or implemented endpoints.
2. API contracts omit implemented FastAPI endpoints (33+ of 55 monolith routes), document non-existent routes/fields, and fail to disclose frontend-backend endpoint drift.
3. Event schemas, Kafka consumer group reality (`4` active in-process/contracted CGs + `cg.dlq.inspector.v1` trace label vs `1` planned `cg.agent.anomaly.v1`), Prometheus `fmdp_*` metrics, PBKDF2/HS256 security algorithms, and `lakehouse-*` MinIO bucket names conflict across code, models, docs, and runbooks.
4. `docker-compose.yml` has a verified host port `9000` collision between `clickhouse` and `minio` in `--profile lakehouse`, `.env.example` omits Compose variables, and operational runbooks cite nonexistent `/health` and mismatched Grafana/frontend ports.
5. Governance docs (`docs/product/14-governance/`, `docs/templates/`, `docs/contracts/`, `.agents/`) carry outdated baseline counts (`11` roles vs `19`, `56` templates vs `57`, `16` diagrams vs `22` active, `ADR-001..006` vs `ADR-001..008`), 18 broken internal path references, and legacy `DOCS-002`/`DOCS-003` validation claims without independent verification evidence.

## Program Scope & Non-Negotiable Constraints

- Unified execution across **Workstream A** (`DOCS-003` Technical Consistency), **Workstream B** (Architecture Baseline Reconciliation), **Workstream C** (Operations & Deployment Verification), and **Workstream D** (Governance & Consolidation).
- **Runtime Code Safety**: Do NOT modify `src/` or `frontend/` runtime business logic. Only minimal, configuration-focused, documented, and regression-tested fixes to `docker-compose.yml`/`.env.example` are permitted where a verified configuration defect blocks valid topology.
- **Identifier & History Preservation**: Preserve all existing IDs (`FR-01..10`, `ADR-001..008`, `CAP-*`, `NFR-*`, `BR-*`, `AC-*`, `COMP-*`, `DOM-*`, `API-*`, `TC-*`, `DIAG-*`, etc.) and preserve Git history and predecessor work-item directories.

