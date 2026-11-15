# Work Item Directory (`work-items/FEAT-002-frontend-experience-layer/`)

## 1. Directory Purpose

Tracks the design, implementation, governance synchronization, and verification of **FEAT-002**: the independent **Frontend Experience Layer** (`frontend/`) in TypeScript, HTML5, CSS3, connecting to Application Plane (Plane B) via REST API, WebSocket, and SSE.

## 2. Scope and Boundaries

- **Belongs in this directory**: Lifecycle artifacts for `FEAT-002` following `work-items/_template/` (`README.md`, `request.md`, `discovery.md`, `impact-analysis.md`, `artifact-plan.yaml`, `implementation-plan.md`, `verification-plan.md`, `review.md`, `state.yaml`).
- **Does NOT belong here**: Production TypeScript frontend code (`frontend/`), Backend Python code (`src/`), canonical YAML models (`models/`), or permanent human-readable engineering specs (`docs/`).

## 3. Agent Role and Responsibilities

- **Primary Authors**: `architecture-modeler`, `ux-modeler`, `documentation-architect`.
- **Auditors**: `qa-reviewer`, `security-reviewer`, `documentation-auditor`.

## 4. Authoritative Inputs

1. [work-items/README.md](../README.md) — Work-item lifecycle contract.
2. [AGENTS.md](../../AGENTS.md) — Root documentation engineering contract & 12-Step Execution Protocol.
3. [.agents/rules/data-platform-observability.md](../../.agents/rules/data-platform-observability.md) — Latency, cardinality & truth rules.
4. [.agents/rules/data-truth-classification.md](../../.agents/rules/data-truth-classification.md) — Strict AS-IS vs unimplemented/unavailable status honesty.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `README.md` | Directory overview & governance contract | Required | `work-items/_template/README.md` |
| `request.md` | Change intake, objectives & non-negotiables | Required | `work-items/_template/request.md` |
| `discovery.md` | Audited AS-IS codebase & infrastructure evidence | Required | `work-items/_template/discovery.md` |
| `impact-analysis.md` | Cross-plane, CSP, boundary & compatibility impact | Required | `work-items/_template/impact-analysis.md` |
| `artifact-plan.yaml` | Machine-readable artifact plan & signal flags | Required | `work-items/_template/artifact-plan.yaml` |
| `implementation-plan.md` | Sequenced implementation & rollout stages | Required | `work-items/_template/implementation-plan.md` |
| `verification-plan.md` | Test & validator acceptance matrix | Required | `work-items/_template/verification-plan.md` |
| `review.md` | Audit & gate evaluation log | Required | `work-items/_template/review.md` |
| `state.yaml` | Machine-readable state machine ledger | Required | `work-items/_template/state.yaml` |

## 6. Directory and File Organization

Flat directory containing the 9 canonical work-item files for `FEAT-002`.

## 7. Document Creation Rules

- Preserve `work-items/_template/` section structure and YAML keys.
- Tag every verified observation as `FACT`, unvalidated assumptions as `[ASSUMPTION — REQUIRES VALIDATION]`, and unresolved items as `[OPEN QUESTION]`.

## 8. Creation Workflow

1. Audit AS-IS frontend assets, headless backend APIs, and Vite tooling.
2. Record evidence in `discovery.md` and impact in `impact-analysis.md`.
3. Build independent TypeScript SPA under `frontend/` across the 6 core modules.
4. Synchronize `docker-compose.yml`, `deploy/nginx/nginx.conf`, models (`models/ux/ux.yaml`, `models/architecture/components.yaml`), and C4 diagrams (`docs/diagrams/system/02-c4-container.md`).
5. Run automated validators (`tools/validators/run_all.py`) and test suites.

## 9. Relationships and Dependencies

Depends on completed work items `ARCH-001`, `DATA-001`, `DOCS-001`, and `FEAT-001`.

## 10. Quality Gate

All 9 work-item files exist, zero placeholders remain, tests and validators pass, and `state.yaml` transitions sequentially through `G0_DISCOVERY` .. `G6_RELEASE`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/run_all.py
cd frontend; npm run build; npm test
```

## 12. Agent Restrictions

- Never connect the browser directly to internal databases (Kafka, Redis, ClickHouse, PostgreSQL, MinIO).
- Never violate Clean Architecture boundaries in Backend.

