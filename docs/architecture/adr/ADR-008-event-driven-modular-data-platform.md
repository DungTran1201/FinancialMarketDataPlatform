# Architecture Decision Record (ADR) — `ADR-008`

| Document Metadata | Value |
|---|---|
| **Document ID** | `ADR-008` |
| **Title** | Event-Driven Modular Data Platform Architecture & Sub-Plane Isolation |
| **Version** | `1.0.0` |
| **Status** | `APPROVED` (`BASELINED`) |
| **Authoring Role** | `data-platform-architect` |
| **Review Role** | `documentation-architect` |
| **Created Date** | `2026-11-15` |
| **Updated Date** | `2026-11-15` |
| **Work Item Reference** | `work-items/ARCH-001-event-driven-modular-restructure/` |
| **Canonical Model Reference** | `models/architecture/architecture.yaml` |
| **Source References** | `docs/architecture/00-architecture-overview.md`, `docs/architecture/14-data-platform-v01-and-microservices-architecture.md`, `docs/diagrams/architecture/19-event-driven-modular-platform-layers.md`, `src/README.md` |

---

## 1. Purpose `[MANDATORY]`

Records the structural reorganization of `FinancialMarketDataPlatform` (`src/`, `deploy/`, `models/`, `tests/`) into an **Event-Driven Modular Data Platform** enforcing explicit bounded responsibilities across `shared`, `ingestion`, `streaming`, `lakehouse`, `serving`, and `intelligence`.

---

## 2. Scope & Boundaries `[MANDATORY]`

Applies to all Python packages under `src/`, infrastructure manifests under `deploy/`, canonical Data Platform models under `models/data-platform/`, verification suites under `tests/`, and synchronized architecture documentation (`docs/`).

---

## 3. Context & Problem Statement `[MANDATORY]`

- **Context**: Following `DATA-001` (`ADR-007`), `src/` mixed architectural boundaries and concerns: `src/collectors/publisher.py` combined exchange ingestion (`TokenBucketRateLimiter`, `ProductionExchangeHistoricalCollector`) with Kafka streaming infrastructure (`PartitionedEventStreamingBroker`); `src/quality/lineage_and_observability.py` combined cross-plane Prometheus metrics with Lakehouse catalog lineage; `src/backend/modules/analytics/presentation/router.py` imported quantitative math directly from `src/agent/tools/gateway.py` (Plane B -> Plane C coupling); and `tests/unit/` held contract, integration, end-to-end, security, and performance suites in one directory.
- **Problem Statement**: Restructure source code, deployment assets, canonical Data Platform models, and test suites cleanly by **business responsibility and architectural boundary** without altering runtime behavior, duplicating compatibility shims, or fragmenting the API Modular Monolith unnecessarily.

---

## 4. Selected Option & Decision Rationale `[MANDATORY]`

- **Selected Option**: Reorganize `src/` into six top-level modular subsystems (`shared/`, `ingestion/`, `streaming/`, `lakehouse/`, `serving/`, `intelligence/`) with AST-verified DAG isolation (`TC-006`), formalize `models/data-platform/`, standardize `deploy/`, and align `tests/` by verification discipline.
- **Rationale**:
  1. Extracting `src/shared/domain/quant.py` and `src/shared/security/primitives.py` removes Plane B -> Plane C and Gateway -> IAM domain coupling cleanly without bloating `shared/`.
  2. Splitting `src/collectors/publisher.py` separates exchange ingestion (`src/ingestion/`) behind `EventPublisherPort` from Kafka broker infrastructure (`src/streaming/infrastructure/kafka_broker.py`).
  3. Keeping core bounded contexts under `src/serving/api/modules/` preserves Modular Monolith simplicity for `--profile core`, while placing optional thin ASGI entrypoints in `src/serving/api/services/` preserves `--profile microservices` (`DEP-006`) without code duplication.
  4. Retaining `deploy/nginx/` and `deploy/tls/` alongside `deploy/{docker,kafka,postgres,clickhouse,object-storage,iceberg,observability}/` preserves `ZONE-2` edge TLS separation.

