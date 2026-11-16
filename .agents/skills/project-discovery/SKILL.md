---
name: project-discovery
description: Audits codebase and specs into AS-IS facts, assumptions, and open blockers under Documentation V2.
---

# Skill: Project & Current-State Discovery (`SKILL-001`)

## 1. Description

Audits repository state (`src/`, `frontend/`, `deploy/`, `tests/`, `pyproject.toml`), Plane/Domain/Capability indexes, and upstream dependencies into evidence-backed `AS-IS` vs `TARGET` registers, `[ASSUMPTION]` tags, and `open_questions` / `blockers` entries.

## 2. Trigger Conditions

- Lifecycle Stage 1 (`Discovery and Scope`), `QG-1-SCOPE` readiness checks, or impact analysis prior to capability changes (`discovery-analyst`, `business-analyst`).

## 3. Authoritative Inputs

- `AGENTS.md`, `docs/README.md`, `docs/docs-index.yaml`, `docs/governance/standards/ai-agent-and-discovery-standards.md`, target `capability.yaml`, `src/`, `frontend/`, `deploy/`, `docker-compose.yml`, `tests/`.

## 4. Preconditions

1. Mandatory discovery chain (`AGENTS.md` -> `docs/README.md` -> `docs/docs-index.yaml` -> Plane -> Domain -> `capability.yaml`) completed.

## 5. Execution Procedure

1. Resolve the owning Plane (`data-plane`, `application-plane`, `intelligence-plane`, `overview`, or `governance`), Domain, and Capability via `.agents/config/document-map.yaml`.
2. Inspect `capability.yaml` (`risk_tier`, `risk_signals`, `depends_on`, `code_paths`, `test_paths`, `open_questions`, `blockers`).
3. Inspect actual implementation files in `src/`, `frontend/`, `deploy/`, `docker-compose.yml`, and `tests/` to establish `AS-IS` reality.
4. Execute the 6-step impact analysis per `docs/governance/traceability-and-impact-analysis.md`.
5. Update `capability.yaml` or overview/capability `AS-IS vs. TARGET` tables, tagging unconfirmed hypotheses `[ASSUMPTION]` and unresolved gaps `[OPEN]` or `BLOCKED`.
6. Run `python scripts/docs/validate_docs.py`.

## 6. Output Artifacts

- Updated `capability.yaml` (`implementation_status`, `open_questions`, `blockers`, `code_paths`, `test_paths`) and evidence-backed discovery/context specifications under `docs/overview/` or owning capability directories.

## 7. Validation

```powershell
python scripts/docs/validate_docs.py
python tools/validators/run_all.py
```

## 8. Failure Handling

- Record missing upstream facts or unresolved policy conflicts as `[OPEN]` / `BLOCKED` in `capability.yaml`, keep `status: DRAFT`, and resolve all validator errors before finishing.

## 9. Restrictions

- Never invent product requirements, endpoints, or business rules; never infer `AS-IS` implementation from legacy docs or filenames alone.

## 10. Related Skills

- `data-platform-discovery`, `documentation-creation`, `traceability-audit`
