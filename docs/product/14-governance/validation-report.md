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
| **Updated Date** | `2026-11-15` |
| **Work Item Reference** | `work-items/DOCS-001-documentation-engineering-foundation/` (extended by `work-items/DOCS-004-full-documentation-remediation/`) |

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

---

## 2. `DOCS-004` Upgraded Semantic & Parity Validation Results (`2026-11-15`)

Under `work-items/DOCS-004-full-documentation-remediation/`, all validators in `tools/validators/` were upgraded with semantic parity and integrity checks, covered by isolated negative tests (`TC-017` in `tests/unit/test_documentation_validators.py`):

| Check | Command Executed | Scope Verified | Result |
|---|---|---|---|
| Documentation Suite | `.\.venv\Scripts\python.exe tools/validators/run_all.py` | `10/10` scripts: `19` roles, `22` rules, `25` skills, `8` change types, `120` managed README directories, `57` templates, `38` YAML models (incl. `data-platform`), `21` ID namespaces (`ADR-001..008`, `DIAG-COMP`), `34` diagrams (`22` active + label quoting & `DIAG-*` uniqueness), all Markdown files (relative links & active backticked path resolution), traceability + FastAPI `55` routes / `5` `EventType`s / `6` Kafka topics / `docker-compose.yml` port collision / `prometheus.yml` parity, and `9` work items | `PASS` (`0` errors) |
| Python Full Suite (`TC-001..017`) | `.\.venv\Scripts\pytest.exe tests -v` | All `58` tests across architecture, contract, data quality, e2e, integration, performance, resilience, and unit suites (including `8` test methods / subtests in `TC-017`) | `PASS` (`58 passed`, `0` failed) |
| Standard Unittest Suite | `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` | Discovery parity across `tests/` | `PASS` (`55` tests `OK`) |
| Static Lint | `.\.venv\Scripts\ruff.exe check src tests tools` | Code style & import hygiene across `src/`, `tests/`, and `tools/` | `PASS` (`0` errors) |
| Frontend JS Tests & Build | `npm test --prefix frontend` & `npm run build --prefix frontend` | `node --test tests/**/*.test.js` (`3` passed) and `tsc && vite build` (`34` modules) | `PASS` |
| Compose All-Profile Config | `docker compose --profile core --profile lakehouse --profile intelligence --profile observability --profile bi --profile microservices --profile frontend config --quiet` | Cross-profile YAML & port resolution (`minio` host port `9010` vs `clickhouse` `9000`) | `PASS` |
| Live Container Startup & Load | `docker compose --profile core up -d` (`NFR-001`, `NFR-002`) | Multi-container runtime and production latency benchmarks | `NOT_RUN` |
