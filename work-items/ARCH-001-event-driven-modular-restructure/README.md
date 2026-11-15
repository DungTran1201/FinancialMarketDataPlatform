# Work Item `ARCH-001` — Event-Driven Modular Data Platform Restructure (`work-items/ARCH-001-event-driven-modular-restructure/`)

## 1. Directory Purpose

This directory tracks Work Item `ARCH-001`, governing the structural reorganization of `FinancialMarketDataPlatform` into an **Event-Driven Modular Data Platform** cleanly separating `shared`, `ingestion`, `streaming`, `lakehouse`, `serving`, and `intelligence` under `src/`, standardizing `deploy/`, introducing `models/data-platform/`, restructuring `tests/` by test discipline, and synchronizing documentation, diagrams, ADRs, and READMEs.

## 2. Scope and Boundaries

- **Belongs in this directory**: The 9 lifecycle control files for `ARCH-001` (`README.md`, `request.md`, `discovery.md`, `impact-analysis.md`, `artifact-plan.yaml`, `implementation-plan.md`, `verification-plan.md`, `review.md`, `state.yaml`).
- **Does NOT belong here**: Production source code (`src/`), deployment configs (`deploy/`), canonical YAML models (`models/`), or architecture baseline docs (`docs/architecture/`).

## 3. Agent Role and Responsibilities

- **Primary Owning Roles**: `data-platform-architect`, `data-engineer`, and `system-architect`.
- **Audit Role**: `documentation-auditor`.

## 4. Authoritative Inputs

1. Root Operating Contract: [AGENTS.md](../../AGENTS.md)
2. Platform Architecture Specs: [00-architecture-overview.md](../../docs/architecture/00-architecture-overview.md) and [14-data-platform-v01-and-microservices-architecture.md](../../docs/architecture/14-data-platform-v01-and-microservices-architecture.md)
3. Canonical Models: `models/architecture/`, `models/domain/`, `models/deployment/`, `models/testing/`
4. Boundary Guardrails: `.agents/config/data-platform-boundaries.yaml` and `tests/architecture/test_clean_architecture_boundaries.py`

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `README.md` | Directory overview and rules for Work Item `ARCH-001` | Required | [work-items/_template/README.md](../_template/README.md) |
| `request.md` | Formal architectural restructure request and constraints | Required | [work-items/_template/request.md](../_template/request.md) |
| `discovery.md` | Legacy structure inventory, coupling findings, and fact register | Required | [work-items/_template/discovery.md](../_template/discovery.md) |
| `impact-analysis.md` | Cross-module dependency mapping and risk analysis | Required | [work-items/_template/impact-analysis.md](../_template/impact-analysis.md) |
| `artifact-plan.yaml` | Machine-readable artifact plan for `ARCH-001` | Required | [work-items/_template/artifact-plan.yaml](../_template/artifact-plan.yaml) |
| `implementation-plan.md` | Sequenced migration plan across `src/`, `deploy/`, `models/`, `tests/`, and `docs/` | Required | [work-items/_template/implementation-plan.md](../_template/implementation-plan.md) |
| `verification-plan.md` | Verification matrix covering `pytest`, `unittest`, `dbt`, `docker compose`, and `run_all.py` | Required | [work-items/_template/verification-plan.md](../_template/verification-plan.md) |
| `review.md` | Gate review and architectural sign-off log | Required | [work-items/_template/review.md](../_template/review.md) |
| `state.yaml` | Machine-checked workflow state transitions (`INTAKE -> ... -> DONE`) | Required | [work-items/_template/state.yaml](../_template/state.yaml) |

## 6. Directory and File Organization

Contains the standard 9 flat control files matching `work-items/_template/`.

## 7. Document Creation Rules

- Maintain strictly verified facts (`FACT`), tagged assumptions (`[ASSUMPTION — REQUIRES VALIDATION]`), and recorded architectural decisions (`ADR-008`).
- Pass `tools/validators/validate_work_items.py` and `tools/validators/validate_readmes.py`.

## 8. Creation Workflow

1. Audit legacy `src/`, `deploy/`, `models/`, `tests/`, and runtime scripts (`discovery.md`).
2. Record full Old -> New mapping and dependency impact (`impact-analysis.md`).
3. Plan modular refactor and artifact sync (`artifact-plan.yaml`, `implementation-plan.md`).
4. Execute migration, remove redundant legacy paths, and run verification (`verification-plan.md`, `review.md`, `state.yaml`).

## 9. Relationships and Dependencies

- Supersedes layout conventions introduced under `DOCS-001` and `DATA-001` via `ADR-008` without altering baseline domain semantics (`ADR-001` through `ADR-007`).

## 10. Quality Gate

- Zero broken imports, zero boundary violations (`TC-006`), all existing and added tests pass, and `tools/validators/run_all.py` reports 0 errors.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_work_items.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- **Do NOT** duplicate modules across old and new paths as compatibility shims.
- **Do NOT** alter financial domain invariants (`Decimal` precision, monotonic hot state, blocking DQ gates) during restructuring.

