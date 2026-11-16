---
name: documentation-creation
description: Authors template-governed Documentation V2 specs and scoped README indexes from docs/governance/templates/.
---

# Skill: Template-Governed Documentation Authoring (`SKILL-002`)

## 1. Description

Authors and updates Markdown specifications, YAML manifests/contracts, and scoped `README.md` indexes strictly from `docs/governance/templates/` in conformance with `docs/governance/schemas/` and `docs/governance/standards/writing-standards.md`.

## 2. Trigger Conditions

- Any Documentation V2 authoring or synchronization task (`documentation-architect` and owning capability roles).

## 3. Authoritative Inputs

- `AGENTS.md`, `docs/docs-index.yaml`, `docs/governance/documentation-architecture.md`, `docs/governance/catalog/artifact-applicability-matrix.yaml`, `docs/governance/catalog/artifact-catalog.yaml`, `.agents/config/document-map.yaml`, `docs/governance/templates/`.

## 4. Preconditions

1. Target Plane, Domain, Capability, `risk_tier`, and active `risk_signals` resolved; artifact applicability verified in `artifact-applicability-matrix.yaml`.

## 5. Execution Procedure

1. Look up the required template path and schema in `docs/governance/catalog/artifact-catalog.yaml` and `.agents/config/document-map.yaml`.
2. Instantiate from `docs/governance/templates/` with complete YAML frontmatter matching `docs/governance/schemas/document-frontmatter.schema.json`.
3. Place the file at its narrowest owning scope (`docs/overview/`, `docs/<plane>/`, `docs/<plane>/domains/<domain>/`, or `capabilities/<capability>/`).
4. Populate prose strictly from verified `AS-IS` code/test evidence and authoritative `TARGET` contracts, tagging `[ASSUMPTION]` or `[OPEN]` explicitly.
5. Update sibling `README.md` indexes and `capability.yaml` (`required_artifacts`, `authoritative_documents`) without creating empty placeholder folders.
6. Run `python scripts/docs/validate_docs.py`.

## 6. Output Artifacts

- Template-compliant Markdown specifications, capability manifests, and scoped `README.md` indexes under `docs/`.

## 7. Validation

```powershell
python scripts/docs/validate_docs.py
python tools/validators/run_all.py
```

## 8. Failure Handling

- Keep `status: DRAFT` (or `IN_REVIEW`) if `[OPEN]` questions or `TBD` items remain; fix all `validate_docs.py` errors before finishing.

## 9. Restrictions

- Never author documents into retired V1 directories (`docs/product/`, `docs/templates/`, `docs/diagrams/`, `docs/archive/`, `models/`, `work-items/`).
- Never create empty placeholder directories or duplicate governance standards prose.

## 10. Related Skills

- `documentation-review`, `traceability-audit`, `documentation-validation`
