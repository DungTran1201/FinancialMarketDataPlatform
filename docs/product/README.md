---
doc_id: "DOC-PRD-ROOT"
title: "Product & Requirements Documentation Index"
version: "1.0.0"
status: "IN_REVIEW"
implementation_status: "NOT_IMPLEMENTED"
owner: "Principal Business Analyst & Product Manager"
purpose: "Central index for product vision, SRS, multi-asset use cases, RTM, acceptance criteria, glossary, and roadmap."
scope: "Phase 1 versioned baseline deliverables under docs/product/."
dependencies:
  - "docs/README.md"
  - "docs/phase-reports/phase-1-acceptance-and-decisions.md"
references:
  - "docs/product/vision-and-scope.md"
  - "docs/product/srs.md"
  - "docs/product/use-cases.md"
  - "docs/product/requirements-traceability-matrix.md"
  - "docs/product/acceptance-criteria.md"
  - "docs/product/glossary.md"
  - "docs/product/roadmap.md"
assumptions:
  - "P1-PKG-001 baseline accepted with conditions pending RTM conflict check prior to Phase 2 implementation."
open_issues:
  - "OPEN-P1-002 resolved to Binance + OKX; exact rate limits & instrument depth to be verified during Phase 2 PoC"
review_criteria:
  - "Unique IDs across BR/FR/NFR/UC/AC"
  - "Zero undocumented scope changes without version bump"
---

# Product & Requirements (`docs/product/`)

Stores the versioned **Phase 1 — Requirements and Product Definition** baseline:
- [vision-and-scope.md](vision-and-scope.md) — Product scope, exclusions, exchanges (`Binance` + `OKX`), user roles.
- [srs.md](srs.md) — Software Requirements Specification (`FR-*`, `NFR-*`, `RES-*`, methodological rules).
- [use-cases.md](use-cases.md) — Core multi-asset & quant workflows (`UC-01`..`UC-10`).
- [requirements-traceability-matrix.md](requirements-traceability-matrix.md) — Full RTM + pre-Phase 2 conflict & ambiguity audit.
- [acceptance-criteria.md](acceptance-criteria.md) — Binary testable `AC-01`..`AC-15`.
- [glossary.md](glossary.md) — Canonical market microstructure & flow terminology.
- [roadmap.md](roadmap.md) — Releases `R0`..`R4` mapped to Phases `1..9`.

## Update Rules
- Any requirement modification requires version increment and RTM update.
- No Phase 2 selection may weaken an `ACCEPTED`/`APPROVED` requirement silently.
