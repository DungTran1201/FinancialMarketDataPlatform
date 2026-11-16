---
doc_id: APP-ARCH-API-001
title: "API & Integration Architecture (REST, SSE & WebSocket)"
doc_type: architecture
plane: application-plane
scope_level: plane
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/main.py"
    - "src/serving/api/gateway/observability.py"
    - "frontend/src/services/api/client.ts"
related_docs:
  - APP-ARCH-ROOT-001
  - APP-ARCH-COMPAT-001
  - APP-ERR-SHARED-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Documented API envelope patterns, streaming transports, pagination limits, and rate-limiting tiers."
---

# API & Integration Architecture (REST, SSE & WebSocket)

## 1. Scope, Context & Envelope Divergence Across Routers

1. **Module Envelope (`{ "data": ..., "meta": ... }`)**: Used by `/api/v1/auth`, `/market`, `/historical`, `/analytics`, `/catalog`, `/platform`, `/agents`, and `/reports`.
2. **Flat JSON Envelope (No `data`/`meta` Wrapper)**: Used by `/api/v1/observability/*`, `/api/v1/data-platform/v01/*`, `/api/v1/microservices/*`, and `/api/v1/health/*`. Frontend `client.ts` contains custom branching to unwrap `{ data }` when present without hiding flat telemetry objects.
3. **Decimal Wire Serialization**: Price, volume, VWAP, and volatility values are serialized as strings (`"89500.00"`) inside REST module payloads to avoid IEEE-754 rounding, except `get_observability_candles()` which emits both numeric floats (`open/high/low/close/volume`) for UI charts and exact string duplicates (`open_str`, `high_str`, `low_str`, `close_str`).

## 2. Building Blocks: Streaming Transports & Rate Limiting

- **SSE (`GET /api/v1/observability/stream`)**: Emits `event: snapshot`, `event: trace` (pushed via `trace_registry.subscribe`), and `event: heartbeat` every `2.5s` on queue timeout.
- **SSE (`GET /api/v1/agents/runs/{run_id}/events`)**: Replays finished `evidence_trail` entries as `event: tool_invocation` followed by `event: run_completed` (non-blocking replay because runs finish synchronously on `POST`).
- **WebSocket (`WS /ws/v1/observability/stream`)**: Pushes initial `snapshot`, live `trace` frames, `3.0s` `heartbeat`, and responds to `{ "type": "ping" }` with `{ "type": "pong" }`.
- **Middleware Rate-Limit Tiers (`src/shared/security/primitives.py`)**: `AUTH=10`, `AGENT_TRIGGER=5`, `HEAVY_ANALYTICS=30`, `MARKET_READ=120` req/min per SHA-256 HMAC client IP token (`X-Forwarded-For` trusted blindly without reverse-proxy allowlist).
