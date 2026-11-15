# Discovery & Technical Consistency Register: DOCS-003

| Metadata | Value |
|---|---|
| **Work Item ID** | `DOCS-003` |
| **Discovery Date** | `2026-11-15` |
| **Auditing Roles** | `Lead Documentation Architect`, `System Architect`, `Data Platform Architect`, `Diagram Engineer` |
| **Repository Baseline** | Git Commit `f0329d3` on `main` |

---

## 1. Fact Classification Register (14 Historical Findings)

| Fact ID | Subject / Location | Observed Technical Fact (`AS-IS`) | Canonical Authority (`TARGET`) | Classification | Status |
|---|---|---|---|---|---|
| `FACT-01` | `docs/README.md` Line 25 | Contained broken relative link `[models/](../../models/)` traversing above repo root. | Repository root `models/` accessible via `../models/`. | `FACT` | `REMEDIATED` |
| `FACT-02` | `docs/contracts/requirements-matrix.md` | Functional requirements `FR-01..10` were artificially mapped 1:1 to sequential component IDs `COMP-001..COMP-010`. | `models/architecture/components.yaml` defines true component IDs (`COMP-001` ws-collector, `COMP-006` backend-api, `COMP-009` DataPlatformV01Pipeline). | `FACT` | `REMEDIATED` |
| `FACT-03` | `docs/contracts/requirements-matrix.md` BR-002 | Referenced non-existent rate limiter module `src/ingestion/infrastructure/rate_limiter.py`. | Production code resides at `src/ingestion/application/rate_limiter.py`. | `FACT` | `REMEDIATED` |
| `FACT-04` | `docs/contracts/api-contracts.md` Section 3 | Exemplar JSON used pseudo-fields `source_provider`, `occurred_at`, `MARKET_KLINE`, and string `event_id`. | `src/shared/contracts/events/market_events.py` defines `EventEnvelopeV1` with `provider`, `exchange_event_time`, `event_type`, and UUIDv5 `event_id`. | `FACT` | `REMEDIATED` |
| `FACT-05` | `docs/diagrams/data-platform/06-event-streaming.md` | Diagram labeled `market.raw.tickers.v1` as `Compact+Delete`, and included consumer group `cg.agent.anomaly.v1` unlisted in `topics.yaml`. | `models/data-platform/topics.yaml` specifies `cleanup_policy: delete`. Added `cg.agent.anomaly.v1` to `topics.yaml` for complete alignment. | `FACT` | `REMEDIATED` |
| `FACT-06` | `docs/diagrams/data-platform/08-end-to-end-data-platform-v01-pipeline.md` | Flowchart displayed Stage 8 (Data Quality Gates) preceding Stage 7 (Gold Analytical Marts) without narrative explanation. | `src/lakehouse/orchestration/pipeline.py` enforces Stage 8 before Stage 7 because Gold promotion is strictly gated by DQ results (`can_promote_to_gold`). | `FACT` | `REMEDIATED` |
| `FACT-07` | `docs/operations/deployment-guide.md` Table 1 | Listed `reverse-proxy` instead of `edge-gateway`, port 3001 for Grafana instead of 3000, and omitted backend worker containers (`collector-ws`, etc.). | `docker-compose.yml` defines service `edge-gateway` (80/443), `frontend` (3001:3000), `grafana` (3000), and 4 core worker services. | `FACT` | `REMEDIATED` |
| `FACT-08` | `docs/architecture/README.md` | Listed architecture documents `00..13` and `ADR-001..006`, omitting doc `14` and `ADR-007..008`. | Repository contains `14-data-platform-v01-and-microservices-architecture.md` and `ADR-007`, `ADR-008`. | `FACT` | `REMEDIATED` |
| `FACT-09` | `.agents/config/document-map.yaml` | Metadata timestamp was frozen at `2026-11-12`. | Updated to active date `2026-11-15`. | `FACT` | `REMEDIATED` |
| `FACT-10` | `work-items/DOCS-002-documentation-architecture-reorganization/target-documentation-tree.md` | Contained 5 Windows-specific absolute hyperlinks (`file:///c:/...`). | Replaced with repository-relative markdown paths (`../../docs/...`). | `FACT` | `REMEDIATED` |
| `FACT-11` | `models/architecture/components.yaml` | COMP-001 through COMP-017 comprehensively cover Ingestion, Streaming, Lakehouse, Serving, Intelligence, Microservices, and Frontend. | Synchronized across all architecture and contract documents. | `FACT` | `VERIFIED` |
| `FACT-12` | `models/data-platform/topics.yaml` | 6 Kafka topics (`trades.v1`, `klines.v1`, `tickers.v1`, `orderbook.v1`, `anomalies.v1`, `dlq.v1`) and 5 consumer groups. | Aligned with `src/streaming/contracts/topics.py` and Diagram 06. | `FACT` | `VERIFIED` |
| `FACT-13` | `docs/specifications/` Status | Preserved Phase 0 baseline specifications remain authoritative for requirements `FR-01..10`, NFRs, and entity schemas. | Cross-linked from `docs/contracts/` and `docs/overview/`. | `FACT` | `VERIFIED` |
| `FACT-14` | `docs/archive/` Role | Preserves superseded architecture evolution without masquerading as active documentation. | Clearly tagged `SUPERSEDED` / `ARCHIVED` with cross-references to active ADRs. | `FACT` | `VERIFIED` |

---

## 2. Decision Register

- `DECISION-001`: Preserve all existing Document IDs, ADR IDs, Requirement IDs, and Diagram IDs without renumbering to avoid breaking external and cross-work-item references.
- `DECISION-002`: Reconcile Diagram 08 and `pipeline.py` by retaining the execution dependency order (Stage 8 before Stage 7) and adding an architectural narrative explaining the pre-promotion data quality gate.
- `DECISION-003`: Synchronize `models/data-platform/topics.yaml` to include `cg.agent.anomaly.v1`, unifying the model with Diagram 06 and `src/intelligence/`.
