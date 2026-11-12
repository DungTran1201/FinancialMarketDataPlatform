# Unresolved Issues, Assumptions & Deferred Scope Register (`GOV-OQ-001`)

| Document Metadata | Value |
|---|---|
| **Document ID** | `GOV-OQ-001` |
| **Title** | Unresolved Questions & Deferred Product Scope Register |
| **Version** | `1.0.0` |
| **Status** | `BASELINED` |
| **Authoring Role** | `discovery-analyst` |
| **Review Role** | `documentation-auditor` |
| **Created Date** | `2026-11-12` |
| **Updated Date** | `2026-11-12` |
| **Work Item Reference** | `work-items/DOCS-001-documentation-engineering-foundation/` |

---

## 1. Deferred Scope & Open Questions (`OPEN QUESTION`)

| ID | Category | Description | Status | Resolution Path |
|---|---|---|---|---|
| `OQ-001` | Website Product Scope | Website business features, user personas, screen inventory (`SCR-###`), and product Use Cases (`WEB-UC-###`) are intentionally not defined during `DOCS-001` framework initialization. | `DEFERRED_BY_DIRECTIVE` | Initiate Work Item `FEAT-001` using `.agents/skills/project-discovery/SKILL.md` when Website product requirements are provided. |
| `OQ-002` | Production Empirical Benchmarks | Tier-1 / Tier-2 ClickHouse + Kafka disk contention and LLM token cost baselines require live container benchmark execution during Phase 1–5 implementation. | `OPEN` | Tracked in `docs/specifications/non-functional-requirements.md` Section 6. |
