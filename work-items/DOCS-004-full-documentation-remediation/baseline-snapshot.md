# Pre-Edit Repository Baseline Snapshot (`DOCS-004`)

- **Captured Date**: `2026-11-15`
- **Branch**: `docs/DOCS-003-consistency-remediation` (matched `origin/docs/DOCS-003-consistency-remediation` before remediation edits)
- **Baseline Commit HEAD**: `c954d32f33dcc6b4200804662b4bdae2b3a3ddbd`
- **Main Branch Reference**: `main` at `f0329d3b6c7e50703d581d2144da2b5be3481c98` (`1` commit behind `docs/DOCS-003-consistency-remediation`)
- **Working Tree State at Capture**: Clean (zero uncommitted modifications)

## Verified Baseline Inventory Counts

| Category | Verified Count | Authoritative Observation Source |
|---|---|---|
| Markdown files (active repository scan) | `401` | Pre-edit repository file scan (`audit_markdown.json`) |
| Document templates (`docs/templates/**/*.template.md`) | `57` | Recursive filesystem scan (`inventory_deep.json`) |
| Diagram files (`docs/diagrams/**/*.md`) | `34` (`22` active diagrams + `12` `.template.md`) | Recursive filesystem scan (`inventory_deep.json`) |
| Canonical model YAML files (`models/**/*.yaml`) | `38` (`26` canonical `.yaml` + `12` `.template.yaml`) | Recursive filesystem scan (`inventory_deep.json`) |
| `.agents/` configuration assets | `19` roles, `22` rules, `25` skills, `7` YAML configs | Recursive `.agents/` scan (`inventory_deep.json`) |
| Managed directories with 12-section `README.md` | `119 / 119` | `tools/validators/validate_readmes.py` target tree |
| Work items present prior to `DOCS-004` | `7` (`ARCH-001`, `DATA-001`, `DOCS-001`, `DOCS-002`, `DOCS-003`, `FEAT-001`, `FEAT-002`) | `work-items/` directory inspection |
| FastAPI Monolith routes (`src/serving/api/main.py`) | `55` (`54` HTTP + `1` WS `/ws/v1/observability/stream`) | Live FastAPI route/router extraction (`routes_exact.json`) |
| Standalone `svc-*` microservice apps (`src/serving/api/services/`) | `7` (`svc-market-hot`, `svc-historical-backfill`, `svc-analytics-quant`, `svc-catalog-governance`, `svc-iam-security`, `svc-intelligence-agent`, `svc-data-plane-v01`) | Live FastAPI route extraction (`routes_exact.json`) |
| Docker Compose services (`docker-compose.yml`) | `24` services across `7` profiles (`core`, `frontend`, `lakehouse`, `intelligence`, `observability`, `bi`, `microservices`) | `docker-compose.yml` YAML parse (`inventory_deep.json`) |

## Baseline Command Verification (Pre-Edit Execution)

| Check Command | Baseline Exit | Observed Result |
|---|---|---|
| `.\.venv\Scripts\python.exe tools/validators/run_all.py` | `0` (`PASS`) | All `10/10` legacy structural validators passed (`0` semantic runtime parity checks present in legacy scripts) |
| `.\.venv\Scripts\pytest.exe tests -v` | `0` (`PASS`) | `50` passed across `11` Python test files |
| `npm test --prefix frontend` | `0` (`PASS`) | `3` passed (`node --test tests/**/*.test.js` across `formatters.test.js` and `router.test.js` — NOT Vitest/App.test.tsx) |
| `docker compose config --quiet` | `0` (`PASS`) | Compose YAML syntax valid (static port `9000` host collision undetected without profile runtime conflict check) |

