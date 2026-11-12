# Automated Documentation Validation Report (`GOV-VAL-001`)

| Document Metadata | Value |
|---|---|
| **Document ID** | `GOV-VAL-001` |
| **Title** | Documentation Engineering Framework Validation Report |
| **Version** | `1.0.0` |
| **Status** | `BASELINED` |
| **Authoring Role** | `documentation-auditor` |
| **Review Role** | `qa-reviewer` |
| **Created Date** | `2026-11-12` |
| **Updated Date** | `2026-11-12` |
| **Work Item Reference** | `work-items/DOCS-001-documentation-engineering-foundation/` |

---

## 1. Executed Validation Suite Summary

Command executed:
```powershell
.\.venv\Scripts\python.exe tools/validators/run_all.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

| Validator Script | Scope Verified | Errors | Result |
|---|---|---|---|
| `tools/validators/validate_agent_config.py` | `AGENTS.md`, 11 roles, 10 rules, 16 skills, `hooks.json`, skill registries | `0` | `PASS` |
| `tools/validators/validate_artifact_matrix.py` | `artifact-matrix.yaml`, `change-types.yaml`, `document-map.yaml` path resolution | `0` | `PASS` |
| `tools/validators/validate_readmes.py` | 100% README coverage & all 12 mandatory sections across all managed directories | `0` | `PASS` |
| `tools/validators/validate_templates.py` | 14 template categories, 57 `.template.md` files, metadata & placeholders | `0` | `PASS` |
| `tools/validators/validate_models.py` | 12 canonical model domains, 29 YAML files, metadata & source references | `0` | `PASS` |
| `tools/validators/validate_identifiers.py` | 21 identifier namespaces, regex patterns, preserved `FR-01..10` & `ADR-001..006` | `0` | `PASS` |
| `tools/validators/validate_diagrams.py` | 18 diagram categories, 28 diagram files, valid Mermaid syntax headers | `0` | `PASS` |
| `tools/validators/validate_docs.py` | Preserved 25 baseline files, H1 titles, no duplicate `/diagrams` root | `0` | `PASS` |
| `tools/validators/validate_traceability.py` | Bidirectional links across `FR`, `BR`, `AC`, `TC`, `THR`, `CTRL`, and `ADR` | `0` | `PASS` |
| `tools/validators/validate_work_items.py` | `_template` and `DOCS-001` 9-file completeness, state transitions & artifact plans | `0` | `PASS` |
| `tests/architecture/` & `tests/unit/` | 12 Clean Architecture boundary & contract unit tests | `0` | `PASS` |
