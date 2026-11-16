---
doc_id: "DOC-DATA-ROOT"
title: "Data Engineering Specifications Index"
version: "1.0.0"
status: "DRAFT"
implementation_status: "PLANNED"
owner: "Principal Data Engineer"
purpose: "Reserved Phase 3 home for canonical multi-asset data models, exchange source catalogs (Binance/OKX), contracts, DQ rules, retention, and lineage."
scope: "Data contracts, Parquet schemas, SQLite WAL metadata schemas, and exchange mapping specs."
dependencies:
  - "docs/product/srs.md"
  - "docs/architecture/README.md"
references:
  - "docs/product/glossary.md"
assumptions:
  - "Full schemas and contracts are authored in Phase 3 after Phase 2 PoCs validate bus and storage choices."
open_issues:
  - "Phase 3 authoring begins only after Phase 2 PoC acceptance."
review_criteria:
  - "Binance Spot/Perp/Expiry and OKX Spot/Swap/Futures schemas mapped cleanly without key collisions"
---

# Data Engineering (`docs/data-engineering/`)

Phase 3+ specification domain covering:
- Canonical Instrument Model & Multi-Exchange Normalization (Binance & OKX)
- Source Catalog (API limits, weight budgets, payload differences, regional constraints)
- Event Envelopes, Dead-Letter Contracts & Idempotency Keys
- Medallion Storage Layout (Bronze/Silver/Gold Parquet + SQLite WAL metadata)
- Data Quality, Retention, Compaction & Lineage Specifications

## Status
Directory initialized cleanly for Phase 3 documentation-first contract authoring; zero premature application code present.
