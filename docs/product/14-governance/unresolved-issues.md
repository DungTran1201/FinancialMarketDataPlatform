# Unresolved Issues, Assumptions & Deferred Scope Register (`GOV-OQ-001`)

| Document Metadata | Value |
|---|---|
| **Document ID** | `GOV-OQ-001` |
| **Title** | Unresolved Questions & Deferred Product Scope Register |
| **Version** | `1.0.0` |
| **Status** | `BASELINED` |
| **Authoring Role** | `discovery-analyst` |
| **Review Role** | `documentation-auditor` |
| **Created Date** | `2026-11-12` |
| **Updated Date** | `2026-11-15` |
| **Work Item Reference** | `work-items/DOCS-001-documentation-engineering-foundation/` (extended by `DOCS-004`) |

---

## 1. Deferred Scope & Open Questions (`OPEN QUESTION`)

| ID | Category | Description | Status | Resolution Path |
|---|---|---|---|---|
| `OQ-001` | Website & Frontend Product Scope | Core operational observatory & workspace modules are realized in `FEAT-002` (`frontend/` TypeScript + Vite SPA, `SCR-002`..`SCR-007`); broader external retail web/auth workflows (`WEB-UC-###`, public user registration) remain outside the current Phase 0/v0.1 baseline. | `PARTIALLY_RESOLVED` | `FEAT-002` covers internal SPA (`SCR-002`..`SCR-007`); future external web scope requires explicit product initiation under `.agents/skills/project-discovery/SKILL.md`. |
| `OQ-002` | Production Empirical Benchmarks | Tier-1 / Tier-2 ClickHouse + Kafka disk contention and LLM token cost baselines require live container benchmark execution during Phase 1–5 implementation (`UNVERIFIED_UNDER_PRODUCTION_LOAD`). | `OPEN` | Tracked in `docs/specifications/non-functional-requirements.md` Section 6. |

---

## 2. Tracked Runtime Application Engineering Proposals (Out of Docs Scope per `DOCS-004` Rule 1.4)

| Proposal ID | Category | Verified Evidence & Drift Summary | Status | Recommended Resolution Path |
|---|---|---|---|---|
| `PROP-APP-001` | Frontend API Path Alignment | Client calls in `frontend/src/services/` (`/market/price`, `/historical/klines` query params, `/analytics/volatility`, `/catalog/datasets`, `GET /api/v1/agents/runs`, `GET /auth/api-keys`, `POST /observability/stream/control`) diverge from live FastAPI routes (`/api/v1/market/prices/{symbol}`, `/api/v1/historical/klines/{symbol}`, `/api/v1/analytics/statistics/{symbol}`, `/api/v1/data-platform/v01/lineage`, `/api/v1/catalog/instruments`, `POST /api/v1/agents/runs`, `POST /api/v1/auth/api-keys`). | `PROPOSED_SEPARATE_PR` | Align `frontend/src/services/` clients (or add backend compatibility routers) in an application PR (`FEAT`). |
| `PROP-APP-002` | Standalone Worker CLI Entrypoints | Worker scripts (`ws_collector.py`, `rest_backfill.py`, `hot_redis.py:main`, `analytics_ch.py:main`, `bronze/consumer.py`, `intelligence/main.py`) are CLI config-logging stubs; actual active runtime execution runs in-process inside `backend-api` and `svc-data-plane-v01`. | `PROPOSED_SEPARATE_PR` | Wire standalone worker entrypoints into continuous Kafka/WebSocket consumer loops when running distributed workers. |
| `PROP-APP-003` | Lakehouse Bucket Env Normalization | Legacy `LAKEHOUSE_BUCKET=market-data` env var in `.env.example` coexists with the 4 `lakehouse-{bronze,silver,gold,checkpoints}` buckets provisioned by `deploy/object-storage/init-buckets.sh`. | `PROPOSED_SEPARATE_PR` | Consolidate `.env` and storage configuration exclusively around the 4 medallion bucket variables (`lakehouse-bronze`, `lakehouse-silver`, `lakehouse-gold`, `lakehouse-checkpoints`). |
| `PROP-APP-004` | Non-IAM Route Auth/RBAC Enforcement | `/api/v1/auth/*` (`IAM`) implements `PBKDF2-HMAC-SHA256` & `HS256` HMAC JWT/API tokens and `ControlledToolGateway` enforces agent RBAC, but non-IAM domain routers (`market`, `historical`, `analytics`, `catalog`, `platform`, `agents/runs`, `reports`, `data-platform/v01`, `observability`) lack route-level JWT/RBAC `Depends(...)` guards (`runtime_rbac_enforced: false`). | `PROPOSED_SEPARATE_PR` | Enforce FastAPI authentication and scope dependencies across all domain routers before external deployment. |
| `PROP-APP-005` | Agent Node Parity & Stream Subscriptions | `MarketIntelligenceGraph` currently runs 5 nodes (`ADR-006`) vs 6 target nodes (`ADR-007`), `cg.agent.anomaly.v1` is not wired in `src/intelligence/main.py`, and `WS /ws/v1/market/stream` remains `PLANNED` alongside active `WS /ws/v1/observability/stream`. | `PROPOSED_SEPARATE_PR` | Decide 5- vs 6-node target, wire `cg.agent.anomaly.v1` consumer, and implement or retire `/ws/v1/market/stream`. |
