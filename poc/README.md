# Phase 2 Isolated Technology Proof-of-Concept (`poc/`)

This directory contains **isolated, reproducible Phase 2 benchmarks and external exchange probes** authorized under `DEC-P0-002` (Hybrid Native Windows Python 3.12 + Containerized NATS JetStream).

> **Strict Isolation Rule**: Scripts here evaluate technology suitability and measure real RAM/CPU/disk/latency limits on this `7.85 GB` host. None of this code is production implementation (`src/` remains clean until Phase 4).

## Execution Order

1. Start bounded NATS JetStream container:
   ```powershell
   docker compose -f poc/docker-compose.nats.yml up -d
   ```
2. Run isolated probes via greenfield `.venv`:
   - `POC-01` (NATS durability, ACK/NAK, DLQ, container restart, replay):
     `.\.venv\Scripts\python.exe poc/poc_01_nats_jetstream.py`
   - `POC-02` (Bounded hot cache + concurrent SQLite WAL):
     `.\.venv\Scripts\python.exe poc/poc_02_cache_sqlite.py`
   - `POC-03` (1M-row ZSTD Parquet: DuckDB vs Polars rollup & ASOF pit-join):
     `.\.venv\Scripts\python.exe poc/poc_03_analytics_parquet.py`
   - `POC-04` (Combined Hybrid multi-process + `SIGKILL` crash/replay recovery):
     `.\.venv\Scripts\python.exe poc/poc_04_combined_hybrid.py`
   - `POC-05` (Live public Binance + OKX REST/WSS API & schema probe):
     `.\.venv\Scripts\python.exe poc/poc_05_exchange_probe.py`
