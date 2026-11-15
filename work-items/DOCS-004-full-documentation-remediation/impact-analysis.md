# Cross-Subsystem Impact & Remediation Risk Analysis — `DOCS-004`

## 1. Impact Across Documentation & Governance Layers

| Workstream | Subsystem Scope | Defect Classes Addressed | Risk Mitigation |
|---|---|---|---|
| **A — DOCS-003 Completion** | `models/`, `docs/specifications/`, `docs/contracts/`, `tests/`, `.agents/config/identifier-registry.yaml` | Stale routes, payload schemas, Kafka topics/CGs, DQ/security primitives, missing test-to-TC mappings | Canonical models updated first; automated parity checks added to `tools/validators/` |
| **B — Architecture Reconciliation** | `docs/architecture/{00..14,adr/*}`, `models/architecture/`, `docs/overview/`, `docs/diagrams/` | Implemented vs planned conflation, 5 vs 6 LangGraph nodes, in-process vs distributed containers, `svc-*` gaps | Preserve `ADR-001..008` history while annotating runtime `AS-IS` vs `TARGET` explicitly |
| **C — Operations Verification** | `docker-compose.yml`, `.env.example`, `docs/operations/*`, `docs/development/*`, `models/deployment/` | ClickHouse vs MinIO host port `9000` collision, wrong `/health` & Grafana/frontend ports, fake Prometheus metrics/alerts, missing Compose env vars | Minimal port `9010` override for MinIO host port only; regression-test `docker compose config` across all profiles |
| **D — Governance & Consolidation** | `docs/product/14-governance/`, `docs/templates/`, `docs/product/*/README.md`, `docs/features/`, `docs/archive/`, `docs/README.md`, `README.md`, `.agents/`, `work-items/{DOCS-002,DOCS-003}` | Conflicting destination/template rules, stale counts (`11` vs `19` roles, `16` vs `22` diagrams), 18 broken path refs, `DOCS-002`/`DOCS-003` unverified sign-off claims | Preserve predecessor work items cleanly via non-destructive correction addenda; fix all broken refs; add validator negative tests |

## 2. Backward Compatibility & Identifier Impact

- Zero existing identifiers (`FR-01..10`, `ADR-001..008`, `COMP-*`, `DOM-*`, `API-*`, `TC-*`, `DIAG-*`, `DOCS-001..003`, `DATA-001`, `ARCH-001`, `FEAT-001..002`) are renumbered or deleted.
- New API contracts (`API-023+`) and test cases (`TC-016+` / `TC-*` alignments) extend `.agents/config/identifier-registry.yaml` and `models/` monotonically without breaking existing IDs.

