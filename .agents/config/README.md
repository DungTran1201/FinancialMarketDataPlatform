# Agent Workflow & Governance Configuration (`.agents/config/`)

## 1. Directory Purpose

`.agents/config/` stores the machine-readable YAML registries that control phase mapping, artifact selection by change type, work-item classification, phase quality gates, identifier namespaces, and artifact status lifecycles.

## 2. Scope and Boundaries

- **Belongs in this directory**: `document-map.yaml`, `artifact-matrix.yaml`, `change-types.yaml`, `phase-gates.yaml`, `identifier-registry.yaml`, `status-lifecycle.yaml`, and `data-platform-boundaries.yaml`.
- **Does NOT belong in this directory**: Prose documentation (`docs/`), canonical domain data (`models/`), or Python scripts (`tools/`).

## 3. Agent Role and Responsibilities

Maintained by `documentation-architect` and validated by `documentation-auditor`.

## 4. Authoritative Inputs

1. `AGENTS.md` — Root operating contract.
2. `.agents/README.md` — Agent OS overview.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `document-map.yaml` | Maps 15 lifecycle phases and shared baselines to models, diagrams, and templates | Required | `.agents/config/document-map.yaml` |
| `artifact-matrix.yaml` | Defines baseline and conditional artifacts per change type | Required | `.agents/config/artifact-matrix.yaml` |
| `change-types.yaml` | Defines FEAT, BUG, ARCH, DATA, SEC, INFRA, REFACTOR, DOCS and risk tiers R1..R3 | Required | `.agents/config/change-types.yaml` |
| `phase-gates.yaml` | Defines G0_DISCOVERY..G6_RELEASE gates and state transitions | Required | `.agents/config/phase-gates.yaml` |
| `identifier-registry.yaml` | Defines canonical ID prefixes, regex patterns, and preserved IDs | Required | `.agents/config/identifier-registry.yaml` |
| `status-lifecycle.yaml` | Defines DRAFT, PROPOSED, IN_REVIEW, APPROVED, BASELINED transitions | Required | `.agents/config/status-lifecycle.yaml` |
| `data-platform-boundaries.yaml` | Defines Three-Plane boundaries, storage responsibilities, and implemented vs target components | Required | `.agents/config/data-platform-boundaries.yaml` |

## 6. Directory and File Organization

Seven flat YAML configuration files inside `.agents/config/`.

## 7. Document Creation Rules

All files must be valid YAML 1.2 with `version` and `metadata` keys, referencing real repository paths.

## 8. Creation Workflow

1. Read `.agents/config/README.md`.
2. Verify that any path added to `document-map.yaml` or `artifact-matrix.yaml` exists in the repository.
3. Validate YAML syntax and schema via `validate_agent_config.py` and `validate_artifact_matrix.py`.

## 9. Relationships and Dependencies

Consumed directly by `tools/validators/` scripts and all Agent skills during work-item planning and verification.

## 10. Quality Gate

All 7 YAML files parse cleanly and every referenced path resolves on disk.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT remove preserved identifier ranges (`FR-01..10`, `ADR-001..006`) from `identifier-registry.yaml`.
- Do NOT reference non-existent directories in `document-map.yaml`.
