---
doc_id: "PHR-000"
title: "Phase 0 — Repository Discovery, Environment Assessment & Baseline Report"
version: "1.0.0"
status: "ACCEPTED"
implementation_status: "VERIFIED"
owner: "Principal Software Architect & System Analyst"
purpose: "Records verified Phase 0 inspection of repository legacy state, Windows host hardware (7.85 GB RAM), constraints, risks, and clean-room decisions."
scope: "Baseline host and repository state captured on 2026-11-16 prior to orphan branch creation."
dependencies:
  - "AGENTS.md"
references:
  - "docs/phase-reports/phase-1-acceptance-and-decisions.md"
assumptions:
  - "Host hardware limits (7.85 GB RAM, 15.54 GB free C:) represent the initial single-node deployment target."
open_issues:
  - "DEC-P0-003 (C: vs E: historical Parquet offloading threshold to be tuned during Phase 2/4)"
review_criteria:
  - "All 10 Phase 0 deliverables accounted for with measured hardware numbers"
---

# Phase 0 — Repository & Environment Discovery Report

## 1. Host Environment & Hardware Measurements (Verified 2026-11-16)

| Component | Measured Specification | Impact / Constraint |
|---|---|---|
| **OS** | Microsoft Windows 10 Pro (64-bit) Build `19045` | `CRLF`/`LF` care; avoid slow heavy Windows bind mounts for DB WALs. |
| **CPU** | 12th Gen Intel Core i5-12400F (`6C / 12T` @ `2500 MHz`) | Isolate CPU-heavy DuckDB/ML loops from async WS ingest. |
| **Physical RAM** | **`7.85 GB` total**, **`1.58 GB` free** at inspection | Hard total platform ceiling $\le 2.2\text{ GB}$ nominal / $\le 3.2\text{ GB}$ peak; avoid multi-GB JVM/OLAP daemons. |
| **WSL2 / Docker** | Docker CLI `28.5.1`, Compose `v2.40.0-desktop.1`; Engine **OFF**; `%USERPROFILE%\.wslconfig` absent | Default WSL2 heuristic (~50% RAM) would starve host unless bounded; justifies Hybrid Native Windows + lightweight NATS container for PoC. |
| **Disk (`C:` / `E:`)** | `C:` `237.86 GB` total / **`15.54 GB` free**; `E:` `465.76 GB` / **`271.82 GB` free** | Enforce strict Bronze/Silver compaction & quotas on `C:`; rebuild slim Python `.venv` without PySpark/Kafka/Iceberg bloat. |
| **Runtimes** | Python `3.12.9` (`py -3.12` / `.venv`), host `python 3.8.10`, `uv 0.11.29`, `Node v24.18.0`, `Git 2.51.0` | Greenfield packages (`duckdb`, `polars`, `nats-py`) absent in legacy `.venv`; `nats-server`/`duckdb` CLI absent on `PATH`. |

## 2. Legacy Repository Inspection & Resolution (`DEC-P0-001`)

Direct inspection on `2026-11-16` confirmed the working tree on `feat/data-plane-production-delivery` (`e7708e0`) still contained legacy code (`src/` `149` files), Documentation V2 (`docs/` `372` files), `frontend/` (`59` files), `deploy/` (`16` files), and `.local_lakehouse/` (`1,709` files).
- **Executed Resolution**: Preserved all legacy branches (`main`, `feat/data-plane-production-delivery`, `arch/*`, `docs/*`) untouched; created isolated orphan branch `greenfield/main`; removed legacy artifacts from `greenfield/main`; replaced legacy V2 hooks/validator with clean greenfield validation (`validate_greenfield.py`).

