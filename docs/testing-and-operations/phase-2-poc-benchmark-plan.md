---
doc_id: "OPS-POC-PLAN-001"
title: "Phase 2 Technology PoC Benchmark Plan & Acceptance Thresholds"
version: "1.0.0"
status: "IN_REVIEW"
implementation_status: "PLANNED"
owner: "Performance Engineer & Principal QA Engineer"
purpose: "Defines exact isolated PoC workloads, datasets, measurement instrumentation, reproducible scripts, and measurable pass/fail criteria covering all 12 Phase 2 requirements plus live Binance/OKX API probing."
scope: "Isolated PoCs under poc/ using Hybrid Native Windows Python 3.12 + Containerized NATS JetStream (`DEC-P0-002`)."
dependencies:
  - "docs/architecture/technology-evaluation-matrix.md"
  - "docs/architecture/resource-budget.md"
  - "docs/product/acceptance-criteria.md"
references:
  - "docs/work-items/phase-2-work-items.md"
assumptions:
  - "PoCs run on the physical host (7.85 GB RAM, i5-12400F, Windows 10 Pro) without running full production application code."
open_issues:
  - "Verify Docker Desktop Linux engine startup & WSL2 RAM overhead before running NATS JetStream container benchmarks."
review_criteria:
  - "Covers all 12 Section 6 evaluation points with explicit methodology and known limitations"
  - "Includes real Binance & OKX public REST/WS capability and rate-limit check"
---

# Phase 2 Isolated PoC Benchmark Plan

## 1. Benchmark Environment & Ground Rules (Section 6 Compliance)

- **Target Hardware Baseline**: Windows 10 Pro Build `19045`, 12th Gen Intel Core i5-12400F (`6C/12T`), `7.85 GB` RAM, `C:` `15.54 GB` free.
- **Software Versions Under Test**: Python `3.12.9`, `nats-py 2.16.0`, `nats:2.10-alpine` (Docker Desktop container bounded `mem_limit: 256m`), `duckdb 2.0.0`, `polars 2.1.0`, `pyarrow 26.0.1`, `sqlite3 3.45.3`, `psutil 7.2.2`, `httpx 0.28.1`, `websockets 17.4`.
- **Reporting Integrity**: Every PoC run outputs machine-readable JSON + raw timing percentiles (`p50/p95/p99/max`), `psutil` RSS/CPU% time series, Docker `stats` RSS/CPU%, exact dataset byte sizes, test duration, and an explicit list of limitations (e.g., synthetic tick bursts vs real live volatility spikes).

## 2. Isolated Workloads & Measurable Pass/Fail Criteria

| Probe ID | Section 6 Criteria Covered | Exact Workload & Dataset | Measurement & Reproducibility | Acceptance Threshold |
|---|---|---|---|---|
| **`POC-01`** | `#1` NATS throughput/latency, `#2` ACK & redelivery, `#3` Replay/Recovery, `#7` NATS RAM, `#11` Broker interruption, `#12` Container + app restart recovery | JetStream FileStore stream (`max_bytes=256MB`); publish `20,000` JSON market envelopes (`~450 B` avg) at `2,000–5,000 msg/s`; pull consumer pulls `250/batch`; **Fault Test A**: consumer NAKs/drops mid-stream & recovers; **Fault Test B**: `docker restart` NATS container mid-run & reconnect; **Fault Test C**: full time/seq replay from sequence 1. | `time.perf_counter_ns()` publish-to-consume latency; `docker stats --no-stream`; message ID set equality check. | Sustained $\ge 2,000\text{ msg/s}$; publish+consume `p99 < 50 ms`; `0` lost ACKed messages after container restart; auto-reconnect `< 15 s`; NATS container RSS `<= 256 MB`. |
| **`POC-02`** | `#4` Bounded In-Process Cache behavior, `#5` SQLite WAL read/write concurrency, `#7` Cache RAM | Simulate `20` instruments x `1,000`-entry tick rings + `100`-level L2 books receiving `50,000` updates while a separate asyncio task writes `1,000` watermark/job/checkpoint transactions and `5` reader tasks query SQLite WAL (`busy_timeout=5000`). | `tracemalloc` + `psutil.Process().memory_info().rss`; lock-error count (`sqlite3.OperationalError`). | Ring memory plateau strictly flat after warmup (`< 60 MB` overhead); `0` unhandled SQLite lock errors; SQLite commit `p95 < 15 ms`. |
| **`POC-03`** | `#6` DuckDB vs Polars Parquet analytical workloads, `#7` Engine RAM, `#9` CPU, `#10` Disk I/O & growth | Generate `1,000,000` synthetic canonical trade/bar rows (`ZSTD` partitioned Parquet on SSD); compare (a) **DuckDB** (`memory_limit='768MB'`, `threads=4`) vs (b) **Polars LazyFrame** executing 1m OHLCV rollup, VWAP, realized vol, and point-in-time `ASOF` join. | Peak process RSS via `psutil`, CPU %, Parquet compression ratio (`MB` on disk), wall latency over 5 runs. | Analytical rollup latency `< 500 ms`; point-in-time ASOF join `< 1,500 ms`; peak worker RSS `<= 900 MB`; compressed disk footprint measured & extrapolated cleanly to `5 GB` quota. |
| **`POC-04`** | `#8` Combined complete PoC RAM, `#9` Combined CPU, `#10` Combined Disk I/O, `#12` Process `SIGKILL` & restart recovery | Run NATS JetStream container + Process 1 (`ingest+cache`) + Process 2 (`JetStream pull -> Parquet atomic writer + SQLite WAL + periodic DuckDB query`) **simultaneously for 60–120 seconds** under `1,500 msg/s`; inject `SIGKILL` on Process 2 mid-run, restart it, verify deduplicated final count + zero `.tmp` corrupt files. | Polled `psutil` RSS/CPU every `500 ms` + `docker stats`; verify row equality `set(published) == set(parquet_silver)`. | Combined Python RSS + NATS container RSS `<= 1.2 GB` during PoC; DuckDB query causes `< 20 ms` hot-path `p99` jitter; `0` missing/corrupt Parquet rows after `SIGKILL` recovery. |
| **`POC-05`** | `OPEN-P1-002` Exchange API Verification (`Binance` & `OKX`) | Live read-only HTTPS REST + short WSS smoke check against **Binance** (`Spot` + `USDT-M Perp/Expiry`) and **OKX** (`SPOT` + `SWAP` + `FUTURES` + check `OPTION` availability), capturing real latency, rate-limit headers, `ctVal` contract multipliers, symbol schemas, and regional reachability. | `httpx` + `websockets` bounded `10s` check; JSON summary saved without leaking keys. | Confirmed reachability status, exact differences in field schemas/units/sequence IDs, and documented rate limits before Phase 3 contracts. |

