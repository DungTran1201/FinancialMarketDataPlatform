---
doc_id: "PRD-UC-001"
title: "Core Multi-Asset & Quantitative Intelligence Use Cases (UC-01..UC-10)"
version: "1.0.0"
status: "ACCEPTED"
implementation_status: "NOT_IMPLEMENTED"
owner: "Principal Business Analyst"
purpose: "Defines end-to-end actor flows, preconditions, and edge/failure paths across Data, Intelligence, and Application planes."
scope: "All v1 platform workflows for Binance + OKX across Spot, Perpetual, and Expiry Futures."
dependencies:
  - "docs/product/srs.md"
references:
  - "docs/product/acceptance-criteria.md"
  - "docs/product/requirements-traceability-matrix.md"
assumptions:
  - "All operator configuration actions require authenticated RBAC tokens."
open_issues: []
review_criteria:
  - "Explicit failure and recovery paths specified for every use case"
---

# Core Use Cases (`UC-01` .. `UC-10`)

| UC ID | Name & Primary Actor | Preconditions | Main Flow Summary | Exception & Recovery Flows |
|---|---|---|---|---|
| `UC-01` | **Register Binance & OKX Instruments**<br/>*Actor*: `ROLE-OPS` | Valid JWT/API key with `operator` or `admin` role. | Submit canonical instrument definitions (`binance:spot:BTC/USDT`, `okx:swap:BTC/USDT`, `okx:expiry:...`) $\rightarrow$ validate contract multiplier & tick/lot rules $\rightarrow$ persist to SQLite catalog $\rightarrow$ connectors subscribe. | Duplicate key $\rightarrow$ `409`; invalid `contract_type` $\rightarrow$ `422`; unauth/non-operator $\rightarrow$ `401/403`. |
| `UC-02` | **Live Multi-Exchange Streaming & L2 Order Book Reconstruction**<br/>*Actor*: System | Registered active instruments + NATS JetStream online. | Exchange WS feeds arrive $\rightarrow$ normalizer maps payload to canonical `EventEnvelope` preserving raw source provenance $\rightarrow$ JetStream `PubAck` $\rightarrow$ Stream consumer builds OHLCV + REST-synced L2 book (`u`/`pu` or `seqId`/`prevSeqId`) + OFI/CVD $\rightarrow$ Bounded hot cache & client WS push. | WS drop $\rightarrow$ backoff + mark `STALE`; sequence gap or crossed book $\rightarrow$ invalidate book, pause OFI/depth, trigger REST resync; malformed frame $\rightarrow$ quarantine in DLQ. |
| `UC-03` | **Watermarked Historical Backfill & Gap Healing**<br/>*Actor*: `ROLE-OPS` / Auto-Gap | SQLite watermark initialized; exchange REST rate budget available. | Request date range or detected gap $\rightarrow$ paginated REST pull respecting token bucket (`<=80%` weight ceiling) $\rightarrow$ deterministic ID dedup $\rightarrow$ Bronze/Silver Parquet flush $\rightarrow$ watermark updated to `SYNCED`. | Exchange `429`/`418`/`5xx` $\rightarrow$ backoff & retry; exhausted retries $\rightarrow$ mark job `FAILED` retaining checkpoint cursor for safe resume. |
| `UC-04` | **Medallion Compaction & Data Quality Gating**<br/>*Actor*: Batch Worker | Uncompacted Bronze/Silver files exist on SSD. | Worker validates Silver rows (monotonic time, finite prices, `low <= open/close <= high`, non-crossed BBO, gap ratio) $\rightarrow$ compacts small Parquet partitions $\rightarrow$ promotes clean data to Gold $\rightarrow$ updates DuckDB views & SQLite lineage. | Critical DQ violation $\rightarrow$ block Gold promotion (`can_promote_to_gold=False`), log DQ verdict, keep prior Gold state intact. |
| `UC-05` | **Multi-Asset Microstructure, Liquidity & Derivatives Analysis**<br/>*Actor*: `ROLE-QA` | User authenticated; Data Plane serving APIs live. | Analyst opens Modules 2–8 $\rightarrow$ queries DuckDB historical Gold/Silver + live WS hot deltas $\rightarrow$ inspects Spot vs OKX Swap basis, funding carry, OI delta, bps depth, and OFI/CVD cleanly separated by flow taxonomy. | Stale feed (`age > threshold`) renders explicit `DEGRADED / STALE` warning rather than synthetic fallback numbers. |
| `UC-06` | **Point-in-Time Research Dataset Snapshot & EDA**<br/>*Actor*: `ROLE-QR` | Silver/Gold Parquet populated across target range. | Researcher configures instrument basket, horizon, and feature specs $\rightarrow$ DuckDB/Polars builds immutable snapshot enforcing `available_at <= decision_time` $\rightarrow$ computes ADF/KPSS, ACF, lead-lag stats $\rightarrow$ persists dataset hash & experiment log. | Insufficient historical coverage or unresolved gap flags surfaced explicitly in dataset DQ report before training. |
| `UC-07` | **Tiered Model Training & Purged Walk-Forward Eval**<br/>*Actor*: `ROLE-QR` / `ROLE-MLE` | Verified dataset snapshot + registered Feature Catalog version. | Worker trains Tier 0 baselines + candidate Tier 1 (`HAR-RV`, `GARCH`, `HMM`, `OFI`) or Tier 2 ML across purged/embargoed splits deducting taker fees + L2 slippage + funding $\rightarrow$ saves Model Card & calibration report to SQLite. | Candidate failing Tier 0 hurdle marked `NOT_PROMOTED`; oversized job trips memory guard cleanly without crashing Realtime Core. |
| `UC-08` | **DQ-Aware Real-Time Inference & Abstention**<br/>*Actor*: System | Promoted model artifact + online feature state ready. | On bar close / trigger, check stream freshness, book sync, and PSI feature drift $\rightarrow$ compute prediction + `q10/q50/q90` uncertainty interval + top drivers $\rightarrow$ persist & emit via WS/SSE. | Degraded upstream feed, unsynced book, or PSI drift breach emits explicit `ABSTAINED` (`abstention_flag=True`) or Tier 0 fallback. |
| `UC-09` | **Persistent Stream Crash & Restart Replay Recovery**<br/>*Actor*: System / `ROLE-OPS` | NATS JetStream file store & SQLite WAL enabled. | Process kills mid-ingest (`SIGKILL`) or NATS container restarts $\rightarrow$ connector reconnects, JetStream redelivers unacknowledged messages from durable sequence $\rightarrow$ idempotent Silver merge completes without duplicate final records. | Repeatedly failing poison payload exceeding `max_deliver` routes cleanly to DLQ so healthy events resume. |
| `UC-10` | **DLQ Inspection, Resource Monitoring & Backups**<br/>*Actor*: `ROLE-OPS` / `ROLE-ADM` | Operator/Admin authenticated. | Inspect live RSS memory (`<= 3.2 GB`), CPU, `C:` disk quota, JetStream lag, SQLite WAL stats, and DLQ payloads in Modules 13–14 $\rightarrow$ replay remediated DLQ batch or trigger verified SQLite + Parquet backup snapshot. | `C:` disk free drops below alert threshold $\rightarrow$ alert operator, prune oldest expired Bronze partitions per TTL policy, pause optional backfills. |

