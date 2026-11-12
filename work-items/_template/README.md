# Work Item Template Directory (`work-items/_template/`)

## 1. Directory Purpose

`work-items/_template/` contains the canonical 9-file blueprint used to instantiate every new work item folder under `work-items/<TYPE>-<NNN>-<slug>/`. It standardizes change intake, discovery evidence registration, impact analysis, artifact planning, implementation planning, verification, review, and lifecycle state tracking.

## 2. Scope and Boundaries

- **Belongs in `work-items/_template/`**: Only the reusable template files for work items (`README.md`, `request.md`, `discovery.md`, `impact-analysis.md`, `artifact-plan.yaml`, `implementation-plan.md`, `verification-plan.md`, `review.md`, `state.yaml`).
- **Does NOT belong here**: Active work item data, feature requirements, or domain/architecture specifications (see `docs/templates/` for engineering document templates).

## 3. Agent Role and Responsibilities

- **Primary Owning Roles**: `documentation-architect` and `discovery-analyst`.
- **Responsibility**: Copy these templates into a new work item directory and replace placeholder tokens (`[WORK-ITEM-ID]`, `[TO BE COMPLETED]`) with verified change evidence.

## 4. Authoritative Inputs

1. [work-items/README.md](../README.md) — Work item subsystem contract.
2. [.agents/config/change-types.yaml](../../.agents/config/change-types.yaml) — Change type and risk definitions.
3. [.agents/config/artifact-matrix.yaml](../../.agents/config/artifact-matrix.yaml) — Artifact selection rules.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `README.md` | Template for work-item directory index | Required | `work-items/_template/README.md` |
| `request.md` | Template for change intake and classification | Required | `work-items/_template/request.md` |
| `discovery.md` | Template for current-state audit and fact classification | Required | `work-items/_template/discovery.md` |
| `impact-analysis.md` | Template for cross-plane and artifact impact analysis | Required | `work-items/_template/impact-analysis.md` |
| `artifact-plan.yaml` | Template for machine-readable artifact action plan | Required | `work-items/_template/artifact-plan.yaml` |
| `implementation-plan.md` | Template for sequenced execution steps | Required | `work-items/_template/implementation-plan.md` |
| `verification-plan.md` | Template for automated and manual verification steps | Required | `work-items/_template/verification-plan.md` |
| `review.md` | Template for audit and gate sign-off | Required | `work-items/_template/review.md` |
| `state.yaml` | Template for work-item state machine tracking | Required | `work-items/_template/state.yaml` |

## 6. Directory and File Organization

All 9 template files sit flat inside `work-items/_template/`. Do not create nested subdirectories inside `_template/`.

## 7. Document Creation Rules

- Preserve all section headers and YAML keys when instantiating a new work item.
- Never hardcode specific product features into `_template/` files.

## 8. Creation Workflow

1. Inspect `work-items/README.md`.
2. Copy all files from `work-items/_template/` to `work-items/<TYPE>-<NNN>-<slug>/`.
3. Populate `state.yaml` with `status: INTAKE` or `DISCOVERY`.
4. Complete each lifecycle artifact sequentially as gates are cleared.

## 9. Relationships and Dependencies

- Referenced by `tools/validators/validate_work_items.py` as the structural schema for all active work item folders.

## 10. Quality Gate

- All 9 template files exist, contain no hardcoded feature IDs, and pass `validate_work_items.py`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_work_items.py
```

## 12. Agent Restrictions

- **Do NOT** edit `work-items/_template/` files to store active work item progress.
- **Do NOT** remove mandatory YAML keys from `state.yaml` or `artifact-plan.yaml`.

