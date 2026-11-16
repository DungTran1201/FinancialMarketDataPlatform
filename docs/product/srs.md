---
doc_id: "PRD-SRS-001"
title: "Software Requirements Specification (SRS) — Version 1.0.0 Baseline"
version: "1.0.0"
status: "ACCEPTED"
implementation_status: "NOT_IMPLEMENTED"
owner: "Requirements Engineer & System Analyst"
purpose: "Authoritative versioned catalog of Business Rules (BR), Plane Functional Requirements (FR-DP/FR-INT/FR-APP), Non-Functional Requirements (NFR), and 8 GB Resource Targets."
scope: "Data Plane, Intelligence Plane, and Application Plane across v1 releases R0-R4."
dependencies:
  - "docs/product/vision-and-scope.md"
  - "docs/phase-reports/phase-1-acceptance-and-decisions.md"
references:
  - "docs/product/use-cases.md"
  - "docs/product/requirements-traceability-matrix.md"
  - "docs/product/acceptance-criteria.md"
assumptions:
  - "ASM-P1-003: Native Windows Python 3.12 + containerized NATS JetStream stays within the 8 GB host memory envelope during PoC and dev."
  - "ASM-P1-004: Default cost assumptions in walk-forward eval (spot taker vs perp taker + L2 book impact) will be configurable per venue/instrument."
open_issues:
  - "OPEN-P1-003: Exact Bronze raw retention cap on C: (days vs GB ceiling) pending Phase 2 storage growth PoC."
review_criteria:
  - "Every FR has a globally unique ID and plane assignment"
  - "Every NFR has a measurable target or explicit Phase 2 verification benchmark"
---

# Software Requirements Specification (SRS `v1.0.0`)

## 1. System Business & Methodological Rules (`BR-*`)

| ID | Rule Title | Authoritative Specification |
|---|---|---|
| `BR-METH-001` | Canonical Instrument Model | Every record MUST include `exchange`, `market`, `base_currency`, `quote_currency`, `asset`, `instrument_id`, `symbol`, `contract_type` (`SPOT \| PERPETUAL \| DATED_FUTURE \| OPTION`), `data_source`, `event_type`, `exchange_event_time`, `ingestion_time`, and numeric `contract_multiplier` (for derivatives contracts like OKX `SWAP`/`FUTURES`). |
| `BR-METH-002` | Flow Taxonomy Discipline | Separate metrics & UI domains into `Trade Flow`, `Order Flow`, `Liquidity Flow`, `Derivatives Positioning`, `On-chain Flow` (out of v1 scope unless justified), and `Fund Flow`. Prohibits labeling volume, OI changes, or funding rates as capital inflow. |
| `BR-METH-003` | Source Provenance Retention | Store original raw exchange event metadata/payload checksum or Bronze raw partition alongside canonical fixed-point `Decimal` representations. |
| `BR-METH-004` | No Silent Drops | Malformed payloads, out-of-range prices/volumes, or crossed books MUST emit explicit DLQ records or quality flags (`validation_status`) rather than silent drops. |
| `BR-METH-005` | Evidence & Abstention | Every online forecast MUST carry model ID/version, feature timestamp, uncertainty interval (`q10`/`q50`/`q90` or predictive std), `data_quality_status`, and `abstention_flag`. |
| `BR-METH-006` | Baseline Hurdle Gate | Complex models (Tier 1–3) MUST beat Tier 0 baselines out-of-sample net of fees, estimated L2 slippage, and funding before promotion. |

## 2. Data Plane Functional Requirements (`FR-DP-*`)

### 2.1 Ingestion & Source Health (`CAP-DP-ING`)
- `FR-DP-ING-001`: Implement independent exchange connectors and normalizers for **Binance** (Spot + Perp/Expiry Futures) and **OKX** (Spot + Swap/Perp + Expiry Futures; optional Options evaluation).
- `FR-DP-ING-002`: Ingest WebSocket public streams (trades, L2 depth diffs, BBO/ticker, mark/funding streams) and REST APIs (instrument metadata, klines/history, L2 snapshots, OI & funding history).
- `FR-DP-ING-003`: Enforce exchange-specific token-bucket rate limiters capped at $\le 80\%$ of documented IP/UID API weight limits, honoring `Retry-After` and HTTP `429`/`418` headers.
- `FR-DP-ING-004`: Maintain exponential backoff with full jitter on WebSocket disconnects and track live source health (`CONNECTING | STREAMING | STALE | BACKOFF | STOPPED`, reconnect count, message lag).
- `FR-DP-ING-005`: Execute bounded, idempotent historical backfills persisted via SQLite WAL watermarks per `(instrument_id, stream_type, interval)`.

