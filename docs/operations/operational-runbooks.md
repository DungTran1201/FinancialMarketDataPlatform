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

- **Alert**: `KafkaConsumerLagHigh` (`fmdp_consumer_lag_records > 5000` for `> 3m`).
- **Severity**: P2 (High).
- **Potential Causes**:
  - High burst traffic during market volatility spikes.
  - Slow database writes in ClickHouse or disk write stalls in MinIO.
  - Consumer process crash or GC pause.

### Diagnostic Steps:
1. Inspect Prometheus lag metric:
   ```powershell
   curl http://localhost:9090/api/v1/query?query=fmdp_consumer_lag_records
   ```
2. Inspect consumer logs:
   ```powershell
   docker compose logs -n 100 svc-data-plane-v01
   ```
3. Inspect storage layer health:
   ```powershell
   docker exec -it fmdp-clickhouse clickhouse-client --query "SELECT count() FROM system.merges"
   ```

### Resolution Steps:
- If a consumer is stuck, restart the consumer container:
  ```powershell
  docker compose restart svc-data-plane-v01
  ```
- If disk I/O is saturated, trigger compaction off-peak.

---

## Runbook 2: Exchange Rate Limit Throttling (`RB-002`)

- **Alert**: `ExchangeRateLimitWarning` (HTTP 429 received from Binance).
- **Severity**: P1 (Critical).
- **Symptoms**: `_request_with_retry` triggers exponential backoff; watermarks stop advancing.

### Diagnostic Steps:
1. Check ingestion logs for rate limiter headers:
   ```powershell
   docker compose logs -n 50 svc-market-hot | Select-String "429"
   ```
2. Verify weight counter: Ensure `X-MBX-USED-WEIGHT-1M` remains `< 960` (80% ceiling).

### Resolution Steps:
- The `TokenBucketRateLimiter` automatically sleeps for the duration indicated in `Retry-After`.
- If backfill jobs are consuming too much weight, pause historical backfills temporarily:
  ```powershell
  curl -X POST http://localhost:8000/api/v1/historical/backfill/pause
  ```

---

## Runbook 3: Missing Interval Gap Healing (`RB-003`)

- **Symptom**: `DetectedStreamGap` logged by `WebSocketStreamCollector`; watermark marked `GAP_DETECTED`.
- **Automatic Behavior**: The platform automatically invokes `HistoricalRestBackfillWorker.execute_backfill(...)` to fetch the missing kline range from REST endpoints and fill the lakehouse partition.
- **Manual Trigger** (if auto-healing fails):
  ```powershell
  curl -X POST http://localhost:8000/api/v1/historical/backfill \
    -H "Content-Type: application/json" \
    -d '{"symbol": "BTCUSDT", "interval": "1m", "start_time": 1731630000000, "end_time": 1731633600000}'
  ```

