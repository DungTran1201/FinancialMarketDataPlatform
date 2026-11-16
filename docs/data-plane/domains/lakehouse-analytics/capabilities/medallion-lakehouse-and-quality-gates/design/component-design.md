---
doc_id: CAP-DP-LAK-COMP-001
title: "Component Design: Medallion Engines & DataPlatformV01Pipeline"
doc_type: specification
plane: data-plane
scope_level: capability
domain: lakehouse-analytics
capability_id: CAP-DP-LAK-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: data-architect
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/lakehouse/orchestration/pipeline.py"
    - "src/lakehouse/silver/merge_engine.py"
    - "src/lakehouse/gold/mart_engine.py"
related_docs:
  - CAP-DP-LAK-SPEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Documented 12-stage orchestration composition root and float usage caveat inside volatility math."
---

# Component Design: Medallion Engines & DataPlatformV01Pipeline

## 1. 12-Stage Orchestrator Decomposition (`pipeline.py:100-874`) `[REQUIRED]`

- `DataPlatformV01Pipeline.run_end_to_end_pipeline()` wires `BinancePayloadNormalizer`, `PartitionedEventStreamingBroker`, `ProductionExchangeHistoricalCollector`, `HotStateProjector`, `ClickHouseBatchSink`, `BronzeParquetArchiver`, `SilverLakehouseMergeEngine`, `DataQualityGateEngine`, `GoldLayerMartEngine`, `IngestionWatermarkStore`, `DataObservabilityMetricsCollector`, `DataLineageGovernanceRegistry`, and `PipelineTraceRegistry`.
- `step_realtime_tick_and_collect_telemetry()` (`L627-870`) injects oscillating synthetic trade frames for live demo/test telemetry.

## 2. Precision & Timing Implementation Notes `[REQUIRED]`

- Gold realized volatility (`mart_engine.py:136-137`) uses `math.log(ratio)` via `float()` conversion before quantizing back to `Decimal`; summary & liquidity spread metrics execute strictly in `Decimal`.
- Stage 2 & 3 pipeline timings are split deterministically (`72%` ingestion / `28%` validation at `L229-230`).
