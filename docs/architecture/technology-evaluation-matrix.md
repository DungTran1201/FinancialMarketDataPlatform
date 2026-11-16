---
doc_id: "ARCH-TECH-001"
title: "Technology Evaluation Matrix — Lightweight 8 GB Stack"
version: "1.0.0"
status: "IN_REVIEW"
implementation_status: "PLANNED"
owner: "Principal Software Architect & Data Infrastructure Engineer"
purpose: "Evaluates candidate technologies per Section 3.3 and Section 3.4 constraints, justifies selections against the 8 GB host limit, and documents trade-offs and non-selected heavyweight tools."
scope: "Messaging, Hot State, Metadata DB, Analytical Engine, Lakehouse Storage, Backend, Quant ML, and Frontend stack."
dependencies:
  - "docs/product/srs.md"
  - "docs/phase-reports/phase-0-discovery-report.md"
references:
  - "docs/testing-and-operations/phase-2-poc-benchmark-plan.md"
  - "docs/architecture/resource-budget.md"
assumptions:
  - "Selected candidates must be empirically confirmed by Phase 2 isolated PoCs before Phase 3/4 lock-in."
open_issues:
  - "Validate DuckDB vs Polars memory peaks under 5M-row scan in WI-P2-003."
review_criteria:
  - "Justifies every candidate against Section 3.4 prohibitions and 8 GB hardware cap"
---

# Technology Evaluation Matrix (`Phase 2`)

## 1. Messaging & Event Streaming

| Candidate | Pros (8 GB Host) | Cons / Trade-Offs | Preliminary Verdict |
|---|---|---|---|
| **NATS JetStream** (Containerized lightweight Go binary) | Single ~15–20 MB image; ~60–150 MB RAM; disk FileStore w/ replay, pull consumers, consumer groups, `max_deliver` DLQ & deduplication windows; zero JVM. | Requires running single Docker container (`DEC-P0-002`) during PoC/prod; smaller analytical ecosystem than Kafka Connect. | **Primary Candidate (`ARCH-ADR-002`)** |
| **Redis Streams** | Fast memory+AOF streams; consumer groups (`XREADGROUP`). | Keeps full un-trimmed stream history primarily in RAM (conflicts with 8 GB constraint on backlogs/replay). | **Rejected** (Memory pressure on large replay backlogs) |
| **Apache Kafka / Redpanda** | Enterprise partitioning & compaction. | Explicitly restricted by §3.4; JVM/Kraft or multi-GB memory footprint unacceptable on `7.85 GB` Windows workstation (`1.58 GB` free). | **Rejected** (§3.4 Hardware mismatch) |
| **In-Process `asyncio.Queue` / Memory PubSub** | Zero infra dependency. | Explicitly **forbidden** (§3.4): zero persistence across crash/restart, no durable ACK/replay. | **Rejected** (Violates durability rule) |

## 2. Hot State & Transactional Metadata

| Layer | Candidate Selected | Rejected Alternatives & Why |
|---|---|---|
| **Ephemeral Hot State** | **Bounded In-Process Cache** (`LRU` + `deque` capped per symbol in `fmdp-realtime-api`) | **SQLite** rejected for tick hot-path frequency (§3.4 write lock overhead); **Redis** deferred as unnecessary standalone daemon when single-node API reads in-process state in sub-milliseconds. |
| **Metadata, Watermarks, Jobs, Experiments, Model Registry** | **SQLite WAL Mode (`3.45.3`)** w/ serialized single async writer | **PostgreSQL** avoided by §3.4 unless distributed multi-writer concurrency becomes mandatory; SQLite gives ACID WAL transactions, zero container RAM (`< 15 MB`), instant file backup. |

## 3. Analytical Engine & Lakehouse Storage

| Layer | Candidate Selected | Alternative Evaluation & Why |
|---|---|---|
| **Analytical Storage** | **Apache Parquet (`ZSTD`) on Local SSD** via centralized micro-batch writer + periodic compaction | **Delta Lake / Iceberg REST catalog / MinIO** avoided in v1 to prevent S3/REST container RAM & small-file complexity; clean directory partitioning + SQLite lineage gives zero-daemon ACID atomic replacement (`os.replace`). |
| **Analytical Engine** | **DuckDB (`memory_limit` capped) + PyArrow** (with selective Polars streaming transforms) | **DuckDB** (`2.0.0`) validated in `POC-03` (`1M` rows: **`367.35 MB` peak RSS**, `24.14 ms` median rollup, `122.98 ms` 50k `ASOF` join) beating Polars (`957.86 MB` peak RSS during `join_asof` sort). ClickHouse/Spark rejected (§3.4). |

## 4. Backend, Quant Intelligence & Frontend Stack

| Layer | Candidate Selected | Rationale & Trade-Offs |
|---|---|---|
| **Backend API** | **Python 3.12 + FastAPI + Uvicorn + Pydantic v2 + `websockets` + `httpx`** | Native Windows/Linux compatibility, async I/O, typed schema contracts, lightweight RSS (`~150–300 MB`), zero extra runtime daemons. |
| **Quant & ML** | **NumPy + SciPy + Statsmodels + `arch` + `scikit-learn` + `LightGBM`** (strictly incremental Tier 0 $\rightarrow$ Tier 2) | Runs fast on CPU (`i5-12400F`); avoids bloated PyTorch/CUDA/LLM runtime GBs unless Tier 3 sequence/DeepLOB research explicitly proves gain later. |
| **Frontend SPA** | **Vanilla TypeScript (`^5.7`) + Vite + TradingView Lightweight Charts / uPlot (Canvas)** | Zero framework bloat, ultra-low bundle & browser heap (`< 150 MB`), 60 FPS live candlestick/depth rendering cleanly reflecting only verified backend capabilities. Evaluated vs heavy charting suites in Phase 2/3. |
