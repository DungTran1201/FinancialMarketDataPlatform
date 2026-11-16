---
doc_id: APP-DOM-MKT-001
title: "Domain: Market Experience & Data Catalog"
doc_type: index
plane: application-plane
scope_level: domain
domain: market-experience-and-catalog
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/market/presentation/router.py"
    - "src/serving/api/modules/historical/presentation/router.py"
    - "src/serving/api/modules/analytics/presentation/router.py"
    - "src/serving/api/modules/catalog/presentation/router.py"
    - "frontend/src/modules/market-analytics/MarketAnalyticsModule.ts"
    - "frontend/src/modules/data-management/DataManagementModule.ts"
related_docs:
  - APP-ROOT-001
  - APP-DOM-MKT-SPEC-001
  - APP-DOM-MKT-GLOSS-001
  - CAP-APP-MKT-DOC-001
  - CAP-APP-CAT-DOC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Created Market Experience & Data Catalog domain root housing query portal and instrument catalog capabilities."
---

# Domain: Market Experience & Data Catalog

## 1. Domain Documentation

- [domain-specification.md](domain-specification.md) (`APP-DOM-MKT-SPEC-001`)
- [glossary.md](glossary.md) (`APP-DOM-MKT-GLOSS-001`)

## 2. Capabilities

- [CAP-APP-MKT-001 — Market & Analytics Query Portal](capabilities/market-and-analytics-query-portal/README.md) (`IN_REVIEW` / `MEDIUM`)
- [CAP-APP-CAT-001 — Instrument & Data Catalog](capabilities/instrument-and-data-catalog/README.md) (`IN_REVIEW` / `MEDIUM`)
