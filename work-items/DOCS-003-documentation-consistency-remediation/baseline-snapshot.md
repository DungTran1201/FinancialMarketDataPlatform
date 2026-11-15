# Baseline Snapshot: DOCS-003

| Metadata | Value |
|---|---|
| **Work Item ID** | `DOCS-003` |
| **Snapshot Date** | `2026-11-15` |
| **Git Commit** | `f0329d3` on branch `main` |
| **Dedicated Branch** | `docs/DOCS-003-consistency-remediation` |

---

## 1. Repository Inventory Baseline

- **Total Managed Markdown Files**: 357 files across `docs/`, `work-items/`, `.agents/`.
- **Total Canonical YAML Models**: 38 model files across 12 categories in `models/`.
- **Total Technical Diagrams**: 34 Mermaid diagram files across 6 domains in `docs/diagrams/`.
- **Total Architecture Decision Records (ADRs)**: 8 approved ADRs (`ADR-001` through `ADR-008`) in `docs/architecture/adr/`.
- **Total Architecture Documents**: 15 baselined architecture documents (`00` through `14`) in `docs/architecture/`.
- **Total Functional Requirements**: 10 baselined requirements (`FR-01` through `FR-10`) in `models/requirements/requirements.yaml`.
- **Total Acceptance Criteria**: 4 baselined criteria (`AC-001` through `AC-004`) in `models/requirements/acceptance-criteria.yaml`.
- **Total Test Cases**: 15 baselined test cases (`TC-001` through `TC-015`) in `models/testing/testing.yaml`.
- **Total Architectural Components**: 17 components (`COMP-001` through `COMP-017`) in `models/architecture/components.yaml`.
- **Total Kafka Topics**: 6 canonical topics in `models/data-platform/topics.yaml`.
- **Total Consumer Groups**: 4 registered consumer groups in baseline (`topics.yaml`), 1 additional group (`cg.agent.anomaly.v1`) identified for registration.
- **Docker Compose Services**: 24 containerized services across profiles `core`, `microservices`, `lakehouse`, `intelligence`, `observability`, `bi`, and `frontend`.

---

## 2. Pre-Remediation Discrepancies Inventory

1. `docs/README.md`: Broken root path traversal `../../models/` at line 25.
2. `docs/contracts/requirements-matrix.md`: Fictional 1:1 sequential mapping `FR-01..10` to `COMP-001..COMP-010`.
3. `docs/contracts/requirements-matrix.md`: Invalid rate-limiter path `src/ingestion/infrastructure/rate_limiter.py`.
4. `docs/contracts/api-contracts.md`: Non-canonical JSON envelope schema diverging from `EventEnvelopeV1`.
5. `docs/diagrams/data-platform/06-event-streaming.md`: Discrepancy on ticker topic cleanup policy and unlisted consumer group.
6. `docs/diagrams/data-platform/08-end-to-end-data-platform-v01-pipeline.md`: Missing architectural narrative explaining Stage 8 preceding Stage 7.
7. `docs/operations/deployment-guide.md`: Container name `reverse-proxy` instead of `edge-gateway`, port 3001 Grafana, missing worker containers.
8. `docs/architecture/README.md`: Missing doc 14 and ADR-007..008 in table of contents and scope sections.
9. `.agents/config/document-map.yaml`: Stale metadata date `2026-11-12`.
10. `work-items/DOCS-002-.../target-documentation-tree.md`: Windows absolute `file:///c:/...` hyperlinks.
