# Ingestion Subsystem (`src/ingestion/`)

Owns **Stages 1–3** of the Data Platform lifecycle: exchange metadata discovery, WebSocket live collection, weight-governed REST historical backfill, sequence gap detection, watermark durability, and provider payload normalization.

## Layer Structure

| Directory | Responsibility | Dependency Rule |
|---|---|---|
| `domain/` | Value objects (`ExchangeSymbolMetadata`, `DetectedStreamGap`, `WatermarkRecord`) and hexagonal ports (`PayloadNormalizerPort`, `EventPublisherPort`, `HistoricalCollectorPort`, `WatermarkStorePort`) | Pure Python; zero IO/framework imports. |
| `application/` | `TokenBucketRateLimiter`, `SequenceAndGapDetector`, `WebSocketStreamCollector`, `HistoricalRestBackfillWorker` | Depends only on `ingestion.domain` and `shared`. |
| `providers/` | Isolated per-exchange adapters (`binance/normalizer.py`, `binance/rest_client.py`) terminating exchange-specific JSON schemas into `EventEnvelopeV1` or `DeadLetterEnvelopeV1` | Never leaks exchange wire formats outside `providers/`. |
| `infrastructure/` | Concrete watermark persistence adapter (`IngestionWatermarkStore` over SQLite WAL / PostgreSQL) | Implements `WatermarkStorePort`. |
| `entrypoints/` | Container worker CLI entrypoints (`ws_collector.py`, `rest_backfill.py`) | Composition entrypoints for `collector-ws` and `collector-rest`. |

