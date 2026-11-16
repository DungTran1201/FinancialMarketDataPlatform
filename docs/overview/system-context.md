---
doc_id: OVR-CTX-001
title: "Platform System Context & External Boundaries"
doc_type: specification
plane: platform
scope_level: platform
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: system-architect
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docker-compose.yml"
    - "deploy/nginx/nginx.conf"
    - "src/shared/config/settings.py"
    - "src/ingestion/providers/binance/rest_client.py"
related_docs:
  - OVR-ROOT-001
  - OVR-PROD-001
  - OVR-DIAG-CTX-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: system-architect
    summary: "Documented platform system context, actors, external integrations, trust boundaries, and container ports from verified runtime configs."
---

# Platform System Context & External Boundaries

Derived visual view: [system-context.md](diagrams/system-context.md) (`DIAG-OVR-CTX-001`).

## 1. System Boundary `[REQUIRED]`

`FinancialMarketDataPlatform` encloses three architectural Planes inside the runtime host/Docker boundary (`frontend`, `edge-gateway`, `backend-api` monolith or 7 domain ASGI workers, internal Python data/intelligence engines, and declared stateful stores: `kafka`, `redis`, `clickhouse`, `postgres`, `minio`, `prometheus`, `grafana`, `superset`).

## 2. Human Actors & External Consumers `[REQUIRED]`

| Actor | Role / Type | Protocol & Entry Point (`AS-IS` vs `TARGET`) | Purpose |
|---|---|---|---|
| **Market Data End User / Analyst / Admin** | Human Browser User | `AS-IS`: Vite HTTP `:3000` or Docker `frontend` `:3001` (`deploy/nginx/nginx.conf` `:80->:443` HTTPS `fmdp.local`). API calls proxied via `/api/*` & `/ws/*`. | Monitor pipeline telemetry, charts, orderbooks, datasets, AI reports & API keys. |
| **Quant / API Client / Bot** | External Consumer / Operator | `HTTP/1.1` REST (`:8000` / `:443`) + SSE (`/api/v1/observability/stream`) + WebSocket (`/ws/v1/observability/stream`). | Programmatic queries, backfill triggers, ingestion injection, AI run triggers. |

## 3. External Upstream Providers & Infrastructure Systems `[REQUIRED]`

| External System | Protocol & Endpoint Config | Direction | `AS-IS` Integration Reality (`7880c85`) |
|---|---|---|---|
| **Binance Spot REST API** | `HTTPS` (`https://api.binance.com/api/v3/exchangeInfo`, `/klines`, configured via `BINANCE_REST_BASE_URL`) | Inbound Pull | `ProductionExchangeHistoricalCollector` defaults to `use_embedded_asgi_transport=True` (in-memory FastAPI ASGI simulator). Real `httpx` client exists only if toggled `False`. |
| **Binance Spot WebSocket** | `WSS` (`wss://stream.binance.com:9443/ws`, `BINANCE_WS_BASE_URL`) | Inbound Push (Target) | `NOT_IMPLEMENTED` in `src/` (`collector-ws` entrypoint exits immediately; `ws_service.py` accepts caller-injected frames only). |
| **External LLM Provider** | Target `LLM_PROVIDER` (`gpt-4o-mini` in `.env.example:89`) | Outbound HTTPS (Target) | `NOT_IMPLEMENTED` (`DeterministicMockLLMAdapter` only; `LLM_API_KEY` empty in `.env.example`). |
| **Local Stateful Infrastructure Stack** | Kafka `:9092`, Redis `:6379`, ClickHouse `:8123`/`:9000`, Postgres `:5432`, MinIO `:9000`/`:9001`, Prometheus `:9090`, Grafana `:3000`, Superset `:8088` | Internal Stores | Declared in `docker-compose.yml` across `core`/`lakehouse`/`intelligence`/`observability`/`bi` profiles; runtime uses in-memory/SQLite/local-disk simulations rather than live external client calls. |

## 4. Trust Boundaries

1. **TB-1 (Public Edge -> Nginx / API Gateway)**: Untrusted external HTTP/WS traffic crosses Nginx (`nginx.conf:53-189`, TLSv1.2/1.3, rate limits `120r/m`/`10r/m`) into FastAPI `defense_in_depth_middleware`. **Gap**: `SEC-AUDIT-003` & `004` show unauthenticated API endpoints and unconditional trust in `X-Forwarded-For`.
2. **TB-2 (Upstream Exchange -> Ingestion Normalizer)**: Untrusted market payloads validated strictly by `BinancePayloadNormalizer` (`Decimal`, finite non-negative checks, UTC timestamps); malformed payloads quarantined to `market.dlq.v1`.
3. **TB-3 (AI Agent -> Data & Control Stores)**: Orchestrator cannot query stores or run raw SQL directly; all data access crosses `ControlledToolGateway` (`APPROVED_TOOL_POLICIES` RBAC + row/timeout bounds).
4. **TB-4 (Control Plane -> Local Storage / Target DBs)**: SQLite `.local_storage/control_watermarks.db` and `.local_lakehouse/` filesystem writes execute under container process user (`nobody` in `Dockerfile.python`).
