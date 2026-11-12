# Identifier Allocation & Preservation Rule (`RULE-006`)

| Metadata | Value |
|---|---|
| **Rule ID** | `RULE-006` |
| **Rule Slug** | `identifiers` |
| **Activation Mode** | `Always Active` |
| **Status** | `BASELINED` |
| **Updated Date** | `2026-11-12` |

---

## 1. Purpose & Scope

Enforces `.agents/config/identifier-registry.yaml` namespaces, preserves existing Data Platform IDs (`FR-01..10`, `ADR-001..006`), and prohibits renumbering approved artifacts.

## 2. Mandatory Directives

1. **README-First Compliance**: Always inspect the `README.md` of any target directory in `docs/`, `models/`, `work-items/`, `.agents/`, or `tools/` before creating or modifying files inside it.
2. **Registry Alignment**: Conform strictly to `.agents/config/document-map.yaml`, `.agents/config/artifact-matrix.yaml`, `.agents/config/identifier-registry.yaml`, and `.agents/config/status-lifecycle.yaml`.
3. **Evidence Preservation**: Distinguish `FACT`, `ASSUMPTION`, `DECISION`, and `OPEN QUESTION`. Never fabricate product requirements or operational metrics.
4. **Deterministic Verification**: Run `tools/validators/run_all.py` after modifying any governed artifact.

## 3. Prohibited Actions

- Never create parallel or duplicate documentation roots.
- Never overwrite or renumber existing baselined identifiers (`FR-01..10`, `ADR-001..006`).
- Never promote an artifact with `[TO BE COMPLETED]` placeholders to `APPROVED` or `BASELINED`.

## 4. Verification Mechanism

- Automated check via `tools/validators/run_all.py` and gate review in `work-items/<ID>/review.md`.
