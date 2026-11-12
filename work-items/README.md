# Work Items Engineering Subsystem (`work-items/`)

## 1. Directory Purpose

`work-items/` is the change-control and artifact-planning subsystem for the **FinancialMarketDataPlatform** repository. It governs how every non-trivial engineering change (`FEAT`, `BUG`, `ARCH`, `DOCS`, `DATA`, `SEC`, `INFRA`, `REFACTOR`) progresses through a deterministic 10-stage lifecycle (`INTAKE → DISCOVERY → IMPACT → DESIGN → PLAN_REVIEW → IMPLEMENT → VERIFY → SYNC → RELEASE → DONE`) before and during modification of canonical models (`models/`), documentation (`docs/`), diagrams (`docs/diagrams/`), or source code (`src/`).

## 2. Scope and Boundaries

- **Belongs in `work-items/`**:
  - Change intake requests (`request.md`), current-state discovery and reference audits (`discovery.md`), cross-plane impact analyses (`impact-analysis.md`), artifact selection plans (`artifact-plan.yaml`), execution plans (`implementation-plan.md`), verification plans (`verification-plan.md`), review records (`review.md`), and work-item state machines (`state.yaml`).
  - The reusable work-item blueprint in `work-items/_template/`.
- **Does NOT belong in `work-items/`**:
  - Authoritative product or platform SRS, SAD, ADRs, API specifications, domain models, or canonical YAML models. Final documents must always reside in `docs/` and `models/`.

## 3. Agent Role and Responsibilities

- **Primary Owning Roles**:
  - `discovery-analyst` (`.agents/agents/discovery-analyst.md`): Populates `request.md`, `discovery.md`, and `impact-analysis.md`.
  - `documentation-architect` (`.agents/agents/documentation-architect.md`): Selects required and conditional artifacts in `artifact-plan.yaml` using `.agents/config/artifact-matrix.yaml`.
  - `documentation-auditor` (`.agents/agents/documentation-auditor.md`): Audits completion in `review.md` and verifies `state.yaml` transitions.

## 4. Authoritative Inputs

Before creating or updating a work item, Agents must consult:
1. [AGENTS.md](../AGENTS.md) — Root operating contract and source-of-truth hierarchy.
2. [.agents/config/change-types.yaml](../.agents/config/change-types.yaml) — Change taxonomy and risk classification rules.
3. [.agents/config/artifact-matrix.yaml](../.agents/config/artifact-matrix.yaml) — Mandatory and conditional artifact selection rules.
4. [.agents/config/phase-gates.yaml](../.agents/config/phase-gates.yaml) — Gate entry/exit criteria (`G0_DISCOVERY` through `G6_RELEASE`).

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `README.md` | Work item overview, scope boundary, and file index | Required | [work-items/_template/README.md](_template/README.md) |
| `request.md` | Captures user intent, classification, scope, and constraints | Required | [work-items/_template/request.md](_template/request.md) |
| `discovery.md` | Records FACT / ASSUMPTION / DECISION / OPEN QUESTION evidence | Required | [work-items/_template/discovery.md](_template/discovery.md) |
| `impact-analysis.md` | Identifies affected planes, models, docs, diagrams, and code | Required | [work-items/_template/impact-analysis.md](_template/impact-analysis.md) |
| `artifact-plan.yaml` | Machine-readable selection of `CREATED`, `UPDATED`, `REVIEWED`, `UNCHANGED`, `DEPRECATED` artifacts | Required | [work-items/_template/artifact-plan.yaml](_template/artifact-plan.yaml) |
| `implementation-plan.md` | Step-by-step execution sequence and rollback strategy | Required | [work-items/_template/implementation-plan.md](_template/implementation-plan.md) |
| `verification-plan.md` | Deterministic test and validator commands required to pass | Required | [work-items/_template/verification-plan.md](_template/verification-plan.md) |
| `review.md` | Audit findings, quality gate sign-off, and unresolved items | Required | [work-items/_template/review.md](_template/review.md) |
| `state.yaml` | Current lifecycle state (`INTAKE`..`DONE`) and gate status | Required | [work-items/_template/state.yaml](_template/state.yaml) |

