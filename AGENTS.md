# AGENTS.md — Greenfield Multi-Asset Data Platform & Quantitative Intelligence Contract

This repository operates as a **documentation-first greenfield project** on branch `greenfield/main`, engineered explicitly for an **8 GB RAM single-node workstation** (`CON-HW-001`) using a **Hybrid Native Windows + Containerized NATS JetStream** initial evaluation runtime (`DEC-P0-002`).

> **Legacy Isolation Rule (`DEC-P0-001`)**: Historical prior work remains untouched on legacy Git branches (`main`, `feat/data-plane-production-delivery`, etc.). Agents MUST NOT copy legacy code, Docker stacks, schemas, or documentation from legacy branches into `greenfield/main`.

---

## 1. Mandatory Agent Reading Order

Before creating specifications, PoC benchmarks, or code, agents MUST read in sequence:

1. [AGENTS.md](AGENTS.md) — Root greenfield engineering contract.
2. [.agents/README.md](.agents/README.md) & [.agents/rules/greenfield-engineering-rules.md](.agents/rules/greenfield-engineering-rules.md) — Engineering rules, lifecycle gates, and validator policy.
3. [.agents/workflows/phase-lifecycle.md](.agents/workflows/phase-lifecycle.md) — Phase 0–9 progression gates and Work-Item lifecycle rules.
4. [docs/README.md](docs/README.md) — Documentation hub, directory conventions, and metadata standard.

---

## 2. Core Engineering & Honesty Rules

1. **Controlled Phase Progression**: Never skip phases or implement application/infrastructure modules before Phase 1–3 gates and Phase 2 isolated PoCs are documented and accepted.
2. **Evidence Over Opinions**: Never cite unmeasured throughput, latency, memory usage, or model profitability. Every PoC and performance claim must cite hardware specs, software versions, raw outputs, and known limitations.
3. **Separate Target Design from Actual Reality**: Always distinguish `PLANNED | NOT_IMPLEMENTED | POC_VALIDATED | PARTIALLY_IMPLEMENTED | IMPLEMENTED | VERIFIED` (`implementation_status`) from documentation review status (`DRAFT | IN_REVIEW | ACCEPTED | APPROVED | DEPRECATED`).
4. **Methodological Precision**: Maintain strict canonical instrument keys (`exchange`, `market`, `base_asset`, `quote_currency`, `symbol`, `contract_type`) across Binance and OKX; never equate trading volume, open interest, or funding rate with net capital inflow; guard all research features against look-ahead leakage.
5. **Never Disable Validation**: All documentation and work-item updates must pass `.\.venv\Scripts\python.exe tools/validators/run_all.py`.

---

## 3. Repository Validation Command

```powershell
.\.venv\Scripts\python.exe tools/validators/run_all.py
```
