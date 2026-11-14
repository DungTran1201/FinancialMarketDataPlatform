---
name: architecture-modeling
description: C4 views, SADs, and ADRs in models/architecture/ and docs/.
---

# Skill: System, Data & Software Architecture Modeling (`SKILL-005`)

## 1. Description

Models system context, C4 containers/components (`COMP-###`), SADs, and ADRs (`ADR-###`) in `models/architecture/` and `docs/`.

## 2. Trigger Conditions

- Phase `05-system-analysis`, `06-architecture`, or `ARCH` work items (`architecture-modeler`, `data-platform-architect`).

## 3. Authoritative Inputs

- `models/architecture/architecture.yaml`, `components.yaml`, `docs/architecture/00..13-*.md`, `docs/architecture/adr/ADR-001..006`, `docs/templates/architecture/`.

## 4. Preconditions

1. Target `README.md` read; preserved baseline `ADR-001..006` and Three-Plane boundaries (`.agents/config/data-platform-boundaries.yaml`) verified.

## 5. Execution Procedure

1. Update `models/architecture/architecture.yaml` and `components.yaml` first with `COMP-###` IDs and plane assignments (`Plane A`, `Plane B`, `Plane C`).
2. Author or update SAD/C4/ADR documents in `docs/product/06-architecture/` or `docs/architecture/` using `docs/templates/architecture/`.
3. Clearly separate `AS-IS/FACT` (`src/`, `docker-compose.yml`) from `DOCUMENTED TARGET`.
4. Synchronize derived C4/architecture diagrams in `docs/diagrams/` and run `python tools/validators/run_all.py`.

## 6. Output Artifacts

- `models/architecture/*.yaml`, `docs/product/06-architecture/*.md`, `docs/architecture/adr/ADR-###.md`.

## 7. Validation

```powershell
python tools/validators/run_all.py
```

## 8. Failure Handling

- Record unapproved topology choices as `[PROPOSED — NOT APPROVED]` or `[OPEN QUESTION]`; fix all validator errors.

## 9. Restrictions

- Never overwrite preserved `docs/architecture/00..13` or `ADR-001..006` without an approved `ARCH` work item; never violate Three-Plane isolation.

## 10. Related Skills

- `diagram-modeling`, `data-platform-discovery`, `security-threat-modeling`
