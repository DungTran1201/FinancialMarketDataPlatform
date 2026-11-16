# Scoped Diagram Governance & Derived View Rule (`RULE-004`)

| Metadata | Value |
|---|---|
| **Rule ID** | `RULE-004` |
| **Rule Slug** | `diagrams` |
| **Activation Mode** | `Always Active` |
| **Status** | `APPROVED` |
| **Updated Date** | `2026-11-16` |

---

## 1. Purpose & Scope

Enforces Documentation V2 rules from `docs/governance/standards/diagram-standards.md` so all diagrams live adjacent to their owning scope, declare `is_authoritative: false`, and remain strictly derived from authoritative specifications and code.

## 2. Mandatory Directives

1. **Scoped Placement**: Place diagrams strictly in `docs/overview/diagrams/`, `docs/<plane>/architecture/diagrams/`, or capability `design/`, `workflows/`, `security/`, and `data/` folders using templates from `docs/governance/templates/diagrams/`.
2. **Derived View Frontmatter**: Set `doc_type: diagram`, `source_of_truth.is_authoritative: false`, and list exact upstream `source_of_truth.authoritative_source` files.
3. **Mandatory Sections & Syntax**: Include `Diagram Metadata` and `Legend` sections, valid Mermaid headers (or `.bpmn` refs), balanced `subgraph`/`end` blocks, and quoted labels containing parentheses/brackets (`id["Label (Detail)"]`).

## 3. Prohibited Actions

- Never recreate a detached repository-wide `docs/diagrams/` directory.
- Never treat a diagram as a primary source of truth or introduce undocumented components, routes, or stores inside Mermaid blocks.

## 4. Verification Mechanism

- `scripts/docs/validate_docs.py` (`VAL-DIAG-SOT-001`, `VAL-DIAG-META-001`, `VAL-DIAG-MERMAID-001`).
