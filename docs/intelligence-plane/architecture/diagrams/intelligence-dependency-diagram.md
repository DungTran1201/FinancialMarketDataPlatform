---
doc_id: DIAG-INT-DEP-001
title: "Intelligence Plane Dependency Diagram"
doc_type: diagram
plane: intelligence-plane
scope_level: plane
status: DRAFT
implementation_status: IMPLEMENTED
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
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Created Intelligence Plane module dependency DAG enforced by AST boundary tests."
---

# Intelligence Plane Dependency Diagram

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-INT-DEP-001` |
| **Purpose** | Show allowed and forbidden Python import dependencies inside `src/intelligence/` and across subsystems. |
| **Scope & Owner** | `plane` (`intelligence-plane`) / `ai-engineer` |
| **Authoritative Source** | [intelligence-architecture.md](../intelligence-architecture.md) (`INT-ARCH-001`) |
| **Notation** | Mermaid `flowchart TB` (Module Dependency Graph) |
| **Version & Status** | `2.0.0` / `DRAFT` (`IMPLEMENTED`) |

```mermaid
flowchart TB
    subgraph INT_PKG["src/intelligence/"]
        MAIN["main.py (agent-worker)"]
        ORCH["orchestrator/graph.py"]
        WF["workflows/investigation.py"]
        REP["reporting/validator.py"]
        GW["tools/gateway.py"]
        CTR["tools/contracts.py"]
    end

    SHARED["src/shared/ (PlatformConfig)"]
    SERVING["src/serving/infrastructure/runtime.py (Composition Root)"]
    DATA_PKG["src/ingestion, src/streaming, src/lakehouse"]

    MAIN -->|"imports config"| SHARED
    ORCH -->|"imports state"| WF
    ORCH -->|"imports validator"| REP
    ORCH -->|"imports gateway"| GW
    ORCH -->|"imports tool enum"| CTR
    WF -->|"imports envelope"| CTR
    GW -->|"imports policies"| CTR
    SERVING -->|"wires handlers & graph"| ORCH
    SERVING -->|"registers 10 handlers"| GW
    ORCH -.->|"FORBIDDEN by AST test"| DATA_PKG
    ORCH -.->|"FORBIDDEN by AST test"| SERVING
```

**Legend**: Solid arrows (`-->`) denote permitted Python imports verified by `test_clean_architecture_boundaries.py`; dashed arrows (`-.->`) denote prohibited dependencies.

