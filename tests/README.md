# Automated Verification Suite (`tests/`)

Tests are structured strictly by verification discipline matching CI quality gates and [qa-and-testing-standards.md](../docs/governance/standards/qa-and-testing-standards.md).

## Test Categories

| Directory | Verification Scope | Reference IDs |
|---|---|---|
| `architecture/` | AST enforcement of Clean Architecture layer purity & inter-module DAG isolation (`src/` boundary rules) | `TC-006` |
| `docs/` | Documentation V2 schema, frontmatter, applicability matrix, link/anchor, diagram & traceability validator tests | `GOV-STD-QA-001` |
| `unit/` | Pure domain invariants (`InstrumentKey`, `DecimalPrice`, `BoundedTimeRange`), deterministic quant math, rate limiter, watermark store, & defense primitives | `TC-007`, `TC-008` |
| `contract/` | Event envelope UUIDv5 determinism, Kafka partition keys, topic/dataset contracts, hot/OLAP port contracts, Tool Gateway RBAC | `TC-001`..`TC-005`, `TC-014` |
| `data_quality/` | Blocking DQ rules (`DQ-KLINE-*`), Bronze->Silver natural-key merge idempotency, Stage 9 Iceberg compaction & Gold `Decimal` verification | `TC-012` |
| `integration/` | Independent Plane A / Plane B / Plane C & inter-plane hot-cache/fallback/investigation workflows | `TC-009` |
| `e2e/` | Zero-mock 12-stage End-to-End `DataPlatformV01Pipeline` execution + 8 ASGI microservice dispatch & gateway routing | `TC-011` |
| `resilience/` | WS sequence gap auto-healing via REST backfill, corrupt payload DLQ isolation, Redis monotonic drop, anomaly 15-min cooldown | `TC-013` |
| `performance/` | 100-bot (600 API operation) concurrent swarm latency SLA & Data Plane internal consistency audit | `TC-010` |

