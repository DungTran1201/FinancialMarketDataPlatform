# Financial Market Data Platform & Quantitative Intelligence (Greenfield)

Resource-disciplined multi-asset Data Platform, Quantitative Intelligence workbench, and Evidence-First analytical SPA built from a clean baseline on branch `greenfield/main`.

## Core Constraints & Scope

- **Hardware Target**: Single-node `8 GB RAM` workstation (`C:` SSD disk-quota aware; optional `E:` cold storage).
- **Initial Exchanges**: Binance and OKX (`Spot`, `Perpetual Futures`, `Expiry/Delivery Futures`).
- **Initial PoC Runtime (`DEC-P0-002`)**: Native Windows Python `3.12` + lightweight containerized **NATS JetStream** + **DuckDB** + **Parquet** + **SQLite WAL** (metadata/checkpoints only) + bounded in-process hot state.
- **Current Lifecycle Stage**: Phase 1 Baseline Accepted with Conditions $\rightarrow$ Repository Preparation & Phase 2 Architecture / Benchmark Planning.

## Entrypoints

- Agent Rules & Workflow: [AGENTS.md](AGENTS.md) | [.agents/README.md](.agents/README.md)
- Documentation Hub: [docs/README.md](docs/README.md)
- Validation Suite: `.\.venv\Scripts\python.exe tools/validators/run_all.py`

