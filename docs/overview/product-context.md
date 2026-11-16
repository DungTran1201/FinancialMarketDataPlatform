---
doc_id: OVR-PROD-001
title: "Platform Product Context & Scope"
doc_type: specification
plane: platform
scope_level: platform
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: business-analyst
accountable_role: business-analyst
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/main.py"
    - "frontend/src/app/router/router.ts"
    - "src/lakehouse/orchestration/pipeline.py"
    - "src/intelligence/workflows/investigation.py"
related_docs:
  - OVR-ROOT-001
  - OVR-CTX-001
  - OVR-REQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Authored evidence-based platform product context separating AS-IS implemented scope from TARGET and OPEN decisions."
---

# Platform Product Context & Scope

## 1. Product Purpose & Problem Statement `[REQUIRED]`

`FinancialMarketDataPlatform` (FMDP) is designed to unify real-time cryptocurrency market data acquisition, standardized multi-tier storage (hot cache, OLAP rollups, and Bronze/Silver/Gold medallion datasets), low-latency serving APIs, interactive observability/analytics UI screens, and bounded AI-assisted anomaly investigation into one architecturally governed platform.

**Current `AS-IS` Reality**: All 12 data pipeline stages (`DataPlatformV01Pipeline`), REST/SSE/WS endpoints (`src/serving/api/`), 6-screen browser SPA (`frontend/src/`), and 5-node `MarketIntelligenceGraph` operate in-process using in-memory brokers/stores, an embedded Binance REST ASGI simulator, local SQLite watermarks, and local disk Parquet files, while full Docker container services (`docker-compose.yml`) are wired only as infrastructure declarations (`SIMULATED` / `PARTIALLY_IMPLEMENTED`).

## 2. Intended Users & Stakeholders `[REQUIRED]`

| Persona / Role | Codebase Representation (`UserRole`) | Primary Platform Needs (`AS-IS` UI / API Access) |
|---|---|---|
| **Viewer** | `UserRole.VIEWER` (`iam/domain/ports.py:11`) | Read market prices, snapshots, order books, historical candles, quant analytics, and generated reports. |
| **Quantitative Analyst** | `UserRole.ANALYST` (`iam/domain/ports.py:12`) | All Viewer reads plus triggering on-demand AI market anomaly investigations (`agent:trigger`). |
| **Platform Operator / DataOps** | `UserRole.OPERATOR` (`iam/domain/ports.py:13`) | Manage monitored instruments, trigger backfill/compaction/demo pipelines, and monitor consumer lag, E2E traces, and storage health. |
| **Platform Administrator** | `UserRole.ADMIN` (`iam/domain/ports.py:14`) | Full operator capabilities plus API key management and security governance (`iam:admin`, *currently un-enforced at router level*). |
| **Service Principal / Bot** | `UserRole.SERVICE` (`iam/domain/ports.py:15`) | Programmatic API ingestion/polling (**Gap**: `ROLE_CAPABILITIES` omits `UserRole.SERVICE` in `ports.py:18-44`). |

## 3. Product Boundaries & Supported Workflows `[REQUIRED]`

### 3.1 In-Scope Workflows (Observed in Code & Frontend)
1. **Market Data Acquisition & Normalization**: Normalize Binance Spot `trade`, `kline`, `24hrTicker`, and `depth20` frames into deterministic `EventEnvelopeV1` records (routing malformed records to DLQ) plus paginated REST historical kline backfill and gap healing (`src/ingestion/`).
2. **Real-Time Projection & Anomaly Detection**: Maintain monotonic latest price/24h snapshot/order book views, OHLCV rollups, Pearson correlation & log-return realized volatility, and rolling z-score anomaly detection with cooldown suppression (`src/streaming/`).
3. **Medallion Lakehouse & Data Governance**: Archive raw Bronze Parquet, execute natural-key Silver deduplication with custom Iceberg v2 manifests, block bad data via DQ gates, and compute Gold Decimal marts + 12-node lineage (`src/lakehouse/`).
4. **Experience & Observability SPA (`frontend/`)**: 6 screens covering Overview Dashboard, Data Flow Observatory (12-stage DAG + live SSE traces), Market Analytics (Candlestick canvas + Order Book + Quant), Data Management (Dataset Registry + DQ + Lineage), AI Workspace, and Administration.
5. **Bounded Intelligence Workflow**: Execute 5-node investigation graphs via a 10-tool whitelisted `ControlledToolGateway` and validate provenance citations against executed tool invocations (`src/intelligence/`).

### 3.2 Out-of-Scope Responsibilities
- Live order routing, trade execution, custody, fiat rails, portfolio accounting, or brokerage clearing (`OUT_OF_SCOPE` everywhere in codebase).
- Automated production trading decisions without human review.
- Unaudited free-form SQL execution by LLMs (`execute_raw_sql` explicitly blocked by `ControlledToolGateway`).
- `[OPEN]` Multi-exchange live WebSocket support beyond Binance (`notebooks/workers/coinbase_worker.py` exists only as an unreferenced prototype).

## 4. Known Limitations & Unresolved Product Decisions

| ID | Category | Current Gap / Question | Impact | Owner | Status |
|---|---|---|---|---|---|
| `OPEN-PROD-001` | Target Scope | Confirm whether Coinbase/Kraken live connectors belong in release scope beyond Binance (`notebooks/` prototypes exist; `src/` supports `binance` only). | Ingestion domain backlog & connector roadmap. | `business-analyst` | `OPEN` |
| `OPEN-PROD-002` | Security Release Blocker | Critical IAM flaws `SEC-AUDIT-001`..`005` allow unauthenticated admin JWT minting and unprotected endpoints (`iam/presentation/router.py`). | Blocks any multi-user or external deployment. | `security-architect` | `BLOCKED` |
| `OPEN-PROD-003` | Live Infrastructure | Containerized workers (`collector-ws`, `collector-rest`, `consumer-*`, `agent-worker`) are exit-immediately stubs; Compose uses simulated fallback in `backend-api`. | Production persistence & continuous live ingestion not operational. | `data-architect` / `system-architect` | `OPEN` |
| `ASSUMP-PROD-001` | UI Auth Alignment | `[ASSUMPTION]` Frontend currently defaults browser sessions to `quant_admin` with no login screen (`auth.service.ts:18-27`); assumes target release requires real login screen + RBAC route guards before exposure. | UX & IAM capability design. | `business-analyst` | `[ASSUMPTION]` |
