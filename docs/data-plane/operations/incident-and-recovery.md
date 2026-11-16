---
doc_id: DP-OPS-REC-001
title: "Data Plane Incident Response & Recovery Procedures"
doc_type: specification
plane: data-plane
scope_level: plane
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: devops-sre
accountable_role: devops-sre
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/ingestion/application/ws_service.py"
    - "src/lakehouse/silver/merge_engine.py"
    - "src/lakehouse/quality/gates.py"
related_docs:
  - DP-OPS-RB-001
  - DP-ARCH-RES-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Documented gap replay, DQ block containment, Iceberg snapshot rollback semantics, and OPEN RPO/RTO targets."
---

# Data Plane Incident Response & Recovery Procedures

## 1. Recovery Objectives & Open Decisions `[REQUIRED]`

| Metric | Target | Current Reality | Owner & Status |
|---|---|---|---|
| **RPO (Data Loss Tolerance)** | `OPEN` (Requires stakeholder approval) | In-process memory (`_topics`, `_trades_table`, `_klines_table`) is volatile across container restarts unless JSON state or live stores are used; Bronze `.local_lakehouse/` & SQLite watermarks persist on local disk. | `devops-sre` (`OPEN`) |
| **RTO (Recovery Time Objective)** | `OPEN` | No automated container failover or snapshot restore drills exist yet. | `devops-sre` (`OPEN`) |

## 2. Incident Playbooks `[REQUIRED]`

| Incident Scenario | Detection Signal | Containment & Recovery Steps | Verification Evidence |
|---|---|---|---|
| **WS Sequence Gap Detected** | Watermark status `GAP_DETECTED`; `SequenceAndGapDetector` emits `DetectedStreamGap` | `WebSocketStreamCollector` invokes `HistoricalRestBackfillWorker.execute_backfill()` across `[missing_from, missing_to]`, resets watermark to `SYNCED`, and deduplicates via natural key in downstream sinks. Manual equivalent: `POST /api/v1/historical/backfill-jobs`. | `tests/resilience/test_gap_recovery_and_dlq.py` |
| **DLQ Spike (`FMDPDeadLetterQueueSpike`)** | Prometheus alert `increase(fmdp_dlq_events_total[5m]) > 10` | Query `GET /api/v1/observability/traces?only_errors=true` or `broker.dlq_events`; identify upstream exchange schema break or corrupt sender (`error_type`/`error_message`); repair normalizer and replay sanitized payload. | `tests/e2e/test_data_platform_v01_e2e.py` |
| **Data Quality Gate Blocked Gold Promotion** | `can_promote_to_gold == false`; `DQ-KLINE-001..004` / `DQ-TRADE-001..003` errors | Silver rows remain quarantined from Gold marts automatically. Inspect `failed_rule_ids`, correct corrupt Bronze batch or re-backfill symbol window, re-run `POST /api/v1/catalog/lakehouse/pipeline`. | `tests/data_quality/test_medallion_quality_gates.py` |
| **Corrupt Silver Compaction / Metadata** | Corrupted post-compaction manifest | Because `merge_engine.py` preserves up to `max_snapshots_to_keep=5` `v{id}.metadata.json` files locally (and atomic `.tmp` writes prevent partial Parquet files), roll back `version-hint.text` to the prior snapshot ID or re-merge from Bronze `.local_lakehouse/bronze/`. | `tests/data_quality/test_medallion_quality_gates.py` |
