---
doc_id: "PRD-GLOSS-001"
title: "Multi-Asset Market Data & Quantitative Glossary"
version: "1.0.0"
status: "ACCEPTED"
implementation_status: "NOT_APPLICABLE"
owner: "Quantitative Researcher & Principal Business Analyst"
purpose: "Establishes unambiguous definitions distinguishing market flows, contract types, timestamps, and quantitative validity terms."
scope: "All specifications, UI labels, schemas, and code comments across greenfield/main."
dependencies:
  - "docs/product/vision-and-scope.md"
references:
  - "docs/product/srs.md"
assumptions:
  - "All team roles adopt these canonical terms without aliasing."
open_issues: []
review_criteria:
  - "Explicitly contrasts Trade Flow, Order Flow, Liquidity Flow, Derivatives Positioning, and Fund Flow"
---

# Multi-Asset & Quantitative Glossary

| Term | Canonical Definition | Methodological Warning / Distinction |
|---|---|---|
| **Instrument (`instrument_id`)** | Canonical unique market contract, e.g., `binance:perp:BTC/USDT` or `okx:expiry:BTC/USDT:20261225`. | Never identify an instrument solely by raw `symbol` (e.g., `BTCUSDT` omits venue and contract type). |
| **Contract Type** | `SPOT` (immediate settlement), `PERPETUAL` (no expiry, funding anchored), `DATED_FUTURE` (fixed expiry settlement), `OPTION` (strike/expiry/right). | `PERPETUAL` (`SWAP` on OKX) uses contract multiplier & funding rates absent in `SPOT`. |
| **Trade Flow** | Executed transactions on the tape: price, size, quote notional, and taker aggressor side (`BUY` vs `SELL`). | Measures realized aggressive volume & **Cumulative Volume Delta (CVD)** — NOT net fiat inflow. |
| **Order Flow** | Resting limit-order book changes (`ADD`, `CANCEL`, `MODIFY`) captured across L2 snapshots/deltas and aggregated into **Order Flow Imbalance (OFI)**. | Captures liquidity intent and queue pressure, distinct from executed Trade Flow. |
| **Liquidity Flow** | Instantaneous market depth, quoted/effective bid-ask spreads, depth within bps bands, estimated market-impact slippage, and post-trade depth replenishment speed. | Measures execution cost and fragility, NOT price direction alone. |
| **Derivatives Positioning** | Leveraged exposure & carry metrics: Open Interest (OI contracts & notional), Open Interest Delta, Funding Rate, and Spot–Perp Basis. | Rising OI + rising price indicates new leveraged positions (longs vs shorts matching 1:1), NOT "money flowing into spot market". |
| **Fund Flow / On-Chain Flow** | Verified net asset transfers across ETFs, custody wallets, or exchange reserve addresses. | Excluded from v1 unless external verified source is explicitly integrated; never infer from trading volume. |
| **Point-in-Time Alignment** | Research constraint requiring every feature value to carry `available_at <= decision_time` using `ingestion_time`/watermark availability. | Prevents look-ahead leakage from late exchange messages or unclosed bars. |
| **Model Abstention** | Explicit refusal by inference service (`abstention_flag=True`) to issue an actionable forecast when DQ degrades or feature PSI drift exceeds threshold. | Prefer explicit abstention over emitting false confidence on corrupt book/stale feeds. |
