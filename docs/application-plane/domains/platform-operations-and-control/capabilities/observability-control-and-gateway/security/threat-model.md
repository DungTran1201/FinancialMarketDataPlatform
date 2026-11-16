---
doc_id: CAP-APP-OPS-TM-001
title: "Threat Model: Observability, Control & Gateway"
doc_type: specification
plane: application-plane
scope_level: capability
domain: platform-operations-and-control
capability_id: CAP-APP-OPS-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: security-architect
accountable_role: devops-sre
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/gateway/observability.py"
    - "src/serving/api/gateway/service.py"
    - "src/serving/api/services/data_plane.py"
related_docs:
  - CAP-APP-OPS-SEC-001
  - DIAG-APP-OPS-TM-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Evaluated unauthenticated compute exhaustion, SSRF/Binance egress trigger, internal dispatch abuse, and stream exhaustion."
---

# Threat Model: Observability, Control & Gateway

Derived threat diagram: [threat-model-diagram.md](threat-model-diagram.md) (`DIAG-APP-OPS-TM-001`).

## 1. Assets, Entry Points & Trust Boundaries

- **Assets**: Runtime compute/memory, downstream `svc-*` microservice endpoints, outbound internet egress (`api.binance.com`), Lakehouse Silver/Gold storage, and SSE/WS telemetry streams.
- **Entry Points**: Public FastAPI endpoints (`POST /observability/demo/emit`, `POST /live/probe`, `POST /data-platform/v01/run`, `POST /microservices/dispatch/{id}`, `WS /ws/v1/observability/stream`) plus unauthenticated `GET /platform/config` and `/metrics`.
- **Trust Boundaries**: Untrusted API/WebSocket callers <-> FastAPI Gateway (`:8000`) <-> `PlatformRuntimeContainer` / `MicroserviceRegistry` / Binance HTTPS.

## 2. Threat Scenarios & `AS-IS` Risk Assessment

| Threat ID | Scenario | Severity | `AS-IS` Mitigations & Gaps | Residual Risk |
|---|---|---|---|---|
| `THR-OPS-001` | **Unauthenticated Pipeline & Simulation DoS**: Caller loops `POST /data-platform/v01/run` or `/demo/emit?action=run_full_pipeline` saturating asyncio loop and disk Lakehouse Parquet writes. | `CRITICAL` | Zero JWT/RBAC guards (`SEC-AUDIT-003`); rate limiter maps `/observability` & `/data-platform` to permissive `MARKET_READ` (`120`/min) or default tier! | `CRITICAL` (`BLOCKED`) |
| `THR-OPS-002` | **Internal ASGI Dispatch Abuse**: Attacker calls `POST /api/v1/microservices/dispatch/svc-iam-security` with arbitrary `path` and JSON body bypassing external gateway middleware checks. | `HIGH` | Zero auth and zero path allowlist on internal dispatch target. | `HIGH` (`BLOCKED`) |
| `THR-OPS-003` | **Outbound Binance Probe Abuse**: Unauthenticated caller triggers `POST /observability/live/probe` with `fetch_binance=true` repeatedly draining rate limits or probing host network latency. | `MEDIUM` | Capped `limit=50`, `3.5s` timeout; zero auth guard. | `MEDIUM` (`OPEN`) |
| `THR-OPS-004` | **Unauthenticated WS / SSE Connection Exhaustion**: Flooding open connections fills `trace_registry` subscriber lists. | `MEDIUM` | `finally` cleanup present; no max-connection limit or Bearer handshake check. | `MEDIUM` (`OPEN`) |
