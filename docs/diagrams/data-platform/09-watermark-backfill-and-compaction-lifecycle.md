# Diagram 09 — Watermark Backfill, Gap Detection & Iceberg Compaction Lifecycle (`DIAG-DATA-009`)

| Diagram Metadata | Value |
|---|---|
| **Diagram ID** | `DIAG-DATA-009` |
| **Title** | Watermark Backfill, Gap Detection & Iceberg Compaction Lifecycle |
| **Diagram Category** | `docs/diagrams/data-platform/` |
| **Notation / Mermaid Type** | `Mermaid (sequenceDiagram)` |
| **Status** | `IMPLEMENTED` |
| **Version** | `1.1.0` |
| **Authoritative Document Reference** | `docs/architecture/14-data-platform-v01-and-microservices-architecture.md` |
| **Canonical Model Reference** | `models/data-platform/retention.yaml`, `models/process/processes.yaml` |
| **Related Artifact IDs** | `FR-02`, `FR-03`, `BR-001`, `TC-003` |

## 1. Purpose

Illustrates the closed-loop sequence governing stream gap detection (`SequenceAndGapDetector`), rate-limited REST backfill (`TokenBucketRateLimiter`), durable SQLite WAL watermark progression (`IngestionWatermarkStore` in `src/ingestion/infrastructure/watermark_store.py`; PostgreSQL target in multi-host control plane), and Stage 9 Apache Iceberg v2 small-file compaction into `.local_lakehouse/`.

---

## 2. Mermaid Sequence Diagram (`DIAG-DATA-009`)

```mermaid
sequenceDiagram
    autonumber
    participant WS as WebSocketStreamCollector
    participant GAP as SequenceAndGapDetector
    participant WM as IngestionWatermarkStore (SQLite WAL)
    participant REST as HistoricalRestBackfillWorker
    participant EX as Exchange HTTP (/api/v3/klines)
    participant KFK as Kafka (market.raw.klines.v1)
    participant BRZ as BronzeParquetArchiver
    participant SLV as SilverLakehouseMergeEngine

    WS->>GAP: observe_kline(provider, symbol, interval, open_time)
    GAP-->>WS: DetectedStreamGap(gap_start, gap_end, missing_candles)
    WS->>WM: upsert_watermark(status="GAP_DETECTED")
    REST->>WM: upsert_watermark(status="BACKFILLING", last_open_time=gap_start)
    REST->>EX: GET /api/v3/klines?symbol=BTCUSDT&startTime=...&endTime=...
    EX-->>REST: 200 OK + X-MBX-USED-WEIGHT-1M Header + Kline Array
    REST->>REST: TokenBucketRateLimiter.record_request_weight()
    REST->>KFK: publish_event(EventEnvelopeV1)
    REST->>WM: upsert_watermark(status="SYNCED", last_open_time=final_open_time)
    KFK->>BRZ: poll_topic(cg.lakehouse.bronze.v1)
    BRZ->>BRZ: archive_batch() -> part_kline_*.parquet (ZSTD)
    BRZ->>SLV: merge_bronze_klines_to_silver()
    SLV->>SLV: compact_and_snapshot_iceberg_table() -> compacted_*.parquet + v{snapshot_id}.metadata.json
```

