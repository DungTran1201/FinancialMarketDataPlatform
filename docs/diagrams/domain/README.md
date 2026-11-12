# Diagram Category: DDD Bounded Context, Class & Entity-Relationship Diagrams (`docs/diagrams/domain/`)

## 1. Directory Purpose

Standardizes and stores `DIAG-DOM / DIAG-ERD` technical diagrams for `domain` within the unified `docs/diagrams/` subsystem.

## 2. Scope and Boundaries

- **Belongs in this directory**: `DIAG-DOM / DIAG-ERD` Mermaid diagram markdown files (`*.md`) and category `README.md`.
- **Does NOT belong in this directory**: Authoritative prose requirements (`docs/product/07-domain/`) or canonical YAML models (`models/domain/domain.yaml`).

## 3. Agent Role and Responsibilities

Primary authoring role: `domain-modeler`; audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `models/domain/domain.yaml` — Canonical structured model (authoritative entity/state/component source).
2. `docs/product/07-domain/` — Authoritative human-readable specification.
3. `docs/diagrams/README.md` — Master diagram engineering rules.
4. `.agents/rules/diagrams.md` — Derived-view and Mermaid syntax rules.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `domain-diagram.template.md` | Reusable `DIAG-DOM / DIAG-ERD` Mermaid diagram template | Conditional | `docs/diagrams/domain/domain-diagram.template.md` |

## 6. Directory and File Organization

Directory `docs/diagrams/domain/` containing `README.md` and `DIAG-DOM / DIAG-ERD` markdown diagram files named `<NNN>-<kebab-slug>.md` or `<ID>-<kebab-slug>.md`.

## 7. Document Creation Rules

1. Assign a unique `DIAG-DOM-<NNN>` ID conforming to `.agents/config/identifier-registry.yaml`.
2. Reference `models/domain/domain.yaml` and `docs/product/07-domain/` in the metadata header.
3. Represent both happy paths and alternative/exception paths where applicable.
4. Quote any Mermaid node label containing parentheses `()` or brackets `[]`.

## 8. Creation Workflow

1. Read `docs/diagrams/domain/README.md`.
2. Inspect `models/domain/domain.yaml` and `docs/product/07-domain/` to confirm all nodes and edges exist in authoritative sources.
3. Author or update the Mermaid diagram file.
4. Cross-reference the diagram file in the corresponding specification document.
5. Run `tools/validators/validate_diagrams.py`.

## 9. Relationships and Dependencies

Derived visual view of `models/domain/domain.yaml` and `docs/product/07-domain/`.

## 10. Quality Gate

All diagram files in `docs/diagrams/domain/` contain valid Mermaid fenced code blocks, architectural explanations, and pass `validate_diagrams.py`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT use a diagram in this folder as the sole definition of a requirement, API, or state machine.
- Do NOT invent components, actors, or flows not present in the upstream model and specification.
