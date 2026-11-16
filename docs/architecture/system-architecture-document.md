---
doc_id: "ARCH-SAD-001"
title: "System Architecture Document (SAD) — Resource-Aware Three-Plane Architecture"
version: "1.0.0"
status: "IN_REVIEW"
implementation_status: "PLANNED"
owner: "Principal Software Architect & Data Platform Architect"
purpose: "Defines the three-plane logical boundaries, isolated runtime processes, Hybrid Native Windows + NATS PoC topology, Binance/OKX connector isolation, and failure recovery architecture."
scope: "Data Plane, Intelligence Plane, Application Plane, and Shared Domain Core on single-node 8 GB baseline with clean future scale-out ports."
dependencies:
  - "docs/product/srs.md"
  - "docs/product/requirements-traceability-matrix.md"
references:
  - "docs/architecture/technology-evaluation-matrix.md"
  - "docs/architecture/resource-budget.md"
  - "docs/architecture/threat-model.md"
  - "docs/diagrams/c4-container.md"
  - "docs/diagrams/data-flow-diagram.md"
assumptions:
  - "Real-time capture must remain isolated from heavy DuckDB scans and ML walk-forward training."
  - "SQLite serves metadata, checkpoints, jobs, and model registry only; zero per-tick hot writes go to SQLite."
open_issues:
  - "Verify Docker Desktop WSL2 memory headroom alongside IDE on this 7.85 GB host during WI-P2-003."
review_criteria:
  - "Clean dependency isolation across planes via protocol ports"
  - "Bounded memory and queues across every long-running process"
---

# System Architecture Document (SAD)

## 1. Architectural Strategy for an 8 GB Single-Node System

Rather than deploying heavyweight multi-container JVM/OLAP clusters (Kafka, Spark, ClickHouse, PostgreSQL, Redis) and attempting to shrink them afterward, the architecture splits work into **three lightweight, resource-capped runtime units** built cleanly around typed **adapter ports**:

1. **Runtime Unit A — Containerized NATS JetStream (`nats-jetstream`)**:
   - Single memory-capped Docker container (`mem_limit: 256m`, `127.0.0.1:4222`) using disk-backed FileStore with hard `max_bytes` and `max_age` limits.
   - Guarantees persistent delivery, explicit ACK/NAK redelivery, pull-consumer backpressure (`max_ack_pending`), bounded time/sequence replay, and DLQ subjects (`mkt.dlq.*`) without JVM overhead.
2. **Runtime Unit B — Native Realtime Core & Serving Process (`fmdp-realtime-api`, Windows Python 3.12 asyncio)**:
   - Hosts exchange WebSocket/REST ingestion adapters (**Binance** & **OKX**), canonical normalizer, L2 sequence-validated order book reconstructor, event-time OHLCV & OFI/CVD/liquidity calculators, **bounded in-process LRU/ring hot state**, and **FastAPI** serving REST + latest-state-conflated WS/SSE feeds.
   - Never runs heavy DuckDB scans or ML fitting directly on the `asyncio` event loop; instrument catalog state loads into RAM at startup/reload (`AUD-P1-003` resolution).
3. **Runtime Unit C — Isolated Batch Lakehouse & Quant Worker (`fmdp-batch-quant-worker`, Python 3.12 OS process)**:
   - Pulls durable batches from JetStream (`cg.lakehouse.bronze`), writes ZSTD Parquet (`Bronze -> Silver -> Gold`) using a **centralized single-writer partition micro-batcher** + atomic temp-file rename (`write .tmp -> fsync -> os.replace`).
   - Serializes all SQLite WAL writes (`catalog`, `watermarks`, `backfill_jobs`, `dq_audits`, `experiments`, `model_registry`, `forecasts`) through an asynchronous single-writer gate so concurrent tasks never trigger SQLite write-lock failures.
   - Executes **DuckDB** (`SET memory_limit='768MB'`, thread cap, query timeout) and **Polars** lazy queries + Tier 0/1/2 walk-forward training & calibration in separate worker address space so analytical spikes stay completely isolated from Runtime Unit B.

## 2. Three-Plane & Exchange Adapter Boundaries

- **Shared Core (`domain_core`)**: Canonical `InstrumentId`, `ContractType` (`SPOT | PERPETUAL | DATED_FUTURE | OPTION`), fixed-point `Decimal` types, `EventEnvelope`, `FlowType`, abstract `BusPort`, `HotStatePort`, `MetadataPort`, `AnalyticsQueryPort`, `ExchangeAdapterPort`, `ModelStorePort`. Zero infrastructure imports.
- **Binance & OKX Isolation (`OPEN-P1-002` compliance)**:
  - Each venue implements an isolated `ExchangeAdapterPort` handling vendor symbols (`BTCUSDT` vs `BTC-USDT-SWAP`), order book sequence rules (`u`/`pu` vs `seqId`/`prevSeqId`), quantity unit conversions (base units vs OKX `ctVal` contract multipliers), rate-limit headers, and millisecond UTC epochs.
  - Both raw source metadata/payload digest (Bronze) and normalized canonical `EventEnvelope` preserve `exchange_event_time` and `ingestion_time`.
- **Upward Migration Path**: Because business logic binds solely to typed ports, moving later to Linux Docker Compose or splitting workers onto separate nodes requires swapping configuration/adapters (`NATS` cluster URL or external store adapter) rather than rewriting domain logic.

## 3. Resilience, Backpressure & Restart Recovery Architecture

- **Slow Analytical Consumer**: JetStream pull consumers fetch bounded batches (`batch=200..500`); unconsumed events spool safely to NATS FileStore disk within stream byte cap without swelling Python RAM.
- **Slow UI Client**: FastAPI WebSocket fan-out tracks bounded per-client send queues (`maxsize=1` or small coalescing map per symbol) applying **latest-state-wins conflation** instead of unbounded queuing.
- **L2 Book Gap Recovery**: Sequence mismatch or crossed spread (`best_bid >= best_ask`) immediately sets book status to `UNSYNCED`, suppresses OFI/liquidity metrics (`BR-METH-004`), and schedules rate-limited REST baseline snapshot resync.
- **Crash Recovery**: On ungraceful worker/container restart (`AC-03`, `AC-15`), NATS redelivers unacknowledged events from durable consumer offsets, atomic Parquet temp writes discard partial `.tmp` files cleanly, and Silver natural-key deduplication avoids duplicate final rows.
