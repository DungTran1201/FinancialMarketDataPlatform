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
| **Agent Operating System** | `.agents/` | 11 Agent roles, 10 Operating rules, 16 Engineering skills, 6 YAML registries, `hooks.json` | `BASELINED` |
| **Shared Platform Architecture** | `docs/architecture/` | 14 core architecture docs (`00`..`13`) + 6 ADRs (`ADR-001..006`) | `BASELINED` |
| **Shared Platform Specifications** | `docs/specifications/` | 5 core platform specifications (`data-requirements`, `data-dictionary`, `data-contracts`, `api-specification`, `non-functional-requirements`) | `BASELINED` |
| **Product 15-Phase Lifecycle** | `docs/product/00..14/` | 15 lifecycle phases + nested use-case/ADR folders with operational READMEs | `BASELINED` (Structure) |
| **Feature Package Workspace** | `docs/features/` | 11-document self-contained feature specification standard | `BASELINED` (Structure) |
| **Document Template Library** | `docs/templates/` | 14 categories and 57 reusable `.template.md` blueprints | `BASELINED` |
| **Canonical YAML Models** | `models/` | 12 domain model folders with `.template.yaml` and canonical `.yaml` files | `BASELINED` |
| **Unified Diagram Subsystem** | `docs/diagrams/` | 18 diagram categories, 16 baselined platform diagrams + 12 reusable diagram templates | `BASELINED` |
| **Work Item Control System** | `work-items/` | `_template/` (9 files) + `DOCS-001-documentation-engineering-foundation/` | `BASELINED` |
| **Automated Validation Suite** | `tools/` | 10 validators + `run_all.py` + 4 workspace lifecycle hooks | `BASELINED` |
