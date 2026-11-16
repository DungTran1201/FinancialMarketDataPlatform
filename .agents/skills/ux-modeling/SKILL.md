---
name: ux-modeling
description: Documents SPA screens, user flows, and frontend-backend compatibility in docs/application-plane/.
---

# Skill: UX Information Architecture & Screen Modeling (`SKILL-011`)

## 1. Description

Documents frontend SPA navigation, screen modules, UI states (`loading`, `empty`, `error`, `stale-data`), user flows, and frontend-to-backend compatibility mismatches across `docs/application-plane/architecture/` and Application Plane domain capabilities.

## 2. Trigger Conditions

- Application Plane UI architecture updates, frontend module/API alignment, or screen flow changes (`ux-modeler`, `fullstack-engineer`).

## 3. Authoritative Inputs

- `frontend/src/app/router/router.ts`, `frontend/src/modules/`, `frontend/src/services/`, `frontend/src/stores/`, `docs/application-plane/architecture/frontend-architecture.md`, `docs/application-plane/architecture/screen-and-api-compatibility-matrix.md`.

## 4. Preconditions

1. Owning Application Plane capability `capability.yaml` and actual `frontend/src/` code inspected.

## 5. Execution Procedure

1. Verify actual hash routes, module components, and API service calls in `frontend/src/` against backend FastAPI routes (`src/serving/api/`).
2. Update `docs/application-plane/architecture/frontend-architecture.md`, `screen-and-api-compatibility-matrix.md`, and owning capability `use-cases/` or `workflows/`.
3. Record any unaligned paths (`COMPAT-*`), mock fallbacks, or default auth persona gaps (`ASSUMP-*`) transparently.
4. Synchronize derived diagrams in `docs/application-plane/architecture/diagrams/frontend-backend-components.md` and run `python scripts/docs/validate_docs.py`.

## 6. Output Artifacts

- Updated `frontend-architecture.md`, `screen-and-api-compatibility-matrix.md`, capability use-cases/workflows, and derived interaction diagrams.

## 7. Validation

```powershell
python scripts/docs/validate_docs.py
npm test --prefix frontend
npm run build --prefix frontend
```

## 8. Failure Handling

- Tag unconfirmed UI layout or auth-flow expectations as `[ASSUMPTION]` or `[OPEN]`; fix all validator errors.

## 9. Restrictions

- Never document decommissioned `/ui/data-flow` as active UI; never invent unverified API calls; never recreate `models/ux/` or `docs/product/11-ux/`.

## 10. Related Skills

- `use-case-modeling`, `api-contract`, `diagram-modeling`
