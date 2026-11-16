---
doc_id: "DOC-ROOT-001"
title: "Documentation Hub — Greenfield Multi-Asset Data & Quantitative Intelligence Platform"
version: "1.0.0"
status: "IN_REVIEW"
implementation_status: "NOT_APPLICABLE"
owner: "System Analyst & Principal Software Architect"
purpose: "Root index, directory conventions, naming rules, metadata requirements, and update instructions for greenfield documentation."
scope: "All documentation under docs/ on branch greenfield/main."
dependencies:
  - "AGENTS.md"
  - ".agents/hooks.json"
references:
  - "docs/governance/README.md"
  - "docs/phase-reports/README.md"
  - "docs/product/README.md"
  - "docs/architecture/README.md"
assumptions:
  - "Legacy branches remain intact; this directory contains zero legacy documentation copied as authoritative architecture."
open_issues:
  - "OPEN-P1-002 (resolved to OKX; connector API verification scheduled in Phase 2 PoC)"
review_criteria:
  - "Passes tools/validators/run_all.py with 0 errors"
  - "Every subdirectory contains a valid README.md explaining purpose, naming, and dependencies"
---

# Documentation Hub (`docs/`)

Documentation is a **first-class deliverable** of `FinancialMarketDataPlatform` on `greenfield/main`. No application code is implemented before Phase 1 requirements, Phase 2 architecture/PoCs, and Phase 3 contracts are documented and accepted.

## Directory Structure & Purpose

| Directory | Purpose | Lifecycle Focus |
|---|---|---|
| [governance/](governance/README.md) | Standards, validation rules, templates, phase/readiness checklists | All Phases |
| [phase-reports/](phase-reports/README.md) | Phase 0..9 sign-off packages, PoC evidence, readiness reports | Phase Gates `0..9` |
| [product/](product/README.md) | Vision, SRS, multi-asset use cases, RTM, acceptance criteria, glossary, roadmap | Phase 1 (protected baseline) |
| [architecture/](architecture/README.md) | SAD, technology evaluation matrix, ADRs, 8 GB resource budget, threat model | Phase 2 |
| [data-engineering/](data-engineering/README.md) | Canonical data model, exchange source catalog (Binance/OKX), contracts, DQ, retention, lineage | Phase 3+ |
| [quantitative-intelligence/](quantitative-intelligence/README.md) | Research methodology, reference library, feature catalog, model cards, walk-forward eval specs | Phase 3+ |
| [api-and-integration/](api-and-integration/README.md) | REST OpenAPI, WebSocket/SSE specs, JetStream event schemas, RBAC/Auth & error specs | Phase 3+ |
| [application-ux/](application-ux/README.md) | Information architecture, user flows, specifications for the 15 UI modules | Phase 3+ |
| [testing-and-operations/](testing-and-operations/README.md) | Benchmark plans, test strategy, runbooks, backup/restore, monitoring & alerts | Phase 2+ |
| [diagrams/](diagrams/README.md) | Centralized Mermaid architecture, data-flow, sequence, state, ERD & threat diagrams | Phase 2+ |
| [work-items/](work-items/README.md) | Tracked work items (`BACKLOG` through `COMPLETE`) and traceability links | All Phases |

## Naming Conventions & Mandatory Metadata Header

1. Use `kebab-case.md` filenames.
2. Every directory MUST have a non-empty `README.md`.
3. Every Markdown file under `docs/` MUST start with valid YAML frontmatter containing: `doc_id`, `title`, `version`, `status`, `owner`, `purpose`, `scope`, `dependencies`, `references`, `assumptions`, `open_issues`, and `review_criteria`.
4. Maintain single-authoritative-source boundaries: architecture diagrams live in [diagrams/](diagrams/README.md) and reference authoritative specs rather than duplicating them.

## How Agents Must Update Documentation

1. Read [AGENTS.md](../AGENTS.md) and this index first.
2. Check existing work items in [work-items/](work-items/README.md) before creating specs.
3. Update cross-links and run `.\.venv\Scripts\python.exe tools/validators/run_all.py` after edits (automatically verified by the `PostToolUse` hook).

