---
doc_id: "DOC-ARCH-ROOT"
title: "System Architecture & ADRs Index"
version: "1.0.0"
status: "IN_REVIEW"
implementation_status: "PLANNED"
owner: "Principal Software Architect & Data Platform Architect"
purpose: "Index of Phase 2 architecture documents, technology evaluation matrix, 8 GB resource budget, threat model, and ADRs."
scope: "System-wide architecture boundaries, communication contracts, and Phase 2 PoC-validated technology choices."
dependencies:
  - "docs/product/srs.md"
  - "docs/product/requirements-traceability-matrix.md"
references:
  - "docs/diagrams/README.md"
assumptions:
  - "Deployment baseline is single-node 8 GB RAM host using Hybrid Native Windows + Containerized NATS JetStream during PoC."
open_issues:
  - "ADRs remain PROPOSED until Phase 2 isolated PoCs generate empirical evidence."
review_criteria:
  - "All lightweight stack picks backed by PoC benchmark plan before implementation"
---

# System Architecture (`docs/architecture/`)

Authoritative home for Phase 2 architecture design, technology evaluations, 8 GB resource budgets, security threat model, and Architecture Decision Records (`decisions/`).

## Directory Structure & Naming
- `system-architecture-document.md` — Three-plane logical & runtime design.
- `technology-evaluation-matrix.md` — Candidate comparisons & justified picks.
- `resource-budget.md` — Idle/nominal/peak RAM, CPU, and disk quotas.
- `threat-model.md` — Trust boundaries, attack surfaces & mitigations.
- `decisions/adr-NNNN-<slug>.md` — Numbered Architecture Decision Records.

## Update Rules
- Diagrams are stored in [docs/diagrams/](../diagrams/README.md) and linked here.
- Benchmark numbers remain marked `[TARGET]` until PoC evidence is recorded in `docs/testing-and-operations/`.

