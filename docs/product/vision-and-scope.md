---
doc_id: "PRD-VIS-001"
title: "Product Vision, System Scope, Boundaries & Multi-Exchange Strategy"
version: "1.0.0"
status: "ACCEPTED"
implementation_status: "NOT_IMPLEMENTED"
owner: "Product Manager & Principal Business Analyst"
purpose: "Establishes product purpose, target personas, in-scope analytical pillars, strict non-goals, external exchange dependencies (Binance & OKX), and multi-asset principles."
scope: "End-to-end scope of the Multi-Asset Data Platform & Quantitative Intelligence System on branch greenfield/main."
dependencies:
  - "docs/phase-reports/phase-0-discovery-report.md"
  - "docs/phase-reports/phase-1-acceptance-and-decisions.md"
references:
  - "docs/product/srs.md"
  - "docs/product/glossary.md"
assumptions:
  - "ASM-P1-001: Public Binance and OKX WebSocket/REST endpoints cover Spot, Perpetual/Swap, and Expiry Futures without trading API credentials."
  - "ASM-P1-002: Single-node user concurrency is 1-5 human analysts/researchers plus background ingestion/inference workers."
open_issues:
  - "OPEN-P1-006: Confirm regional accessibility and exact rate-limit tiers of api.binance.com and www.okx.com from this host during Phase 2 connector spike."
  - "OPEN-P1-007: Confirm whether Options instruments on OKX enter Release R1 or defer to R2+ after Spot/Perp/Expiry validation."
review_criteria:
  - "All 12 project vision capabilities covered without claiming black-box trading"
  - "Explicit Binance + OKX structural distinctions preserved"
---

# Product Vision & Scope

## 1. Product Vision

Design and validate a **single-node, resource-disciplined Multi-Asset Data Platform combined with Quantitative Intelligence** capable of transforming raw streaming and historical exchange feeds into **transparent microstructure analytics, derivatives positioning insight, reproducible quantitative research, and calibrated forecasts with explicit uncertainty bounds**.

The platform is strictly an **evidence-based decision support and quantitative research system** — **never a black-box automated trading bot**.

## 2. Target Users & Roles

| Role ID | Persona | Core Responsibilities & Permissions |
|---|---|---|
| `ROLE-QR` | **Quantitative Researcher / Financial Data Scientist** | Curate leak-free point-in-time datasets, run statistical tests/EDA, define parity-checked features, evaluate Tier 0–2 models via purged walk-forward validation. |
| `ROLE-QA` | **Market Analyst / Discretionary Trader** | Explore multi-asset dashboards, order flow (OFI/CVD), L2 liquidity/slippage profiles, funding/OI positioning, cross-asset lead-lag, volatility regimes, and live forecast intervals. |
| `ROLE-MLE` | **ML / MLOps Engineer** | Govern Model Registry, promote models strictly beating Tier 0 baselines, monitor prediction drift/calibration, configure abstention/fallback rules. |
| `ROLE-OPS` | **Data Platform / SRE Operator** | Configure tracked instruments, run bounded historical backfills, manage NATS lag/DLQ replay, compaction, disk retention, backups, and 8 GB host health. |
| `ROLE-ADM` | **Security / Platform Admin** | Manage local accounts, hashed API keys, RBAC capabilities, and rate-limit protections. |

## 3. Initial Multi-Exchange & Multi-Asset Scope (`OPEN-P1-002`)

Supported venues in initial baseline:
1. **Binance**: Spot (`api.binance.com` / `stream.binance.com`), USDT-M Perpetual & Expiry/Delivery Futures (`fapi.binance.com` / `fstream.binance.com`, plus COIN-M where configured).
2. **OKX**: Unified v5 API (`www.okx.com` / `ws.okx.com`) covering `SPOT`, `SWAP` (Perpetual), `FUTURES` (Expiry/Delivery), and optional `OPTION` evaluation (`OPEN-P1-007`).

**Exchange Normalization Mandate**: Binance and OKX differ structurally in symbol formats (`BTCUSDT` vs `BTC-USDT-SWAP`), order book sequencing (`u`/`pu` vs `seqId`/`prevSeqId`), volume units (base/quote vs contracts x contract value), funding intervals, and timestamp epochs. Each venue MUST use a dedicated connector and source adapter translating into one canonical model while archiving verbatim raw payload provenance.

## 4. Explicit Non-Goals & Exclusions

- No order execution, smart order routing, exchange account keys, custody, or fiat settlement.
- No conflation of trading volume, Open Interest delta, or funding rate with "net capital inflow".
- No silent fallback to hardcoded mock prices, synthetic candles, or uncalibrated forecast displays.
- No heavyweight distributed middleware (Kafka, ClickHouse, Spark, Flink, Postgres, Kubernetes) without quantified overriding proof against the `7.85 GB` host budget.

