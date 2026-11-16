---
doc_id: "PRD-AC-001"
title: "Measurable Acceptance Criteria Catalog (AC-01..AC-15)"
version: "1.0.0"
status: "ACCEPTED"
implementation_status: "NOT_IMPLEMENTED"
owner: "Principal QA Engineer & Requirements Engineer"
purpose: "Defines binary PASS/FAIL acceptance criteria mapped to all functional, multi-asset, 8 GB hardware, security, and UI evidence requirements."
scope: "Verification gates across Phases 2, 4, 5, 6, 7, 8, and 9."
dependencies:
  - "docs/product/srs.md"
  - "docs/product/use-cases.md"
references:
  - "docs/product/requirements-traceability-matrix.md"
assumptions:
  - "Thresholds defined in PoC/NFR criteria are verified using deterministic synthetic harnesses AND real Binance/OKX sandbox/public feeds."
open_issues:
  - "Exact default feed staleness threshold (e.g. 2000ms vs 5000ms per stream type) to be confirmed via Phase 2 Binance/OKX API latency checks."
review_criteria:
  - "Every criterion is objective, reproducible, and has a single verifiable pass condition"
---

# Acceptance Criteria (`AC-01` .. `AC-15`)

| AC ID | Requirement Group | Binary PASS / FAIL Verification Condition |
|---|---|---|
| `AC-01` | Canonical Instrument Identity | All `SPOT`, `PERPETUAL`, and `DATED_FUTURE` records across Binance & OKX carry unique `instrument_id`, distinct `contract_type`, and explicit `contract_multiplier`; zero primary-key collisions occur across ingest, SQLite, Parquet, and API queries. |
| `AC-02` | DLQ & No Silent Discard | Injecting `100` malformed, negative-price, or crossed-book events routes `100/100` to persistent DLQ with raw payload checksum/copy, error code, and UTC timestamp; `0` invalid rows appear in Silver/Gold Parquet. |
| `AC-03` | JetStream Durability & Replay | Delivering `10,000` sustained messages across `NATS JetStream` file storage + killing consumer (`SIGKILL`) mid-stream + restarting results in **0 lost ACKed messages** and exact row count deduplicated in Silver Parquet. |
| `AC-04` | L2 Book Sync & Flow Integrity | Simulated WebSocket sequence drop (`gap` in `u`/`pu` or `seqId`/`prevSeqId`) invalidates book within `< 1` tick, suppresses OFI/depth emissions (`validation_status=BOOK_UNSYNCED`), triggers REST snapshot resync, and resumes cleanly. |
| `AC-05` | Medallion DQ Gate | Staging invalid Silver bars (`high < low` or gap violation) causes DQ Gate to block Gold promotion (`can_promote_to_gold=False`), preserves prior valid Gold partition, and writes audit row in SQLite. |
| `AC-06` | No Leakage & Feature Parity | Point-in-time dataset validator verifies `100%` of training rows obey `available_at <= decision_time`; replaying historical ticks through online vs offline pipelines matches within `< 1e-6` float / exact `Decimal` tolerance. |
| `AC-07` | Baseline Gate & Net Cost Eval | Purged walk-forward harness deducts venue taker fee + simulated L2 slippage + funding carry and rejects automatic promotion (`promoted=False`) for any Tier 1/2 model failing Tier 0 baseline metrics. |
| `AC-08` | DQ-Aware Inference & Abstention | Under stale feed (`age > staleness_threshold_ms`) or corrupted book state, online inference emits `abstention_flag=True` (or flagged baseline fallback) within `p95 < 25 ms` without fabricating normal confidence scores. |
| `AC-09` | Hot-Path Latency & Isolation | Under `1,500 events/s` sustained ingest + `2` active WS subscribers + concurrent 30-day DuckDB rollup query, hot-path ingest-to-cache `p95 < 50 ms`, `p99 < 150 ms`, DuckDB query `p95 < 500 ms`, and concurrent query shifts WS p99 by `< 20 ms`. |
| `AC-10` | 8 GB Memory & Disk Quotas | Over a 2-hour endurance test on this Windows host (`7.85 GB` RAM): total platform RSS stays `<= 1.0 GB` idle, `<= 2.2 GB` nominal, `<= 3.2 GB` peak; local storage on `C:` remains `<= 5.0 GB`. |
| `AC-11` | Backpressure & Slow Consumers | Pausing analytical batch consumer for `30s` buffers bounded backlog on JetStream disk without API crash; throttling a UI WS client applies latest-state-wins conflation with `<=` bounded server buffer memory. |
| `AC-12` | Authentication & RBAC | `100%` protected endpoints return `401` without valid credentials and `403` when accessed by insufficient role (`VIEWER` calling config/backfill/training routes); passwords and API keys stored strictly hashed. |
| `AC-13` | Honest Zero-Mock UI | All implemented UI modules render live backend data, show `source`, `UTC timestamp`, `DQ badge`, and `ABSTAINED / UNAVAILABLE` states explicitly; automated scan confirms zero mock price fallback arrays in `frontend/`. |
| `AC-14` | Multi-Exchange Parity (`Binance` + `OKX`) | Live public REST/WS PoC + Phase 4 adapters successfully parse and normalize Spot, Perpetual, and Expiry Futures feeds from BOTH **Binance** and **OKX**, accurately converting OKX contract units (`ctVal`) vs Binance base/quote volumes into canonical quote/base fields. |
| `AC-15` | Hybrid Runtime Restart Continuity | Stopping and restarting BOTH the containerized NATS JetStream container AND native Python consumer process recovers active consumer subscriptions, SQLite WAL state, and disk-backed stream cursors within `< 30s` with zero state corruption. |
