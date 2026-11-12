# Discovery & Reference Architecture Audit — DOCS-001

| Metadata | Value |
|---|---|
| **Work Item ID** | `DOCS-001` |
| **Authoring Role** | `discovery-analyst` & `documentation-architect` |
| **Status** | `COMPLETED` |
| **Created Date** | `2026-11-12` |
| **Updated Date** | `2026-11-12` |

---

## 1. Sources Inspected

### 1.1. Reference Repository (`https://github.com/DungTran1201/AgentHarnessBuilderTools/tree/main`)
- **Root & Agent OS**: `AGENTS.md`, `.agents/README.md`, `.agents/agents/*`, `.agents/rules/*`, `.agents/skills/*`, `.agents/config/{document-map.yaml,artifact-matrix.yaml,change-types.yaml,phase-gates.yaml}`, `.agents/catalog/*`, `.agents/hooks.json`, `.agents/skill-registry.yaml`, `.agents/skills_manifest.json`.
- **15-Phase Documentation Lifecycle**: `docs/README.md`, `docs/00-discovery/` through `docs/14-governance/`, and nested folders (`docs/03-business-process/diagrams/`, `docs/04-use-cases/diagrams/`, `docs/04-use-cases/specifications/`).
- **Feature Package Pattern**: `docs/features/project-management/` (`00-scope-assumptions-decisions.md` through `10-implementation-readiness.md` + `README.md`).
- **Canonical Models**: `models/README.md` and `models/{requirements,process,context,architecture,domain,api,interaction,state,security,ux,testing,deployment}/`.
- **Diagrams**: `diagrams/{bpmn,component,context,deployment,sequence,state,swimlane}/`.
- **Work Items**: `work-items/README.md`, `work-items/_template/{request.md,discovery.md,impact-analysis.md,artifact-plan.yaml,implementation-plan.md,verification-plan.md,review.md,state.yaml}`.
- **Validation & Hooks**: `tools/validators/{run_all.py,validate_docs.py,validate_models.py,validate_traceability.py,validate_artifact_matrix.py,validate_hooks.py,validate_skill_registry.py}` and `tools/hooks/{pre_command_guard.py,sensitive_file_guard.py,post_doc_write_check.py,post_model_write_check.py,stop_readiness_check.py}`.

### 1.2. Target Repository (`FinancialMarketDataPlatform`)
- **Existing Architecture Docs**: `docs/architecture/00-architecture-overview.md` through `13-performance-and-scalability.md` and `docs/architecture/adr/ADR-001` through `ADR-006`.
- **Existing Specifications**: `docs/specifications/{data-requirements.md,data-dictionary.md,data-contracts.md,api-specification.md,non-functional-requirements.md}`.
- **Existing Diagrams**: `docs/diagrams/{system,data-platform,backend,agent,deployment,security}/` (`01` through `16`).
- **Existing Code & Tests**: `src/`, `tests/`, `deploy/`, `docker-compose.yml`, `pyproject.toml`, `.env.example`.

---

## 2. Verified Facts (`FACT`)

- **FACT-01 (Reference Pattern — Phase READMEs)**: In `AgentHarnessBuilderTools`, each phase directory (`00-discovery` .. `14-governance`) uses its `README.md` as an operational contract defining purpose, source-of-truth precedence, required inputs/outputs, and quality gates.
- **FACT-02 (Reference Pattern — Feature Packages)**: Feature documentation in `docs/features/<feature-slug>/` is structured into a self-contained 11-document package (`00` Scope/Assumptions $\rightarrow$ `01` Feature Inventory $\rightarrow$ `02` SRS $\rightarrow$ `03` Domain/Use Cases $\rightarrow$ `04` Architecture/API $\rightarrow$ `05` State $\rightarrow$ `06` UX $\rightarrow$ `07` Security $\rightarrow$ `08` Testing $\rightarrow$ `09` API Examples $\rightarrow$ `10` Implementation Readiness).
- **FACT-03 (Reference Pattern — Canonical Models)**: `models/` holds machine-readable YAML files (`*.yaml`) and reusable templates (`*.template.yaml`) that serve as structured sources for `docs/` and `diagrams/`.
- **FACT-04 (Target Repo Constraints)**: `FinancialMarketDataPlatform` already uses `docs/diagrams/` as its diagram root (containing 16 diagrams across 6 subdirectories) and `docs/architecture/` + `docs/specifications/` for its Data Platform, Backend, and Intelligence Plane foundation.
- **FACT-05 (Reference Contamination Exclusions)**: `AgentHarnessBuilderTools` contains AI-Chan product-specific elements (`.agents/rules/ponytail.md`, VRM avatar state models, Discord OAuth/bot workflows, `ai-backend/` local companion code) that are specific to that application and **must not** be copied into `FinancialMarketDataPlatform`.

---

## 3. Explicit Assumptions (`ASSUMPTION — REQUIRES VALIDATION`)

- **ASSUMP-01**: Future Website/Product engineering artifacts will reside under `docs/product/00-discovery/` through `docs/product/14-governance/` and `docs/features/<feature-slug>/`, while shared platform-wide architecture remains in `docs/architecture/` and `docs/specifications/`.

---

## 4. Architectural Decisions (`DECISION`)

- **DEC-01 (Single Diagram Root)**: Preserve `docs/diagrams/` as the single diagram root in the repository rather than creating a competing top-level `/diagrams/` directory, and extend `docs/diagrams/` with the missing lifecycle diagram categories (`context`, `architecture`, `component`, `process`, `process/bpmn`, `process/swimlane`, `use-case`, `sequence`, `state`, `domain`, `api`, `ux`) alongside existing (`system`, `data-platform`, `backend`, `agent`, `deployment`, `security`).
- **DEC-02 (Namespace Disambiguation)**: Preserve all existing Data Platform IDs (`FR-01..10`, `ADR-001..006`) and allocate explicit prefixes (`WEB-FR-###`, `DP-FR-###`, `DIAG-CTX-###`, etc.) in `.agents/config/identifier-registry.yaml`.

---

## 5. Open Questions (`OPEN QUESTION`)

- **OQ-01**: When Website Product Discovery begins in a subsequent task, which target user personas (Retail Trader, Institutional Quant, Internal Data Operator) will be prioritized for Phase 1 Website MVP? *(Deferred to future `FEAT` work item; out of scope for `DOCS-001` framework initialization).*

