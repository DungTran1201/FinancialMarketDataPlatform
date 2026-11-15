---
name: project-discovery
description: Audits codebase and specs into FACT, ASSUMPTION, DECISION, OPEN QUESTION registers.
---

# Skill: Project & Current-State Discovery (`SKILL-001`)

## 1. Description

Audits repository state, reference architectures, and requirements inputs into evidence registers (`FACT`, `ASSUMPTION`, `DECISION`, `OPEN QUESTION`).

## 2. Trigger Conditions

- Phase `00-discovery` or Work Item `discovery.md` / `impact-analysis.md` authoring (`discovery-analyst`).

## 3. Authoritative Inputs

- `AGENTS.md`, target `README.md`, `work-items/<ID>/`, `models/context/` (when instantiated), `models/architecture/architecture.yaml`, and `models/requirements/requirements.yaml`, `docs/templates/discovery/`, `src/`, `docker-compose.yml`.

## 4. Preconditions

1. Target directory `README.md` read; upstream evidence classified (`FACT` vs `ASSUMPTION` vs `DECISION` vs `OPEN QUESTION`).

## 5. Execution Procedure

1. Inspect `models/context/` (when instantiated), `models/architecture/architecture.yaml`, and `models/requirements/requirements.yaml`, baseline specs (`docs/architecture/`, `docs/specifications/`), and `src/` implementation state.
2. Update `models/context/` (when instantiated), `models/architecture/architecture.yaml`, and `models/requirements/requirements.yaml` first with stable IDs from `.agents/config/identifier-registry.yaml`.
3. Author discovery/impact docs in `docs/product/00-discovery/` or `work-items/<ID>/` using `docs/templates/discovery/`.
4. Tag unverified hypotheses with `[ASSUMPTION — REQUIRES VALIDATION]` and unresolved ambiguities with `[OPEN QUESTION]`.
5. Run `python tools/validators/run_all.py`.

## 6. Output Artifacts

- `models/context/` (when instantiated), `models/architecture/architecture.yaml`, and `models/requirements/requirements.yaml`, `docs/product/00-discovery/*.md`, `work-items/<ID>/discovery.md`, `impact-analysis.md`.

## 7. Validation

```powershell
python tools/validators/run_all.py
```

## 8. Failure Handling

- Record missing upstream facts as `[OPEN QUESTION]`, keep status `DRAFT`/`REVIEW_REQUIRED`, and fix all validator errors before finishing.

## 9. Restrictions

- Never invent product requirements, endpoints, or business rules; never overwrite baselined Data Platform files without an approved work item.

## 10. Related Skills

- `data-platform-discovery`, `documentation-creation`, `traceability-audit`
