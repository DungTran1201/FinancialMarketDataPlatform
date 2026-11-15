# Sequenced Implementation Plan — `DOCS-004`

Execution follows the 12-Step Model-Driven Protocol (`AGENTS.md`):
1. **Workstream Setup (`G0 -> G3`)**: Capture `baseline-snapshot.md`, `canonical-source-register.yaml`, `document-inventory.csv`, and `discovery.md`.
2. **Governance & Canonical Models (`models/` + `.agents/config/`)**: Update `.agents/config/{identifier-registry,document-map,artifact-matrix}.yaml` and all canonical YAML models (`models/api/`, `models/architecture/`, `models/data-platform/`, `models/deployment/`, `models/requirements/`, `models/testing/`, `models/security/`, `models/ux/`, `models/process/`, `models/domain/`) first.
3. **Configuration Defect Fix (`docker-compose.yml` & `.env.example`)**: Apply minimal host port conflict fix (`MINIO_API_PORT:-9010`), clean misleading `lakehouse` comment, align `.env.example`, and test `docker compose --profile ... config`.
4. **Prose Reconciliation (Workstreams A–D)**: Update `README.md`, `docs/README.md`, `docs/overview/`, `docs/architecture/{00..14,adr/*}`, `docs/specifications/`, `docs/contracts/`, `docs/operations/`, `docs/development/`, `docs/archive/`, `docs/product/**`, `docs/templates/**`, `docs/features/`, and `.agents/` skills/agents/rules to eliminate broken references and clearly tag `IMPLEMENTED` vs `PARTIALLY_IMPLEMENTED` vs `PLANNED`.
5. **Derived Diagram Synchronization (`docs/diagrams/**`)**: Update all active diagrams (`01..19`, `ux/01`) and `docs/diagrams/README.md` to reflect updated `models/`.
6. **Historical Work-Item Addenda (`DOCS-002`, `DOCS-003`)**: Add factual correction addenda and fix `DOCS-003/remediation-matrix.md` formatting while preserving history.
7. **Automated Semantic Validators & Negative Tests (`tools/validators/`, `tests/unit/test_documentation_validators.py`)**: Add semantic checks for FastAPI route parity, EventEnvelope/Kafka topic/CG parity, Compose port/profile parity, diagram consistency, and broken internal path refs, plus `tmp_path`-isolated negative tests.
8. **Full Verification & Acceptance Package (`G4 -> G6`)**: Re-run every validator, Python pytest suite, ruff lint, frontend test/build, and Compose config check; publish `remediation-matrix.{csv,md}`, `traceability-matrix.csv`, `documentation-consolidation-matrix.csv`, `final-acceptance.yaml`, and `final-acceptance-report.md`.

