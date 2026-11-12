# Architecture Templates (`docs/templates/architecture/`)

## 1. Directory Purpose

Provides reusable markdown templates for lifecycle phase `06-architecture`, targeting `docs/product/06-architecture/` and feature packages in `docs/features/`.

## 2. Scope and Boundaries

- **Belongs in this directory**: Reusable `*.template.md` files for `architecture` documentation (`SAD.template.md, system-context.template.md, C4-container.template.md, C4-component.template.md, architecture-overview.template.md, ADR.template.md`).
- **Does NOT belong in this directory**: Populated project documents (which must be saved in `docs/product/06-architecture/` or `docs/features/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `architecture-modeler`; review role: `documentation-architect`.

## 4. Authoritative Inputs

1. `docs/templates/README.md` — Master template library contract.
2. `docs/product/06-architecture/README.md` — Target lifecycle phase operating contract.
3. `models/architecture/architecture.yaml` — Associated canonical model.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `SAD.template.md` | Software Architecture Document (SAD) (`ARCH-SAD-[NNN]`) | Required | `docs/templates/architecture/SAD.template.md` |
| `system-context.template.md` | System Context Specification (C4 Level 1) (`ARCH-CTX-[NNN]`) | Required | `docs/templates/architecture/system-context.template.md` |
| `C4-container.template.md` | C4 Container Architecture Specification (C4 Level 2) (`ARCH-C4C-[NNN]`) | Required | `docs/templates/architecture/C4-container.template.md` |
| `C4-component.template.md` | C4 Component Architecture Specification (C4 Level 3) (`ARCH-COMP-[NNN]`) | Required | `docs/templates/architecture/C4-component.template.md` |
| `architecture-overview.template.md` | Architecture Overview & Plane Blueprint (`ARCH-OVW-[NNN]`) | Required | `docs/templates/architecture/architecture-overview.template.md` |
| `ADR.template.md` | Architecture Decision Record (ADR) (`ADR-[NNN]`) | Required | `docs/templates/architecture/ADR.template.md` |

## 6. Directory and File Organization

Flat directory `docs/templates/architecture/` containing `README.md` and 6 `.template.md` files.

## 7. Document Creation Rules

Instantiate templates into the target phase directory, assign a stable ID from `.agents/config/identifier-registry.yaml`, and preserve all `[MANDATORY]` sections.

## 8. Creation Workflow

1. Read `docs/templates/architecture/README.md` and `docs/product/06-architecture/README.md`.
2. Inspect authoritative canonical model `models/architecture/architecture.yaml`.
3. Copy the selected `.template.md` file to `docs/product/06-architecture/`.
4. Populate verified facts and explicitly tag assumptions/open questions.
5. Run `tools/validators/validate_templates.py` and `tools/validators/validate_docs.py`.

## 9. Relationships and Dependencies

Mapped to `docs/product/06-architecture/` in `.agents/config/document-map.yaml`.

## 10. Quality Gate

All templates in this folder pass `validate_templates.py` and `validate_readmes.py` with zero errors.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT edit files inside `docs/templates/architecture/` to hold feature-specific data.
- Do NOT invent unverified requirements when instantiating these templates.
