---
doc_id: "DOC-ARCH-ADR-ROOT"
title: "Architecture Decision Records (ADRs) Index"
version: "1.0.0"
status: "IN_REVIEW"
implementation_status: "PLANNED"
owner: "Principal Software Architect"
purpose: "Indexes numbered Architecture Decision Records governing messaging, storage, runtime topology, multi-asset adapters, and quantitative architecture."
scope: "All ADRs under docs/architecture/decisions/ on greenfield/main."
dependencies:
  - "docs/architecture/README.md"
  - "docs/architecture/technology-evaluation-matrix.md"
references:
  - "docs/architecture/decisions/adr-0001-three-plane-hybrid-runtime.md"
  - "docs/architecture/decisions/adr-0002-nats-jetstream-for-durable-messaging.md"
  - "docs/architecture/decisions/adr-0003-sqlite-wal-parquet-duckdb-storage-split.md"
assumptions:
  - "Initial ADRs remain IN_REVIEW until Phase 2 PoC evidence confirms memory and recovery behavior."
open_issues:
  - "PoC execution under WI-P2-003 required to graduate ADRs to ACCEPTED"
review_criteria:
  - "Each ADR covers Context, Options Considered, Decision, Resource Justification, and Consequences"
---

# Architecture Decision Records (`docs/architecture/decisions/`)

| ADR ID | Title | Status | PoC Gate |
|---|---|---|---|
| `ARCH-ADR-001` | [adr-0001-three-plane-hybrid-runtime.md](adr-0001-three-plane-hybrid-runtime.md) | `IN_REVIEW` | `WI-P2-003` (Combined runtime & process isolation) |
| `ARCH-ADR-002` | [adr-0002-nats-jetstream-for-durable-messaging.md](adr-0002-nats-jetstream-for-durable-messaging.md) | `IN_REVIEW` | `WI-P2-003` (Throughput, ACK/replay, restart) |
| `ARCH-ADR-003` | [adr-0003-sqlite-wal-parquet-duckdb-storage-split.md](adr-0003-sqlite-wal-parquet-duckdb-storage-split.md) | `IN_REVIEW` | `WI-P2-003` (SQLite WAL concurrency & DuckDB scan) |

## Authoring Rules
1. Name files `adr-NNNN-<kebab-title>.md`.
2. Explicitly reject heavyweight distributed alternatives unless backed by quantitative 8 GB workload justification.
