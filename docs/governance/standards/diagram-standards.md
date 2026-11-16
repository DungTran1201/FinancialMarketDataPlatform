---
doc_id: GOV-STD-DIAG-001
title: "Technical Diagramming Standards & Notation Conventions"
doc_type: standard
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: system-architect
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/standards/diagram-standards.md"
related_docs:
  - GOV-STD-ARCH-001
  - GOV-CAT-MAT-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Defined risk-based diagram applicability, 13 canonical diagram types, mandatory metadata, legend/direction rules, and syntax conventions."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: system-architect
    summary: "Initial Documentation V2 diagram standards."
---

# Technical Diagramming Standards & Notation Conventions

Diagrams are **derived visual views** governed by their authoritative prose/YAML/contract source documents. A diagram MUST NEVER invent undocumented components, endpoints, tables, security controls, or requirements.

## 1. Risk-Based Applicability (No Blanket Diagram Mandate)

Authors MUST NOT generate every diagram type for every feature. Diagram selection MUST follow the scope and risk rules in [artifact-applicability-matrix.yaml](../catalog/artifact-applicability-matrix.yaml):

| Diagram Type | Standard Notation | Permitted Mermaid Header / Format | When Required / Applicable | Typical Placement |
|---|---|---|---|---|
| **System Context** | C4 Level 1 | `flowchart TB` / `C4Context` | Platform overview and external system integrations | `overview/diagrams/` |
| **C4 Container** | C4 Level 2 | `flowchart TB` / `C4Container` | Plane runtime processes, stores, and protocol boundaries | `<plane>/architecture/` |
| **C4 Component** | C4 Level 3 | `flowchart TB` / `C4Component` | Complex capabilities with >=3 internal modules or strict DAG layers | `<capability>/design/` |
| **Deployment** | C4 Deployment / Topology | `flowchart TB` | Capabilities adding containers, network zones, ports, or infra tiers | `<plane>/operations/` or `<capability>/operations/` |
| **BPMN Swimlane** | BPMN 2.0.2 | `flowchart TB` (actor subgraphs) or BPMN 2.0 XML | Multi-actor workflows with handoffs, gateways, or SLA boundaries | `<capability>/workflows/` |
| **UML Use Case** | UML 2.5.1 | `flowchart LR` | Capabilities with multiple human/system actor roles & boundary scopes | `<capability>/use-cases/` |
| **UML Sequence** | UML 2.5.1 | `sequenceDiagram` | Multi-step sync/async runtime calls, retries, fallbacks, or auth flows | `<capability>/design/` or `workflows/` |
| **UML State Machine** | UML 2.5.1 | `stateDiagram-v2` | Entities/jobs/runs with >=3 stateful transitions or failure states | `<capability>/design/` |
| **Component Diagram** | UML / Module Graph | `flowchart TB` | Static module/package dependency boundaries & ports/adapters | `<capability>/design/` |
| **ERD** | Crow's Foot / ERD | `erDiagram` | Capabilities owning relational or analytical tables (`MEDIUM`/`HIGH` risk) | `<capability>/data/` |
| **Data Flow Diagram (DFD)** | Pipeline / Lineage Flow | `flowchart LR` / `flowchart TD` | Data Plane ingestion, streaming, medallion stages, and sink branching | `<plane>/architecture/` or `<capability>/data/` |
| **Threat Model Diagram** | Trust Boundary / DFD | `flowchart TB` | `HIGH`/`CRITICAL` risk, auth/authz, external exposure, or write-capable tools | `<capability>/security/` |
| **Agent Workflow Diagram** | State / Execution Graph | `flowchart TD` / `stateDiagram-v2` | Intelligence Plane orchestrator nodes, tool gateway guards, and loop limits | `intelligence-plane/...` |

## 2. Mandatory Diagram Metadata & Wrapper Rules

Every diagram file MUST contain YAML frontmatter plus a Diagram Metadata table specifying:

1. **Title & Purpose**: Concise human-readable title and one-sentence analytical purpose.
2. **Diagram ID**: Unique `DIAG-<SCOPE>-NNN` matching `^[A-Z][A-Z0-9-]*[A-Z0-9]$`.
3. **Owner & Scope**: `owner_role` and `scope_level` (`platform | plane | domain | capability`).
4. **Authoritative Source Document (`source_of_truth.authoritative_source`)**: Exact file path(s) and `doc_id` from which the diagram is derived.
5. **Notation**: Exact notation (`Mermaid flowchart`, `Mermaid sequenceDiagram`, `Mermaid stateDiagram-v2`, `Mermaid erDiagram`, or `BPMN 2.0.2 XML`).
6. **Legend**: Explicit legend defining node shapes, line styles (sync vs. async, `AS-IS` vs. `TARGET`), and trust boundary boxes whenever mixed states or edge types appear.
7. **Version & Status**: Must match frontmatter `version` and `status` (`DRAFT | IN_REVIEW | APPROVED | DEPRECATED`).

## 3. Naming, Direction & Mermaid Syntax Validation Rules

1. **Direction**: Data flows SHOULD use `LR` (left-to-right) or `TD`/`TB` (top-to-bottom); system context/C4/deployment diagrams SHOULD use `TB`.
2. **Relationship Labels**: Every edge MUST label the protocol, event, or action (e.g., `-->|"HTTPS REST /v1"|`, `-.->|"Async Kafka market.raw.*.v1"|`). Unlabeled arrows MUST NOT be used outside structural grouping.
3. **Mermaid Quoting**: Node labels containing parentheses `()`, brackets `[]`, colons `:`, or slash characters MUST be double-quoted (e.g., `node_id["Service Name (Port 8000)"]`) to guarantee deterministic rendering.
4. **Validation**: Automated validation checks fenced Mermaid syntax headers, metadata completeness, valid `source_of_truth`, and optional rendering via `mmdc` when installed. Templates with examples live under `docs/governance/templates/diagrams/`.
