# Discovery & Fact Classification Register (`DOCS-002`)

| Metadata | Value |
|---|---|
| **Work Item ID** | `DOCS-002` |
| **Stage** | `DISCOVERY` |
| **Audit Scope** | Entire repository (`docs/`, `models/`, `src/`, `frontend/`, `deploy/`, `tests/`) |
| **Updated Date** | `2026-11-15` |
| **Owning Agent Role** | `discovery-analyst` & `documentation-architect` |

---

## 1. Fact Classification Register

In accordance with Section 4 of `AGENTS.md` and Rule `RULE-001`, all discovery findings are strictly classified into `FACT`, `ASSUMPTION`, `DECISION`, and `OPEN QUESTION`.

### 1.1. Verified Facts (`FACT`)

- `FACT-001`: **Documentation Inventory**: `docs/` contains 186 Markdown files across 6 top-level directories: `architecture/` (25 files), `diagrams/` (53 files), `product/` (28 files), `specifications/` (6 files), `templates/` (72 files), and `features/` (1 file), plus root `docs/README.md`.
- `FACT-002`: **Canonical Models**: `models/` contains 38 YAML files across 12 domain directories (`api/`, `architecture/`, `context/`, `data-platform/`, `deployment/`, `domain/`, `interaction/`, `process/`, `requirements/`, `security/`, `state/`, `testing/`, `ux/`).
- `FACT-003`: **Preserved Baseline Files**: `tools/validators/validate_docs.py` enforces the mandatory existence and non-zero size of 25 baseline files (`docs/architecture/00..13`, `docs/architecture/adr/ADR-001..006`, and `docs/specifications/data-requirements.md..non-functional-requirements.md`).
- `FACT-004`: **Managed Directories Contract**: `tools/validators/validate_readmes.py` strictly requires every managed directory in `.agents/`, `docs/`, `models/`, `work-items/`, and `tools/` to contain a `README.md` with a top-level H1 title and all 12 mandatory sections.
- `FACT-005`: **Mermaid Diagram Validation**: `tools/validators/validate_diagrams.py` requires every `.md` file in `docs/diagrams/` (except `README.md`) to contain a valid ` ```mermaid ` code block matching approved Mermaid diagram types.
- `FACT-006`: **Implemented Codebase Reality**:
  - `src/` contains 6 architectural bounded directories: `ingestion/`, `streaming/`, `lakehouse/`, `serving/`, `intelligence/`, and `shared/`.
  - `frontend/` contains a fully functional TypeScript/Vite application with 6 modules (`dashboard`, `market-analytics`, `data-flow`, `data-management`, `ai-workspace`, `administration`).
  - `deploy/` contains Docker Compose configs supporting `--profile core` (single process) and `--profile microservices` (8 isolated services on ports 8000..8007).
  - `tests/` contains 50 automated tests covering unit, contract, integration, data quality, e2e, resilience, and performance.
- `FACT-007`: **Link Audit & Inconsistency Detection**:
  - A full-repository link graph scan discovered 4 broken links:
    1. `docs/architecture/adr/ADR-007-microservices-and-data-platform-v01.md`: Linked to nonexistent `ADR-001-modular-monolith-and-three-plane-separation.md` (correct target: `ADR-001-overall-architecture.md`).
    2. `docs/architecture/adr/ADR-007-microservices-and-data-platform-v01.md`: Linked to nonexistent `ADR-002-streaming-backbone-and-polyglot-storage.md` (correct target: `ADR-002-event-driven-data-platform.md`).
    3. `docs/architecture/adr/ADR-007-microservices-and-data-platform-v01.md`: Linked to nonexistent `ADR-005-idempotency-deduplication-and-event-ordering.md` (correct target: `ADR-005-query-and-caching-strategy.md`).
    4. `docs/product/11-ux/screen-specifications.md`: Linked to deleted `src/serving/api/gateway/ui.py` (superseded by `frontend/src/modules/data-flow/DataFlowModule.ts`).

### 1.2. Recorded Decisions (`DECISION`)

- `DECISION-001`: Adopt a **Domain & Reader-Journey Centric Target Architecture** (`docs/overview/`, `docs/contracts/`, `docs/operations/`, `docs/development/`, `docs/archive/`) alongside preserved baseline architecture and specifications.
- `DECISION-002`: Resolve all 4 detected broken links in-place to achieve 100% link integrity across all 367 internal links.
- `DECISION-003`: Retain all 25 baseline files and 22 production diagrams at their canonical locations, enriching them with cross-references and domain index portals rather than destructive moving.
- `DECISION-004`: Ensure all newly created domain directories contain complete, compliant 12-section `README.md` files satisfying `validate_readmes.py`.

### 1.3. Working Assumptions (`ASSUMPTION`)

- `ASSUMPTION-001`: Developers prefer starting from a 5-minute Quickstart (`docs/development/developer-quickstart.md`) and high-level System Overview (`docs/overview/system-overview.md`) rather than directly parsing `docs/architecture/00-architecture-overview.md`.
- `ASSUMPTION-002`: SRE/DevOps teams need operational runbooks and disaster recovery plans consolidated in `docs/operations/` rather than dispersed across `docs/product/13-operations/` and `deploy/README.md`.

### 1.4. Open Questions (`OPEN QUESTION`)

- `OPEN QUESTION-001`: Should `docs/product/00` through `docs/product/10` be populated with full specification files in future feature cycles, or maintained as phase-gate audit markers? *(Recommendation: Maintain as phase-gate markers linking to canonical specifications in `docs/specifications/` and `models/` to avoid double-entry maintenance).*

