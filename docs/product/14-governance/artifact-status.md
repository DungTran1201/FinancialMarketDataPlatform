# Artifact Status & Lifecycle Register (`GOV-STAT-001`)

| Document Metadata | Value |
|---|---|
| **Document ID** | `GOV-STAT-001` |
| **Title** | Repository Artifact Status & Promotion Register |
| **Version** | `1.0.0` |
| **Status** | `BASELINED` |
| **Authoring Role** | `documentation-auditor` |
| **Review Role** | `documentation-architect` |
| **Created Date** | `2026-11-12` |
| **Updated Date** | `2026-11-12` |
| **Work Item Reference** | `work-items/DOCS-001-documentation-engineering-foundation/` |

---

## 1. Artifact Status Classification Summary

In accordance with `.agents/config/status-lifecycle.yaml`:
- **`BASELINED`**: Verified Phase 0 Data Platform architecture (`docs/architecture/00..13`, `ADR-001..006`), shared specifications (`docs/specifications/*`), core platform canonical models (`models/requirements/`, `models/architecture/`, `models/domain/`, `models/api/`, `models/security/`, `models/testing/`, `models/deployment/`), Agent governance (`.agents/`), and validation tooling (`tools/`).
- **`TEMPLATE`**: All 57 document templates in `docs/templates/**/*.template.md`, 12 model templates in `models/**/*.template.yaml`, 12 diagram templates in `docs/diagrams/**/*.template.md`, and `work-items/_template/*`.
- **`DRAFT`**: `models/ux/ux.yaml` and future Website product feature specifications under `docs/product/00..13` (intentionally unpopulated until Website product discovery begins).

---

## 2. Subsystem Status Table

| Artifact Group | Path Pattern | Current Status | Promotion Gate Cleared |
|---|---|---|---|
| Shared Architecture & ADRs | `docs/architecture/**` | `BASELINED` | Phase 0 + `G6_RELEASE` |
| Shared Platform Specifications | `docs/specifications/**` | `BASELINED` | Phase 0 + `G6_RELEASE` |
| Platform Diagrams (`01`..`16`) | `docs/diagrams/{system,data-platform,backend,agent,deployment,security}/*` | `BASELINED` | Phase 0 + `G6_RELEASE` |
| Reusable Document Templates | `docs/templates/**/*.template.md` | `TEMPLATE` | `validate_templates.py` |
| Canonical Platform Models | `models/{requirements,process,context,architecture,domain,api,interaction,state,security,testing,deployment}/*.yaml` | `BASELINED` | `validate_models.py` |
| Canonical UX Model | `models/ux/ux.yaml` | `DRAFT` | Unpopulated product placeholder |
| Work Item `DOCS-001` | `work-items/DOCS-001-documentation-engineering-foundation/` | `DONE` | `G6_RELEASE` |
