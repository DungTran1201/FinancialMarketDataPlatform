# Documentation Engineering Decision Log (`GOV-DEC-001`)

| Document Metadata | Value |
|---|---|
| **Document ID** | `GOV-DEC-001` |
| **Title** | Documentation Engineering Governance Decision Log |
| **Version** | `1.0.0` |
| **Status** | `BASELINED` |
| **Authoring Role** | `documentation-architect` |
| **Review Role** | `documentation-auditor` |
| **Created Date** | `2026-11-12` |
| **Updated Date** | `2026-11-12` |
| **Work Item Reference** | `work-items/DOCS-001-documentation-engineering-foundation/` |

---

## 1. Recorded Governance Decisions

| Decision ID | Date | Decision Summary | Rationale |
|---|---|---|---|
| `DEC-DOC-001` | `2026-11-12` | Preserve `docs/architecture/` and `docs/specifications/` as the shared platform baseline while placing the 15-phase product lifecycle under `docs/product/00..14/`. | Prevents duplicating or overwriting the 25 existing Data Platform, Backend, and Agent specifications. |
| `DEC-DOC-002` | `2026-11-12` | Maintain `docs/diagrams/` as the single unified diagram root across the repository. | Avoids creating a competing top-level `/diagrams/` folder that would split diagram discovery. |
| `DEC-DOC-003` | `2026-11-12` | Use `WEB-*` identifier prefixes (`WEB-FR-###`, `WEB-UC-###`, `WEB-ADR-###`) for future Website product artifacts. | Preserves existing Data Platform IDs (`FR-01..10`, `ADR-001..006`) without collisions or renumbering. |
| `DEC-DOC-004` | `2026-11-12` | Exclude AI-Chan product-specific artifacts (`ponytail.md`, VRM companion, Discord bot skills) when adapting `AgentHarnessBuilderTools`. | Keeps `.agents/`, `models/`, and `docs/` 100% focused on `FinancialMarketDataPlatform`. |
