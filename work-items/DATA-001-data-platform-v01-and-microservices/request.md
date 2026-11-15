# Work Item Request — `DATA-001`: Zero-Mock Data Platform v0.1 & Microservices Transition

## 1. Request Summary

On branch `arch/microservices`, analyze existing Data Platform documentation, diagrams, and codebase; eliminate all Data Plane mocks; author supplementary Data Platform documentation and diagrams; build the complete 12-stage End-to-End Data Platform v0.1; and transition the runtime architecture from Modular Monolith to Domain Microservices (`ADR-007`).

## 2. Objectives

1. Replace `SimulatedExchangeHistoricalCollector` with `ProductionExchangeHistoricalCollector` (`httpx.AsyncClient` + `TokenBucketRateLimiter` + `SequenceAndGapDetector` + Stage 1 `exchangeInfo` discovery).
2. Build executable engines for Stage 2 (`WebSocketStreamCollector`, `HistoricalRestBackfillWorker`, `IngestionWatermarkStore`), Stage 7 (`GoldLayerMartEngine`), Stage 9 (`compact_and_snapshot_iceberg_table`), Stage 11 (`DataObservabilityMetricsCollector`), and Stage 12 (`DataLineageGovernanceRegistry`).
3. Orchestrate all 12 stages in `DataPlatformV01Pipeline` (`src/processing/pipeline_v01.py`).
4. Decompose runtime into 8 domain microservices in `src/microservices/` while maintaining Clean Architecture boundaries (`TC-006`) and gateway compatibility (`svc-api-gateway`).

