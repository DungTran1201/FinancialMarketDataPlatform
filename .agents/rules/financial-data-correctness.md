# Data Rule — Financial Data Correctness (`DATA-RULE-002`)

| Metadata | Value |
|---|---|
| **Rule ID** | `DATA-RULE-002` |
| **Rule Slug** | `financial-data-correctness` |
| **Trigger Scope** | Market data ingestion, event modeling, transformations, storage schemas, quantitative calculations, and API/Agent outputs |
| **Activation Mode** | `Always Active` |
| **Status** | `BASELINED` |
| **Updated Date** | `2026-11-12` |

---

## 1. Purpose & Scope

Guarantees exact numerical representation (`Decimal`), timezone-aware UTC timestamps, and financial candle/trade invariants across all ingestion, streaming, storage, and analytical paths.

## 2. Mandatory Directives

1. **Exact Decimal Precision**: Use exact `Decimal` types (`Decimal128(18)` / `NUMERIC(38, 18)`) for prices, quantities, volumes, rates, and persisted monetary values.
2. **UTC Timestamp Separation**: Preserve timezone-aware UTC timestamps and distinguish `exchange_event_time`, `ingested_at`, and processing time.
3. **Financial Invariants**: Validate trade positivity (`price > 0`, `quantity > 0`), non-negative volumes (`>= 0`), and OHLC candle invariants (`high >= max(open, close, low)` and `low <= min(open, close, high)`).
4. **Explicit Units & Ordering**: Declare quote/base asset meaning, interval, rounding policy, and late-arrival/sequence behavior per event type.

## 3. Prohibited Actions

- Do not persist financial prices, quantities, or volumes as binary floating-point (`float` / `DOUBLE`).
- Do not round or rescale financial values implicitly.
- Do not mix exchange timestamps and ingestion timestamps in deduplication/version logic without an explicit documented rule.

## 4. Verification Mechanism

- Automated contract and unit tests (`tests/unit/test_contracts_and_guardrails.py`), ClickHouse/PostgreSQL DDL inspection, and `tools/validators/run_all.py`.

