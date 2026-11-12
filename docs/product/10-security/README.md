# Phase 10 — Product Security & STRIDE Threat Modeling (`docs/product/10-security/`)

## 1. Directory Purpose

Authoritative documentation space for **Phase 10 — Product Security & STRIDE Threat Modeling** within the 15-phase product lifecycle (`docs/product/`).

## 2. Scope and Boundaries

- **Belongs in this directory**: Phase `10-security` specifications instantiated from `docs/templates/security/`.
- **Does NOT belong in this directory**: Canonical YAML models (`models/security/threat-model.yaml`), diagrams (`docs/diagrams/security/`), or shared Data Platform baselines (`docs/architecture/`, `docs/specifications/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `security-reviewer` (`.agents/agents/security-reviewer.md`); audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `docs/product/README.md` — Product lifecycle overview.
2. `models/security/threat-model.yaml` — Canonical model for this phase.
3. `docs/templates/security/README.md` — Template usage rules for this phase.
4. `docs/specifications/` & `docs/architecture/` — Shared platform contracts and constraints.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `security-specification.md` | Product auth, session, RBAC & CSP specification | Conditional | `docs/templates/security/security-specification.template.md` |
| `threat-model.md` | STRIDE threat model (`THR-###`) & controls (`CTRL-###`) | Conditional | `docs/templates/security/threat-model.template.md` |

## 6. Directory and File Organization

Directory `docs/product/10-security/` containing `README.md` and phase artifacts selected via `work-items/<ID>/artifact-plan.yaml`.

## 7. Document Creation Rules

Instantiate all documents from `docs/templates/security/`, assign stable IDs from `.agents/config/identifier-registry.yaml` (using `WEB-*` prefixes where disambiguation from Data Platform IDs is needed), and keep status as `DRAFT` until reviewed.

## 8. Creation Workflow

1. Read `docs/product/10-security/README.md` and `docs/templates/security/README.md`.
2. Inspect upstream canonical model `models/security/threat-model.yaml` and shared platform specs.
3. Copy the required template from `docs/templates/security/` into `docs/product/10-security/`.
4. Populate verified facts, tag any `[ASSUMPTION — REQUIRES VALIDATION]` or `[OPEN QUESTION]`, and update traceability.
5. Synchronize any derived diagrams in `docs/diagrams/security/`.
6. Run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

Consumes structured data from `models/security/threat-model.yaml`, uses templates from `docs/templates/security/`, and links to diagrams in `docs/diagrams/security/`.

## 10. Quality Gate

All created artifacts in `docs/product/10-security/` conform to `docs/templates/security/` metadata standards and pass `validate_docs.py` and `validate_traceability.py`.

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
