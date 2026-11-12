# Diagram Category: Business & Operational Process Diagrams (Parent Index) (`docs/diagrams/process/`)

## 1. Directory Purpose

Standardizes and stores `DIAG-BPMN / DIAG-SWIM` technical diagrams for `process` within the unified `docs/diagrams/` subsystem.

## 2. Scope and Boundaries

- **Belongs in this directory**: `DIAG-BPMN / DIAG-SWIM` Mermaid diagram markdown files (`*.md`) and category `README.md`.
- **Does NOT belong in this directory**: Authoritative prose requirements (`docs/product/03-business-process/`) or canonical YAML models (`models/process/processes.yaml`).

## 3. Agent Role and Responsibilities

Primary authoring role: `process-modeler`; audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `models/process/processes.yaml` — Canonical structured model (authoritative entity/state/component source).
2. `docs/product/03-business-process/` — Authoritative human-readable specification.
3. `docs/diagrams/README.md` — Master diagram engineering rules.
4. `.agents/rules/diagrams.md` — Derived-view and Mermaid syntax rules.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `process-diagram.template.md` | Reusable `DIAG-BPMN / DIAG-SWIM` Mermaid diagram template | Conditional | `docs/diagrams/process/process-diagram.template.md` |

## 6. Directory and File Organization

Directory `docs/diagrams/process/` containing `README.md` and `DIAG-BPMN / DIAG-SWIM` markdown diagram files named `<NNN>-<kebab-slug>.md` or `<ID>-<kebab-slug>.md`.

## 7. Document Creation Rules

1. Assign a unique `DIAG-BPMN-<NNN>` ID conforming to `.agents/config/identifier-registry.yaml`.
2. Reference `models/process/processes.yaml` and `docs/product/03-business-process/` in the metadata header.
3. Represent both happy paths and alternative/exception paths where applicable.
4. Quote any Mermaid node label containing parentheses `()` or brackets `[]`.

## 8. Creation Workflow

1. Read `docs/diagrams/process/README.md`.
2. Inspect `models/process/processes.yaml` and `docs/product/03-business-process/` to confirm all nodes and edges exist in authoritative sources.
3. Author or update the Mermaid diagram file.
4. Cross-reference the diagram file in the corresponding specification document.
5. Run `tools/validators/validate_diagrams.py`.

## 9. Relationships and Dependencies

Derived visual view of `models/process/processes.yaml` and `docs/product/03-business-process/`.

## 10. Quality Gate

All diagram files in `docs/diagrams/process/` contain valid Mermaid fenced code blocks, architectural explanations, and pass `validate_diagrams.py`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT use a diagram in this folder as the sole definition of a requirement, API, or state machine.
- Do NOT invent components, actors, or flows not present in the upstream model and specification.
