---
doc_id: CAP-DP-ING-TS-001
title: "Test Scenarios: Exchange Ingestion & Backfill"
doc_type: specification
plane: data-plane
scope_level: capability
domain: market-data-ingestion
capability_id: CAP-DP-ING-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: qa-lead
accountable_role: qa-lead
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "tests/resilience/test_gap_recovery_and_dlq.py"
    - "tests/e2e/test_data_platform_v01_e2e.py"
related_docs:
  - CAP-DP-ING-SPEC-001
requirement_ids:
  - TS-ING-001
  - TS-ING-002
  - TS-ING-003
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: qa-lead
    summary: "Documented positive, poison-frame DLQ, pagination, and gap-healing scenarios."
---

# Test Scenarios: Exchange Ingestion & Backfill

## 1. Scenario Matrix `[REQUIRED]`

| Scenario ID | Linked FR / SEC | Preconditions | Scenario Summary | Expected Outcome | Environment Reality |
|---|---|---|---|---|---|
| `TS-ING-001` | `FR-ING-003`, `FR-ING-004` | Clean SQLite DB + embedded ASGI exchange simulator | Closed klines arrive with a 3-minute gap (`t+1m` skipped to `t+4m`). | Watermark marks `GAP_DETECTED`, executes REST backfill (`3` events), marks `SYNCED`, publishes all frames. | Executed in-process (`test_gap_recovery_and_dlq.py`) |
| `TS-ING-002` | `FR-ING-001`, `SEC-ING-001` | In-memory broker | Trade frame contains negative price `"-42.50"`. | Rejected by normalizer and written as 1 `DeadLetterEnvelopeV1` on `market.dlq.v1`. | Executed in-process (`test_gap_recovery_and_dlq.py`) |
| `TS-ING-003` | `FR-ING-002`, `RULE-ING-002` | `max_page_size=2`, `TokenBucketRateLimiter` ceiling `80` | Request 6-bar range triggering multi-page REST calls & weight limit pause. | All 6 bars returned across multiple sequential requests without dropping bars. | Executed in-process (`test_data_platform_v01_e2e.py`, `test_domain_and_quant.py`) |

## 2. Test Coverage Limitations

Live continuous `websockets` disconnect tests and live exchange REST calls remain unverified by CI (`GAP-QA-001`).
