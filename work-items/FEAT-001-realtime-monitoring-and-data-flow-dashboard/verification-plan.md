# Verification Plan — FEAT-001

| Metadata | Value |
|---|---|
| **Work Item ID** | `FEAT-001` |
| **Authoring Role** | `qa-reviewer` / `documentation-auditor` |
| **Status** | `VERIFIED` |
| **Created Date** | `2026-11-15` |
| **Updated Date** | `2026-11-15` |

---

## 1. Automated Validation Commands

```powershell
.\.venv\Scripts\ruff.exe check src tests
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\pytest.exe tests -v
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 2. Acceptance Criteria Verification Matrix

| Criterion ID | Description | Verification Method | Status |
|---|---|---|---|
| `AC-OBS-01` | UI `/ui/data-flow` & `/ui/assets/*` return HTTP 200 with safe non-`none` CSP allowing `'self'` JS/CSS/SSE/WS while API CSP stays `default-src 'none'` | `pytest` integration + `test_security_and_defense.py` | `PASSED` |
| `AC-OBS-02` | Parallel branch latencies (`hot_branch_ms`, `olap_branch_ms`, `lakehouse_branch_ms`) computed independently; E2E Serving latency never sums parallel branches | `pytest` unit/integration assertion | `PASSED` |
| `AC-OBS-03` | Live Kafka partition/offset/lag inspector accurately shows pending lag before Bronze commit and 0 lag after commit | `pytest` integration assertion | `PASSED` |
| `AC-OBS-04` | Lakehouse explorer lists real Bronze/Silver/Gold Parquet files & Iceberg v2 `v*.metadata.json` manifests on disk | `pytest` integration assertion | `PASSED` |
| `AC-OBS-05` | OHLCV Candlestick endpoint returns exact `1m` bars and deterministic `Decimal` rollups (`5m`, `15m`, `1h`) with zero fabricated bars | `pytest` integration assertion | `PASSED` |
| `AC-OBS-06` | Clean Architecture import boundaries (`TC-006`) & API-016 backward compatibility (`TC-011`) pass | `unittest` & `pytest` full suite | `PASSED` |
| `AC-OBS-07` | All 10 governance validators pass with zero errors | `tools/validators/run_all.py` | `PASSED` |
