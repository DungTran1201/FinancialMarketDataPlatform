---
name: data-platform-discovery
description: Audits AS-IS vs TARGET data platform services, flows, and gaps across Data Plane code and V2 docs.
---

# Skill: Data Platform Evidence-Led Discovery (`SKILL-019`)

## 1. Description

Evidence-led discovery of current (`AS-IS`) vs. target (`TARGET`) data platform services, data paths, gaps, and ownership across Data Plane (`docs/data-plane/`), `src/`, `deploy/`, `docker-compose.yml`, and `tests/`.

## 2. Trigger Conditions

- Repository onboarding, data-platform audits, major pipeline changes, or implementation-readiness reviews (`data-platform-architect`, `data-engineer`, `financial-data-platform-reviewer`).

## 3. Authoritative Inputs

- `AGENTS.md`, `docs/docs-index.yaml`, `docs/data-plane/README.md`, `docs/data-plane/architecture/`, `.agents/config/data-platform-boundaries.yaml`, `src/`, `deploy/`, `docker-compose.yml`, `tests/`.

## 4. Preconditions

1. Mandatory V2 discovery chain completed; active role loaded; runtime state verified from code/config rather than filenames alone.

## 5. Execution Procedure

1. Inventory services, packages (`src/shared/`, `src/ingestion/`, `src/streaming/`, `src/lakehouse/`, `src/serving/`, `src/intelligence/`), SQL schemas (`deploy/`), Compose profiles, and CI workflows.
2. Trace source-to-sink paths and identify Kafka topic, Redis key, ClickHouse table, and Iceberg/dbt model boundaries.
3. Inspect implementations and tests alongside `docs/data-plane/` and `docs/overview/`; classify each capability's `implementation_status` accurately (`PLANNED`, `NOT_IMPLEMENTED`, `SIMULATED`, `PARTIALLY_IMPLEMENTED`, `IMPLEMENTED`, `VERIFIED`).
4. Identify contract gaps, owner gaps, reliability risks, quality coverage, and operational visibility.
5. Record exact file/line evidence paths and distinguish executable production code from declarative specs and exploratory notebooks (`notebooks/`).
6. Update owning `capability.yaml` (`open_questions`, `blockers`, `implementation_status`) and `docs/data-plane/` specs, then run `python scripts/docs/validate_docs.py`.

## 6. Output Artifacts

- Discovery findings, `AS-IS` vs. `TARGET` capability tables, evidence registers, data-flow maps, and updated `capability.yaml` manifests under `docs/data-plane/`.

## 7. Validation

```powershell
python scripts/docs/validate_docs.py
python -m pytest tests/architecture/ tests/contract/ -v
```

## 8. Failure Handling

- Mark inaccessible external sources as unknown and record unresolved points as `[OPEN]` / `BLOCKED`; never replace missing evidence with silent assumptions.

## 9. Restrictions

- No production code mutation during discovery unless explicitly authorized.
- Never run destructive commands or expose secrets.

## 10. Related Skills

- `project-discovery`
- `architecture-modeling`
- `data-governance-lineage`
- `data-platform-testing-recovery`
