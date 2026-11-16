# Documentation V2 Authoring & Template Governance Rule (`RULE-002`)

| Metadata | Value |
|---|---|
| **Rule ID** | `RULE-002` |
| **Rule Slug** | `documentation` |
| **Activation Mode** | `Always Active` |
| **Status** | `APPROVED` |
| **Updated Date** | `2026-11-16` |

---

## 1. Purpose & Scope

Ensures all Markdown specifications under `docs/` follow Documentation V2 scoping (`Platform -> Plane -> Domain -> Capability`), instantiate reusable templates from `docs/governance/templates/`, and satisfy `document-frontmatter.schema.json`.

## 2. Mandatory Directives

1. **Narrowest Owning Scope**: Author specifications at the narrowest owning scope per `docs/governance/documentation-architecture.md` and `.agents/config/document-map.yaml`.
2. **Template & Frontmatter Compliance**: Instantiate new documents from `docs/governance/templates/` and include complete YAML frontmatter matching `docs/governance/schemas/document-frontmatter.schema.json`.
3. **Normative Writing Standards**: Follow `docs/governance/standards/writing-standards.md` (English only, single H1, sequential heading hierarchy, zero empty sections, ISO-8601 dates, valid relative links).
4. **Applicability Discipline**: Author only artifacts marked `REQUIRED`, `CONDITIONAL` (when signals trigger), or justified `RECOMMENDED` in `docs/governance/catalog/artifact-applicability-matrix.yaml`.

## 3. Prohibited Actions

- Never create empty placeholder directories under `docs/` or `docs/archive/`.
- Never duplicate governance standards prose inside `.agents/` or capability specifications.
- Never promote a document containing unresolved `TBD`, `TODO`, `FIXME`, or `[TO BE COMPLETED]` tokens to `APPROVED`.

## 4. Verification Mechanism

- Automated schema, frontmatter, link, heading, and structure checks via `scripts/docs/validate_docs.py`.
