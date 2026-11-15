# Technical Consistency Audit: DOCS-003

| Metadata | Value |
|---|---|
| **Work Item ID** | `DOCS-003` |
| **Audit Date** | `2026-11-15` |
| **Auditing Roles** | `System Architect`, `Data Platform Architect` |
| **Scope** | Cross-Subsystem Alignment: Code (`src/`) vs Models (`models/`) vs Specs (`docs/`) vs Containers (`docker-compose.yml`) |

---

## 1. Data Ingestion & Rate Limiting Consistency
- **Finding**: `docs/contracts/requirements-matrix.md` referenced `src/ingestion/infrastructure/rate_limiter.py`.
- **Code Investigation**: Inspected filesystem. Discovered `TokenBucketRateLimiter` class is defined in `src/ingestion/application/rate_limiter.py`.
- **Resolution**: Updated `docs/contracts/requirements-matrix.md` rule `BR-002` enforcement point to `src/ingestion/application/rate_limiter.py`.

## 2. Event Envelope & Serialization Consistency
- **Finding**: `docs/contracts/api-contracts.md` exhibited an unversioned JSON example featuring obsolete keys (`source_provider`, `occurred_at`, `MARKET_KLINE`).
- **Code Investigation**: Inspected `src/shared/contracts/events/market_events.py` and `models/data-platform/events.yaml`. The production contract is `EventEnvelopeV1`:
  - `schema_version`: `"1.0.0"`
  - `event_id`: Deterministic UUIDv5 (`uuid.uuid5(NAMESPACE_FMDP, ...)`)
  - `provider`: `"binance"`
  - `symbol`: string
  - `event_type`: `EventType` enum (`"kline"`, `"trade"`, etc.)
  - `exchange_event_time`: ISO-8601 UTC timestamp
  - `ingested_at`: ISO-8601 UTC timestamp
  - `payload`: dictionary of exact financial metrics
  - `sequence_id`: integer or null
- **Resolution**: Replaced the exemplar payload in `docs/contracts/api-contracts.md` with a valid `EventEnvelopeV1` payload and documented `DeadLetterEnvelopeV1`.

## 3. Kafka Topic & Consumer Group Consistency
- **Finding**: Diagram 06 included consumer group `cg.agent.anomaly.v1` which was missing in `models/data-platform/topics.yaml`. Ticker topic was labeled `Compact+Delete` while model specified `delete`.
- **Code Investigation**: `src/streaming/contracts/topics.py` defines the canonical topics and consumer groups. In addition, `src/intelligence/` consumes anomaly events.
- **Resolution**: Registered `cg.agent.anomaly.v1` in `models/data-platform/topics.yaml` targeting `src/intelligence/main.py`. Updated Diagram 06 label to `6 Partitions (delete)`.

## 4. Lakehouse Orchestrator Execution Flow Consistency
- **Finding**: Diagram 08 illustrated Stage 8 (Data Quality Gates) preceding Stage 7 (Gold Analytical Marts) in the flowchart.
- **Code Investigation**: Inspected `src/lakehouse/orchestration/pipeline.py` method `run_end_to_end_pipeline()`.
  - Stage 6 executes Silver standardization (`merge_bronze_klines_to_silver`).
  - Stage 8 executes automated data quality gates (`validate_kline_dataset`, `validate_trade_dataset`).
  - Stage 7 executes Gold mart materialization **only if** `can_promote_to_gold=true`.
  - Stage 9 executes small-file compaction and Apache Iceberg v2 snapshot manifest generation.
- **Resolution**: Confirmed that Diagram 08 correctly reflects the runtime dataflow dependency. Enhanced Diagram 08 with an architectural explanatory note detailing why Stage 8 must gate Stage 7.

## 5. Deployment Topology & Container Consistency
- **Finding**: `docs/operations/deployment-guide.md` contained outdated service names (`reverse-proxy` instead of `edge-gateway`), incorrect Grafana port (3001 vs 3000), and lacked backend workers.
- **Code Investigation**: Audited `docker-compose.yml`. Found 24 services across `core`, `microservices`, `lakehouse`, `intelligence`, `observability`, `bi`, and `frontend` profiles.
- **Resolution**: Synchronized the deployment topology table in `docs/operations/deployment-guide.md` to reflect all 24 services, exact profile tags, host ports, and healthcheck endpoints.

## 6. Architecture Baseline Directory Completeness
- **Finding**: `docs/architecture/README.md` omitted doc 14 and ADR-007..008.
- **Code Investigation**: Files `14-data-platform-v01-and-microservices-architecture.md`, `ADR-007-microservices-and-data-platform-v01.md`, and `ADR-008-event-driven-modular-data-platform.md` exist and are baselined.
- **Resolution**: Updated `docs/architecture/README.md` across sections 1, 2, 5, 6, 7, 10, and 12.
