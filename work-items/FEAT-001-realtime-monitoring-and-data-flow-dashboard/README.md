# Work Item Directory (`work-items/FEAT-001-realtime-monitoring-and-data-flow-dashboard/`)

## 1. Directory Purpose

Tracks the design, implementation, governance synchronization, and verification of **FEAT-001**: the **Data Platform Real-Time Monitoring & Interactive Data Flow Observatory** (`Exchange -> Ingestion -> Kafka -> Redis / ClickHouse / Iceberg -> Silver -> Gold -> Serving -> API / Dashboard / Agent`).

## 2. Scope and Boundaries

- **Belongs in this directory**: Lifecycle artifacts for `FEAT-001` following `work-items/_template/` (`README.md`, `request.md`, `discovery.md`, `impact-analysis.md`, `artifact-plan.yaml`, `implementation-plan.md`, `verification-plan.md`, `review.md`, `state.yaml`).
- **Does NOT belong here**: Production Python code (`src/`), canonical YAML models (`models/`), or permanent human-readable engineering specs (`docs/`).

## 3. Agent Role and Responsibilities

- **Primary Authors**: `discovery-analyst`, `architecture-modeler`, `documentation-architect`.
- **Auditors**: `qa-reviewer`, `security-reviewer`, `documentation-auditor`.

## 4. Authoritative Inputs

1. [work-items/README.md](../README.md) — Work-item lifecycle contract.
2. [AGENTS.md](../../AGENTS.md) — Root documentation engineering contract & 12-Step Execution Protocol.
3. [.agents/rules/data-platform-observability.md](../../.agents/rules/data-platform-observability.md) — Parallel-branch latency, cardinality & truth rules.
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

Flat directory containing the 9 canonical work-item files for `FEAT-001`.

## 7. Document Creation Rules

- Preserve `work-items/_template/` section structure and YAML keys.
- Tag every verified observation as `FACT`, unvalidated assumptions as `[ASSUMPTION — REQUIRES VALIDATION]`, and unresolved items as `[OPEN QUESTION]`.

## 8. Creation Workflow

1. Audit AS-IS code and compose configuration on branch `arch/microservices`.
2. Record evidence in `discovery.md` and impact in `impact-analysis.md`.
3. Update canonical models (`models/`), observability primitives (`src/shared/observability/`), runtime (`src/serving/infrastructure/runtime.py`), APIs/UI (`src/serving/api/gateway/`), and tests (`tests/`).
4. Synchronize docs/diagrams and run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

Depends on completed baseline work items `ARCH-001`, `DATA-001`, and `DOCS-001`.

## 10. Quality Gate

All 9 work-item files exist, zero placeholders remain, tests and validators pass, and `state.yaml` transitions sequentially through `G0_DISCOVERY` .. `G6_RELEASE`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/run_all.py
.\.venv\Scripts\pytest.exe tests -v
```

## 12. Agent Restrictions

- Never fabricate runtime state, Kafka cluster topology, or synthetic candlestick bars disguised as live data.
- Never bypass `src/serving/api/**` Clean Architecture import boundaries enforced by `tests/architecture/test_clean_architecture_boundaries.py`.

