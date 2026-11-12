# Master Documentation System Index (`docs/`)

## 1. Directory Purpose

`docs/` is the authoritative human-readable specification and engineering documentation root for `FinancialMarketDataPlatform`. It unifies the preserved Data Platform & Backend baseline (`docs/architecture/`, `docs/specifications/`), the 15-phase Product & Website engineering lifecycle (`docs/product/00-discovery` through `14-governance`), self-contained feature packages (`docs/features/`), the centralized template catalog (`docs/templates/`), and the unified technical diagram subsystem (`docs/diagrams/`).

## 2. Scope and Boundaries

- **Belongs in this directory**: `architecture/`, `specifications/`, `product/`, `features/`, `templates/`, and `diagrams/`.
- **Does NOT belong in this directory**: Machine-readable canonical YAML models (`models/`), change-control logs (`work-items/`), or Agent configs (`.agents/`).

## 3. Agent Role and Responsibilities

Governed by `documentation-architect` and audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `AGENTS.md` — Root Agent operating system contract.
2. `.agents/config/document-map.yaml` — Master directory and phase mapping.
3. `models/` — Canonical structured YAML models.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `architecture/` | Preserved shared Data Platform, Backend & Agent architecture (00..13 + ADRs) | Required | `docs/architecture/README.md` |
| `specifications/` | Preserved shared Data Platform & API specifications | Required | `docs/specifications/README.md` |
| `product/` | 15-phase Product & Website lifecycle documentation (`00`..`14`) | Required | `docs/product/README.md` |
| `features/` | Self-contained feature documentation packages | Conditional | `docs/features/README.md` |
| `templates/` | Centralized reusable document template library (14 categories) | Required | `docs/templates/README.md` |
| `diagrams/` | Unified technical diagram subsystem (`DIAG-*`) | Required | `docs/diagrams/README.md` |

## 6. Directory and File Organization

Divided into 6 top-level subdirectories under `docs/` without duplicate documentation roots.

## 7. Document Creation Rules

Every document must be instantiated from `docs/templates/`, carry a registered identifier from `.agents/config/identifier-registry.yaml`, and synchronize with `models/`.

## 8. Creation Workflow

1. Read `AGENTS.md` and `docs/README.md`.
2. Navigate to the target subdirectory (`docs/product/<phase>/`, `docs/architecture/`, or `docs/features/<slug>/`) and read its `README.md`.
3. Update the corresponding canonical YAML model in `models/` first.
4. Instantiate the required template from `docs/templates/`.
5. Run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

Renders human-readable specifications from `models/` and links to visual views in `docs/diagrams/`.

## 10. Quality Gate

100% of managed subdirectories under `docs/` contain a valid 12-section `README.md` and pass `tools/validators/run_all.py`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT create a second copy of `docs/architecture/` or `docs/specifications/` inside `docs/product/`.
- Do NOT overwrite existing baselined Data Platform architecture or ADR files without an approved `ARCH` work item.
- Do NOT invent Website business features or mark unverified specs as `APPROVED`.
