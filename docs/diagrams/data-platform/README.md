# Diagram Category: Data Platform, Ingestion, Event Streaming & Medallion Flow Diagrams (Existing Baseline) (`docs/diagrams/data-platform/`)

## 1. Directory Purpose

Standardizes and stores `DIAG-DATA` technical diagrams for `data-platform` within the unified `docs/diagrams/` subsystem.

## 2. Scope and Boundaries

- **Belongs in this directory**: `DIAG-DATA` Mermaid diagram markdown files (`*.md`) and category `README.md`.
- **Does NOT belong in this directory**: Authoritative prose requirements (`docs/architecture/04-data-platform-architecture.md`) or canonical YAML models (`models/process/processes.yaml`).

## 3. Agent Role and Responsibilities

Primary authoring role: `architecture-modeler`; audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `models/process/processes.yaml` — Canonical structured model (authoritative entity/state/component source).
2. `docs/architecture/04-data-platform-architecture.md` — Authoritative human-readable specification.
3. `docs/diagrams/README.md` — Master diagram engineering rules.
4. `.agents/rules/diagrams.md` — Derived-view and Mermaid syntax rules.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `04-overall-data-platform.md` | Baselined platform diagram (`DIAG-DATA`) | Required (Baselined) | `docs/diagrams/data-platform/04-overall-data-platform.md` |
| `05-data-ingestion.md` | Baselined platform diagram (`DIAG-DATA`) | Required (Baselined) | `docs/diagrams/data-platform/05-data-ingestion.md` |
| `06-event-streaming.md` | Baselined platform diagram (`DIAG-DATA`) | Required (Baselined) | `docs/diagrams/data-platform/06-event-streaming.md` |
| `07-bronze-silver-gold-flow.md` | Baselined platform diagram (`DIAG-DATA`) | Required (Baselined) | `docs/diagrams/data-platform/07-bronze-silver-gold-flow.md` |

## 6. Directory and File Organization

Directory `docs/diagrams/data-platform/` containing `README.md` and `DIAG-DATA` markdown diagram files named `<NNN>-<kebab-slug>.md` or `<ID>-<kebab-slug>.md`.

## 7. Document Creation Rules

1. Assign a unique `DIAG-DATA-<NNN>` ID conforming to `.agents/config/identifier-registry.yaml`.
2. Reference `models/process/processes.yaml` and `docs/architecture/04-data-platform-architecture.md` in the metadata header.
3. Represent both happy paths and alternative/exception paths where applicable.
4. Quote any Mermaid node label containing parentheses `()` or brackets `[]`.

## 8. Creation Workflow

1. Read `docs/diagrams/data-platform/README.md`.
2. Inspect `models/process/processes.yaml` and `docs/architecture/04-data-platform-architecture.md` to confirm all nodes and edges exist in authoritative sources.
3. Author or update the Mermaid diagram file.
4. Cross-reference the diagram file in the corresponding specification document.
5. Run `tools/validators/validate_diagrams.py`.

## 9. Relationships and Dependencies

Derived visual view of `models/process/processes.yaml` and `docs/architecture/04-data-platform-architecture.md`.

## 10. Quality Gate

All diagram files in `docs/diagrams/data-platform/` contain valid Mermaid fenced code blocks, architectural explanations, and pass `validate_diagrams.py`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT use a diagram in this folder as the sole definition of a requirement, API, or state machine.
- Do NOT invent components, actors, or flows not present in the upstream model and specification.
