---
name: ux-modeling
description: Information architecture, user flows, and screens in models/ux/ and docs/product/11-ux/.
---

# Skill: UX Information Architecture & Screen Modeling (`SKILL-011`)

## 1. Description

Models navigation hierarchy, user flows, and screen specifications (`UX-###`, `SCR-###`) in `models/ux/` and `docs/product/11-ux/`.

## 2. Trigger Conditions

- Phase `11-ux` or frontend/dashboard/screen flow changes (`ux-modeler`).

## 3. Authoritative Inputs

- `models/ux/ux.yaml`, `navigation.yaml`, `screens.yaml`, `models/requirements/`, `models/api/`, `docs/product/11-ux/README.md`, `docs/templates/ux/`.

## 4. Preconditions

1. Target `README.md` read; backing use cases (`UC-###`) and API endpoints (`API-###`) verified.

## 5. Execution Procedure

1. Update `models/ux/ux.yaml`, `navigation.yaml`, and `screens.yaml` first with `UX-###` and `SCR-###` IDs, states (`loading`, `empty`, `error`, `stale-data`), and API bindings.
2. Author UX/screen specs in `docs/product/11-ux/` from `docs/templates/ux/`.
3. Synchronize derived sitemap/flow diagrams in `docs/diagrams/ux/` and run `python tools/validators/run_all.py`.

## 6. Output Artifacts

- `models/ux/*.yaml`, `docs/product/11-ux/*.md`, `docs/diagrams/ux/*.md`.

## 7. Validation

```powershell
python tools/validators/run_all.py
```

## 8. Failure Handling

- Tag unconfirmed UI layout or interaction choices as `[ASSUMPTION — REQUIRES VALIDATION]` or `[OPEN QUESTION]`.

## 9. Restrictions

- Never invent screens or UI widgets that call unapproved backend endpoints or bypass `Plane B` API boundaries.

## 10. Related Skills

- `use-case-modeling`, `api-contract`, `diagram-modeling`
