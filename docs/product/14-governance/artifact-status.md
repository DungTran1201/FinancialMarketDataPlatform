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
- **`BASELINED`**: Verified Data Platform architecture (`docs/architecture/00..14`, `ADR-001..008`), shared specifications (`docs/specifications/*`), core platform canonical models (`models/requirements/`, `models/architecture/`, `models/domain/`, `models/data-platform/`, `models/api/`, `models/security/`, `models/testing/`, `models/deployment/`, `models/ux/`), Agent governance (`.agents/`), and validation tooling (`tools/`). Note: individual platform claims carry explicit implementation status markers (`IMPLEMENTED`, `PARTIALLY_IMPLEMENTED`, `PLANNED`, `DEPRECATED`) under `DOCS-004`.
- **`TEMPLATE`**: All 57 document templates in `docs/templates/**/*.template.md`, 12 model templates in `models/**/*.template.yaml`, 12 diagram templates in `docs/diagrams/**/*.template.md`, and `work-items/_template/*`.
- **`PARTIALLY_IMPLEMENTED` / `DRAFT` (`00..13`)**: Populated feature specs exist in `docs/features/FEAT-001-*` and `FEAT-002-*` alongside active UX/ops specs (`docs/product/11-ux/*`, `docs/product/13-operations/*`); unpopulated product lifecycle placeholders remain clearly marked where deferred.

---

## 2. Subsystem Status Table

| Artifact Group | Path Pattern | Current Status | Promotion Gate Cleared |
|---|---|---|---|
| Shared Architecture & ADRs | `docs/architecture/**` (`00..14`, `ADR-001..008`) | `BASELINED` | Phase 0 + `DOCS-004` Reconciliation |
| Shared Platform Specifications & Contracts | `docs/specifications/**`, `docs/contracts/**` | `BASELINED` | Phase 0 + `DOCS-004` Reconciliation |
| Active Platform Diagrams (22 `DIAG-*`) | `docs/diagrams/{system,data-platform,backend,agent,deployment,security,ux}/*` | `BASELINED` | `validate_diagrams.py` + `DOCS-004` |
| Reusable Document Templates | `docs/templates/**/*.template.md` | `TEMPLATE` | `validate_templates.py` |
| Canonical Platform Models | `models/{requirements,process,context,architecture,domain,data-platform,api,interaction,state,security,testing,deployment,ux}/*.yaml` | `BASELINED` | `validate_models.py` |
| Feature Packages | `docs/features/FEAT-001-*`, `FEAT-002-*` | `BASELINED` | `validate_docs.py` |
| Work Items | `work-items/{ARCH-001,DATA-001,DOCS-001,DOCS-002,DOCS-003,DOCS-004,FEAT-001,FEAT-002}-*` | `ACTIVE` / `DONE` | `validate_work_items.py` |
