---
doc_id: CAP-APP-OPS-RULE-001
title: "Business Rules: Observability, Control & Gateway"
doc_type: specification
plane: application-plane
scope_level: capability
domain: platform-operations-and-control
capability_id: CAP-APP-OPS-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: devops-sre
accountable_role: fullstack-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/infrastructure/runtime.py"
    - "src/serving/api/gateway/observability.py"
related_docs:
  - CAP-APP-OPS-REQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Documented honest Kafka broker accounting rule, TCP probe TTL cache, and candle policy."
---

# Business Rules: Observability, Control & Gateway

## 1. Enforced Telemetry Honesty & Bounds Rules (`AS-IS`)

- **`RULE-OPS-001` (Single-Node KRaft Broker Honesty)**: `probe_external_infrastructure()` MUST report only Broker 1 active (`LIVE_CONTAINER` or `IN_PROCESS_ACTIVE`) and explicitly report Brokers 2 & 3 as `UNAVAILABLE` matching `docker-compose.yml` (`runtime.py:710-739`).
- **`RULE-OPS-002` (No Fake Candles Policy)**: `/api/v1/observability/candles` emits stored/rolled-up ClickHouse bars only (`no_fake_candles_policy: true`) and never fabricates synthetic candles when empty (`runtime.py:1483,1522`).
- **`RULE-OPS-003` (Bounded Probe Cache & Simulation Sizes)**: `probe_external_infrastructure()` caches TCP probe checks for `5.0s` (`force=True` bypasses cache); `/demo/emit` bounds `count` between `1..25`.

## 2. Unmet Constraints (`OPEN`)

- **`RULE-OPS-004` (`OPEN`)**: Replace `DashboardModule` hardcoded `"5/5 Connected"` card (`COMPAT-005`) with live `/live/probe` state.
