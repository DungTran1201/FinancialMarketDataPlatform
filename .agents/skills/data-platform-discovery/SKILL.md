---
name: data-platform-discovery
description: Audits AS-IS vs TARGET data platform services, flows, and gaps.
---

# Skill: Data Platform Evidence-Led Discovery (`SKILL-019`)

## 1. Description

Evidence-led discovery of current (`AS-IS/FACT`) vs. target (`DOCUMENTED TARGET`) data platform services, data paths, gaps, and ownership.

## 2. Trigger Conditions

- Repository onboarding, data-platform audits, major pipeline changes, or implementation-readiness reviews (`data-platform-architect`, `data-engineer`, `financial-data-platform-reviewer`).

## 3. Authoritative Inputs

- `AGENTS.md`, target `README.md`, `docs/architecture/` (`00..13`, `ADR-001..006`), `docs/specifications/`, `.agents/config/data-platform-boundaries.yaml`, `src/`, `deploy/`, `docker-compose.yml`, `models/`, `tests/`, `work-items/`.

## 4. Preconditions

1. Target `README.md` read; active role loaded; runtime state verified from code/config rather than filenames alone.

## 5. Execution Procedure

1. Inventory services, packages (`src/collectors/`, `src/consumers/`, `src/processing/`, `src/quality/`, `src/transformation/`, `src/backend/`, `src/agent/`), SQL schemas (`deploy/`), Compose profiles, and CI workflows.
2. Trace source-to-sink paths and identify Kafka topic, Redis key, ClickHouse table, and Iceberg/dbt model boundaries.
3. Inspect implementations and tests alongside architecture documents; classify each capability as `AS-IS/FACT`, partial scaffold, `DOCUMENTED TARGET`, `PROPOSED`, `ASSUMPTION`, or `OPEN QUESTION`.
4. Identify contract gaps, owner gaps, reliability risks, quality coverage, and operational visibility.
5. Record exact file/line evidence paths and distinguish executable production code from declarative specifications and exploratory notebooks (`notebooks/`).
6. Produce discovery/impact analysis artifacts in `work-items/<ID>/` or `docs/product/00-discovery/` and run `tools/validators/run_all.py`.

## 6. Output Artifacts

- Discovery report, `AS-IS` vs. `TO-BE` capability matrix, evidence register, data-flow map, risk/gap register, and work-item impact analysis.

## 7. Validation

```powershell
python tools/validators/run_all.py
python -m unittest discover -s tests -v
```

## 8. Failure Handling

- Mark inaccessible external sources as unknown and record unresolved points as `[OPEN QUESTION]`; never replace missing evidence with silent assumptions.

## 9. Restrictions

- No production code mutation during discovery unless explicitly assigned in a work item.
- Never run destructive commands or expose secrets.

## 10. Related Skills

- `project-discovery`
- `architecture-modeling`
- `data-governance-lineage`
- `data-platform-testing-recovery`

