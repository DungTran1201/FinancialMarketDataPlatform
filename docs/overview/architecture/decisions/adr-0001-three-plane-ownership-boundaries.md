---
doc_id: ADR-OVR-001
title: "ADR-OVR-001: Three-Plane Ownership & Acyclic Module Boundaries"
doc_type: adr
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
  is_authoritative: true
  authoritative_source:
    - "tests/architecture/test_clean_architecture_boundaries.py"
    - "src/serving/infrastructure/runtime.py"
related_docs:
  - OVR-ADR-ROOT-001
  - OVR-ARCH-3P-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: system-architect
    summary: "Documented MADR 4.0 record for FMDP three-plane ownership model backed by AST tests."
---

# ADR-OVR-001: Three-Plane Ownership & Acyclic Module Boundaries

## 1. Context and Problem Statement `[REQUIRED]`

Market data acquisition, stateful streaming/lakehouse pipelines, HTTP/SPA user serving, and AI investigation agents have distinct scaling characteristics, security risk profiles, and engineering owners. Coupling domain rules directly to web frameworks, storage drivers, or LLM adapters creates circular dependencies and untestable spaghetti modules.

## 2. Decision Drivers

- Enforce Clean Architecture domain purity (`*/domain/*.py`).
- Allow independent testing of ingestion, streaming, lakehouse, serving APIs, and AI tools.
- Maintain explicit ownership boundaries across `Data`, `Application`, and `Intelligence` Planes.

## 3. Considered Options `[REQUIRED]`

1. **Flat Layered Backend**: Single package hierarchy mixing FastAPI routers, Kafka/Parquet logic, and LangGraph calls.
2. **Three-Plane Modular Packages with Shared Kernel & Composition Roots**: Isolate `src/shared/`, Data (`src/ingestion`, `src/streaming`, `src/lakehouse`), Application (`src/serving`, `frontend`), and Intelligence (`src/intelligence`) connected via clean ports and composition roots (`PlatformRuntimeContainer`, `DataPlatformV01Pipeline`).

## 4. Decision Outcome `[REQUIRED]`

Adopt **Option 2 (Three-Plane Ownership Model with AST Boundary Enforcement)**:

- `src/shared/` holds only framework-agnostic contracts, primitives, quant math, crypto/WAF utilities, metrics, and tracing.
- `test_clean_architecture_boundaries.py` enforces zero forbidden driver/framework imports in `domain/` modules and acyclic package imports via Python AST inspection.
- Cross-plane runtime wiring is centralized strictly inside explicit composition roots (`runtime.py`, `pipeline.py`).

## 5. Consequences `[REQUIRED]`

- **Positive**: All 3 AST boundary tests pass; individual engines test cleanly in isolation without containers or mocks of internal domain logic.
- **Negative / Risk**: Because `PlatformRuntimeContainer` composes all three Planes in one Python process by default, teams MUST avoid conflating logical Plane boundaries with separate OS process boundaries unless target workers are wired (`ADR-OVR-002`).