### 2.2 Persistent Event Streaming & Validation (`CAP-DP-STR`)
- `FR-DP-STR-001`: Publish normalized canonical `EventEnvelope` records into a disk-backed persistent message broker (Phase 2 PoC candidate: NATS JetStream) with deterministic deduplication IDs, stream retention bounds, ACK/redelivery, consumer groups, and bounded replay.
- `FR-DP-STR-002`: Route invalid payloads to a dedicated DLQ subject/stream retaining raw payload, failure class, error detail, exchange/connector ID, and UTC failure timestamp.
- `FR-DP-STR-003`: Enforce explicit pull-based consumer prefetch / `max_ack_pending` backpressure bounds so stalled consumers never cause unbounded memory growth.

### 2.3 Real-Time Stream & Microstructure Processing (`CAP-DP-RTP`)
- `FR-DP-RTP-001`: Aggregate trade events using event-time watermarks into canonical OHLCV bars (`1s`, `1m`, `5m`, `15m`, `1h`, `4h`, `1d`) with `taker_buy_volume`, `trade_count`, `vwap`, and late-event / completeness indicators.
- `FR-DP-RTP-002`: Reconstruct deterministic L2 order books per instrument from REST baseline snapshot + sequence-checked WS deltas (Binance `U`/`u`/`pu`; OKX `seqId`/`prevSeqId`), invalidating state and triggering automated REST resync on any sequence gap or crossed book (`bid >= ask`).
- `FR-DP-RTP-003`: Compute real-time microstructure & order flow metrics on valid state: quoted spread (abs & bps), microprice, multi-level depth (`5/10/25/50 bps`), L1/L5 Order Flow Imbalance (OFI), Cumulative Volume Delta (CVD), and estimated market-impact slippage across notional buckets.
- `FR-DP-RTP-004`: Track derivatives positioning metrics (funding rate, next funding time, annualized carry, mark-index/spot basis bps, open interest in both contracts and quote-value terms, OI delta).
- `FR-DP-RTP-005`: Emit real-time feature snapshots synchronized with closed bars / microstructure windows into bounded in-memory hot state and streaming outputs.

### 2.4 Medallion Storage, Quality & Lineage (`CAP-DP-LAK`)
- `FR-DP-LAK-001`: Archive Medallion Parquet tiers (`ZSTD`): Bronze (verbatim source payload + metadata partitioned by date/exchange), Silver (canonical typed events/OHLCV/book snapshots/derivatives), Gold (clean multi-asset aggregations & point-in-time feature matrices).
- `FR-DP-LAK-002`: Use centralized single-writer micro-batch flushing and periodic partition compaction to avoid small-file proliferation and lock contention on local SSD.
- `FR-DP-LAK-003`: Enforce Silver $\rightarrow$ Gold Data Quality gates (monotonic time, finite prices, `low <= open/close <= high`, non-negative volume/OI, gap ratio thresholds, non-crossed BBO) blocking promotion on critical failures.
- `FR-DP-LAK-004`: Query Silver/Gold Parquet via DuckDB inside memory-bounded worker pools isolated from real-time ingestion, while enforcing retention TTL & disk ceiling pruning.
- `FR-DP-LAK-005`: Persist SQLite WAL dataset lineage tables connecting Bronze sources $\rightarrow$ Silver partitions $\rightarrow$ Gold tables $\rightarrow$ Research datasets.

### 2.5 Data Serving APIs (`CAP-DP-SRV`)
- `FR-DP-SRV-001`: Expose paginated, bounded REST APIs for canonical instruments, OHLCV, trades, reconstructed order books, derivatives stats, microstructure series, features, DQ status, and DLQ inspection.
- `FR-DP-SRV-002`: Push real-time market updates, DQ alerts, and system telemetry over WebSocket/SSE using per-client bounded queues with latest-state-wins conflation.

## 3. Intelligence Plane Functional Requirements (`FR-INT-*`)

