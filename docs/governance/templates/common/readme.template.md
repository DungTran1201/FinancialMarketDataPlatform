---
doc_id: TPL-COM-README-001
title: "Template: Scoped Navigation README"
doc_type: template
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: documentation-tooling-engineer
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/templates/common/readme.template.md"
related_docs:
  - GOV-TPL-ROOT-001
  - GOV-STD-AGENT-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created concise scoped README template for Plane, Domain, and Capability navigation."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: documentation-tooling-engineer
    summary: "Initial V2 scoped README template."
---

# Template: Scoped Navigation README

Use this template for every Plane (`docs/<plane>/README.md`), Domain (`domains/<domain>/README.md`), and Capability (`capabilities/<capability>/README.md`) index so Agents can navigate without scanning unrelated directories.

---

```yaml
---
doc_id: "<SCOPE-INDEX-001>"
title: "<Scope Name>"
doc_type: "index"
plane: "<plane>"
scope_level: "<plane|domain|capability>"
status: "DRAFT"
implementation_status: "NOT_APPLICABLE"
version: "0.1.0"
owner_role: "<owner-role>"
accountable_role: "<accountable-role>"
created_at: "YYYY-MM-DD"
updated_at: "YYYY-MM-DD"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "<path/to/this/README.md>"
related_docs: []
---
```

# `<Scope Name>`

## 1. Purpose & Ownership Boundary `[REQUIRED]`

- **Owner Role**: `<role>`
- **Scope**: `<1-3 sentences describing what belongs here and what belongs elsewhere>`

## 2. Authoritative Artifacts & Navigation `[REQUIRED]`

| Artifact | Purpose | Status | Link |
|---|---|---|---|
| `<filename>` | `<purpose>` | `DRAFT` | `[<filename>](<filename>)` |

## 3. Child Scopes / Capabilities `[CONDITIONAL: Required for Plane and Domain READMEs]`

| Name | Scope Summary | Owner | Path |
|---|---|---|---|
| `<child>` | `<summary>` | `<role>` | `[<child>/](<child>/README.md)` |

## 4. Related Code & Runtime Paths `[CONDITIONAL: Required when runtime code exists]`

- `<src/...>`
- `<tests/...>`
