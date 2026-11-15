# Source Code (`src/`) — Event-Driven Modular Data Platform

`src/` organizes all runtime code by **architectural plane and domain boundary** rather than by technical file type (`ADR-008`).

## Subsystem Boundaries & Dependency DAG

```text
shared/  <── zero upward dependencies; only cross-cutting primitives, config, contracts, metrics & security
   ▲
   ├── ingestion/     (External WS/REST collectors, rate limits, watermarks, Binance provider)
   ├── streaming/     (Kafka broker adapter, consumer contracts, hot Redis & ClickHouse stream sinks, anomaly detector)
   ├── lakehouse/     (Bronze Parquet archiver, Silver merge & Iceberg compaction, Gold marts + dbt, DQ gates, catalog)
   ├── serving/       (Modular Monolith FastAPI modules, Unified Gateway, Observatory UI, split ASGI services, DI runtime)
   └── intelligence/  (LangGraph orchestrator, workflows, Controlled Tool Gateway, provenance report validator)
```

## Non-Negotiable Architecture Rules (`tests/architecture/test_clean_architecture_boundaries.py`)

1. Core logic across `ingestion/`, `streaming/`, `lakehouse/{bronze,silver,gold,quality,catalog}/`, `serving/api/`, and `intelligence/` **MUST NEVER** import directly from each other.
2. Pure `domain/` layers (`shared/domain/`, `ingestion/domain/`, `serving/api/modules/*/domain/`) must import zero web, database, streaming, or agent frameworks.
3. Only explicit **composition roots** wire concrete implementations across subsystems:
   - `src/lakehouse/orchestration/pipeline.py` (`DataPlatformV01Pipeline` — 12-stage end-to-end Data Plane runner)
   - `src/serving/infrastructure/runtime.py` (`PlatformRuntimeContainer` — Serving DI container)
4. `src/shared/` holds strictly shared config, versioned contracts, math/domain primitives, OpenMetrics collectors, and edge cryptographic/WAF primitives — never bounded-context business logic.