### 3.1 Quantitative Research & Features (`CAP-INT-RES`, `CAP-INT-FEA`)
- `FR-INT-RES-001`: Build versioned, hash-verified research datasets enforcing strict point-in-time alignment (`available_at <= decision_time`) to forbid future data leakage.
- `FR-INT-RES-002`: Provide EDA & statistical testing workflows (ADF/KPSS stationarity, ACF/PACF, fat-tail/kurtosis diagnostics, cross-asset lead-lag analysis) with SQLite experiment logging (seed, dataset hash, hyperparameters, metrics).
- `FR-INT-RES-003`: Maintain a curated Research Reference Library linking each model/estimator to verified papers/DOIs/docs and explicit limitations.
- `FR-INT-FEA-001`: Define a versioned Feature Catalog computing identical definitions offline (DuckDB/Polars) and online (streaming state): log returns, realized volatility (`RV`, Parkinson, Garman-Klass, Yang-Zhang), OFI, CVD, depth imbalance, effective spread, funding/basis/OI deltas, cross-asset correlations, lead-lag features, and volatility/trend regime indicators.
- `FR-INT-FEA-002`: Validate online-vs-offline feature parity automatically on replayed historical streams.

### 3.2 Models, Evaluation & Online Inference (`CAP-INT-MOD`, `CAP-INT-INF`)
- `FR-INT-MOD-001`: Implement tiered models with mandatory Model Cards documenting justification, data needs, compute cost, and limitations:
  - **Tier 0 Baselines**: Random Walk/Persistence, Moving Averages, OLS/Ridge Linear Regression, Logistic Regression, Time-Series Momentum.
  - **Tier 1 Statistical/Econometric**: ARIMA/ARIMAX, EWMA Volatility, GARCH(1,1), HAR-RV, Hidden Markov Models (regimes), OFI Regression.
  - **Tier 2 Tabular/Quantile ML (only when beating Tier 0/1)**: LightGBM / HistGradientBoosting / Quantile Regression (`q10`, `q50`, `q90`) / Random Forest. Sequence models (TCN/GRU) and Tier 3 (DeepLOB, Hawkes) remain deferred unless justified within 8 GB compute bounds.
- `FR-INT-MOD-002`: Implement Purged & Embargoed Walk-Forward Evaluation scoring statistical accuracy, probabilistic calibration (Brier/Pinball/LogLoss), regime stability, overfitting warnings, and **net economic metrics accounting for fees, estimated L2 slippage, and funding carry**.
- `FR-INT-INF-001`: Execute online multi-horizon inference (return distribution/direction, volatility, liquidity/spread state, order flow pressure, regime classification, uncertainty bounds) with local feature-driver explanations.
- `FR-INT-INF-002`: Enforce DQ-aware gating prior to inference: automatically **abstain** (or explicitly fall back to Tier 0 degraded flag) when feeds are stale, books unsynced, or feature PSI drift breaches threshold.
- `FR-INT-INF-003`: Persist all predictions in SQLite and asynchronously reconcile realized outcomes to track live calibration drift and health.

## 4. Application Plane Functional Requirements (`FR-APP-*`)

### 4.1 Security, Access & Control (`CAP-APP-SEC`)
- `FR-APP-SEC-001`: Enforce authenticated JWT Bearer / hashed API Key credentials with strict RBAC (`ROLE-QA`, `ROLE-QR`, `ROLE-MLE`, `ROLE-OPS`, `ROLE-ADM`, `SERVICE`) across all mutating, trigger, admin, and experiment APIs (zero default admin bypass).
- `FR-APP-SEC-002`: Enforce Pydantic v2 validation, query row/range bounds, tiered sliding-window rate limits, structured error envelopes, and non-blocking health probes (`/health/live`, `/health/ready`).

