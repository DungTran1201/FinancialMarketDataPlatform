---
doc_id: DP-DOM-ING-001
title: "Domain: Market Data Ingestion"
doc_type: index
plane: data-plane
scope_level: domain
domain: market-data-ingestion
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: data-architect
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/ingestion/"
related_docs:
  - DP-ROOT-001
  - DP-DOM-ING-SPEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Registered market-data-ingestion Data Plane domain and CAP-DP-ING-001."
---

# Domain: Market Data Ingestion

Owns acquisition of exchange spot market events, strict schema/decimal normalization, weight-aware REST pagination, sequence-gap detection, DLQ quarantine, and watermark persistence (`src/ingestion/`).

- [domain-specification.md](domain-specification.md) (`DP-DOM-ING-SPEC-001`)
- Capabilities:
  - `CAP-DP-ING-001`: [exchange-realtime-and-backfill-ingestion](capabilities/exchange-realtime-and-backfill-ingestion/README.md) (`PARTIALLY_IMPLEMENTED`)
