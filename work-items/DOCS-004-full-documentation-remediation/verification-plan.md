# Independent Verification Plan — `DOCS-004`

| Check ID | Verification Scope | Exact Command | Current Status |
|---|---|---|---|
| `VER-01` | Documentation Validator Suite (upgraded semantic + structural checks across all 10 scripts) | `.\.venv\Scripts\python.exe tools/validators/run_all.py` | `PASS` (`10/10` validators passed, `0` errors) |
| `VER-02` | Python Architecture, Contract, Unit, DQ, Integration, E2E, Resilience, Swarm & Validator Negative Tests (`TC-001`..`TC-017`) | `.\.venv\Scripts\pytest.exe tests -v` | `PASS` (`58 passed`, `0` failed; `python -m unittest discover -s tests -v`: `55` ran, `OK`) |
| `VER-03` | Code & Tooling Lint Compliance (`src/`, `tests/`, `tools/`) | `.\.venv\Scripts\ruff.exe check src tests tools` | `PASS` (`0` errors) |
| `VER-04` | Frontend Node JS Helper Tests (`formatters.test.js`, `router.test.js`) | `npm test --prefix frontend` | `PASS` (`3/3` passed via `node --test`, `0` failed) |
| `VER-05` | Frontend Production Vite Build (`tsc && vite build`) | `npm run build --prefix frontend` | `PASS` (`34` modules transformed, exit `0`) |
| `VER-06` | Docker Compose Profile Config & Host Port Collision Regression Check | `docker compose --profile core --profile lakehouse --profile intelligence --profile observability --profile bi --profile microservices --profile frontend config --quiet` | `PASS` (exit `0`, zero host port `9000` conflict) |
| `VER-07` | CI Workflow YAML Integrity | `.\.venv\Scripts\python.exe -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml', encoding='utf-8'))"` | `PASS` (`CI_YAML_OK`, exit `0`) |
| `VER-08` | Full Runtime Live-Container Start (`docker compose up`) & Multi-Node Cluster Benchmarks (`NFR-001`, `NFR-002`) | `docker compose --profile core up -d` | `NOT_RUN` (outside static remediation scope; latency SLAs remain `UNVERIFIED_UNDER_PRODUCTION_LOAD`) |
