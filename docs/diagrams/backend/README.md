# Diagram Category: Backend Modular Monolith, Request Lifecycle, CQRS & Cache Diagrams (Existing Baseline) (`docs/diagrams/backend/`)

## 1. Directory Purpose

Standardizes and stores `DIAG-C4 / DIAG-SEQ` technical diagrams for `backend` within the unified `docs/diagrams/` subsystem.

## 2. Scope and Boundaries

- **Belongs in this directory**: `DIAG-C4 / DIAG-SEQ` Mermaid diagram markdown files (`*.md`) and category `README.md`.
- **Does NOT belong in this directory**: Authoritative prose requirements (`docs/architecture/05-backend-architecture.md`) or canonical YAML models (`models/architecture/components.yaml`).

## 3. Agent Role and Responsibilities

Primary authoring role: `architecture-modeler`; audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `models/architecture/components.yaml` — Canonical structured model (authoritative entity/state/component source).
2. `docs/architecture/05-backend-architecture.md` — Authoritative human-readable specification.
3. `docs/diagrams/README.md` — Master diagram engineering rules.
4. `.agents/rules/diagrams.md` — Derived-view and Mermaid syntax rules.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `08-backend-module-architecture.md` | Baselined platform diagram (`DIAG-C4 / DIAG-SEQ`) | Required (Baselined) | `docs/diagrams/backend/08-backend-module-architecture.md` |
| `09-backend-request-lifecycle.md` | Baselined platform diagram (`DIAG-C4 / DIAG-SEQ`) | Required (Baselined) | `docs/diagrams/backend/09-backend-request-lifecycle.md` |
| `10-cqrs-read-write.md` | Baselined platform diagram (`DIAG-C4 / DIAG-SEQ`) | Required (Baselined) | `docs/diagrams/backend/10-cqrs-read-write.md` |
| `11-cache-architecture.md` | Baselined platform diagram (`DIAG-C4 / DIAG-SEQ`) | Required (Baselined) | `docs/diagrams/backend/11-cache-architecture.md` |

## 6. Directory and File Organization

Directory `docs/diagrams/backend/` containing `README.md` and `DIAG-C4 / DIAG-SEQ` markdown diagram files named `<NNN>-<kebab-slug>.md` or `<ID>-<kebab-slug>.md`.

## 7. Document Creation Rules

1. Assign a unique `DIAG-C4-<NNN>` ID conforming to `.agents/config/identifier-registry.yaml`.
2. Reference `models/architecture/components.yaml` and `docs/architecture/05-backend-architecture.md` in the metadata header.
3. Represent both happy paths and alternative/exception paths where applicable.
4. Quote any Mermaid node label containing parentheses `()` or brackets `[]`.

## 8. Creation Workflow

1. Read `docs/diagrams/backend/README.md`.
2. Inspect `models/architecture/components.yaml` and `docs/architecture/05-backend-architecture.md` to confirm all nodes and edges exist in authoritative sources.
3. Author or update the Mermaid diagram file.
4. Cross-reference the diagram file in the corresponding specification document.
5. Run `tools/validators/validate_diagrams.py`.

## 9. Relationships and Dependencies

Derived visual view of `models/architecture/components.yaml` and `docs/architecture/05-backend-architecture.md`.

## 10. Quality Gate

All diagram files in `docs/diagrams/backend/` contain valid Mermaid fenced code blocks, architectural explanations, and pass `validate_diagrams.py`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT use a diagram in this folder as the sole definition of a requirement, API, or state machine.
- Do NOT invent components, actors, or flows not present in the upstream model and specification.
