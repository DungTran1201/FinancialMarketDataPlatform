---
name: srs-generation
description: Synthesizes capability-specification.md and system-requirements.md without monolithic V1 SRS duplication.
---

# Skill: Capability Specification & Requirements Synthesis (`SKILL-004`)

## 1. Description

Synthesizes capability requirements (`BR`, `FR`, `NFR`, `RULE`, `AC`), `AS-IS vs. TARGET` behavior, dependencies, and open questions into a capability's authoritative `requirements/capability-specification.md` and updates the platform index `docs/overview/system-requirements.md`.

## 2. Trigger Conditions

- Lifecycle Stage 2 (`Requirements Analysis`) or Stage 3 (`Specification`) when creating or consolidating capability specifications (`requirements-engineer`, `business-analyst`).

## 3. Authoritative Inputs

- `docs/governance/documentation-architecture.md` (prohibits monolithic cross-system SRS files), `docs/governance/standards/requirements-standards.md`, `docs/governance/templates/product-and-requirements/capability-specification.template.md`, `system-requirements.template.md`, and `capability.yaml`.

## 4. Preconditions

1. Owning `capability.yaml` initialized and source code/configs inspected for `AS-IS` state.

## 5. Execution Procedure

1. Read `capability.yaml` (`in_scope`, `out_of_scope`, `depends_on`, `code_paths`, `open_questions`, `blockers`).
2. Populate `<capability>/requirements/capability-specification.md` strictly from `docs/governance/templates/product-and-requirements/capability-specification.template.md`.
3. Cross-reference every `FR-*`, `NFR-*`, `RULE-*`, and `AC-*` to upstream business drivers and downstream use cases, contracts, and `quality/traceability.yaml`.
4. Ensure `docs/overview/system-requirements.md` indexes top-level platform requirements without duplicating capability-level prose.
5. Run `python scripts/docs/validate_docs.py`.

## 6. Output Artifacts

- `<capability>/requirements/capability-specification.md` and synchronized links in `docs/overview/system-requirements.md` and `quality/traceability.yaml`.

## 7. Validation

```powershell
python scripts/docs/validate_docs.py
python tools/validators/run_all.py
```

## 8. Failure Handling

- Do not promote `capability-specification.md` to `APPROVED` if unresolved `[OPEN]` / `TBD` markers remain or traceability links are incomplete.

## 9. Restrictions

- Never recreate a monolithic `docs/product/02-requirements/SRS.md` covering the entire repository.

## 10. Related Skills

- `requirements-engineering`, `use-case-modeling`, `traceability-audit`
