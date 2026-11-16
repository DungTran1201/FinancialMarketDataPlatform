---
name: architecture-modeling
description: Authors Plane/Overview C4 architectures, MADR 4.0 ADRs, and capability designs in Documentation V2.
---

# Skill: System, Data & Software Architecture Modeling (`SKILL-005`)

## 1. Description

Models Platform Overview and Plane architectures, C4 context/container/component views, MADR 4.0 ADRs (`decisions/adr-*.md`), capability `design/component-design.md`, and Intelligence Plane `design/agent-specification.md` in Documentation V2.

## 2. Trigger Conditions

- Lifecycle Stage 4 (`Architecture and Design`), `QG-3-SPEC-DESIGN`, or architectural/ADR changes across `docs/overview/`, `docs/<plane>/architecture/`, or capability `design/` (`architecture-modeler`, `data-platform-architect`).

## 3. Authoritative Inputs

- `docs/governance/standards/architecture-standards.md`, `docs/governance/standards/ai-agent-and-discovery-standards.md`, `docs/governance/templates/architecture/`, `.agents/config/data-platform-boundaries.yaml`, `src/`, `deploy/`, `docker-compose.yml`, and `tests/architecture/test_clean_architecture_boundaries.py`.

## 4. Preconditions

1. Owning Plane/Overview `README.md` or `capability.yaml` read; Three-Plane boundaries and `AS-IS` code structure verified.

## 5. Execution Procedure

1. Author or update architecture descriptions (`architecture-description.template.md`), component designs (`component-design.template.md`), agent specs (`agent-specification.template.md`), or MADR 4.0 ADRs (`adr.template.md`) at the narrowest owning scope.
2. Ensure architecture docs cover mandatory sections (`scope`, `context`, `building` blocks) and ADRs cover `context`, `option`, `decision`, and `consequence` sections enforced by `validate_docs.py`.
3. Explicitly separate `AS-IS` runtime reality (`src/`, `docker-compose.yml`) from `TARGET` design.
4. Synchronize scoped derived C4 diagrams in `docs/overview/diagrams/` or `docs/<plane>/architecture/diagrams/` and run `python scripts/docs/validate_docs.py`.

## 6. Output Artifacts

- Scoped architecture descriptions, MADR 4.0 ADRs (`decisions/adr-*.md`), capability `design/` specs, and derived C4 Mermaid diagrams.

## 7. Validation

```powershell
python scripts/docs/validate_docs.py
python -m pytest tests/architecture/ -v
```

## 8. Failure Handling

- Record unapproved topology choices as `DRAFT` / `[OPEN]` without fabricating architecture approvals; fix all validator errors.

## 9. Restrictions

- Never violate Three-Plane module isolation (`tests/architecture/test_clean_architecture_boundaries.py`); never recreate V1 `docs/architecture/` or detached `docs/diagrams/`.

## 10. Related Skills

- `diagram-modeling`, `data-platform-discovery`, `security-threat-modeling`
