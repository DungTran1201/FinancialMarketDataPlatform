# Work Item `DATA-001` — End-to-End Data Platform v0.1 & Domain Microservices (`work-items/DATA-001-data-platform-v01-and-microservices/`)

## 1. Directory Purpose

This directory tracks Work Item `DATA-001` ("Upgrade Data Platform to Zero-Mock v0.1 & Transition to Domain Microservices"), which eliminates all Data Plane mocks, builds the complete 12-stage Data Platform v0.1 (`src/processing/pipeline_v01.py`, `src/processing/gold_marts.py`, `src/quality/lineage_and_observability.py`), decomposes the runtime into 8 domain microservices (`src/microservices/`), and authors supplementary documentation (`ADR-007`, `14-data-platform-v01-and-microservices-architecture.md`) and diagrams (`DIAG-DATA-008`, `DIAG-DATA-009`, `DIAG-C4-017`, `DIAG-DEP-018`).

## 2. Scope and Boundaries

- **Belongs in this directory**: The 9 change-control files for `DATA-001` (`README.md`, `request.md`, `discovery.md`, `impact-analysis.md`, `artifact-plan.yaml`, `implementation-plan.md`, `verification-plan.md`, `review.md`, `state.yaml`).
- **Does NOT belong here**: Production source code, canonical models, or documentation files.

## 3. Agent Role and Responsibilities

- **Primary Owning Roles**: `data-engineer`, `data-platform-architect`, and `system-architect`.

## 4. Authoritative Inputs

1. Root Operating Contract: [AGENTS.md](../../AGENTS.md)
2. Data Platform Architecture: [04-data-platform-architecture.md](../../docs/architecture/04-data-platform-architecture.md)
3. Canonical Models: `models/architecture/`, `models/deployment/`, `models/api/`, `models/testing/`

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `README.md` | Operational overview of Work Item `DATA-001` | Required | [work-items/_template/README.md](../_template/README.md) |
| `request.md` | Captures `DATA-001` scope and objectives | Required | [work-items/_template/request.md](../_template/request.md) |
| `discovery.md` | Audit of `arch/microservices` branch gaps and mocks | Required | [work-items/_template/discovery.md](../_template/discovery.md) |
| `impact-analysis.md` | Cross-subsystem impact analysis | Required | [work-items/_template/impact-analysis.md](../_template/impact-analysis.md) |
| `artifact-plan.yaml` | Machine-readable list of created/updated artifacts | Required | [work-items/_template/artifact-plan.yaml](../_template/artifact-plan.yaml) |
| `implementation-plan.md` | Staged engineering execution plan | Required | [work-items/_template/implementation-plan.md](../_template/implementation-plan.md) |
| `verification-plan.md` | Validator and `TC-011` test plan | Required | [work-items/_template/verification-plan.md](../_template/verification-plan.md) |
| `review.md` | Quality gate verification and sign-off | Required | [work-items/_template/review.md](../_template/review.md) |
| `state.yaml` | Lifecycle state progression (`INTAKE -> ... -> DONE`) | Required | [work-items/_template/state.yaml](../_template/state.yaml) |

## 6. Directory and File Organization

Contains the standard 9 work-item files matching `work-items/_template/`.

## 7. Document Creation Rules

- Must adhere to `work-items/README.md` and pass `tools/validators/validate_work_items.py` and `tools/validators/validate_readmes.py`.

## 8. Creation Workflow

1. Audit Data Platform gaps and mocks on `arch/microservices` (`discovery.md`).
2. Record affected models, docs, diagrams, and code in `artifact-plan.yaml`.
3. Execute zero-mock Data Platform v0.1 and microservices decomposition (`implementation-plan.md`).
4. Verify with `TC-011` and `tools/validators/run_all.py` (`verification-plan.md`, `review.md`, `state.yaml`).

## 9. Relationships and Dependencies

- Extends `DOCS-001` and governs `ADR-007`, `COMP-009..COMP-016`, `DEP-006`, `API-011..API-015`, and `TC-011`.

## 10. Quality Gate

- Passes `validate_work_items.py`, `run_all.py`, and all unit/architecture tests with 0 errors.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_work_items.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- **Do NOT** violate Clean Architecture module boundaries (`tests/architecture/test_clean_architecture_boundaries.py`).
- **Do NOT** leave any transport or storage mocks in the Data Platform (`Plane A`).

