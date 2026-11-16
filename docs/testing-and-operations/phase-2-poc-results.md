---
doc_id: "OPS-POC-RES-001"
title: "Phase 2 Isolated PoC Empirical Results (POC-02, POC-03, POC-05) & Docker Blocker"
version: "1.0.0"
status: "IN_REVIEW"
implementation_status: "POC_VALIDATED"
owner: "Performance Engineer & Distributed Systems Engineer"
purpose: "Records exact measured hardware, software versions, raw PoC outputs, limitations, and blockers observed during Phase 2 isolated probes."
scope: "Empirical execution of POC-02, POC-03, and POC-05; documents blocker preventing POC-01 and POC-04."
dependencies:
  - "docs/testing-and-operations/phase-2-poc-benchmark-plan.md"
  - "docs/architecture/resource-budget.md"
references:
  - "poc/results/poc_02_cache_sqlite.json"
  - "poc/results/poc_03_analytics_parquet.json"
  - "poc/results/poc_05_exchanges.json"
assumptions:
  - "POC-02 and POC-03 synthetic datasets are proxies used to verify bounds before Phase 4 real-feed soak tests."
open_issues:
  - "BLOCKER-P2-DOCKER: Docker Desktop service (com.docker.service) is Stopped (Manual) with 1.55 GB host free RAM and no .wslconfig memory cap; POC-01 (NATS JetStream) and POC-04 (Combined Hybrid SIGKILL recovery) cannot execute until Docker Desktop is started safely."
review_criteria:
  - "All raw numbers match JSON evidence verbatim with zero extrapolated production guarantees"
---

# Phase 2 PoC Empirical Evidence (`2026-11-16`)

## 1. Execution Environment & Software Versions Measured

- **Host Hardware**: Windows 10 Pro (64-bit) Build `19045`, 12th Gen Intel Core i5-12400F (`6` cores / `12` logical processors), `7.85 GB` Physical RAM (`1.55 GB` free physical RAM prior to Docker start), `C:` `16.62 GB` free (after replacing `1,400.90 MB` legacy `.venv` with `337.49 MB` greenfield `.venv`), `E:` `271.82 GB` free.
- **Software**: Python `3.12.9`, `sqlite3 3.45.3`, `duckdb 2.0.0`, `polars 2.1.0`, `pyarrow 26.0.1`, `nats-py 2.16.0`, `httpx 0.28.1`, `websockets 17.4`, `psutil 7.2.2`, Docker CLI `28.5.1` (daemon stopped).

## 2. Raw Measured Results Summary

### `POC-02` — Bounded In-Process Cache + Concurrent SQLite WAL ([raw JSON](../../poc/results/poc_02_cache_sqlite.json))
- **Command**: `.\.venv\Scripts\python.exe poc/poc_02_cache_sqlite.py`
- **Bounded Cache (`20` symbols, `1,000`-entry tick rings, `100`-level L2 snapshots, `50,000` updates)**:
  - Elapsed: `0.836 s` (`59,784.2 updates/sec`).
  - Memory: `tracemalloc_current = 2.64 MB`, `tracemalloc_peak = 2.66 MB`, `rss_delta = +3.23 MB`.
- **SQLite WAL Concurrency (`1,000` centralized async commits + `5` concurrent async readers)**:
  - Elapsed: `0.045 s`, `125` concurrent reads completed, **`0` SQLite lock errors**.
  - Write latency: `p50 = 0.015 ms`, **`p95 = 0.026 ms`**, `p99 = 0.038 ms`.
  - Read latency: `p50 = 0.009 ms`, **`p95 = 0.014 ms`**, `p99 = 0.163 ms`.
  - DB size: `12.0 KB`.
- **Known Limitations**: Executed with in-process Python single writer; cross-process SQLite WAL read/write concurrency under `SIGKILL` remains deferred to `POC-04` once NATS container runs.

