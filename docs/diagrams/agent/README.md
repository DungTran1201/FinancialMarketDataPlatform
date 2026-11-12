# Diagram Category: Agentic Intelligence, LangGraph Sequence & Tool Gateway Access Diagrams (Existing Baseline) (`docs/diagrams/agent/`)

## 1. Directory Purpose

Standardizes and stores `DIAG-C4 / DIAG-SEQ / DIAG-SEC` technical diagrams for `agent` within the unified `docs/diagrams/` subsystem.

## 2. Scope and Boundaries

- **Belongs in this directory**: `DIAG-C4 / DIAG-SEQ / DIAG-SEC` Mermaid diagram markdown files (`*.md`) and category `README.md`.
- **Does NOT belong in this directory**: Authoritative prose requirements (`docs/architecture/06-agentic-intelligence-architecture.md`) or canonical YAML models (`models/architecture/components.yaml`).

## 3. Agent Role and Responsibilities

Primary authoring role: `architecture-modeler`; audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `models/architecture/components.yaml` — Canonical structured model (authoritative entity/state/component source).
2. `docs/architecture/06-agentic-intelligence-architecture.md` — Authoritative human-readable specification.
3. `docs/diagrams/README.md` — Master diagram engineering rules.
4. `.agents/rules/diagrams.md` — Derived-view and Mermaid syntax rules.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `12-agentic-intelligence-architecture.md` | Baselined platform diagram (`DIAG-C4 / DIAG-SEQ / DIAG-SEC`) | Required (Baselined) | `docs/diagrams/agent/12-agentic-intelligence-architecture.md` |
| `13-agent-workflow-sequence.md` | Baselined platform diagram (`DIAG-C4 / DIAG-SEQ / DIAG-SEC`) | Required (Baselined) | `docs/diagrams/agent/13-agent-workflow-sequence.md` |
| `14-agent-tool-access.md` | Baselined platform diagram (`DIAG-C4 / DIAG-SEQ / DIAG-SEC`) | Required (Baselined) | `docs/diagrams/agent/14-agent-tool-access.md` |

## 6. Directory and File Organization

Directory `docs/diagrams/agent/` containing `README.md` and `DIAG-C4 / DIAG-SEQ / DIAG-SEC` markdown diagram files named `<NNN>-<kebab-slug>.md` or `<ID>-<kebab-slug>.md`.

## 7. Document Creation Rules

1. Assign a unique `DIAG-C4-<NNN>` ID conforming to `.agents/config/identifier-registry.yaml`.
2. Reference `models/architecture/components.yaml` and `docs/architecture/06-agentic-intelligence-architecture.md` in the metadata header.
3. Represent both happy paths and alternative/exception paths where applicable.
4. Quote any Mermaid node label containing parentheses `()` or brackets `[]`.

## 8. Creation Workflow

1. Read `docs/diagrams/agent/README.md`.
2. Inspect `models/architecture/components.yaml` and `docs/architecture/06-agentic-intelligence-architecture.md` to confirm all nodes and edges exist in authoritative sources.
3. Author or update the Mermaid diagram file.
4. Cross-reference the diagram file in the corresponding specification document.
5. Run `tools/validators/validate_diagrams.py`.

## 9. Relationships and Dependencies

Derived visual view of `models/architecture/components.yaml` and `docs/architecture/06-agentic-intelligence-architecture.md`.

## 10. Quality Gate

All diagram files in `docs/diagrams/agent/` contain valid Mermaid fenced code blocks, architectural explanations, and pass `validate_diagrams.py`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT use a diagram in this folder as the sole definition of a requirement, API, or state machine.
- Do NOT invent components, actors, or flows not present in the upstream model and specification.
