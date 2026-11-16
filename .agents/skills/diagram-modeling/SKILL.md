---
name: diagram-modeling
description: Generates and syncs scoped derived Mermaid diagrams under V2 overview, plane, and capability paths.
---

# Skill: Technical Diagram Authoring & Synchronization (`SKILL-010`)

## 1. Description

Generates and synchronizes derived Mermaid diagrams (`doc_type: diagram`, `is_authoritative: false`) inside `docs/overview/diagrams/`, `docs/<plane>/architecture/diagrams/`, and capability `design/`, `workflows/`, `security/`, and `data/` folders.

## 2. Trigger Conditions

- Any Documentation V2 task requiring creation or synchronization of derived architectural, workflow, sequence, state, ERD, DFD, threat, or agent-workflow diagrams (`architecture-modeler`, `process-modeler`, `domain-modeler`, `api-architect`, `ux-modeler`, `security-reviewer`).

## 3. Authoritative Inputs

- `docs/governance/standards/diagram-standards.md`, `docs/governance/templates/diagrams/`, `.agents/rules/diagrams.md`, and upstream authoritative specs/contracts/code.

## 4. Preconditions

1. Target owning directory and upstream authoritative spec/contract/code inspected.

## 5. Execution Procedure

1. Choose the appropriate diagram template in `docs/governance/templates/diagrams/` (`c4`, `bpmn`, `sequence`, `state-machine`, `erd`, `data-flow`, `deployment`, `threat-model`, `agent-workflow`).
2. Set `doc_type: diagram`, `source_of_truth.is_authoritative: false`, and list exact upstream `source_of_truth.authoritative_source` files.
3. Include mandatory `Diagram Metadata` and `Legend` sections, a valid Mermaid header, balanced `subgraph`/`end` blocks, and quoted labels containing parentheses/brackets (`id["Label (Detail)"]`).
4. Place the diagram adjacent to its owning scope (never in a detached `docs/diagrams/` directory), link it from the owning spec, and run `python scripts/docs/validate_docs.py`.

## 6. Output Artifacts

- Scoped derived diagram `.md` files under `docs/overview/diagrams/`, `docs/<plane>/architecture/diagrams/`, or capability `design/` / `workflows/` / `security/` / `data/`.

## 7. Validation

```powershell
python scripts/docs/validate_docs.py
python tools/validators/run_all.py
```

## 8. Failure Handling

- Fix any `VAL-DIAG-SOT-001`, `VAL-DIAG-META-001`, or `VAL-DIAG-MERMAID-001` error reported by `validate_docs.py` before finishing.

## 9. Restrictions

- Diagrams are derived views only (`RULE-004`); never invent components, endpoints, or flows absent from authoritative specs/code; never create `docs/diagrams/`.

## 10. Related Skills

- `architecture-modeling`, `process-modeling`, `domain-modeling`
