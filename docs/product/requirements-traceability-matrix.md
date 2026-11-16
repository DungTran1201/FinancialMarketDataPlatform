---
doc_id: "PRD-RTM-001"
title: "Requirements Traceability Matrix (RTM) & Pre-Phase 2 Conflict Audit"
version: "1.0.0"
status: "ACCEPTED"
implementation_status: "NOT_IMPLEMENTED"
owner: "Requirements Engineer & System Analyst"
purpose: "Maps every Business Rule and Capability to SRS Requirements, Use Cases, Acceptance Criteria, Planned Architecture Components, and Work Items; audits and resolves conflicts/ambiguities prior to Phase 2."
scope: "Complete v1 scope across Data Plane, Intelligence Plane, Application Plane, and 8 GB Constraints."
dependencies:
  - "docs/product/srs.md"
  - "docs/product/use-cases.md"
  - "docs/product/acceptance-criteria.md"
references:
  - "docs/phase-reports/phase-1-acceptance-and-decisions.md"
  - "docs/work-items/phase-0-and-1-work-items.md"
assumptions:
  - "Baseline RTM protected under version 1.0.0; any Phase 2 trade-off affecting requirement scope requires explicit change review."
open_issues:
  - "OPEN-P1-003 (Bronze C: retention cap days vs GB) finalized after Phase 2 disk growth benchmark"
review_criteria:
  - "100% FR/NFR coverage in RTM"
  - "Zero unresolved critical conflicts blocking Phase 2 architecture & PoC planning"
---

# Requirements Traceability Matrix (`RTM v1.0.0`)

## 1. End-to-End Traceability Matrix

| BR / Constraint | System Capability | SRS Req IDs | Use Case(s) | Acceptance Criteria | Target Architecture Component (`Phase 2`) | Tracking Work Item |
|---|---|---|---|---|---|---|
| `BR-METH-001`, `OPEN-P1-002` | `CAP-DP-ING`, `CAP-APP-CFG` | `FR-DP-ING-001..005`, `FR-APP-UI-015` | `UC-01`, `UC-02`, `UC-03` | `AC-01`, `AC-14` | Exchange Adapters (`Binance`, `OKX`) + Canonical Instrument Catalog (`SQLite WAL`) | `WI-P2-001`, `WI-P2-003` |
| `CON-TECH-002`, `DEC-P0-002` | `CAP-DP-STR` | `FR-DP-STR-001..003`, `NFR-REL-001`, `NFR-RES-003` | `UC-02`, `UC-09`, `UC-10` | `AC-02`, `AC-03`, `AC-11`, `AC-15` | Containerized `NATS JetStream` + Pull Consumers + DLQ Stream | `WI-P2-001`, `WI-P2-002` |
| `BR-METH-002`, `BR-METH-004` | `CAP-DP-RTP` | `FR-DP-RTP-001..005`, `NFR-PERF-01` | `UC-02`, `UC-05` | `AC-04`, `AC-09` | Process 1 Microstructure & Book Engine + Bounded In-Process Hot Cache | `WI-P2-001`, `WI-P2-003` |
| `BR-METH-003`, `CON-HW-002` | `CAP-DP-LAK` | `FR-DP-LAK-001..005`, `NFR-RES-002`, `NFR-PERF-02` | `UC-03`, `UC-04` | `AC-05`, `AC-09`, `AC-10` | Batch Lakehouse Writer (`Parquet ZSTD`) + `DuckDB` Isolated Query Worker + `SQLite WAL` | `WI-P2-001`, `WI-P2-004` |
| `CON-HW-001`, `DEC-P0-002` | All Planes | `NFR-RES-001..003`, `NFR-MOD-001`, `NFR-OBS-001` | `UC-10` | `AC-09`, `AC-10`, `AC-11` | `8 GB Resource Budget`, Protocol Ports & Metrics Telemetry Collector | `WI-P2-001`, `WI-P2-004` |
| `BR-METH-005`, `BR-METH-006` | `CAP-INT-RES`, `CAP-INT-FEA` | `FR-INT-RES-001..003`, `FR-INT-FEA-001..002` | `UC-06` | `AC-06` | Point-in-Time `DuckDB/Polars` Dataset Builder + Parity Feature Engine + Research Registry | `WI-P2-004`, `WI-P2-005` |
| `BR-METH-005`, `BR-METH-006` | `CAP-INT-MOD`, `CAP-INT-INF` | `FR-INT-MOD-001..002`, `FR-INT-INF-001..003`, `NFR-PERF-03` | `UC-07`, `UC-08` | `AC-07`, `AC-08` | Isolated Quant Trainer (`Tier 0/1/2`) + Walk-Forward Evaluator + DQ-Aware Inference Scorer | `WI-P2-004`, `WI-P2-005` |
| `NFR-SEC-01`, `CON-GOV-001` | `CAP-APP-SEC`, `CAP-DP-SRV`, `UI-01..15` | `FR-DP-SRV-001..002`, `FR-APP-SEC-001..002`, `FR-APP-UI-001..015` | `UC-05`, `UC-10` | `AC-12`, `AC-13` | `FastAPI` Edge Gateway (RBAC + Bounded WS/SSE Conflation) + Lightweight TS SPA | `WI-P2-001`, `WI-P2-006` |

