# Product & Website 15-Phase Engineering Lifecycle (`docs/product/`)

## 1. Directory Purpose

`docs/product/` hosts the 15-phase engineering documentation pipeline (`00-discovery` through `14-governance`) for Product and Website engineering, adapted from `AgentHarnessBuilderTools` and integrated with the shared Data Platform baseline in `docs/architecture/` and `docs/specifications/`.

## 2. Scope and Boundaries

- **Belongs in this directory**: Phases `00-discovery/` through `14-governance/` and their nested specification/ADR directories.
- **Does NOT belong in this directory**: Duplicate copies of shared Data Platform architecture (`docs/architecture/`) or raw YAML models (`models/`).

## 3. Agent Role and Responsibilities

Operated by the 11 specialized Agent roles in `.agents/agents/` under work-item control (`work-items/`).

## 4. Authoritative Inputs

1. `AGENTS.md` — Root Agent operating protocol.
2. `.agents/config/document-map.yaml` — Phase-to-model-and-template map.
3. `docs/architecture/` and `docs/specifications/` — Shared Data Platform baseline.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `00-discovery/` | Phase 00 — Product & Domain Discovery | Required Directory | `docs/product/00-discovery/README.md` |
| `01-planning/` | Phase 01 — Engineering & Delivery Planning | Required Directory | `docs/product/01-planning/README.md` |
| `02-requirements/` | Phase 02 — Requirements Engineering Baseline | Required Directory | `docs/product/02-requirements/README.md` |
| `03-business-process/` | Phase 03 — Business Process & Workflow Modeling | Required Directory | `docs/product/03-business-process/README.md` |
| `04-use-cases/` | Phase 04 — Use Case Modeling & Specifications | Required Directory | `docs/product/04-use-cases/README.md` |
| `05-system-analysis/` | Phase 05 — System Analysis & Boundary Alignment | Required Directory | `docs/product/05-system-analysis/README.md` |
| `06-architecture/` | Phase 06 — Product & Application Architecture | Required Directory | `docs/product/06-architecture/README.md` |
| `07-domain/` | Phase 07 — Product Domain Model & Ubiquitous Language | Required Directory | `docs/product/07-domain/README.md` |
| `08-api/` | Phase 08 — Product API & Integration Contracts | Required Directory | `docs/product/08-api/README.md` |
| `09-behavior/` | Phase 09 — Behavioral Sequence & State Modeling | Required Directory | `docs/product/09-behavior/README.md` |
| `10-security/` | Phase 10 — Product Security & STRIDE Threat Modeling | Required Directory | `docs/product/10-security/README.md` |
| `11-ux/` | Phase 11 — UX Information Architecture & Screen Specifications | Required Directory | `docs/product/11-ux/README.md` |
| `12-testing/` | Phase 12 — QA Test Strategy, Plans & Test Cases | Required Directory | `docs/product/12-testing/README.md` |
| `13-operations/` | Phase 13 — Operations, Deployment & Runbooks | Required Directory | `docs/product/13-operations/README.md` |
| `14-governance/` | Phase 14 — Documentation Governance, Status & Audit Baseline | Required Directory | `docs/product/14-governance/README.md` |

## 6. Directory and File Organization

15 sequential phase directories (`00-discovery` .. `14-governance`), each governed by its own operational `README.md`.

## 7. Document Creation Rules

Never populate product phases with invented features. Only create documents selected by an active work item's `artifact-plan.yaml` using templates from `docs/templates/`.

## 8. Creation Workflow

1. Read `docs/product/README.md` and the target phase's `README.md`.
2. Confirm the artifact is planned in `work-items/<ID>/artifact-plan.yaml`.
3. Update the canonical YAML model in `models/` first.
4. Instantiate the template from `docs/templates/<category>/` into `docs/product/<phase>/`.
5. Run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

Connects product requirements and UX (`00..13`) to shared Data Platform APIs (`docs/specifications/api-specification.md`) and governance (`14-governance`).

## 10. Quality Gate

Every phase directory and nested directory contains a compliant 12-section `README.md` and passes `tools/validators/run_all.py`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT invent Website business features, screens, or use cases without user-approved discovery inputs.
- Do NOT duplicate `docs/architecture/` or `docs/specifications/` files inside `docs/product/`.
