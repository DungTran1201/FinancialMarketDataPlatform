---
doc_id: CAP-APP-OPS-NFR-001
title: "Non-Functional Requirements: Observability, Control & Gateway"
doc_type: specification
plane: application-plane
scope_level: capability
domain: platform-operations-and-control
capability_id: CAP-APP-OPS-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: devops-sre
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/gateway/observability.py"
    - "src/serving/infrastructure/runtime.py"
related_docs:
  - CAP-APP-OPS-REQ-001
  - APP-OPS-SLO-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Documented SSE/WS heartbeat cadence, non-blocking TCP probes, and unestablished SLO targets."
---

# Non-Functional Requirements: Observability, Control & Gateway

## 1. Stream Cadence & Probe Safety (`AS-IS`)

- **Heartbeat Intervals**: SSE `/stream` emits heartbeats on `2.5s` queue timeout; WebSocket `/ws/v1/observability/stream` emits heartbeats every `3.0s`.
- **Non-Blocking Probes**: `probe_external_infrastructure()` runs concurrent asyncio TCP checks across Kafka, Redis, ClickHouse, MinIO, and Postgres with 5s TTL caching; `fetch_live_binance_market_data` caps `limit` at `50` and httpx timeout at `3.5s`.
- **Subscription Cleanup**: Both SSE and WS handlers unsubscribe `sub_id` in `finally:` blocks to avoid subscriber queue leaks.

## 2. Target Fan-Out & Latency SLOs (`OPEN`)

- Maximum concurrent WebSocket/SSE client limits and REST `/overview` p95 latency targets remain **`OPEN`** (`APP-OPS-SLO-001`).