### `POC-03` — 1,000,000-Row ZSTD Parquet: DuckDB vs Polars ([raw JSON](../../poc/results/poc_03_analytics_parquet.json))
- **Command**: `.\.venv\Scripts\python.exe poc/poc_03_analytics_parquet.py`
- **Dataset**: `1,000,000` canonical trade rows across 4 Spot/Perp/Expiry instruments + `50,000` point-in-time decision timestamps; ZSTD Parquet size on SSD = **`3.66 MB`**. Baseline process RSS = `44.8 MB`.
- **DuckDB (`2.0.0`, `memory_limit='768MB'`, `threads=4`)**:
  - 1m OHLCV + VWAP + StdDev rollup (`3,336` bars): runs `[90.26, 24.90, 24.02, 23.95, 24.14] ms` (median **`24.14 ms`**).
  - Point-in-time `ASOF JOIN` (`50k x 1M`): `[127.76, 124.12, 122.98] ms`.
  - **Peak RSS**: **`367.35 MB`**.
- **Polars (`2.1.0`, streaming lazy engine)**:
  - Rollup (`3,336` bars): runs `[112.36, 19.95, 19.53, 16.46, 17.69] ms` (median `19.53 ms`).
  - Point-in-time `join_asof` (`50k x 1M` w/ sort): `[256.60, 223.09, 204.14] ms`.
  - **Peak RSS**: **`957.86 MB`** (2.6x higher RAM footprint than DuckDB due to eager sorting overhead).
- **Architectural Implication**: Select **DuckDB** (`367.35 MB` peak vs `957.86 MB`) as the primary analytical SQL and point-in-time `ASOF` join engine on our `8 GB` machine; reserve Polars strictly for streaming partitioned batch transforms without full-history memory sorts.
- **Known Limitations**: Synthetic periodic price curve compresses heavily (`3.66 MB`); real noisy exchange tick strings/orderbook levels will yield lower compression ratios (`~10–25 MB` per 1M rows estimated `[HYPOTHESIS]`).

### `POC-05` — Live Binance & OKX Public API Capability Probe ([raw JSON](../../poc/results/poc_05_exchanges.json))
- **Command**: `.\.venv\Scripts\python.exe poc/poc_05_exchange_probe.py`
- **Verified Findings**:
  - **Reachability**: `9/9` public REST endpoints (`HTTP 200`, `153–610 ms`) and `3/3` public WSS streams (`380–766 ms` handshake) succeeded from this host (no regional block observed on probed endpoints).
  - **Rate Limits Observed**: Binance Spot `6000` request weight / min (`x-mbx-used-weight-1m`), Binance `fapi`/`dapi` `2400` weight / min (`946` USDT-M + `30` COIN-M symbols including `PERPETUAL`, `CURRENT_QUARTER`, `NEXT_QUARTER`, `TRADIFI_PERPETUAL`).
  - **Critical OKX Protocol Findings**:
    1. OKX WS port `8443` returned notice code `64010` (*"WebSocket port 8443 will be retired soon. Please migrate to port 443."*). Port `443` (`wss://ws.okx.com:443/ws/v5/public`) connected cleanly without warnings.
    2. Contract unit divergence confirmed: `BTC-USDT-SWAP` specifies `ctVal="0.01"` (`ctValCcy="BTC"`); expiry `BTC-USD-261127` specifies `ctVal="100"` (`ctValCcy="USD"`); Spot leaves `ctVal=""`.
    3. OKX `FUTURES` catalog (`293` instruments) and `OPTION` (`1,550` BTC-USD contracts) are live; OKX `books5` returns 4-tuples `[px, contracts, liq_cnt, order_cnt]` + `seqId` vs Binance `[px, qty]` + `U`/`u`.
- **Known Limitations**: Short `10s` smoke probe only; sustained reconnects, OKX 400-level incremental checksums (`books`), and Binance depth snapshot + delta alignment remain to be implemented and tested in Phase 4.

## 3. Blocked Docker-Dependent Probes (`POC-01` & `POC-04`)

- **Blocker Status (`BLOCKER-P2-DOCKER`)**: `com.docker.service` is `Stopped` (`StartType: Manual`), Docker daemon pipe `//./pipe/dockerDesktopLinuxEngine` is offline, and host RAM currently has `1.55 GB` free with no `%USERPROFILE%\.wslconfig` ceiling.
- **Impact**: Real **NATS JetStream** durability, NAK/DLQ routing, container restart continuity (`POC-01`), and combined multi-process `SIGKILL` Parquet/SQLite/NATS crash recovery (`POC-04`) remain **`NOT_RUN`** until Docker Desktop engine is started safely (recommended with `[wsl2] memory=1536MB`).

