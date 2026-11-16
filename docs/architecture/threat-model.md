---
doc_id: "ARCH-SEC-001"
title: "System Threat Model & Security Architecture (8 GB Greenfield Baseline)"
version: "1.0.0"
status: "IN_REVIEW"
implementation_status: "NOT_IMPLEMENTED"
owner: "Security Engineer & Backend Architect"
purpose: "Defines trust boundaries, critical assets, threat scenarios, and mandatory defense controls across ingestion, JetStream, DuckDB/SQLite storage, ML inference, and API/SPA interfaces."
scope: "Single-node Hybrid deployment and future Docker Compose profile."
dependencies:
  - "docs/product/srs.md"
  - "docs/architecture/system-architecture-document.md"
references:
  - "docs/diagrams/threat-model-diagram.md"
  - "docs/product/acceptance-criteria.md"
assumptions:
  - "No exchange private trading keys are ever configured or accepted by this read-only market intelligence platform."
open_issues:
  - "Confirm password hashing package (Argon2 vs PBKDF2-HMAC-SHA256) during Phase 3 auth contract design."
review_criteria:
  - "Zero default/bypassed admin credentials anywhere in API or frontend SPA"
  - "DuckDB queries protected against dynamic SQL injection and path traversal"
---

# Threat Model & Security Architecture

## 1. Protected Assets & Trust Boundaries

- **Assets**: (1) Local operator/researcher credentials, JWT signing key & hashed API keys, (2) Integrity of canonical Silver/Gold Parquet & point-in-time ML datasets, (3) SQLite metadata & Model Registry, (4) `8 GB` host RAM/CPU availability against DoS, (5) Methodological correctness of outputs & alerts.
- **Trust Boundaries**:
  - `TB-1` **External Internet $\rightarrow$ Ingestion Connectors**: Untrusted Binance/OKX WSS & REST payloads over TLS `443`.
  - `TB-2` **Docker Network / Host Loopback $\rightarrow$ NATS JetStream**: Localhost `127.0.0.1:4222` (never `0.0.0.0` unauthenticated).
  - `TB-3` **Browser / External Scripts $\rightarrow$ FastAPI Edge Gateway**: Untrusted HTTP/WS requests, query params, JWT/API keys.
  - `TB-4` **Worker Execution $\rightarrow$ DuckDB / Parquet / SQLite Storage**: Dynamic filter parameters & model loading.

## 2. Threat Matrix & Mandatory Controls (`THR-*`)

| Threat ID | Boundary | Attack / Failure Vector | Mitigation Control (Enforced by `AC-12`, `AC-13`, `AC-02`) |
|---|---|---|---|
| `THR-01` | `TB-3` | Authentication bypass, hardcoded JWT secret, or UI defaulting anonymous users to `ADMIN`. | Require explicit `FMDP_JWT_SECRET` generated/loaded from local secret/env (fail startup in prod mode if missing); store hashed passwords/API keys in SQLite (`verify` against stored hash); enforce `Depends(require_role(...))` on ALL protected/mutating routes; explicit login flow in UI. |
| `THR-02` | `TB-3` | Spoofed `X-Forwarded-For` evading per-IP rate limits or triggering lockout DoS. | Ignore forwarding headers unless peer socket IP matches explicit `TRUSTED_PROXY_CIDRS` list (empty by default on loopback dev). |
| `THR-03` | `TB-3` / `TB-4` | SQL injection or arbitrary local file access via analytical endpoints passed into DuckDB `read_parquet(...)`. | Strictly forbid raw user SQL (`execute_raw_sql` forbidden); bind parameterized SQL placeholders (`?`), validate `instrument_id` & date patterns via Pydantic regex, and pin Parquet globs inside configured base root via `Path.resolve().is_relative_to(...)`. |
| `THR-04` | `TB-1` | Poison exchange payload (`NaN`, negative size, crossed book, malformed JSON, huge nested JSON flood). | Bound WS frame size (`max_size`), strict Pydantic/Decimal validation, quarantine failures cleanly to `mkt.dlq.*`, never emit unvalidated records to hot cache/Silver. |
| `THR-05` | `TB-2` | Unbounded NATS JetStream exposure on LAN (`0.0.0.0:4222`) allowing spoofed market events. | Bind Docker published port strictly to `127.0.0.1:4222:4222`; enable NATS token/user authentication in container config even on localhost. |
| `THR-06` | `TB-3` | Slow-client WebSocket flood exhausting Python `asyncio` memory on `7.85 GB` host. | Hard limit max concurrent WS clients & per-client queue bounds using latest-snapshot conflation + idle ping/pong timeouts. |
| `THR-07` | `TB-4` | Arbitrary Python `pickle` deserialization executing code on Model Registry load. | Prefer safe serialization formats (`ONNX` / LightGBM text/JSON / `skops` / JSON coefficients + checksum verification) over raw untrusted `pickle` blobs. |
