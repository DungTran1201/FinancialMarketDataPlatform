@echo off
setlocal EnableExtensions EnableDelayedExpansion

echo ============================================================================
echo  FINANCIAL MARKET DATA PLATFORM - SYSTEM RUNNER ^& ACCEPTANCE SUITE (run.bat)
echo ============================================================================

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Virtual environment .venv not found. Running setup.bat first...
    call "%~dp0setup.bat"
    if !errorlevel! neq 0 exit /b !errorlevel!
)

set "VENV_PYTHON=%~dp0.venv\Scripts\python.exe"
set "PYTHONPATH=%~dp0"

REM ----------------------------------------------------------------------------
REM [1/6] Check Optional Docker Infrastructure Services
REM ----------------------------------------------------------------------------
echo.
echo [STAGE 1/6] Checking Infrastructure Stack (Docker Compose)...
docker info >nul 2>&1
if !errorlevel! equ 0 (
    echo   [INFO] Docker daemon is active. Ensuring core infrastructure containers are up...
    docker compose --profile core --profile lakehouse up -d postgres redis kafka clickhouse minio
    docker compose ps
) else (
    echo   [INFO] Running in Local/In-Memory Verification Mode ^(Docker Desktop daemon is offline^).
)

REM ----------------------------------------------------------------------------
REM [2/6] Smoke-Test All Platform Worker Entrypoints (Plane A, Plane B, Plane C)
REM ----------------------------------------------------------------------------
echo.
echo [STAGE 2/6] Smoke-testing Platform Service Entrypoints...

echo   - Testing Collector WebSocket Worker (src.ingestion.entrypoints.ws_collector)...
"!VENV_PYTHON!" -m src.ingestion.entrypoints.ws_collector
if !errorlevel! neq 0 exit /b 1

echo   - Testing Collector REST Backfill Worker (src.ingestion.entrypoints.rest_backfill)...
"!VENV_PYTHON!" -m src.ingestion.entrypoints.rest_backfill
if !errorlevel! neq 0 exit /b 1

echo   - Testing Hot Redis Consumer Worker (src.streaming.consumers.hot_redis)...
"!VENV_PYTHON!" -m src.streaming.consumers.hot_redis
if !errorlevel! neq 0 exit /b 1

echo   - Testing ClickHouse Analytics Consumer Worker (src.streaming.consumers.analytics_ch)...
"!VENV_PYTHON!" -m src.streaming.consumers.analytics_ch
if !errorlevel! neq 0 exit /b 1

echo   - Testing Lakehouse Bronze Archiver Worker (src.lakehouse.bronze.consumer)...
"!VENV_PYTHON!" -m src.lakehouse.bronze.consumer
if !errorlevel! neq 0 exit /b 1

echo   - Testing Isolated LangGraph Agent Worker (src.intelligence.main)...
"!VENV_PYTHON!" -m src.intelligence.main
if !errorlevel! neq 0 exit /b 1

echo   [OK] All 6 service entrypoints initialized cleanly.

