# Data Rule — Executable Data Quality Gates (`DATA-RULE-008`)

| Metadata | Value |
|---|---|
| **Rule ID** | `DATA-RULE-008` |
| **Rule Slug** | `data-quality-gates` |
| **Trigger Scope** | Ingestion validation, Bronze/Silver/Gold promotion, dbt tests, Great Expectations, serving, and releases |
| **Activation Mode** | `Always Active` |
| **Status** | `BASELINED` |
| **Updated Date** | `2026-11-12` |

---

## 1. Purpose & Scope

Mandates executable data quality expectations (`QualityExpectationRule`, Great Expectations suites, and dbt data tests) with explicit severity (`CRITICAL` vs. `WARNING`) and promotion blocking across data pipeline stages.

## 2. Mandatory Directives

1. **Structured Rule Metadata**: Assign every quality rule a stable ID (`DQ-*`), target dataset, expression/expectation, severity, owner, execution point, and failure action (`src/quality/expectations/suite_definitions.py`).
2. **Multi-Layer Coverage**: Cover schema validity, completeness, uniqueness, referential integrity, freshness, financial candle/trade invariants, and volume reconciliation.
3. **Promotion Blocking**: Ensure `CRITICAL` quality failures block Silver/Gold promotion or trusted serving, while `WARNING` findings are recorded and alerted.
4. **Execution Evidence**: Persist validation outcomes with dataset version, time window, and run correlation; distinguish declared rules from executed validation runs.

## 3. Prohibited Actions

- Do not silently downgrade rule severity or filter out failing rows to make a pipeline run appear green.
- Do not claim Great Expectations or dbt quality test passage without execution evidence.

## 4. Verification Mechanism

- Expectation suite and dbt test execution, unit verification in `tests/`, and `tools/validators/run_all.py`.

