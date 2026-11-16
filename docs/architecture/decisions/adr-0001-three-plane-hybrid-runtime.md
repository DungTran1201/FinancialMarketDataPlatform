---
doc_id: "ARCH-ADR-001"
title: "ADR-0001: Three-Plane Modular Architecture & Hybrid Windows+NATS PoC Runtime"
version: "1.0.0"
status: "IN_REVIEW"
implementation_status: "PLANNED"
owner: "Principal Software Architect"
purpose: "Records architectural choice separating Realtime Capture/API from Batch DuckDB/Quant work using Clean Port/Adapter boundaries and Hybrid Native Windows + NATS PoC runtime."
scope: "Process topology and module isolation on greenfield/main."
dependencies:
  - "docs/architecture/system-architecture-document.md"
references:
  - "docs/phase-reports/phase-1-acceptance-and-decisions.md"
assumptions:
  - "DEC-P0-002 selects Hybrid Native Windows + containerized NATS JetStream for Phase 2 validation."
open_issues:
  - "Graduate from IN_REVIEW to ACCEPTED upon Phase 2 PoC evidence completion (WI-P2-003)."
review_criteria:
  - "Evaluates monolithic single-process vs multi-container compose vs hybrid 3-unit design"
---

# ADR-0001: Three-Plane Modular Architecture & Hybrid Runtime Split

## Context

The platform must acquire live multi-exchange feeds (`Binance`, `OKX`), run DuckDB analytical scans and walk-forward quant training, and serve a 15-module analytical SPA **within an `8 GB` Windows machine (`7.85 GB` total, `1.58 GB` free before cleanup)**. Legacy multi-service Docker stacks exhaust RAM, whereas putting heavy analytical queries directly inside a single FastAPI `asyncio` event loop freezes live WebSocket ingestion.

## Options Considered

1. **Single All-in-One Python Process**: Simplest startup, zero IPC, **rejected** because DuckDB/LightGBM CPU & GIL pressure directly destabilize async exchange WS ping/pong and L2 book sequencing.
2. **Full Multi-Container Docker Compose (7+ microservices + DBs)**: Good isolation, **rejected** for baseline due to high WSL2/container RAM overhead exceeding host constraints (`DEC-P0-002`).
3. **Three Lightweight Processes / Units Behind Port Interfaces (Selected Proposal)**:
   - Unit 1: Containerized `NATS JetStream` (persistent bus).
   - Unit 2: Native Python `fmdp-realtime-api` (exchange WS/REST + hot microstructure + FastAPI).
   - Unit 3: Native Python `fmdp-batch-quant-worker` (centralized Parquet writer + SQLite WAL writer + bounded DuckDB + Quant/Inference).

## Decision

Adopt **Option 3**, using **Hybrid Native Windows Python 3.12 + Containerized NATS JetStream** for Phase 2 PoC & early build (`DEC-P0-002`), preserving pure domain protocol ports so Unit 2 & Unit 3 can later be containerized cleanly under a compact Linux Compose profile (`2–3` containers total).

## Consequences

- **Positive**: Isolates heavy analytics from ingestion latency (`NFR-PERF-02`), keeps idle RAM `< 500 MB`, avoids WSL2 overhead for Python/DuckDB/UI.
- **Negative**: Requires clean IPC (`NATS` events + `SQLite WAL` single writer / `Parquet` partition visibility) and explicit startup/shutdown orchestration across 2 Python processes + 1 Docker container.

