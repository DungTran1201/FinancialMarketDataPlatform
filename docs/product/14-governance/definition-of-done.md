# Documentation & Engineering Definition of Done (`GOV-DOD-001`)

| Document Metadata | Value |
|---|---|
| **Document ID** | `GOV-DOD-001` |
| **Title** | Framework & Work Item Definition of Done (DoD) |
| **Version** | `1.0.0` |
| **Status** | `BASELINED` |
| **Authoring Role** | `documentation-auditor` |
| **Review Role** | `documentation-architect` |
| **Created Date** | `2026-11-12` |
| **Updated Date** | `2026-11-12` |
| **Work Item Reference** | `work-items/DOCS-001-documentation-engineering-foundation/` |

---

## 1. Mandatory Definition of Done Checklist

A work item or documentation change in `FinancialMarketDataPlatform` is considered **DONE** only when all of the following conditions are verified:

1. **README-First Navigation**: Target directory `README.md` contracts were consulted and every newly created managed directory has a valid 12-section `README.md`.
2. **Work Item Control**: A work item folder in `work-items/<ID>/` contains all 9 required lifecycle files (`request.md`, `discovery.md`, `impact-analysis.md`, `artifact-plan.yaml`, `implementation-plan.md`, `verification-plan.md`, `review.md`, `state.yaml`, `README.md`).
3. **Fact Classification Hygiene**: Facts (`FACT`), assumptions (`[ASSUMPTION — REQUIRES VALIDATION]`), decisions (`DECISION`), and open questions (`[OPEN QUESTION]`) are explicitly separated; no unverified assumption is marked `APPROVED`.
4. **Canonical Model Synchronization**: Applicable structured YAML models in `models/` are updated with valid registered identifiers (`identifier-registry.yaml`).
5. **Template & Diagram Conformance**: Human-readable docs are instantiated from `docs/templates/` and derived diagrams in `docs/diagrams/` match upstream models.
6. **Zero Validator or Test Errors**:
   - `.\.venv\Scripts\python.exe tools/validators/run_all.py` exits with code `0`.
   - `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` exits with code `0`.
