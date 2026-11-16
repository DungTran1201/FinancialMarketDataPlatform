# Agent Workflow & Governance Configuration (`.agents/config/`)

## 1. Directory Purpose

`.agents/config/` stores operational YAML registries that connect the Agent Operating System (`.agents/agents/`, `.agents/rules/`, `.agents/skills/`) to the **Documentation V2** architecture and governance system defined under `docs/governance/`.

## 2. Authority & Non-Duplication Rule

`docs/governance/` is the single normative source of truth for documentation architecture, lifecycle rules, artifact applicability, schemas, templates, and quality gates. The registries in `.agents/config/` map Agent workflows onto those canonical Documentation V2 paths and MUST NOT contradict or duplicate `docs/governance/`.

## 3. Active Registries

| Registry | Purpose | Authoritative V2 Reference |
|---|---|---|
| `document-map.yaml` | Maps Platform Overview, Planes, Domains, Capabilities, diagrams, and templates to V2 paths | `docs/docs-index.yaml`, `docs/governance/documentation-architecture.md` |
| `artifact-matrix.yaml` | Maps work triggers and V2 risk tiers (`LOW`, `MEDIUM`, `HIGH_CRITICAL`) to `ART-*` artifacts | `docs/governance/catalog/artifact-applicability-matrix.yaml` |
| `change-types.yaml` | Maps engineering work types and assessment signals to risk tiers and quality gates | `docs/governance/catalog/artifact-applicability-matrix.yaml`, `docs/governance/change-management.md` |
| `data-platform-boundaries.yaml` | Defines Three-Plane boundaries, storage ownership, contracts, and Medallion responsibilities | `docs/docs-index.yaml`, `docs/overview/three-plane-architecture.md` |
| `identifier-registry.yaml` | Maps canonical V2 identifier namespaces (`doc_id`, `CAP-*`, `FR-*`, `ADR-*`, `DIAG-*`, etc.) | `docs/governance/standards/writing-standards.md` |
| `phase-gates.yaml` | Maps the 9 Documentation V2 lifecycle stages and gates `QG-1-SCOPE..QG-7-OPS` | `docs/governance/documentation-lifecycle.md`, `docs/governance/quality-gates.md` |
| `status-lifecycle.yaml` | Maps decoupled Document Status (`DRAFT..DEPRECATED`) and Implementation Status (`PLANNED..VERIFIED`) | `docs/governance/versioning-and-status.md` |

## 4. Validation Commands

```powershell
.\.venv\Scripts\python.exe scripts/docs/validate_docs.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 5. Agent Restrictions

- Do NOT reference retired Documentation V1 paths (`docs/product/`, `docs/templates/`, `docs/diagrams/`, `docs/architecture/`, `docs/specifications/`, `models/`, `work-items/`).
- Do NOT invent parallel documentation hierarchies or override `docs/governance/` normative policies.
