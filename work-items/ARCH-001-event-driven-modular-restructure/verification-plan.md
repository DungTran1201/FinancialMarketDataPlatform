# Verification Plan — `ARCH-001`

## 1. Automated Verification Gates

| Gate Check | Command | Acceptance Criterion |
|---|---|---|
| Documentation & Model Governance | `.\.venv\Scripts\python.exe tools/validators/run_all.py` | Exit code `0`, `0 error(s)` across all 10 validators |
| Architecture Boundaries (`TC-006`) | `.\.venv\Scripts\python.exe -m pytest tests/architecture -v` | 100% pass enforcing layer & plane isolation across all 6 `src/` modules |
| Full Automated Test Suite | `.\.venv\Scripts\python.exe -m pytest -v` | 100% pass across `architecture`, `unit`, `contract`, `data_quality`, `integration`, `e2e`, `resilience`, `performance` |
| Standard Unittest Discovery | `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` | All test modules discovered cleanly without import errors |
| Linter Check | `.\.venv\Scripts\ruff.exe check src tests` | Zero lint errors |
| dbt Project Parse | `.\.venv\Scripts\dbt.exe parse --project-dir src/lakehouse/gold/dbt --profiles-dir src/lakehouse/gold/dbt` | Clean parse with 0 syntax/config errors |
| Container Entrypoint Smoke Check | `.\.venv\Scripts\python.exe -c "import ..."` on all entrypoints & ASGI apps | All worker `main()` functions and ASGI `app` objects import cleanly |

