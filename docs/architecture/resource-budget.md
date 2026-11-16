---
doc_id: "ARCH-RES-001"
title: "8 GB Resource Budget, Concurrency Limits & Storage Quota Plan"
version: "1.0.0"
status: "IN_REVIEW"
implementation_status: "PLANNED"
owner: "Performance Engineer & SRE"
purpose: "Defines explicit RAM, CPU, queue, WebSocket buffer, and local SSD budgets anchored to Phase 0 host telemetry (7.85 GB RAM, 15.54 GB free C:)."
scope: "PoC Phase 2 and v1 Single-Node Deployment."
dependencies:
  - "docs/phase-reports/phase-0-discovery-report.md"
  - "docs/product/srs.md"
references:
  - "docs/testing-and-operations/phase-2-poc-benchmark-plan.md"
assumptions:
  - "Memory budgets below are design limits to be empirically verified during WI-P2-003 and Phase 8 endurance tests."
open_issues:
  - "WSL2 .wslconfig memory limit tuning if Docker Desktop VM consumes >1.5 GB idle overhead."
  - "DEC-P0-003 confirmation on moving cold Parquet history to E: (271.82 GB free)."
review_criteria:
  - "Sum of nominal service RSS + WSL/Docker overhead respects host RAM without paging storms"
---

# 8 GB Host Resource Budget & Quotas

## 1. Host Baseline vs Runtime Allocation

- **Host Measured Specs**: Windows 10 Pro, i5-12400F (`6C/12T`), **`7.85 GB` Physical RAM** (`1.58 GB` free during heavy IDE inspection), `C:` **`15.54 GB` free**, `E:` **`271.82 GB` free**.
- **WSL2 / Docker Desktop Mitigation (`CON-HW-001`)**: For Hybrid PoC runs, configure `%USERPROFILE%\.wslconfig` (`memory=1536MB` or `2048MB`, `processors=4`) when running Docker Desktop so Windows + Python + browser retain safe headroom.

## 2. Process-by-Process Memory & CPU Targets (`[TARGET]`)

| Component | Idle RSS `[TARGET]` | Nominal Streaming RSS `[TARGET]` | Hard Cap / Peak Limit | CPU / Concurrency Bound |
|---|---|---|---|---|
| **1. `nats-jetstream` container** | `30–60 MB` | `80–150 MB` | **`256 MB`** container `mem_limit` | `1–2` vCPU |
| **2. `fmdp-realtime-api` (Native Python)** | `90–140 MB` | `180–320 MB` | **`450 MB`** watchdog warn | Async single loop (`~20–30` active symbols max) |
| **3. `fmdp-batch-quant-worker` (Python + DuckDB)** | `80–120 MB` | `200–450 MB` | **`1,024 MB`** (`SET memory_limit='768MB'` in DuckDB) | Bounded `2–4` DuckDB threads (`1` worker queue) |
| **4. Frontend Dev/Static Assets (Browser/Vite)** | `40–100 MB` | `100–180 MB` | **`250 MB`** | Client WS conflation <= 20 msg/s UI render |
| **Total Application Stack** | **`~240–420 MB`** | **`~0.56–1.10 GB`** | **`<= 1.98 GB` app peak** (plus `<= 1.2 GB` WSL2 VM overhead = **`<= 3.2 GB` total**) | Leaves margin within `7.85 GB` host |

## 3. Bounded Queue & Cache Design Limits

| Structure | Maximum Bound Target | Overflow / Backpressure Policy |
|---|---|---|
| Hot Trade Ring Buffer (per symbol) | `1,000` ticks | Ring overwrite oldest (Bronze/Silver holds full durable history) |
| Hot L2 Order Book Snapshot | Top `100` levels bid/ask per active instrument | Fixed-depth truncated view in hot RAM; resync clears invalid state |
| Hot OHLCV Cache | `500` recent closed bars per `(instrument, interval)` | Older bars queried via isolated DuckDB Parquet worker |
| JetStream Raw / Normalized Streams | `max_bytes: 512 MB` raw, `512 MB` norm (`max_age: 24h`) | Pull-consumer `max_ack_pending: 500`; reject/trim oldest expired segments past `1 GB` disk ceiling |
| FastAPI Client WebSocket Outbox | `1` latest snapshot per `(client, channel, symbol)` | Coalesce / drop stale intermediate frames cleanly rather than blocking server |

## 4. Storage Quota on `C:` (`15.54 GB` Free) vs Optional `E:`

- Slim greenfield `.venv`: target `<= 350–450 MB` (replaces `1.40 GB` legacy bloat).
- JetStream FileStore cap: **`<= 1.0 GB`**.
- Active Hot SQLite WAL + Model Artifacts: **`<= 250 MB`**.
- Working Bronze + Silver + Gold Parquet on `C:` (active recent window, e.g., 7–14 days ZSTD compacted): **`<= 2.5–3.0 GB`** (total runtime footprint safely `< 4.5 GB`).
- **Cold Archival Option (`DEC-P0-003`)**: Multi-month research datasets and cold Parquet partitions route via env config `FMDP_COLD_STORAGE_DIR=E:\FMDPData\parquet` once multi-month research begins.

