# Work Item Request: Documentation Architecture Reorganization (`DOCS-002`)

| Metadata | Value |
|---|---|
| **Work Item ID** | `DOCS-002` |
| **Title** | Reorganize and Standardize Platform Documentation Architecture |
| **Change Type** | `DOCS` |
| **Risk Tier** | `R2` (Medium / Cross-Subsystem Documentation Impact) |
| **Status** | `APPROVED` |
| **Created Date** | `2026-11-15` |
| **Updated Date** | `2026-11-15` |
| **Requestor** | Principal Engineering / User Request |
| **Owning Agent Role** | `documentation-architect` |

---

## 1. Problem Statement & Motivation

The **FinancialMarketDataPlatform** has undergone substantial rapid development, expanding from an initial Modular Monolith design into a 3-Plane Architecture (Plane A Data Plane, Plane B Serving Gateway, Plane C Intelligence), an 8-service container microservices topology (`arch/microservices`), a zero-mock E2E data pipeline v0.1 (`DATA-001`), and a rich TypeScript/Vite frontend experience layer (`FEAT-002`).

However, the documentation system has accumulated several structural pain points:
1. **Cognitive Overload & Flat Organization**: `docs/architecture/` contains 15 flat, sequentially numbered files (`00`..`14`) and 8 ADRs, requiring developers to read through sequential lists rather than navigating by domain or reader journey.
2. **Lifecycle Fragment vs Reality**: `docs/product/` maintains 15 lifecycle phase folders (`00`..`14`), but the majority of folders contain only a template-governed `README.md` while the actual technical specifications live in `docs/specifications/` or `models/`.
3. **Diagram Template Clutter**: Diagram templates (`*.template.md`) were intermingled with production diagrams in `docs/diagrams/`.
4. **Missing Developer & Operations Portals**: Onboarding developers and DevOps engineers lacked unified, discoverable portals for local environment setup, codebase maps, deployment profiles, and incident runbooks.

---

## 2. Core Objectives

The reorganized documentation architecture must achieve:
- **Understandability**: A developer must understand the end-to-end architecture and local workflow within 5 minutes.
- **Consistency**: Documentation, Mermaid diagrams, canonical YAML models, and production source code must agree 100%.
- **Traceability**: Bidirectional linking from requirements (`FR-*`) to ADRs (`ADR-*`), components (`COMP-*`), diagrams (`DIAG-*`), code, and test cases (`TC-*`).
- **Maintainability**: Clear domain boundaries preventing content duplication.
- **Discoverability**: Two-click access to any technical domain via a unified Reader Journey map.
- **Agent Compatibility**: AI agents can look up, author, and validate documentation deterministically.
- **Backward Compatibility**: Zero broken links, zero lost files, zero renumbered IDs.

---

## 3. Non-Negotiable Constraints

1. **Preserve Document Identity**: Never renumber or alter `ADR-*`, `FR-*`, `NFR-*`, `BR-*`, `AC-*`, `DIAG-*`, `COMP-*`, `API-*`, `TC-*`, `WEB-*`.
2. **Preserve Existing References**: All 25 baseline files required by `validate_docs.py` must remain intact at their canonical locations.
3. **Preserve Canonical Models**: `models/` remains an independent layer of machine-readable YAML models.
4. **Preserve Agent Infrastructure**: All agent roles, rules, skills, configs, and hooks remain fully functional.
5. **No Destructive Migration**: Git history preserved; no deletions of working documents.