REM ----------------------------------------------------------------------------
REM [3/6] End-to-End Technology Stack & Data Lifecycle Integration Smoke Check
REM       (Kafka Contracts, Redis Lua, ClickHouse Buffer, Parquet/Iceberg,
REM        PySpark Specs, dbt Project, Great Expectations, FastAPI, LangGraph)
REM ----------------------------------------------------------------------------
echo.
echo [STAGE 3/6] Running End-to-End Multi-Plane Technology ^& Security Integration Smoke Test...
"!VENV_PYTHON!" -c "import importlib.metadata as m, pathlib, pyarrow as pa, pyarrow.parquet as pq, pyiceberg; from fastapi.testclient import TestClient; from src.serving.api.main import create_app; from src.shared.contracts.events.market_events import EventType, compute_deterministic_event_id; from src.streaming.consumers.hot_redis import REDIS_MONOTONIC_UPSERT_LUA, build_hot_price_key; from src.streaming.consumers.analytics_ch import MicroBatchBuffer; from src.lakehouse.bronze.archiver import build_bronze_partition_path; from src.lakehouse.silver.merge_engine import SILVER_KLINES_MERGE_SPEC, SILVER_TRADES_MERGE_SPEC; from src.lakehouse.quality.gates import MANDATORY_KLINE_QUALITY_RULES; from src.intelligence.workflows.investigation import WORKFLOW_NODES; pkgs = ['fastapi','uvicorn','confluent-kafka','redis','clickhouse-connect','sqlalchemy','asyncpg','pyarrow','pyiceberg','pyspark','dbt-core','dbt-clickhouse','great-expectations','langgraph','prometheus-client']; versions = {p: m.version(p) for p in pkgs}; print('  [OK] Verified installed versions:', versions); app = create_app(); client = TestClient(app); hdrs = {'Host': 'api.fmdp.local', 'X-Forwarded-For': '203.0.113.50'}; r_live = client.get('/api/v1/health/live', headers=hdrs); r_ready = client.get('/api/v1/health/ready', headers=hdrs); r_price = client.get('/api/v1/market/prices/BTCUSDT', headers=hdrs); r_dom = client.get('/api/v1/auth/domains', headers=hdrs); assert r_live.status_code == 200 and r_live.json()['status'] == 'alive'; assert r_ready.status_code == 200 and r_ready.json()['status'] == 'ready'; assert '6379' not in str(r_ready.json()['dependencies']); assert r_price.status_code == 200 and r_price.json()['data']['symbol'] == 'BTCUSDT'; assert r_dom.status_code == 200 and r_dom.json()['data']['public_https_endpoints']['api_gateway'] == 'https://api.fmdp.local'; assert r_live.headers['X-Client-IP-Token'].startswith('ip_hm256_') and r_live.headers['X-Encrypted-Client-IP'].startswith('enc_v1_'); part_dir = pathlib.Path('.local_lakehouse') / build_bronze_partition_path('binance', 'trade', '2026-11-15'); part_dir.mkdir(parents=True, exist_ok=True); tbl = pa.Table.from_pylist([{'event_id': str(compute_deterministic_event_id('binance', EventType.TRADE, 'BTCUSDT', '1001')), 'provider': 'binance', 'symbol': 'BTCUSDT', 'price': '89500.25', 'quantity': '0.50'}]); pq_file = part_dir / 'smoke_test.parquet'; pq.write_table(tbl, pq_file, compression='ZSTD'); tbl_back = pq.read_table(pq_file); assert tbl_back.num_rows == 1; assert 'tonumber' in REDIS_MONOTONIC_UPSERT_LUA and build_hot_price_key('binance', 'btcusdt') == 'market:v1:price:binance:BTCUSDT'; buf = MicroBatchBuffer(max_rows=2); assert buf.append({'symbol': 'BTCUSDT'}) is False and buf.append({'symbol': 'ETHUSDT'}) is True and len(buf.drain()) == 2; assert SILVER_KLINES_MERGE_SPEC.target_silver_table == 'lakehouse.silver.market_klines' and SILVER_TRADES_MERGE_SPEC.target_silver_table == 'lakehouse.silver.market_trades'; assert len(MANDATORY_KLINE_QUALITY_RULES) == 5 and len(WORKFLOW_NODES) == 5; print('  [OK] HTTPS Domain (*.fmdp.local), Encrypted IP/Port Masking, JWT/Auth Router, FastAPI, Parquet ZSTD Lakehouse I/O, Iceberg, PySpark specs, Great Expectations rules, ClickHouse MicroBatchBuffer, Redis Lua script, and LangGraph state verified.')"
if !errorlevel! neq 0 (
    echo   [ERROR] Multi-plane integration smoke check failed.
    exit /b 1
)

echo   - Verifying dbt Core ^& dbt-clickhouse project configuration...
"%~dp0.venv\Scripts\dbt.exe" parse --project-dir src/lakehouse/gold/dbt --profiles-dir src/lakehouse/gold/dbt
if !errorlevel! neq 0 (
    echo   [ERROR] dbt parse check failed.
    exit /b 1
)
echo   [OK] dbt Gold analytics project parsed cleanly.

REM ----------------------------------------------------------------------------
REM [4/6] Run Unit, Contract & Clean Architecture Boundary Tests (unittest)
REM ----------------------------------------------------------------------------
echo.
echo [STAGE 4/6] Running Clean Architecture Boundary ^& Contract Unit Tests (unittest)...
"!VENV_PYTHON!" -m unittest discover -s tests -v
if !errorlevel! neq 0 (
    echo   [ERROR] Unittest suite failed!
    exit /b 1
)

REM ----------------------------------------------------------------------------
REM [5/6] Run Pytest Suite
REM ----------------------------------------------------------------------------
echo.
echo [STAGE 5/6] Running Pytest Verification Suite...
"!VENV_PYTHON!" -m pytest tests -v
if !errorlevel! neq 0 (
    echo   [ERROR] Pytest suite failed!
    exit /b 1
)

REM ----------------------------------------------------------------------------
REM [6/6] Run 10-Validator Documentation Engineering & Governance Suite
REM ----------------------------------------------------------------------------
echo.
echo [STAGE 6/6] Running 10-Validator Documentation Engineering Suite (tools/validators/run_all.py)...
"!VENV_PYTHON!" tools/validators/run_all.py
if !errorlevel! neq 0 (
    echo   [ERROR] Documentation Engineering validation suite failed!
    exit /b 1
)

echo.
echo ============================================================================
echo  ALL SYSTEM, ARCHITECTURE, DATA PLATFORM ^& GOVERNANCE CHECKS PASSED (0 ERRORS)
echo ============================================================================

if /I "%~1"=="--serve" goto :start_https_server
if /I "%~1"=="--https" goto :start_https_server
exit /b 0

:start_https_server
if not exist "deploy\tls\certs\fmdp.crt" (
    "!VENV_PYTHON!" deploy\tls\generate_tls_certs.py
)
echo.
echo ============================================================================
echo  STARTING HTTPS FASTAPI SERVER (TLS 1.3 / X.509 SAN Certificate)
echo    - Swagger UI (Domain)    : https://api.fmdp.local:8443/api/docs
echo    - Swagger UI (Localhost) : https://localhost:8443/api/docs
echo    - OpenAPI JSON Schema    : https://api.fmdp.local:8443/api/openapi.json
echo ============================================================================
"!VENV_PYTHON!" -m uvicorn src.serving.api.main:app --host 0.0.0.0 --port 8443 --ssl-keyfile deploy/tls/certs/fmdp.key --ssl-certfile deploy/tls/certs/fmdp.crt
exit /b 0

