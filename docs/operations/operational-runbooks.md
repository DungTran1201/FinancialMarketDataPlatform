# SRE Operational Runbooks

| Metadata | Value |
|---|---|
| **Document ID** | `DOC-OPS-RUNBOOKS` |
| **Title** | Standard SRE Incident Response Runbooks |
| **Category** | Operations & Reliability |
| **Status** | `APPROVED` |
| **Updated Date** | `2026-11-15` |
| **Authoring Role** | `dataops-engineer` |

---

## Runbook 1: Kafka Consumer Lag Spike (`RB-001`)

- **Alert**: `FMDPConsumerLagHigh` (`alerts.yml`: `fmdp_consumer_lag_records > 5000` for `2m`, severity `critical`). *(Related alert: `FMDPDeadLetterQueueSpike`: `increase(fmdp_dlq_events_total[5m]) > 10` for `1m`.)*
- **Severity**: P2 (High).
- **Potential Causes**:
  - High burst traffic during market volatility spikes.
  - Slow database writes in ClickHouse or local/MinIO disk write stalls.
  - Consumer process crash or pause.

### Diagnostic Steps:
1. Inspect Prometheus lag metric (or gateway `/metrics`):
   ```powershell
   Invoke-RestMethod "http://localhost:9090/api/v1/query?query=fmdp_consumer_lag_records"
   # Or inspect runtime telemetry directly from backend-api:
   Invoke-RestMethod "http://localhost:8000/api/v1/observability/kafka"
   ```
2. Inspect consumer logs (`--profile microservices` or `core`):
   ```powershell
   docker compose logs -n 100 consumer-analytics-ch
   docker compose logs -n 100 svc-data-plane-v01
   ```
3. Inspect ClickHouse merge pressure:
   ```powershell
   docker exec fmdp-clickhouse clickhouse-client --query "SELECT count() FROM system.merges"
   ```

### Resolution Steps:
- If a consumer container is stuck, restart it:
  ```powershell
  docker compose restart consumer-analytics-ch
  ```
- For local v0.1 silver Parquet small-file bloat, trigger Stage 9 compaction via `POST http://localhost:8000/api/v1/data-platform/v01/compaction` during low load.

---

## Runbook 2: Exchange Rate Limit Throttling (`RB-002`)

- **Alert**: Log warning / HTTP `429` or `418` received from Binance REST API *(no dedicated Prometheus alert rule defined yet; `PLANNED`)*.
- **Severity**: P1 (Critical).
- **Symptoms**: Retry backoff triggers in `ProductionExchangeHistoricalCollector`; watermark progression slows or pauses.

### Diagnostic Steps:
1. Check ingestion/backend logs for HTTP `429` responses:
   ```powershell
   docker compose logs -n 50 backend-api | Select-String "429"
   ```
2. Check current persisted watermarks:
   ```powershell
   Invoke-RestMethod "http://localhost:8000/api/v1/data-platform/v01/watermarks"
   ```

### Resolution Steps:
- `TokenBucketRateLimiter` (`src/shared/` / `src/ingestion/`) enforces the conservative `<= 80%` rate-limit ceiling (`<= 960` weight/min) and honors `Retry-After`.
- Wait for the cooldown window before issuing new backfill requests. *(Note: No `/api/v1/historical/backfill/pause` HTTP endpoint exists in the current runtime.)*

---

## Runbook 3: Missing Interval Gap Healing (`RB-003`)

- **Symptom**: Stream sequence gap flagged by `SequenceAndGapDetector` (in-process engine; note standalone `collector-ws` CLI is a startup stub per `PROP-APP-002`).
- **Automatic Behavior**: When running via `DataPlatformV01Pipeline`, `SequenceAndGapDetector` and `HistoricalRestBackfillWorker` detect and heal kline gaps.
- **Manual Trigger (`API-006`)**:
  ```powershell
  curl.exe -X POST http://localhost:8000/api/v1/historical/backfill-jobs `
    -H "Content-Type: application/json" `
    -d '{"symbol": "BTCUSDT", "provider": "binance", "interval": "1m", "candle_count": 10}'
  ```

