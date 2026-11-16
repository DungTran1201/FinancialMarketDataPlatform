---
doc_id: OVR-DIAG-3P-001
title: "Diagram: Three-Plane Ownership & Allowed Dependencies"
doc_type: diagram
plane: platform
scope_level: platform
status: IN_REVIEW
implementation_status: IMPLEMENTED
version: "2.0.0"
owner_role: system-architect
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/overview/three-plane-architecture.md"
related_docs:
  - OVR-ARCH-3P-001
  - ADR-OVR-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: system-architect
    summary: "Derived Three-Plane dependency diagram reflecting AST-verified import DAG."
---

# Diagram: Three-Plane Ownership & Allowed Dependencies

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-OVR-3P-001` |
| **Title & Purpose** | Shows package ownership and AST-enforced dependency rules across Shared Kernel and Three Planes |
| **Owner Role & Scope** | `system-architect / platform` |
| **Authoritative Source** | [three-plane-architecture.md](../three-plane-architecture.md) (`OVR-ARCH-3P-001`) |
| **Notation** | `Mermaid flowchart TB` |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram `[REQUIRED]`

```mermaid
flowchart TB
    shared["Shared Kernel (src/shared/ — Primitives, Contracts, Quant, Crypto, Metrics, Tracing)"]

    subgraph plane_a["Data Plane (src/ingestion, src/streaming, src/lakehouse)"]
        dp_ing["Ingestion & Watermarks"]
        dp_str["Event Streaming, Hot Dicts & OLAP"]
        dp_lak["Medallion Parquet, DQ & Lineage"]
        dp_ing -->|"EventEnvelopeV1"| dp_str
        dp_str -->|"Batches"| dp_lak
    end

    subgraph plane_c["Intelligence Plane (src/intelligence)"]
        int_orch["5-Node Graph Orchestrator"]
        int_gw["ControlledToolGateway (10 Tools)"]
        int_val["ReportValidator"]
        int_orch -->|"Validated Call"| int_gw
        int_orch -->|"Citation Check"| int_val
    end

    subgraph plane_b["Application Plane (src/serving, frontend)"]
        app_spa["Frontend SPA (6 Screens)"]
        app_api["FastAPI Routers & Middleware"]
        app_rt["PlatformRuntimeContainer (Composition Root)"]
        app_spa -->|"HTTPS REST / SSE"| app_api
        app_api -->|"Dispatches"| app_rt
    end

    dp_ing -->|"Imports"| shared
    dp_str -->|"Imports"| shared
    dp_lak -->|"Imports"| shared
    app_api -->|"Imports"| shared
    int_gw -->|"Imports"| shared
    app_rt -->|"Invokes Pipelines & Reads"| dp_str
    app_rt -->|"Triggers Investigation"| int_orch
    int_gw -->|"Injected Read Handlers"| dp_str
```

## 3. Legend `[REQUIRED]`

- **Subgraphs**: Logical ownership Planes matching `docs/docs-index.yaml` and `tests/architecture/test_clean_architecture_boundaries.py`.
- **Prohibited Edges (Enforced by AST)**: Neither Data Plane nor Intelligence Plane imports `src/serving/`; `*/domain/*.py` never imports web or DB drivers.
