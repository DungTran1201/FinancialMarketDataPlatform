---
doc_id: GOV-MIG-DISP-001
title: "Documentation V1 Legacy Cleanup Disposition & Audit Record"
doc_type: migration-report
plane: governance
scope_level: platform
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "1.0.0"
owner_role: documentation-architect
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "Git backup tag docs-v1-legacy-2026-11-16 (commit f0329d3)"
    - "docs/governance/migration/legacy-inventory.md"
related_docs:
  - DOC-ROOT-001
  - GOV-MIG-INV-001
  - GOV-ARCH-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Recorded final disposition of all Documentation V1 files following Phase 1 cleanup and verification on branch docs-v2/phase-1-foundation."
revision_history:
  - version: "1.0.0"
    date: "2026-11-16"
    author_role: documentation-architect
    summary: "Completed legacy tree retirement while preserving full V1 history under annotated Git tag docs-v1-legacy-2026-11-16."
---

# Documentation V1 Legacy Cleanup Disposition & Audit Record

## 1. Recovery & Preservation Guarantee

No active `docs/archive/` directory is retained in the working tree. The complete pre-migration Documentation V1 snapshot remains immutably recoverable via annotated Git backup tag `docs-v1-legacy-2026-11-16` pointing to commit `f0329d3`:

```powershell
# Inspect legacy file list or restore any legacy file for reference during Phase 2
git ls-tree -r --name-only docs-v1-legacy-2026-11-16
git show docs-v1-legacy-2026-11-16:<legacy/path>
```

---

## 2. Final Disposition Table

| Legacy Path / Asset Group | File Count | Final Disposition | Replacement / Target Destination | Rationale |
|---|---|---|---|---|
| `docs/archive/*` | 2 | `DELETED_AS_OBSOLETE` | Git tag `docs-v1-legacy-2026-11-16` | Active archive directory prohibited; contained superseded v0.0 notes. |
| `docs/product/README.md` + `docs/product/00..10`, `12` (15 READMEs), `docs/features/README.md` | 16 | `DELETED_AS_OBSOLETE` | Git tag `docs-v1-legacy-2026-11-16` | Empty speculative lifecycle stubs and root product stub without capability specs. |
| `docs/product/14-governance/*` | 8 | `REPLACED_BY_GOVERNANCE_STANDARD` | `docs/governance/` policies, standards & quality gates | Stale `DOCS-001` snapshot frozen on hardcoded legacy counts. |
| `docs/templates/**` | 72 | `REPLACED_BY_GOVERNANCE_STANDARD` | `docs/governance/templates/` (42 modular Phase 2 templates) | Monolithic 57-template tree with template-count drift (`56` vs `57`). |
| `docs/diagrams/` (12 `.template.md` + 19 `README.md`) | 31 | `REPLACED_BY_GOVERNANCE_STANDARD` | `docs/governance/templates/diagrams/` (9 focused diagram templates) | Eliminated 10 empty diagram categories and detached global README boilerplate. |
| `docs/README.md` | 1 | `REPLACED_BY_GOVERNANCE_STANDARD` | [docs/README.md](../../README.md) & [docs/docs-index.yaml](../../docs-index.yaml) | Replaced legacy 15-phase/38-model links with Documentation V2 discovery entrypoints. |
| `docs/overview/*`, `docs/architecture/**` (excl. `adr/`), `docs/architecture/adr/*`, `docs/specifications/*`, `docs/contracts/*`, `docs/operations/*`, `docs/development/*`, `docs/product/11-ux/*`, `docs/product/13-operations/*`, `docs/diagrams/` (22 instantiated diagrams) | 70 | `RESERVED_FOR_PHASE_2_REBUILD` | Phase 2 target structure (`docs/overview/`, `docs/data-plane/`, `docs/application-plane/`, `docs/intelligence-plane/`) | Contained self-contradictions (monolith vs. 8 microservices, 5 vs. 6 LangGraph nodes, conflicting API routes & Compose ports); retired rather than copied forward so Phase 2 authors re-verify against code and stakeholder intent. |
| `models/**` | 52 | `DELETED_AS_OBSOLETE` | Distributed Phase 2 machine-readable capability files (`capability.yaml`, `openapi.yaml`, `asyncapi.yaml`, `data-contract.yaml`, `authorization-matrix.yaml`, `traceability.yaml`) + `docs/governance/schemas/` | Had zero runtime code or test consumers (`src/`, `tests/`); superseded by capability-owned YAML contracts. |
| `work-items/**` | 71 | `DELETED_AS_OBSOLETE` | Standard PR workflow, Git history & `docs/governance/change-management.md` | Had zero runtime consumers; legacy `DOCS-001` tracking duplicated governance policies. |
| `.agents/agents/`, `catalog/`, `config/`, `rules/`, `skills/`, `skill-registry.yaml`, `skills_manifest.json` | 107 | `DELETED_AS_OBSOLETE` | [AGENTS.md](../../../AGENTS.md) + `docs/governance/` standards | Retired conflicting V1 rules enforcing deleted `models/`, `work-items/`, and 12-section README mandates. |
| `.agents/README.md`, `.agents/hooks.json` | 2 | `REPLACED_BY_GOVERNANCE_STANDARD` | [AGENTS.md](../../../AGENTS.md) & Documentation V2 hooks | Removed `model-post-write-check` and aligned hook pointers to V2. |
| `tools/validators/validate_*.py`, `tools/hooks/post_model_write_check.py` | 11 | `DELETED_AS_OBSOLETE` | [scripts/docs/validate_docs.py](../../../scripts/docs/validate_docs.py) | Replaced hardcoded V1 count validators and model hooks with unified JSON Schema + applicability validator. |
| `tools/validators/run_all.py`, `tools/hooks/{pre_command_guard,post_doc_write_check,stop_readiness_check}.py`, `tools/**/README.md` | 7 | `REPLACED_BY_GOVERNANCE_STANDARD` | Delegated wrapper to `scripts/docs/validate_docs.py` | Preserved backwards compatibility for `.github/workflows/ci.yml`, `run.bat`, `setup.bat`, and `.agents/hooks.json`. |
| `AGENTS.md` | 1 | `REPLACED_BY_GOVERNANCE_STANDARD` | [AGENTS.md](../../../AGENTS.md) | Rebuilt as concise V2 pointer without duplicating standards prose. |
| `README.md`, `tests/README.md` | 2 | `PRESERVED_AS_PROJECT_DOCUMENT` | Updated in place | Removed broken links to retired V1 docs/models while keeping Section 1 and test category overview intact. |
| `src/**/README.md`, `frontend/README.md`, `deploy/README.md`, `notebooks/*` | 14 | `PRESERVED_AS_RUNTIME_ASSET` | Left untouched in Phase 1 | Preserved strictly outside `docs/` so Phase 1 creates zero code or runtime diffs; flagged in [legacy-inventory.md](legacy-inventory.md) for Phase 2 synchronization. |
| `pyproject.toml`, `.github/workflows/ci.yml`, `docker-compose.yml`, `.env.example`, `setup.bat`, `run.bat`, `src/`, `frontend/src/`, `deploy/`, `tests/{architecture,unit,contract,data_quality,integration,e2e,resilience,performance}/` | All runtime & test code | `PRESERVED_AS_RUNTIME_ASSET` | Kept intact (`pyproject.toml` received only `docs` + `dev` `jsonschema` extra) | Non-negotiable isolation rule: zero application behavior, API, DB, or runtime changes in Phase 1. |
