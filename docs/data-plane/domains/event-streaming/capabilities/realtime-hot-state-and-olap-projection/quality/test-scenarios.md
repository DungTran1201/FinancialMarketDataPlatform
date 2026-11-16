---
doc_id: CAP-DP-STR2-TS-001
title: "Test Scenarios: Hot State, OLAP Rollups & Anomaly Cooldown"
doc_type: specification
plane: data-plane
scope_level: capability
domain: event-streaming
capability_id: CAP-DP-STR-002
status: IN_REVIEW
implementation_status: SIMULATED
version: "2.0.0"
owner_role: qa-lead
accountable_role: qa-lead
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "tests/integration/test_three_planes_framework.py"
    - "tests/integration/test_realtime_observability_dashboard.py"
    - "tests/resilience/test_gap_recovery_and_dlq.py"
related_docs:
  - CAP-DP-STR2-SPEC-001
requirement_ids:
  - TS-STR2-001
  - TS-STR2-002
  - TS-STR2-003
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: qa-lead
    summary: "Mapped verified in-memory tests for monotonic drops, Lua args, 5m rollups, and 15m anomaly cooldown."
---

# Test Scenarios: Hot State, OLAP Rollups & Anomaly Cooldown

## 1. Scenario Matrix `[REQUIRED]`

| Scenario ID | Linked FR / RULE | Summary | Expected Result | Test Double Reality |
|---|---|---|---|---|
| `TS-STR2-001` | `FR-STR2-001`, `RULE-STR2-001` | Send older timestamp quote after newer quote + mock Redis `eval` capture | Stale quote dropped (`dropped_out_of_order_count == 1`); Lua `ARGV` indexes match script (`for i=3`). | Python dict + `_FakeRedis` mock |
| `TS-STR2-002` | `FR-STR2-002`, `RULE-STR2-002` | Ingest 3 `AVAXUSDT` `1m` klines -> request `interval=5m` rollup & duplicate update | Exact `100/108/99/102/6.0` rollup (`rolled_up_from_bars=3`); latest timestamp wins on dedup. | Python dict simulation |
| `TS-STR2-003` | `FR-STR2-003`, `RULE-STR2-003` | Trigger 5-sigma spike at `t=0`, replay at `+5m`, trigger at `+16m` | Triggers `t=0`, suppressed `+5m` (`suppressed == 1`), triggers `+16m`. | In-memory cooldown dict |

## 2. Live Database Coverage Gap

No tests connect to running `redis:7.2` or `clickhouse:24.3` containers.
