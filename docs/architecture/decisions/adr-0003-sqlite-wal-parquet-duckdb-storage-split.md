---
doc_id: "ARCH-ADR-003"
title: "ADR-0003: Polyglot Storage Split — Hot LRU, Centralized SQLite WAL & Parquet/DuckDB"
version: "1.0.0"
status: "IN_REVIEW"
implementation_status: "PLANNED"
owner: "Data Platform Architect & Analytics Engineer"
purpose: "Defines strict separation of hot ephemeral state, SQLite WAL transactional metadata, and Parquet/DuckDB analytical lakehouse storage."
scope: "All persistence layers across Planes A, B, and C."
dependencies:
  - "docs/architecture/technology-evaluation-matrix.md"
  - "docs/architecture/resource-budget.md"
references:
  - "docs/testing-and-operations/phase-2-poc-benchmark-plan.md"
assumptions:
  - "All Parquet partition writes and SQLite mutations route through centralized single-writer strategies."
open_issues:
  - "Benchmark SQLite concurrent read/write throughput under PoC workload."
review_criteria:
  - "Zero SQLite usage as a Redis tick-cache replacement; zero DuckDB concurrent OLTP writes"
---

# ADR-0003: Bounded In-Process Hot State + Centralized SQLite WAL + Parquet/DuckDB

## Context

Under Section 3.4, the storage design must eliminate PostgreSQL/Redis/ClickHouse daemon overhead while obeying strict anti-pattern rules: no SQLite-as-Redis hot cache, no DuckDB high-concurrency OLTP writes, and centralized write safety.

## Options Considered

1. **All-in-SQLite (ticks + candles + metadata)**: **Rejected** (violates §3.4; write locks and large table bloat degrade real-time performance).
2. **All-in-DuckDB (online OLTP updates + analytics)**: **Rejected** (violates §3.4; single-writer lock conflicts under multi-service mutations).
3. **Three-Tier Purpose-Fit Split (Selected Proposal)**:
   - **Ephemeral Hot State**: Bounded in-process dicts/ring buffers inside `fmdp-realtime-api` (`BBO`, `L2 book`, recent closed bars).
   - **Durable Operational Metadata**: **SQLite WAL** (`busy_timeout=5000`, `synchronous=NORMAL`) behind a serialized writer service for instruments, watermarks, job states, DQ verdicts, lineage, experiments, models, and forecast records.
   - **Analytical Lakehouse**: Partitioned **Apache Parquet (`ZSTD`)** flushed via centralized micro-batch atomic replace, queried read-only by bounded **DuckDB + Polars** inside Worker Unit C.

## Decision

Adopt Option 3 as the core persistence architecture, verified by Phase 2 SQLite concurrency and DuckDB/Parquet scan benchmarks (`WI-P2-003`).

## Consequences

- **Positive**: Zero external database server RAM overhead (`0 MB` idle daemon), ACID metadata + fast columnar analytics + easy filesystem snapshots/backups.
- **Negative**: Horizontal scale-out beyond one host requires implementing distributed adapters (`PostgresMetadataAdapter`, `ObjectStoreParquetAdapter`) behind existing ports.

