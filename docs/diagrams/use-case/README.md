# Diagram Category: UML Use Case Scope & Actor Packaging Diagrams (`docs/diagrams/use-case/`)

## 1. Directory Purpose

Standardizes and stores `DIAG-UC` technical diagrams for `use-case` within the unified `docs/diagrams/` subsystem.

## 2. Scope and Boundaries

- **Belongs in this directory**: `DIAG-UC` Mermaid diagram markdown files (`*.md`) and category `README.md`.
- **Does NOT belong in this directory**: Authoritative prose requirements (`docs/product/04-use-cases/`) or canonical YAML models (`models/interaction/interactions.yaml`).

## 3. Agent Role and Responsibilities

Primary authoring role: `requirements-engineer`; audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `models/interaction/interactions.yaml` — Canonical structured model (authoritative entity/state/component source).
2. `docs/product/04-use-cases/` — Authoritative human-readable specification.
3. `docs/diagrams/README.md` — Master diagram engineering rules.
4. `.agents/rules/diagrams.md` — Derived-view and Mermaid syntax rules.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `use-case-diagram.template.md` | Reusable `DIAG-UC` Mermaid diagram template | Conditional | `docs/diagrams/use-case/use-case-diagram.template.md` |

## 6. Directory and File Organization

Directory `docs/diagrams/use-case/` containing `README.md` and `DIAG-UC` markdown diagram files named `<NNN>-<kebab-slug>.md` or `<ID>-<kebab-slug>.md`.

## 7. Document Creation Rules

1. Assign a unique `DIAG-UC-<NNN>` ID conforming to `.agents/config/identifier-registry.yaml`.
2. Reference `models/interaction/interactions.yaml` and `docs/product/04-use-cases/` in the metadata header.
3. Represent both happy paths and alternative/exception paths where applicable.
4. Quote any Mermaid node label containing parentheses `()` or brackets `[]`.

## 8. Creation Workflow

1. Read `docs/diagrams/use-case/README.md`.
2. Inspect `models/interaction/interactions.yaml` and `docs/product/04-use-cases/` to confirm all nodes and edges exist in authoritative sources.
3. Author or update the Mermaid diagram file.
4. Cross-reference the diagram file in the corresponding specification document.
5. Run `tools/validators/validate_diagrams.py`.

## 9. Relationships and Dependencies

Derived visual view of `models/interaction/interactions.yaml` and `docs/product/04-use-cases/`.

## 10. Quality Gate

All diagram files in `docs/diagrams/use-case/` contain valid Mermaid fenced code blocks, architectural explanations, and pass `validate_diagrams.py`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT use a diagram in this folder as the sole definition of a requirement, API, or state machine.
- Do NOT invent components, actors, or flows not present in the upstream model and specification.