## 2. Pre-Phase 2 Conflicts, Ambiguities & Missing Acceptance Criteria Audit (`P1-PKG-001` Gate Condition)

Before initiating Phase 2 design & PoC verification, the Requirements team audited `P1-PKG-001` and resolved the following **6 conflicts/gaps**:

| Audit ID | Issue Found in Draft Baseline | Resolution Applied in `v1.0.0` |
|---|---|---|
| `AUD-P1-001` | **Missing Exchange Normalization Acceptance Criterion**: `OKX` uses contract sizes (`ctVal` e.g. `0.01 BTC/contract` on swaps) and `seqId`/`prevSeqId`, whereas `Binance` uses base/quote quantities and `U`/`u`/`pu`. Original `AC-01` tested ID uniqueness only, not unit parity. | **Resolved**: Added explicit `contract_multiplier` to `BR-METH-001` and added binary **`AC-14`** verifying Binance & OKX contract-unit & book-sequence normalization parity. |
| `AUD-P1-002` | **Missing Hybrid Runtime Restart AC**: `DEC-P0-002` mandates testing NATS container persistence + native Windows Python process recovery, which was only partially implied in `AC-03`. | **Resolved**: Added **`AC-15`** explicitly validating full container + Python worker restart recovery within `< 30 s`. |
| `AUD-P1-003` | **Ambiguity on `SQLite` vs `Hot State` Latency Split**: `FR-DP-RTP-05` & `NFR-PERF-01` risked developers querying SQLite on tick hot path for instrument lookup. | **Resolved**: In `NFR-MOD-001` / Phase 2 SAD, active registered instrument metadata is cached in-memory by Process 1 upon startup/reload; SQLite WAL receives async metadata/watermark commits only (zero SQLite query per tick). |
| `AUD-P1-004` | **Conflict between Unbounded Multi-Asset History & `C:` `15.54 GB` Free Disk**: Unlimited `depth20`/tick Bronze archival vs `CON-HW-002` disk cap (`<= 5.0 GB`). | **Resolved**: Bounded `NFR-RES-002` explicitly at `<= 5.0 GB` on `C:`, requiring configurable TTL pruning, ZSTD compaction, and optional `E:\` cold-tier mount (`OPEN-P1-003`). |
| `AUD-P1-005` | **Ambiguity on Model Fallback vs Abstention**: `FR-INT-INF-002` allowed either "abstain or fall back to Tier 0", risking silent fallback masking broken feeds. | **Resolved**: In `BR-METH-005` & `AC-08`, whenever feed is stale or book is unsynced, inference **MUST emit `abstention_flag=True` and explicit `degraded_reason`**, even if an ancillary baseline reference value is shown separately. |
| `AUD-P1-006` | **Scope Clarity on Options & Derivatives**: Original SRS left OKX Options ambiguous for v1 `R1`. | **Resolved**: `R1` core targets **Spot, Perpetual/Swap, and Expiry/Delivery Futures** on Binance & OKX (`AC-14`), while keeping schema extensible for Options (`OPEN-P1-007` checked during Phase 2 OKX API capability probe). |

