# Verification Plan — `DATA-001`

## 1. Verification Suites

1. **Documentation Engineering Validators**: `.\.venv\Scripts\python.exe tools/validators/run_all.py` (all 10 validators must return `0` errors).
2. **Code Quality & Linting**: `.\.venv\Scripts\ruff.exe check src tests` (`0` warnings/errors).
3. **Unit, Contract, Security, 100-Bot Swarm & Data Platform v0.1 / Microservices Test Suite (`TC-001..TC-011`)**: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`.

