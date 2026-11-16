---
doc_id: OVR-ARCH-QA-001
title: "Platform Quality Attributes, Constraints & Open NFR Targets"
doc_type: specification
plane: platform
scope_level: platform
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: system-architect
accountable_role: devops-sre
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "tests/architecture/test_clean_architecture_boundaries.py"
    - "deploy/observability/prometheus/alerts.yml"
    - "src/shared/security/primitives.py"
related_docs:
  - OVR-ROOT-001
  - OVR-REQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: system-architect
    summary: "Mapped ISO 25010 quality attributes to verified mechanisms, unresolved SLA targets, and operational trade-offs."
---

# Platform Quality Attributes, Constraints & Open NFR Targets

## 1. Architectural Quality Scope `[REQUIRED]`

Evaluates system-wide quality characteristics grounded strictly in verified code (`7880c85`). Missing numeric SLA commitments are logged as `OPEN` rather than fabricated.

## 2. Quality Attribute Analysis `[REQUIRED]`

| Quality Attribute | Verified Code / Config Mechanism (`AS-IS`) | Measured / Test Evidence Scope | Unresolved Target / Gap (`OPEN` / `BLOCKED`) |
|---|---|---|---|
| **Functional Suitability & Precision** | `DecimalPrice`, `Decimal128(18)` ClickHouse DDL, deterministic quant math (`quant.py`), UUIDv5 `event_id`s, `DataQualityGateEngine` blocking rules. | Verified in-process (`unit`, `data_quality`, `e2e`). | Live ClickHouse/dbt numeric parity unverified (`GAP-DATA-001`). |
| **Performance Efficiency** | In-process hot dicts / Redis Lua upsert (`volatile-lru`, `256mb` in Compose), `5000`-row ClickHouse buffer (`flush_interval_ms` unimplemented), `2000`-item bounded trace `deque`. | `test_100_bots_data_plane_swarm.py` executed 600 in-process HTTP calls; does not assert latency SLA in test code. | Target p50/p95 API latency, throughput eps & staleness SLA targets remain `OPEN` (legacy docs conflicted; unapproved). |
| **Compatibility & Modularity** | Strict AST package DAG (`test_clean_architecture_boundaries.py`); decoupled AsyncAPI/OpenAPI contracts; `VITE_API_TARGET` proxy env support. | `3` AST architecture boundary tests pass. | Frontend/IAM API key routes (`GET`/`DELETE`) mismatch backend (`GAP-FE-001`). |
| **Reliability & Recoverability** | `SequenceAndGapDetector` + auto-backfill (`ws_service.py`), atomic `.tmp` + `replace()` Parquet writes, DLQ isolation (`market.dlq.v1`), `SlidingWindowRateLimiter`, 900s anomaly cooldown. | Verified in-memory & local disk (`resilience`, `e2e`). | Broker 2/3 unavailable (single KRaft node); zero live crash/restart/backup/restore drills; RTO & RPO targets `OPEN`. |
| **Security & Integrity** | AES-256-GCM IP/endpoint encryption, HMAC-SHA256 IP hash, PBKDF2 (`210,000` iters), path/query regex WAF, HSTS/CSP headers, Nginx TLS 1.2/1.3. | `unit/test_security_and_defense.py` exercises primitives & test routes. | **CRITICAL `BLOCKED`**: `SEC-AUDIT-001`..`005` bypass credential check & leave all protected endpoints unauthenticated. |
| **Maintainability & Operability** | Bounded Prometheus labels, `alerts.yml` (`DLQ > 10/5m`, `Lag > 5000/2m`), trace `t0`–`t9` UI observatory, Documentation V2 schemas/validator. | `test_realtime_observability_dashboard.py` passes in-process. | No Compose `resources.limits`; Grafana datasource not mounted; Superset unconfigured (`GAP-OPS-001`). |
