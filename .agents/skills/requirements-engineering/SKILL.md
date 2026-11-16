---
name: requirements-engineering
description: Models BR, FR, NFR, RULE, and AC inside capability requirements/ specs under Documentation V2.
---

# Skill: Requirements Engineering & Normalization (`SKILL-003`)

## 1. Description

Extracts, normalizes, and models capability business needs (`BR`), functional requirements (`FR`), non-functional requirements (`NFR`), deterministic business rules (`RULE`), and acceptance criteria (`AC`) inside `docs/<plane>/domains/<domain>/capabilities/<capability>/requirements/` and `docs/overview/system-requirements.md`.

## 2. Trigger Conditions

- Lifecycle Stage 2 (`Requirements Analysis`), `QG-2-REQS`, or capability requirement/business-rule changes (`requirements-engineer`, `business-analyst`).

## 3. Authoritative Inputs

- `AGENTS.md`, `docs/governance/standards/requirements-standards.md`, `docs/governance/standards/writing-standards.md`, `docs/governance/templates/product-and-requirements/`, owning `capability.yaml`, and inspected `src/`/`frontend/` code.

## 4. Preconditions

1. Owning capability `capability.yaml` read; existing semantic IDs checked in `.agents/config/identifier-registry.yaml` and existing capability specs.

## 5. Execution Procedure

1. Inspect `capability.yaml`, `docs/overview/system-requirements.md`, and owning `domain-specification.md`.
2. Author or update `requirements/capability-specification.md`, `requirements/business-rules.md`, and `requirements/nfr.md` from `docs/governance/templates/product-and-requirements/`.
3. Assign globally unique, atomic requirement IDs (`FR-<DOM>-NNN`, `BR-<DOM>-NNN`, `NFR-<DOM>-NNN`, `RULE-<DOM>-NNN`, `AC-<DOM>-NNN`) and declare `requirement_ids` in frontmatter.
4. Separate `AS-IS` verified behavior from `TARGET` requirements; log missing thresholds or business choices as `[OPEN]` / `BLOCKED` without inventing SLA numbers.
5. Link requirements into `quality/traceability.yaml` and run `python scripts/docs/validate_docs.py`.

## 6. Output Artifacts

- `requirements/capability-specification.md`, `requirements/business-rules.md`, `requirements/nfr.md`, and updated `quality/traceability.yaml`.

## 7. Validation

```powershell
python scripts/docs/validate_docs.py
python tools/validators/run_all.py
```

## 8. Failure Handling

- Record missing acceptance thresholds or conflicting stakeholder rules as `[OPEN]` in `capability.yaml`, keep `status: DRAFT`, and resolve all validator errors.

## 9. Restrictions

- Never renumber existing requirement IDs; never invent unverified financial rules or SLA thresholds.

## 10. Related Skills

- `srs-generation`, `use-case-modeling`, `traceability-audit`
