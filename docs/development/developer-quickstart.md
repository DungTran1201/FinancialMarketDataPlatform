# Developer Quickstart & Local Setup Guide

| Metadata | Value |
|---|---|
| **Document ID** | `DOC-DEV-QUICKSTART` |
| **Title** | Developer 5-Minute Quickstart & Local Environment Guide |
| **Category** | Developer Experience |
| **Status** | `APPROVED` |
| **Updated Date** | `2026-11-15` |
| **Authoring Role** | `documentation-architect` |

---

## 1. Prerequisites

- **Python**: 3.12+ (tested with Python 3.12.9)
- **Node.js**: v22+ (tested with v22.14.0 & npm 10.9.2)
- **Docker**: Docker Desktop or Engine with Compose v2+
- **Git**: 2.40+

---

## 2. 5-Minute Local Setup

### Step 1: Clone Repository & Create Python Environment
```powershell
# Clone the repository
git clone https://github.com/DungTran1201/FinancialMarketDataPlatform.git
cd FinancialMarketDataPlatform

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
# (Or on Linux / macOS: source .venv/bin/activate)

# Install project dependencies in editable mode
pip install -e ".[dev]"
```

### Step 2: Set Up Frontend Application
```powershell
# Navigate to frontend and install dependencies
cd frontend
npm ci
npm run build
cd ..
```

### Step 3: Run Automated Verification Suite
```powershell
# 1. Run Python test suite (unit, contract, architecture, DQ, integration, E2E, resilience, performance)
.\.venv\Scripts\pytest.exe tests -v

# 2. Run Documentation Engineering Validators (run_all.py orchestrates 10 validator modules)
.\.venv\Scripts\python.exe tools/validators/run_all.py

# 3. Run Frontend unit tests
npm test --prefix frontend
```

---

## 3. Running the System Locally

### Launching via Docker Compose:
```powershell
# Start core infrastructure + single-process modular gateway
docker compose --profile core up -d

# Check running container health
docker compose ps
```

### Launching Backend FastApi Locally (without Docker):
```powershell
# Run backend API server
.\.venv\Scripts\uvicorn.exe src.serving.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Launching Frontend Development Server:
```powershell
cd frontend
npm run dev
# Vite server starts at http://localhost:5173
```

---

## 4. Common Developer Commands Cheat-Sheet

| Command | Purpose |
|---|---|
| `.\.venv\Scripts\pytest.exe tests -v` | Run all Python test suites (`50+` test functions) |
| `.\.venv\Scripts\ruff.exe check src tests tools` | Run Python linter |
| `.\.venv\Scripts\python.exe tools/validators/run_all.py` | Run all documentation and model validators |
| `npm test --prefix frontend` | Run frontend unit tests |
| `npm run build --prefix frontend` | Build frontend production assets to `frontend/dist/` |
| `git status` | Verify clean working tree |

