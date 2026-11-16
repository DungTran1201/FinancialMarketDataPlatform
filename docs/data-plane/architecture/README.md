---
doc_id: DP-ARCH-ROOT-001
title: "Data Plane Architecture Index"
doc_type: index
plane: data-plane
scope_level: plane
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: data-architect
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/data-plane/architecture/README.md"
related_docs:
  - DP-ROOT-001
  - DP-ARCH-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Indexed Data Plane architecture viewpoints, storage design, resilience, observability, ADRs, and diagrams."
---

# Data Plane Architecture

- [data-plane-architecture.md](data-plane-architecture.md) (`DP-ARCH-001` — Plane boundaries, worker topology, hot/historical separation & 12-stage execution)
- [data-storage-architecture.md](data-storage-architecture.md) (`DP-ARCH-STOR-001` — Polyglot store roles: Redis, ClickHouse, SQLite/Postgres watermarks, Bronze/Silver/Gold Parquet & Iceberg)
- [scalability-and-resilience.md](scalability-and-resilience.md) (`DP-ARCH-RES-001` — Delivery guarantees, gap healing, DLQ isolation, backpressure & SPOFs)
- [observability-and-monitoring.md](observability-and-monitoring.md) (`DP-ARCH-OBS-001` — 10-timestamp tracing, Prometheus metrics, alerts & Grafana gap)
- [security-and-trust-boundaries.md](security-and-trust-boundaries.md) (`DP-ARCH-SEC-001` — Provider ingress, DB roles & env secret/config mismatches)
- Decision: [adr-0001-async-delivery-and-idempotent-keys.md](decisions/adr-0001-async-delivery-and-idempotent-keys.md) (`ADR-DP-001`)
- Diagrams (`is_authoritative: false`): [data-plane-c4-container.md](diagrams/data-plane-c4-container.md) (`DIAG-DP-C4-001`), [medallion-and-streaming-dfd.md](diagrams/medallion-and-streaming-dfd.md) (`DIAG-DP-DFD-001`)
