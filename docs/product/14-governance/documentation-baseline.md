# Documentation Engineering Baseline (`GOV-BASE-001`)

| Document Metadata | Value |
|---|---|
| **Document ID** | `GOV-BASE-001` |
| **Title** | Master Documentation Engineering Architecture & Baseline Register |
| **Version** | `1.0.0` |
| **Status** | `BASELINED` |
| **Authoring Role** | `documentation-architect` |
| **Review Role** | `documentation-auditor` |
| **Created Date** | `2026-11-12` |
| **Updated Date** | `2026-11-12` |
| **Work Item Reference** | `work-items/DOCS-001-documentation-engineering-foundation/` |

---

## 1. Documentation Engineering Subsystems Baseline

| Subsystem | Root Path | Baseline Scope | Status |
|---|---|---|---|
| **Root Operating Contract** | `AGENTS.md` | 12-step README-first, model-driven, work-item-controlled protocol | `BASELINED` |
| **Agent Operating System** | `.agents/` | 19 Agent roles, 22 Operating rules, 25 Engineering skills, 6 YAML registries, `hooks.json` | `BASELINED` |
| **Shared Platform Architecture** | `docs/architecture/` | 15 core architecture docs (`00`..`14`) + 8 ADRs (`ADR-001..008`) | `BASELINED` |
| **Shared Platform Specifications** | `docs/specifications/` | 5 core platform specifications (`data-requirements`, `data-dictionary`, `data-contracts`, `api-specification`, `non-functional-requirements`) | `BASELINED` |
| **Product 15-Phase Lifecycle** | `docs/product/00..14/` | 15 lifecycle phases + nested use-case/ADR folders with operational READMEs | `BASELINED` (Structure) |
| **Feature Package Workspace** | `docs/features/` | 11-document self-contained feature specification standard (`FEAT-001`, `FEAT-002`) | `BASELINED` |
| **Document Template Library** | `docs/templates/` | 14 categories and 57 reusable `.template.md` blueprints | `BASELINED` |
| **Canonical YAML Models** | `models/` | 13 domain model folders (38 YAML files, including `models/data-platform/`) with `.template.yaml` and canonical `.yaml` files | `BASELINED` |
| **Unified Diagram Subsystem** | `docs/diagrams/` | 18 diagram categories, 22 active platform diagrams (`DIAG-*`) + 12 reusable diagram templates | `BASELINED` |
| **Work Item Control System** | `work-items/` | `_template/` (9 files) + `ARCH-001`, `DATA-001`, `DOCS-001`, `DOCS-002`, `DOCS-003`, `DOCS-004`, `FEAT-001`, `FEAT-002` | `BASELINED` |
| **Automated Validation Suite** | `tools/` | 10 validators + `run_all.py` + 4 workspace lifecycle hooks | `BASELINED` |
