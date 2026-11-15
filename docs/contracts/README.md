# System Contracts & Specifications Domain (`docs/contracts/`)

## 1. Directory Purpose

`docs/contracts/` serves as the centralized interface portal for all technical, functional, and behavioral contracts of the **FinancialMarketDataPlatform**. It provides a single point of reference for Functional Requirements (`FR-*`), Business Rules (`BR-*`), Acceptance Criteria (`AC-*`), REST API contracts (`API-*`), WebSocket/SSE streams, and Kafka event schemas.

## 2. Scope and Boundaries

- **Belongs in `docs/contracts/`**:
  - Synthesized traceability matrices linking requirements to architecture, code, and test cases.
  - API endpoint catalogs, payload envelopes, and WebSocket streaming protocols.
  - Event schemas, topic definitions, and partition keys.
  - Financial data quality rules and invariant specifications.
- **Does NOT belong in `docs/contracts/`**:
  - The raw canonical YAML models (which live in `models/requirements/`, `models/api/`, `models/data-platform/`).
  - Implementation code or mock clients (which live in `src/` and `tests/`).
  - Work item change intake logs (which live in `work-items/`).

## 3. Agent Role and Responsibilities

- **Primary Owning Role**: `documentation-architect` and `requirements-engineer`.
- **Collaborating Roles**: `api-architect`, `streaming-data-engineer`.
- **Responsibilities**:
  - Maintain 100% bidirectional traceability between canonical models in `models/` and prose contracts.
  - Ensure zero collision and strict adherence to `.agents/config/identifier-registry.yaml`.

## 4. Authoritative Inputs

1. [models/requirements/requirements.yaml](../../models/requirements/requirements.yaml) — Canonical Functional & Non-Functional Requirements.
2. [models/requirements/business-rules.yaml](../../models/requirements/business-rules.yaml) — Canonical Business Rules.
3. [models/requirements/acceptance-criteria.yaml](../../models/requirements/acceptance-criteria.yaml) — Canonical Acceptance Criteria.
4. [models/api/api.yaml](../../models/api/api.yaml) — Canonical API Schema & Endpoints.
5. [models/data-platform/topics.yaml](../../models/data-platform/topics.yaml) — Canonical Kafka Topics.
6. [docs/specifications/api-specification.md](../specifications/api-specification.md) — Preserved Baseline API Spec.
7. [docs/specifications/data-contracts.md](../specifications/data-contracts.md) — Preserved Baseline Data Contracts.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `README.md` | Domain boundaries, inputs, and navigation index | Required | `docs/templates/api/api-specification.template.md` |
| `requirements-matrix.md` | Consolidated requirements, business rules, and acceptance criteria | Required | `docs/templates/requirements/srs.template.md` |
| `api-contracts.md` | Unified REST, WebSocket, and SSE streaming specifications | Required | `docs/templates/api/api-specification.template.md` |

## 6. Directory and File Organization

```text
docs/contracts/
├── README.md               # Domain overview & 12-section contract
├── requirements-matrix.md  # Requirements, BR, and AC matrix
└── api-contracts.md        # API, WebSocket, and Kafka contracts
```

## 7. Document Creation Rules

- Never renumber existing identifiers (`FR-01..10`, `BR-001..003`, `AC-01..04`, `API-001..020`).
- Always cite the upstream canonical YAML model in `models/`.

## 8. Creation Workflow

1. Inspect authoritative YAML models in `models/requirements/` and `models/api/`.
2. Generate human-readable markdown specifications referencing exact models.
3. Verify traceability and run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

- **Upstream**: Derived directly from `models/` and `docs/specifications/`.
- **Downstream**: Consulted by frontend developers, backend engineers, and test suites in `tests/contract/`.

## 10. Quality Gate

- All listed identifiers match patterns registered in `identifier-registry.yaml`.
- 100% bidirectional traceability verified by `tools/validators/validate_traceability.py`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_traceability.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- **Do NOT** redefine canonical models in this directory; `models/` is the authoritative source.
- **Do NOT** introduce new unverified requirements without a formal work item.
