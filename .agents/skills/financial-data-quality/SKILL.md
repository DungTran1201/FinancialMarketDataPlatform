---
name: financial-data-quality
description: Great Expectations, dbt, and stream-sink financial data quality gates.
---

# Skill: Executable Financial Data Quality Controls (`SKILL-022`)

## 1. Description

Define executable data quality controls (`QualityExpectationRule`, Great Expectations, dbt tests) for financial market data across contracts, stream sinks, Iceberg tables, dbt marts, and serving.

## 2. Trigger Conditions

- Data-quality rules, Great Expectations suites, dbt tests, contract validation, dataset promotion, or anomalous/missing market data investigations (`data-quality-governance-engineer`).

## 3. Authoritative Inputs

- `AGENTS.md`, target `README.md`, `docs/specifications/data-contracts.md`, `data-dictionary.md`, `data-requirements.md`, `src/quality/expectations/suite_definitions.py`, `src/shared/contracts/events.py`, `models/testing/testing.yaml`, `models/domain/`.

## 4. Preconditions

1. Target `README.md` read; each quality rule classified as `CRITICAL` or `WARNING` with a declared execution point, owner role, and failure action.

## 5. Execution Procedure

1. Build a dataset-specific quality matrix covering schema validity, completeness, uniqueness, referential integrity, freshness, timeliness, volume, and financial invariants.
2. Encode financial invariants: strictly positive trade price/quantity, OHLC candle ordering (`high >= max(open, close, low)`, `low <= min(open, close, high)`), non-negative volumes, exact `Decimal` precision, and timezone-aware UTC timestamps.
3. Assign each check to the appropriate execution layer: contract validation at ingestion (`EventEnvelopeV1`), table-level checks at Silver (`QualityExpectationRule`), semantic/integrity checks at Gold (`dbt test`), and staleness checks at serving (`GetLatestPriceQueryHandler`).
4. Implement Great Expectations rules (`src/quality/expectations/`) or dbt tests (`src/transformation/dbt/`) with stable IDs (`DQ-*`) and documented severity.
5. Configure quarantine/DLQ routing (`market.dlq.v1`) and promotion blocking for `CRITICAL` failures.
6. Add positive, negative, and boundary unit tests in `tests/` and run `tools/validators/run_all.py`.

## 6. Output Artifacts

- Quality expectation suites (`src/quality/expectations/`), dbt data tests, updated test models (`models/testing/testing.yaml`), and verification reports.

## 7. Validation

```powershell
python tools/validators/run_all.py
python -m unittest discover -s tests -v
```

## 8. Failure Handling

- Quarantine invalid records or block downstream table promotion on `CRITICAL` failures; never silently delete bad rows or relax quality rules without human approval.

## 9. Restrictions

- Do not invent arbitrary domain thresholds without marking `[ASSUMPTION — REQUIRES VALIDATION]`.
- Do not report unexecuted quality declarations as passing runtime checks.
- Do not expose sensitive production payloads in logs.

## 10. Related Skills

- `data-governance-lineage`
- `analytics-engineering-dbt-clickhouse`
- `lakehouse-medallion`
- `data-platform-testing-recovery`

