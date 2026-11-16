---
doc_id: "PRD-MAP-001"
title: "Initial Product Roadmap (Releases R0-R4)"
version: "1.0.0"
status: "ACCEPTED"
implementation_status: "NOT_IMPLEMENTED"
owner: "Product Manager"
purpose: "Defines incremental releases from foundation PoCs to verified 8 GB production readiness."
scope: "Phases 0 through 9 on greenfield/main."
dependencies:
  - "docs/product/srs.md"
  - "docs/product/acceptance-criteria.md"
references:
  - "docs/work-items/phase-0-and-1-work-items.md"
  - "docs/work-items/phase-2-work-items.md"
assumptions:
  - "Each release builds strictly on verified capabilities from prior phases without UI-first mocks."
open_issues:
  - "DEC-P0-003 disk placement decision confirmed prior to Release R1 storage tuning."
review_criteria:
  - "Every release aligns cleanly with Phases 1-9"
---

# Initial Product Roadmap (`R0` – `R4`)

| Release | Name | Deliverables & Core Value | Phases | Acceptance Gate |
|---|---|---|---|---|
| **`R0`** | **Architecture, PoCs & Contracts** | Clean `greenfield/main`, verified Hybrid NATS + DuckDB + Polars + SQLite PoCs, SAD/ADRs/Diagrams, Canonical Multi-Asset & API/Feature Contracts. | `Phases 0–3` | Phase 2 PoC raw evidence report + Phase 3 contract tests passing. |
| **`R1`** | **Multi-Exchange Data Core** | Binance + OKX Spot/Perp/Expiry connectors, NATS JetStream durable delivery + DLQ, L2 book sync, OFI/CVD/Derivatives engine, Bronze/Silver/Gold Parquet + DuckDB query APIs + Ops metrics. | `Phase 4` | `AC-01`..`AC-05`, `AC-09`, `AC-14`, `AC-15`. |
| **`R2`** | **Quant Research & Inference Engine** | Leak-free dataset builder, online/offline feature parity, Tier 0/1/2 models, purged walk-forward net-of-cost evaluation, Model Registry, DQ-gated inference w/ abstention & drift monitor. | `Phase 5` | `AC-06`..`AC-08`. |
| **`R3`** | **15-Module Analytical Workbench & Security** | RBAC + Auth API, lightweight TS SPA covering all 15 modules driven exclusively by verified `R1`/`R2` backend contracts. | `Phase 6` | `AC-12`, `AC-13`. |
| **`R4`** | **Endurance, Security & Production Readiness** | E2E integration, kill/replay chaos drills, SQLite/Parquet backup-restore verification, 2-hour 8 GB memory/CPU/disk soak test, formal Readiness Report. | `Phases 7–9` | `AC-01`..`AC-15` + Section 9 13-point gate. |

