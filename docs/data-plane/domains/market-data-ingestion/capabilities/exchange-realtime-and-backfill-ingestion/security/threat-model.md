---
doc_id: CAP-DP-ING-TM-001
title: "Threat Model: Exchange Realtime & Backfill Ingestion"
doc_type: specification
plane: data-plane
scope_level: capability
domain: market-data-ingestion
capability_id: CAP-DP-ING-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: security-architect
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/ingestion/providers/binance/normalizer.py"
    - "src/ingestion/providers/binance/rest_client.py"
    - "src/serving/api/modules/historical/presentation/router.py"
related_docs:
  - CAP-DP-ING-SEC-001
  - DIAG-DP-ING-TM-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Assessed external exchange payload tampering, REST IP bans, and unauthenticated backfill triggers."
---

# Threat Model: Exchange Realtime & Backfill Ingestion

Derived threat diagram: [threat-model-diagram.md](threat-model-diagram.md) (`DIAG-DP-ING-TM-001`).

## 1. Assets, Actors & Trust Boundaries `[REQUIRED]`

- **Assets**: Financial price/OHLCV integrity (`Decimal`), exchange IP rate-limit reputation (`1200` weight/min), SQLite watermark state, Kafka topic availability.
- **Actors**: Untrusted upstream exchange JSON/HTTP responses, unauthenticated HTTP callers invoking `/api/v1/market/ingest` or `/api/v1/historical/backfill-jobs` (`SEC-AUDIT-003`).
- **Trust Boundaries**: Edge API -> Worker trigger (`TB-1`), External Exchange -> `BinancePayloadNormalizer` (`TB-2`), Worker -> SQLite WAL (`TB-4`).

## 2. Entry Points & Threat Scenarios `[REQUIRED]`

| Threat ID | Entry Point | Threat / Abuse Scenario | Inherent Risk | Mitigations / Gaps | Residual Risk & Verification |
|---|---|---|---|---|---|
| `THR-ING-001` | Exchange WS / REST JSON payload | Inject negative prices, NaN floats, malformed OHLC bars, or huge payload causing pipeline crash or corrupted Gold analytics. | `HIGH` | **Mitigated**: `BinancePayloadNormalizer` enforces finite positive `Decimal`, OHLC bounds, UTC tz, and routes errors to `market.dlq.v1` (`SEC-ING-001`). | `LOW` (`test_gap_recovery_and_dlq.py`) |
| `THR-ING-002` | `POST /api/v1/historical/backfill-jobs` & `/market/ingest` | Unauthenticated external caller triggers abusive backfill/ingestion floods causing exchange IP ban (`418`) or memory DoS. | `CRITICAL` | **UNMITIGATED GAP (`SEC-AUDIT-003`)**: Routes require no JWT/RBAC (`OPERATOR`/`SERVICE` missing). `TokenBucketRateLimiter` caps REST weight only inside client (`SEC-ING-002`). | `CRITICAL` (`BLOCKED` until IAM router auth fixed) |
| `THR-ING-003` | Live Binance REST HTTPS (`use_embedded_asgi_transport=False`) | Spoofed upstream response or retry storm on `429`/`5xx`. | `MEDIUM` | **Partial**: Uses HTTPS default URL (`https://api.binance.com`), capped retries (`max_retries=3`), and `timeout=10.0s`. | `MEDIUM` (live TLS pinning not configured) |