---

## 5. Alternative Options Considered `[MANDATORY]`

1. **Maintain legacy `src/collectors`, `src/consumers`, `src/processing`, `src/backend`, `src/agent` with re-export shims** — *Rejection Reason*: Re-export shims create dual import paths, obscure ownership, and violate zero-duplication governance constraints.
2. **Dissolve the Modular Monolith into 8 independent database-per-service repositories** — *Rejection Reason*: Premature operational complexity; `src/serving/api/modules/*` plus optional `src/serving/api/services/*` deployment wrappers preserve both development velocity and container scaling.

---

## 6. Benefits, Drawbacks & Architectural Limitations `[MANDATORY]`

- **Benefits**: Zero direct imports between `ingestion`, `streaming`, `lakehouse/{bronze,silver,gold,quality,catalog}`, `serving/api`, and `intelligence`; clean 1:1 alignment between codebase modules and `models/data-platform/*`; isolated discipline-specific test suites (`unit`, `contract`, `data_quality`, `integration`, `e2e`, `resilience`, `performance`).
- **Drawbacks**: Requires updating historical path documentation (`DATA-001`, `.agents/` skills, CI/batch scripts) and maintaining composition wiring cleanly inside `src/lakehouse/orchestration/pipeline.py` and `src/serving/infrastructure/runtime.py`.
- **Architectural Limitations**: Only the two designated composition roots may import across multiple subsystems; new developers/agents must strictly observe `tests/architecture/test_clean_architecture_boundaries.py`.

---

## 7. Operational Implications, Consequences & Invalidation Conditions `[MANDATORY]`

- **Operational Implications**: Container CMDs in `docker-compose.yml`, `run.bat`, and `setup.bat` point to `src.serving.api.main:app`, `src.ingestion.entrypoints.*`, `src.streaming.consumers.*`, `src.lakehouse.bronze.consumer`, `src.intelligence.main`, `src.serving.api.services.*`, and `src/lakehouse/gold/dbt`.
- **Consequences**: `tools/validators/run_all.py` enforces 12-section `README.md` and valid metadata schemas across the new `models/data-platform/` category.
- **Conditions That Could Invalidate This Decision**: Physical repository extraction of a bounded context into an independently released Python wheel or separate polyrepo microservice.

---

## 8. Assumptions `[MANDATORY]`

- **ASSUMP-01**: `[ASSUMPTION — REQUIRES VALIDATION]` External Kubernetes/Helm manifests (when introduced outside `docker-compose.yml`) will mount `deploy/observability/`, `deploy/kafka/`, and `deploy/iceberg/` directly.

---

## 9. Open Questions `[MANDATORY]`

- None open for `ARCH-001` baseline; runtime behavior verified end-to-end across all automated suites.

---

## 10. Dependencies `[MANDATORY]`

- **Upstream Dependencies**: `ADR-001` through `ADR-007`, `.agents/rules/data-platform-boundaries`, `work-items/ARCH-001-event-driven-modular-restructure/`.
- **Downstream Consumers**: All `src/`, `deploy/`, `models/data-platform/`, `tests/`, and CI workflows.

---

## 11. Bidirectional Traceability `[MANDATORY]`

| Upstream Artifact ID | Current Artifact ID | Downstream Artifact ID | Verification Reference |
|---|---|---|---|
| `ADR-001`..`ADR-007`, `DATA-001` | `ADR-008` | `COMP-001`..`COMP-016`, `DOM-001`..`DOM-008`, `MODEL-DP-001`..`006` | `TC-006`, `TC-011`, `TC-012`, `TC-013`, `TC-014` |

---

## 12. Approval & Baseline Sign-Off `[CONDITIONAL]`

| Reviewer Role | Reviewer Name / Agent | Review Decision | Date | Evidence / Notes |
|---|---|---|---|---|
| `documentation-architect` | `data-platform-architect` / `system-architect` | `APPROVED` (`BASELINED`) | `2026-11-15` | `pytest` (47 tests), `ruff`, `unittest discover`, `dbt parse`, and `run_all.py` passed. |