## 6. Directory and File Organization

```text
work-items/
├── README.md
├── _template/
│   ├── README.md
│   ├── request.md
│   ├── discovery.md
│   ├── impact-analysis.md
│   ├── artifact-plan.yaml
│   ├── implementation-plan.md
│   ├── verification-plan.md
│   ├── review.md
│   └── state.yaml
└── <TYPE>-<NNN>-<kebab-slug>/
```
- **Folder Naming Convention**: `<TYPE>-<NNN>-<kebab-slug>`, where `<TYPE>` is one of `FEAT`, `BUG`, `ARCH`, `DOCS`, `DATA`, `SEC`, `INFRA`, `REFACTOR` (e.g., `DOCS-001-documentation-engineering-foundation`).

## 7. Document Creation Rules

- Copy all 9 files from `work-items/_template/` when initializing a new work item.
- Every markdown file in a work item must include metadata headers (`Work Item ID`, `Change Type`, `Risk Level`, `Status`, `Created`, `Updated`).
- Valid lifecycle states in `state.yaml`: `INTAKE`, `DISCOVERY`, `IMPACT`, `DESIGN`, `PLAN_REVIEW`, `IMPLEMENT`, `VERIFY`, `SYNC`, `RELEASE`, `DONE`.
- Valid artifact actions in `artifact-plan.yaml`: `CREATED`, `UPDATED`, `REVIEWED`, `UNCHANGED`, `DEPRECATED`.

## 8. Creation Workflow

1. Read this `work-items/README.md` and `work-items/_template/README.md`.
2. Classify the change type (`FEAT`, `BUG`, `ARCH`, `DOCS`, `DATA`, `SEC`, `INFRA`, `REFACTOR`) and risk tier (`R1` Low, `R2` Medium, `R3` High/Cross-Plane) using `.agents/config/change-types.yaml`.
3. Create folder `work-items/<TYPE>-<NNN>-<slug>/` and initialize files from `work-items/_template/`.
4. Complete `request.md` and `discovery.md`, explicitly separating `FACT`, `ASSUMPTION`, `DECISION`, and `OPEN QUESTION`.
5. Complete `impact-analysis.md` and `artifact-plan.yaml` according to `.agents/config/artifact-matrix.yaml`.
6. Advance `state.yaml` through `IMPLEMENT`, `VERIFY`, and `SYNC` as canonical models, docs, and validators are executed.
7. Record final audit evidence in `review.md` and run `validate_work_items.py`.

## 9. Relationships and Dependencies

- **Upstream**: Governed by `.agents/rules/change-lifecycle.md`, `.agents/config/artifact-matrix.yaml`, and `.agents/config/phase-gates.yaml`.
- **Downstream**: Directs which files in `models/`, `docs/product/`, `docs/architecture/`, `docs/features/`, and `docs/diagrams/` are created or modified.

## 10. Quality Gate

A work item passes its quality gate only when:
- All 9 required files exist in `work-items/<ID>-<slug>/`.
- `state.yaml` and `artifact-plan.yaml` parse as valid YAML and conform to `.agents/config/artifact-matrix.yaml`.
- Every artifact listed as `CREATED` or `UPDATED` in `artifact-plan.yaml` exists at its canonical path outside `work-items/`.
- All validators in `tools/validators/run_all.py` exit with code `0`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_work_items.py
.\.venv\Scripts\python.exe tools/validators/validate_artifact_matrix.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- **Do NOT** store final SRS, SAD, ADR, API contract, or canonical YAML models inside `work-items/` as a substitute for `docs/` or `models/`.
- **Do NOT** skip `discovery.md`, `impact-analysis.md`, or `artifact-plan.yaml` for non-trivial changes.
- **Do NOT** mark a work item `DONE` in `state.yaml` if any validator fails or if `ready_for_stop` is `false`.
- **Do NOT** silently convert an `ASSUMPTION` or `OPEN QUESTION` in `discovery.md` into an approved `FACT` without documented evidence.

