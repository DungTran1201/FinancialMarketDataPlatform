# Discovery Register — `DATA-001` (`arch/microservices`)

## 1. Verified Facts (`FACT`)

- `FACT-DATA-001`: Prior to `DATA-001`, `src/collectors/publisher.py` used `SimulatedExchangeHistoricalCollector` (an in-memory synthetic kline generator) and `src/collectors/main_ws.py` / `main_rest.py` only logged startup messages.
- `FACT-DATA-002`: Prior to `DATA-001`, Stages 1 (`exchangeInfo` discovery), 7 (Gold analytical mart materialization), 9 (Iceberg small-file compaction & snapshot metadata), 11 (Prometheus OpenMetrics exposition), and 12 (Governance lineage registry) had documentation specifications in `docs/architecture/04-data-platform-architecture.md` but lacked executable Python engines.
- `FACT-DATA-003`: `tests/architecture/test_clean_architecture_boundaries.py` (`TC-006`) strictly requires `src/backend/modules/` to contain the exact 8 bounded context directories (`market`, `historical`, `analytics`, `catalog`, `iam`, `platform_config`, `agent_api`, `reporting`).

## 2. Recorded Decisions (`DECISION`)

- `DEC-DATA-001` (`ADR-007`): Implement zero-mock Data Platform v0.1 (`src/processing/pipeline_v01.py`) and decompose runtime deployment into 8 standalone ASGI microservices under `src/microservices/` governed by `MicroserviceRegistry`.

