---
doc_id: "DOC-DIAG-ROOT"
title: "Architecture & Engineering Diagrams Index"
version: "1.0.0"
status: "IN_REVIEW"
implementation_status: "NOT_APPLICABLE"
owner: "Principal Software Architect"
purpose: "Centralized directory for Mermaid architectural, data-flow, sequence, deployment, and threat-model diagrams derived from authoritative specs."
scope: "All Mermaid diagram files under docs/diagrams/."
dependencies:
  - "docs/architecture/README.md"
references:
  - "docs/README.md"
assumptions:
  - "Diagrams depict verified design/reality without duplicating authoritative prose."
open_issues: []
review_criteria:
  - "All Mermaid blocks validate syntax & balanced subgraph boundaries via tools/validators/run_all.py"
---

# Centralized Diagrams (`docs/diagrams/`)

Contains standalone Mermaid diagrams synchronized with [docs/architecture/](../architecture/README.md), [docs/product/](../product/README.md), and later data/quant specifications.

## Rules
- Every diagram file MUST declare YAML frontmatter metadata and cite its authoritative source spec in `references`.
- Distinguish solid arrows (`active / verified / primary path`) from dashed arrows (`optional / async / recovery / future path`) in legends.