### 4.2 Frontend Application Modules (`FR-APP-UI-001` .. `FR-APP-UI-015`)
All 15 modules MUST display real source metadata, UTC timestamps, DQ badges, and explicit `DEGRADED / ABSTAINED / UNAVAILABLE` indicators (no mock prices or placeholder metrics):
- `FR-APP-UI-001`: **System Overview** (platform state, tracked assets, stream health, DLQ count, active models, 8 GB RAM/disk gauge).
- `FR-APP-UI-002`: **Market Scanner** (multi-exchange/contract screener across Binance & OKX metrics & DQ badges).
- `FR-APP-UI-003`: **Real-Time Market Dashboard** (live OHLCV + volume/CVD, synced L2 depth ladder, BBO/spread, WS latency).
- `FR-APP-UI-004`: **Multi-Asset Analytics** (Spot vs Perpetual vs Expiry Futures comparison, normalized returns, term structure/basis).
- `FR-APP-UI-005`: **Order Flow Intelligence** (aggressor buy/sell delta, CVD, multi-level OFI, trade size breakdown — explicitly distinct from capital inflow).
- `FR-APP-UI-006`: **Liquidity Analytics** (bps cumulative depth, effective vs quoted spread, slippage-by-notional curve, resilience).
- `FR-APP-UI-007`: **Derivatives Analytics** (funding rate, annualized carry, Spot-Perp basis, Open Interest & OI deltas).
- `FR-APP-UI-008`: **Cross-Asset Analysis** (rolling correlation matrix, dynamic beta, lead-lag cross-correlograms).
- `FR-APP-UI-009`: **Volatility & Market Regime** (EWMA/Parkinson/Garman-Klass/Yang-Zhang RV, GARCH/HAR-RV forecasts, HMM regime timeline).
- `FR-APP-UI-010`: **Quantitative Research** (dataset builder w/ point-in-time check, EDA diagnostics, experiment registry comparator).
- `FR-APP-UI-011`: **Forecasting Dashboard** (real-time quantile fan charts `q10–q90`, driver attributions, DQ gate & abstention flags).
- `FR-APP-UI-012`: **Model Evaluation** (walk-forward tear-sheets vs Tier 0 baseline, calibration plots, net-of-cost diagnostics, live PSI drift).
- `FR-APP-UI-013`: **Data Quality & Observability** (end-to-end latency breakdown, gap/backfill audit, DLQ frame inspector & replay trigger, DQ gate log).
- `FR-APP-UI-014`: **Infrastructure & System Health** (RSS RAM vs 8 GB host cap, CPU %, `C:`/`E:` disk stats, NATS stream bytes/lag, SQLite WAL stats, connector status).
- `FR-APP-UI-015`: **Configuration & Asset Management** (canonical Binance/OKX instrument CRUD, stream subscriptions, backfill triggers, compaction/retention controls, RBAC & API key admin).

## 5. Non-Functional Requirements & 8 GB Resource Targets (`NFR-*`)

| ID | Category | Measurable Requirement / Acceptance Target (`[TARGET]`) |
|---|---|---|
| `NFR-RES-001` | **Host Memory Cap** | Combined platform RSS $\le 1.0\text{ GB}$ idle, $\le 2.2\text{ GB}$ nominal live streaming (`10–20` instruments), and $\le 3.2\text{ GB}$ peak during analytical DuckDB/ML runs on the `7.85 GB` machine. |
| `NFR-RES-002` | **Disk Quota** | Workspace + local SQLite + Parquet working set on `C:` (`15.54 GB` free) capped $\le 5.0\text{ GB}$ via ZSTD compaction and configurable TTL retention (with optional cold archive path on `E:`). |
| `NFR-RES-003` | **Bounded Queues** | Every internal queue, hot cache, WS client send buffer, and JetStream stream enforces hard item/byte bounds; slow UI WS clients use latest-snapshot conflation. |
| `NFR-PERF-001` | **Hot Path Latency** | Normalizer $\rightarrow$ NATS JetStream PubAck $\rightarrow$ Microstructure update $\rightarrow$ Hot cache **p95 $< 50\text{ ms}$**, **p99 $< 150\text{ ms}$** at sustained PoC rate. |
| `NFR-PERF-002` | **Analytical Isolation** | 30-day 1m Parquet DuckDB rollup **p95 $< 500\text{ ms}$**; concurrent analytical queries degrade live WS hot-path p99 by **$< 20\text{ ms}$**. |
| `NFR-PERF-003` | **Online Inference** | Feature retrieval + Tier 0/1/2 prediction + uncertainty + explanation **p95 $< 25\text{ ms}$**. |
| `NFR-REL-001` | **Crash & Replay** | Process `SIGKILL` or NATS container restart yields **0** lost acknowledged events, **0** corrupt Parquet/SQLite files, and automatic replay recovery within **$< 30\text{ s}$**. |
| `NFR-SEC-001` | **Auth & Secret Safety** | `100%` mutating/admin routes require valid credentials (`401`/`403` enforced); API keys & passwords stored hashed; zero plaintext secrets in logs/docs/Git. |
| `NFR-MOD-001` | **Replaceable Adapters** | Event bus, hot cache, metadata store, query engine, exchange connectors, and model store sit behind typed protocol ports testable without heavyweight daemons. |
| `NFR-OBS-001` | **Telemetry Hygiene** | JSON structured logs + Prometheus metrics with strictly bounded label cardinality (no `event_id`/`trade_id`/raw IP labels). |

