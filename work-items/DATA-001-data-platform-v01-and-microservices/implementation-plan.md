# Implementation Plan — `DATA-001`

## 1. Execution Sequence

1. **Stage 1**: Upgrade `src/collectors/publisher.py`, `src/collectors/main_ws.py`, and `src/collectors/main_rest.py` with zero-mock HTTP/ASGI protocol execution, `TokenBucketRateLimiter`, `SequenceAndGapDetector`, and SQLite `IngestionWatermarkStore`.
2. **Stage 2**: Upgrade `src/processing/spark/bronze_to_silver.py` (Silver trades merge + Stage 9 Iceberg v2 compaction) and create `src/processing/gold_marts.py` (Gold analytical marts), `src/quality/lineage_and_observability.py` (Prometheus SLIs + Governance Lineage), and `src/processing/pipeline_v01.py` (12-stage orchestrator).
3. **Stage 3**: Create domain microservices in `src/microservices/` (`svc-api-gateway`, `svc-market-hot`, `svc-historical-backfill`, `svc-analytics-quant`, `svc-catalog-governance`, `svc-iam-security`, `svc-intelligence-agent`, `svc-data-plane-v01`) and update `docker-compose.yml`.
4. **Stage 4**: Update canonical YAML models (`models/`), architecture docs (`ADR-007`, `14-data-platform-v01-and-microservices-architecture.md`), and Mermaid diagrams (`DIAG-DATA-008`, `DIAG-DATA-009`, `DIAG-C4-017`, `DIAG-DEP-018`).
5. **Stage 5**: Execute `TC-011` (`tests/unit/test_data_platform_v01_and_microservices.py`) and `tools/validators/run_all.py`.

