---
doc_id: OVR-REQ-001
title: "Platform System-Wide Requirements Index (BR / FR / NFR / CON / SEC / OPS)"
doc_type: specification
plane: platform
scope_level: platform
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: business-analyst
accountable_role: business-analyst
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/overview/system-requirements.md"
related_docs:
  - OVR-ROOT-001
  - OVR-PROD-001
  - OVR-ARCH-3P-001
requirement_ids:
  - BR-SYS-001
  - BR-SYS-002
  - BR-SYS-003
  - FR-SYS-001
  - FR-SYS-002
  - FR-SYS-003
  - FR-SYS-004
  - NFR-SYS-001
  - NFR-SYS-002
  - CON-SYS-001
  - CON-SYS-002
  - SEC-SYS-001
  - SEC-SYS-002
  - OPS-SYS-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Defined system-level requirements partitioned cleanly by owning plane without duplicating capability specs; kept SLA targets OPEN pending sign-off."
---

# Platform System-Wide Requirements Index

This document defines **platform-wide** requirements (`*-SYS-*`). Individual atomic functional and operational specifications live inside the owning Plane and Capability directories.

## 1. System Business Requirements (`BR-SYS-*`)

| Req ID | Business Need Summary | Owning Plane(s) | Priority | Status |
|---|---|---|---|---|
| `BR-SYS-001` | Provide continuous, auditable crypto spot market data ingestion, hot state, and historical OLAP/lakehouse datasets with deterministic financial precision (`Decimal`). | `data-plane` | `MUST_HAVE (P0)` | `DRAFT` (`OPEN`: live exchange cutover schedule) |
| `BR-SYS-002` | Deliver low-friction interactive API and web experience for market queries, pipeline observability telemetry, data catalog inspection, and access control. | `application-plane` | `MUST_HAVE (P0)` | `DRAFT` (`BLOCKED`: IAM remediation `SEC-AUDIT-001..003`) |
| `BR-SYS-003` | Enable grounded, RBAC-governed AI anomaly investigation reports with verifiable provenance citations and zero prompt arithmetic or direct SQL execution. | `intelligence-plane` | `SHOULD_HAVE (P1)` | `DRAFT` (`OPEN`: external LLM provider decision) |

## 2. System Functional Index (`FR-SYS-*` — Traces to Plane/Capability Specs)

| Req ID | Cross-Plane Behavior Summary | Primary Owner Capability | Verification Method |
|---|---|---|---|
| `FR-SYS-001` | System acquires exchange trade/kline/ticker/orderbook data, validates financial invariants, routes invalid records to `market.dlq.v1`, and maintains monotonic hot + OLAP + lakehouse tiers. | `CAP-DP-ING-001`, `CAP-DP-STR-001`, `CAP-DP-STR-002`, `CAP-DP-LAK-001` | Test (`resilience`, `data_quality`, `e2e`) |
| `FR-SYS-002` | System exposes REST/SSE/WS endpoints for market quotes/candles/analytics, catalog/pipeline controls, observability streams, and SPA views. | `CAP-APP-MKT-001`, `CAP-APP-CAT-001`, `CAP-APP-OPS-001` | Test (`integration`, `e2e`) |
| `FR-SYS-003` | System authenticates users/bots (`POST /auth/token`, API keys), authorizes requests against RBAC capabilities, and defends edges against host spoofing, WAF payloads, and bursts. | `CAP-APP-IAM-001` | Test + Security Audit (`test_security_and_defense.py`) |
| `FR-SYS-004` | System executes bounded 5-node investigation workflows on demand or on anomaly alerts using whitelisted deterministic tools and validates every report citation. | `CAP-INT-ORC-001`, `CAP-APP-AGT-001` | Test (`test_three_planes_framework.py`) |

## 3. System Constraints (`CON-SYS-*`)

| Constraint ID | Description | Source Authority | Enforcement |
|---|---|---|---|
| `CON-SYS-001` | Domain layers (`*/domain/*.py`) MUST maintain zero framework/database driver imports, and subsystem imports MUST follow the approved DAG. | `tests/architecture/test_clean_architecture_boundaries.py` | Automated AST test (`PASS`) |
| `CON-SYS-002` | Monetary prices, volumes, and financial analytics MUST use fixed-point `Decimal` representations (`Decimal128(18)` / `DecimalPrice`), never binary floats for stored prices/balances. | `src/shared/domain/primitives.py:60`, `deploy/clickhouse/init/01_schema.sql` | Unit/DQ tests (`PASS`) |

## 4. Cross-Plane NFRs, Security & Operational Targets (`NFR-SYS-*`, `SEC-SYS-*`, `OPS-SYS-*`)

> **No Fabricated Targets**: Unapproved SLA latency, throughput, availability %, RTO, and RPO targets remain explicitly `OPEN` below.

| Req ID | Quality Area | Target / Policy | Current Verified Reality (`AS-IS`) | Owner & Status |
|---|---|---|---|---|
| `NFR-SYS-001` | **Hot Serving Latency & Availability** | Target p95 / availability % `[OPEN: stakeholder SLA approval required]`. | In-process 100-bot swarm (600 API calls) recorded JSON latency summary without container backends (`test_100_bots_data_plane_swarm.py`). | `devops-sre` (`OPEN`) |
| `NFR-SYS-002` | **Timestamp Precision & TZ** | All persisted timestamps and query time bounds MUST be timezone-aware UTC (`DateTime64(3, 'UTC')` / `TIMESTAMPTZ`). | Enforced on `EventEnvelopeV1` & `BoundedTimeRange`; `DeadLetterEnvelopeV1.failed_at` has static import-time default (`GAP`). | `data-architect` (`PARTIAL`) |
| `SEC-SYS-001` | **Endpoint Authentication & RBAC** | Every protected HTTP/WS operation MUST validate JWT or persisted API key and enforce least-privilege RBAC capabilities. | **FAILING GAP (`SEC-AUDIT-001..003`)**: zero router auth dependencies; `/auth/token` self-verifies password. | `security-architect` (`BLOCKED`) |
| `SEC-SYS-002` | **Confidentiality & Edge Defense** | Secrets (`JWT_SECRET_KEY`, DB/Redis passwords) MUST NOT use hardcoded defaults outside tests; trusted proxy headers ONLY from allowlisted CIDRs. | **FAILING GAP (`SEC-AUDIT-004`)**: default secret in `settings.py:34` and unconditional `X-Forwarded-For` trust. | `security-architect` (`BLOCKED`) |
| `OPS-SYS-001` | **Backup, Recovery & Alerting** | RPO / RTO `[OPEN]`; Prometheus scrape `15s` + DLQ/Lag alerts (`alerts.yml`); bounded Prometheus labels (no `event_id`/`request_id`). | Prometheus metric cardinality discipline verified (`test_realtime_observability_dashboard.py`); Grafana datasource not mounted in Compose. | `devops-sre` (`OPEN`) |
