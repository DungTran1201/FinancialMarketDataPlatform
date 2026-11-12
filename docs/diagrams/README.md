# Unified Technical Diagram Engineering Subsystem (`docs/diagrams/`)

## 1. Directory Purpose

`docs/diagrams/` is the single unified diagram root for `FinancialMarketDataPlatform`. It preserves the 16 baselined Phase 0 platform diagrams (`01`..`16`) and provides dedicated, governed subdirectories for all 18 lifecycle diagram categories (`DIAG-CTX-###`, `DIAG-C4-###`, `DIAG-DATA-###`, `DIAG-BPMN-###`, `DIAG-SWIM-###`, `DIAG-UC-###`, `DIAG-SEQ-###`, `DIAG-STATE-###`, `DIAG-DOM-###`, `DIAG-ERD-###`, `DIAG-API-###`, `DIAG-DEP-###`, `DIAG-SEC-###`, `DIAG-UX-###`).

## 2. Scope and Boundaries

- **Belongs in this directory**: All Mermaid technical diagrams (`*.md`) organized by diagram category and their operational `README.md` contracts.
- **Does NOT belong in this directory**: Standalone specifications without upstream models (`docs/`), or canonical YAML files (`models/`).

## 3. Agent Role and Responsibilities

Authored by `architecture-modeler`, `process-modeler`, `domain-modeler`, `api-architect`, `ux-modeler`, and `security-reviewer`; validated by `documentation-auditor`.

## 4. Authoritative Inputs

1. `models/` — Canonical YAML models (authoritative structured source).
2. `docs/architecture/`, `docs/specifications/`, and `docs/product/` — Authoritative prose specifications.
3. `.agents/rules/diagrams.md` — Diagram governance and derived-view rules.
4. `.agents/config/identifier-registry.yaml` — `DIAG-*` ID conventions.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `system/` | System Context, C4 Container & C4 Component Diagrams (Existing Baseline) (`DIAG-CTX / DIAG-C4`) | Required | `docs/diagrams/system/README.md` |
| `data-platform/` | Data Platform, Ingestion, Event Streaming & Medallion Flow Diagrams (Existing Baseline) (`DIAG-DATA`) | Required | `docs/diagrams/data-platform/README.md` |
| `backend/` | Backend Modular Monolith, Request Lifecycle, CQRS & Cache Diagrams (Existing Baseline) (`DIAG-C4 / DIAG-SEQ`) | Required | `docs/diagrams/backend/README.md` |
| `agent/` | Agentic Intelligence, LangGraph Sequence & Tool Gateway Access Diagrams (Existing Baseline) (`DIAG-C4 / DIAG-SEQ / DIAG-SEC`) | Required | `docs/diagrams/agent/README.md` |
| `deployment/` | Deployment Topology & Docker Compose Profile Diagrams (`DIAG-DEP`) | Required | `docs/diagrams/deployment/README.md` |
| `security/` | Security & Trust Boundary Diagrams (`DIAG-SEC`) | Required | `docs/diagrams/security/README.md` |
| `context/` | Product & System Context Diagrams (`DIAG-CTX`) | Required | `docs/diagrams/context/README.md` |
| `architecture/` | Product & Subsystem Architecture Views (`DIAG-C4`) | Required | `docs/diagrams/architecture/README.md` |
| `component/` | Internal Component & Hexagonal Boundary Diagrams (`DIAG-C4`) | Required | `docs/diagrams/component/README.md` |
| `process/` | Business & Operational Process Diagrams (Parent Index) (`DIAG-BPMN / DIAG-SWIM`) | Required | `docs/diagrams/process/README.md` |
| `process/bpmn/` | BPMN Business Process Flow Diagrams (`DIAG-BPMN`) | Required | `docs/diagrams/process/bpmn/README.md` |
| `process/swimlane/` | Cross-Functional Actor Swimlane Diagrams (`DIAG-SWIM`) | Required | `docs/diagrams/process/swimlane/README.md` |
| `use-case/` | UML Use Case Scope & Actor Packaging Diagrams (`DIAG-UC`) | Required | `docs/diagrams/use-case/README.md` |
| `sequence/` | Runtime Sequence & Interaction Diagrams (`DIAG-SEQ`) | Required | `docs/diagrams/sequence/README.md` |
| `state/` | Lifecycle State Machine Diagrams (`stateDiagram-v2`) (`DIAG-STATE`) | Required | `docs/diagrams/state/README.md` |
| `domain/` | DDD Bounded Context, Class & Entity-Relationship Diagrams (`DIAG-DOM / DIAG-ERD`) | Required | `docs/diagrams/domain/README.md` |
| `api/` | REST, WebSocket & SSE API Topology & Contract Diagrams (`DIAG-API`) | Required | `docs/diagrams/api/README.md` |
| `ux/` | UX Information Architecture, Site Map & User Flow Diagrams (`DIAG-UX`) | Required | `docs/diagrams/ux/README.md` |

## 6. Directory and File Organization

18 category directories under `docs/diagrams/` (including `process/bpmn/` and `process/swimlane/`), preserving all 16 existing diagrams.

## 7. Document Creation Rules

1. **Derived View Rule**: A diagram is a derived view of `models/` and `docs/` — never a standalone source of truth.
2. **Metadata Requirement**: Every new diagram file must include `Diagram ID` (`DIAG-<TYPE>-<NNN>`), `Title`, `Diagram Type`, `Authoritative Source Document`, `Canonical Model Reference`, `Related Artifact IDs`, `Status`, and `Version`.
3. **Mermaid Syntax Standards**: Quote node labels containing parentheses or special characters (`id["Label (Detail)"]`); only use supported Mermaid diagram types (`flowchart`, `sequenceDiagram`, `stateDiagram-v2`, `classDiagram`, `erDiagram`).

## 8. Creation Workflow

1. Read `docs/diagrams/README.md` and the target category `docs/diagrams/<category>/README.md`.
2. Inspect the authoritative canonical model in `models/` and specification in `docs/`.
3. Assign a unique `DIAG-<TYPE>-<NNN>` identifier conforming to `.agents/config/identifier-registry.yaml`.
4. Create or update the diagram markdown file with architectural explanation and valid Mermaid code block.
5. Run `tools/validators/validate_diagrams.py` and `tools/validators/validate_traceability.py`.

## 9. Relationships and Dependencies

Visualizes canonical models in `models/` and is embedded/linked from `docs/architecture/`, `docs/product/`, and `docs/features/`.

## 10. Quality Gate

All diagram directories have a 12-section `README.md`, all 16 existing diagrams are preserved, and all Mermaid blocks pass `validate_diagrams.py`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT create a second top-level `/diagrams/` root outside `docs/diagrams/`.
- Do NOT introduce undocumented components, endpoints, or state transitions inside a diagram that do not exist in `models/` and `docs/`.
- Do NOT delete or overwrite the 16 existing Phase 0 platform diagrams.
