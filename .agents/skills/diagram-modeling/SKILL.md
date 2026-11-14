---
name: diagram-modeling
description: Generates and syncs derived Mermaid diagrams (DIAG-*) in docs/diagrams/.
---

# Skill: Technical Diagram Authoring & Synchronization (`SKILL-010`)

## 1. Description

Generates and synchronizes Mermaid diagrams (`DIAG-*`) in `docs/diagrams/` derived from canonical `models/` and authoritative `docs/`.

## 2. Trigger Conditions

- Any phase requiring creation or synchronization of `DIAG-*` Mermaid views (`architecture-modeler`, `process-modeler`, `domain-modeler`, `api-architect`, `ux-modeler`).

## 3. Authoritative Inputs

- Target category `docs/diagrams/<category>/README.md`, upstream `models/**/*.yaml`, authoritative `docs/`, `.agents/rules/diagrams.md`.

## 4. Preconditions

1. Target `docs/diagrams/<category>/README.md` read; upstream canonical model in `models/` updated first.

## 5. Execution Procedure

1. Allocate a valid `DIAG-<TYPE>-<NNN>` ID per `.agents/config/identifier-registry.yaml`.
2. Author the diagram markdown in `docs/diagrams/<category>/` with a fenced ```mermaid block, upstream model/doc references, and architectural explanation.
3. Quote all Mermaid node labels containing parentheses `()` or brackets `[]` (e.g., `id["Label (Detail)"]`).
4. Link the diagram from its governing specification in `docs/` and run `python tools/validators/run_all.py`.

## 6. Output Artifacts

- `docs/diagrams/<category>/*.md` synchronized with upstream models and specifications.

## 7. Validation

```powershell
python tools/validators/run_all.py
```

## 8. Failure Handling

- Fix any Mermaid syntax or missing-explanation error flagged by `validate_diagrams.py` before finishing.

## 9. Restrictions

- Diagrams are derived views only (`RULE-004`); never invent components, actors, or flows absent from `models/` and `docs/`.

## 10. Related Skills

- `architecture-modeling`, `process-modeling`, `domain-modeling`
