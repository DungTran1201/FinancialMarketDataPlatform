---
doc_id: DIAG-INT-DEP-001
title: "Intelligence Plane Dependency & Clean Architecture AST Boundary Diagram"
doc_type: diagram
plane: intelligence-plane
scope_level: plane
status: DRAFT
implementation_status: VERIFIED
version: "2.0.0"
owner_role: ai-engineer
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/intelligence-plane/architecture/intelligence-architecture.md"
    - "tests/architecture/test_clean_architecture_boundaries.py"
related_docs:
  - INT-ARCH-ROOT-001
  - INT-ARCH-001
  - OVR-ARCH-3P-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Rendered AST-enforced Clean Architecture import boundaries around src/intelligence/."
---

# Intelligence Plane Dependency & Clean Architecture AST Boundary Diagram

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-INT-DEP-001` |
| **Title & Purpose** | Directed Acyclic Import Graph and AST Isolation Rules for `src/intelligence/` |
| **Owner Role & Scope** | `ai-engineer / intelligence-plane` |
| **Authoritative Source** | [intelligence-architecture.md](../intelligence-architecture.md) (`INT-ARCH-001`) |
| **Notation** | `Mermaid flowchart TB` (`Component Dependency Graph`) |
| **Version & Status** | `2.0.0 — DRAFT` |

## 2. Diagram

```mermaid
flowchart TB
    shared["src/shared/ (Config, Quant Math, Primitives)"]
    composition["src/serving/infrastructure/runtime.py (Composition Root)"]

    subgraph intelligence_pkg["src/intelligence/ (Isolated Plane C)"]
        main_ep["main.py (Worker Entrypoint)"]
        orch["orchestrator/graph.py"]
        wf["workflows/investigation.py"]
        rep["reporting/validator.py"]
        gw["tools/gateway.py"]
        ctr["tools/contracts.py"]
    end

    serving_api["src/serving/api/ (Routers & Services)"]
    data_plane["src/ingestion/, src/streaming/, src/lakehouse/"]

    main_ep -->|"Imports PlatformConfig"| shared
    orch -->|"Imports workflows, tools, reporting"| wf
    orch --> rep
    orch --> gw
    orch --> ctr
    wf --> ctr
    gw --> ctr

    composition -->|"Wires 10 Closures & Instantiates Graph"| orch
    composition -->|"Injects Handlers"| gw
    composition -->|"Wires Data Plane Engines"| data_plane

    intelligence_pkg -.->|"FORBIDDEN BY AST TEST (TC-006)"| serving_api
    intelligence_pkg -.->|"FORBIDDEN BY AST TEST (TC-006)"| data_plane
    serving_api -.->|"FORBIDDEN BY AST TEST (TC-006)"| intelligence_pkg
```

## 3. Legend

- **Solid Arrows (`-->`)**: Permitted Python `import` dependencies verified by `tests/architecture/test_clean_architecture_boundaries.py`.
- **Dashed Arrows (`-.->`)**: Strictly prohibited cross-plane imports enforced by AST static checks (`TC-006`).

