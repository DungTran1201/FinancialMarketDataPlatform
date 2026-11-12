# Phase 08 — Product API & Integration Contracts (`docs/product/08-api/`)

## 1. Directory Purpose

Authoritative documentation space for **Phase 08 — Product API & Integration Contracts** within the 15-phase product lifecycle (`docs/product/`).

## 2. Scope and Boundaries

- **Belongs in this directory**: Phase `08-api` specifications instantiated from `docs/templates/api/`.
- **Does NOT belong in this directory**: Canonical YAML models (`models/api/api.yaml`), diagrams (`docs/diagrams/api/`), or shared Data Platform baselines (`docs/architecture/`, `docs/specifications/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `api-architect` (`.agents/agents/api-architect.md`); audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `docs/product/README.md` — Product lifecycle overview.
2. `models/api/api.yaml` — Canonical model for this phase.
3. `docs/templates/api/README.md` — Template usage rules for this phase.
4. `docs/specifications/` & `docs/architecture/` — Shared platform contracts and constraints.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `api-specifications.md` | Product API contracts extending shared `docs/specifications/api-specification.md` | Conditional | `docs/templates/api/API-specification.template.md` |
| `integration-contracts.md` | WebSocket, SSE & inter-service integration contracts | Conditional | `docs/templates/api/integration-contract.template.md` |

## 6. Directory and File Organization

Directory `docs/product/08-api/` containing `README.md` and phase artifacts selected via `work-items/<ID>/artifact-plan.yaml`.

## 7. Document Creation Rules

Instantiate all documents from `docs/templates/api/`, assign stable IDs from `.agents/config/identifier-registry.yaml` (using `WEB-*` prefixes where disambiguation from Data Platform IDs is needed), and keep status as `DRAFT` until reviewed.

## 8. Creation Workflow

1. Read `docs/product/08-api/README.md` and `docs/templates/api/README.md`.
2. Inspect upstream canonical model `models/api/api.yaml` and shared platform specs.
3. Copy the required template from `docs/templates/api/` into `docs/product/08-api/`.
4. Populate verified facts, tag any `[ASSUMPTION — REQUIRES VALIDATION]` or `[OPEN QUESTION]`, and update traceability.
5. Synchronize any derived diagrams in `docs/diagrams/api/`.
6. Run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

Consumes structured data from `models/api/api.yaml`, uses templates from `docs/templates/api/`, and links to diagrams in `docs/diagrams/api/`.

## 10. Quality Gate

All created artifacts in `docs/product/08-api/` conform to `docs/templates/api/` metadata standards and pass `validate_docs.py` and `validate_traceability.py`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT invent unverified product requirements or business rules.
- Do NOT duplicate shared Data Platform specifications from `docs/architecture/` or `docs/specifications/`.
- Do NOT mark any document containing `[TO BE COMPLETED]` or `[OPEN QUESTION]` as `APPROVED`.
