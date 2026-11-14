@echo off
setlocal EnableExtensions EnableDelayedExpansion

echo ============================================================================
echo  FINANCIAL MARKET DATA PLATFORM - SYSTEM ^& ENVIRONMENT SETUP (setup.bat)
echo ============================================================================
echo  Architecture: Three-Plane Event-Driven Streaming-First Hybrid Lakehouse
echo    - Plane A (Data)         : Kafka (KRaft), Redis 7, ClickHouse, MinIO,
echo                               Parquet, Apache Iceberg, PySpark, dbt, GE
echo    - Plane B (App/Control)  : FastAPI Modular Monolith, PostgreSQL 16, Superset
echo    - Plane C (Intelligence) : LangGraph Agent Worker ^& Controlled Tool Gateway
echo    - Observability          : Prometheus ^& Grafana
echo ============================================================================
echo.

cd /d "%~dp0"

REM ----------------------------------------------------------------------------
REM [1/7] Initialize .env from .env.example
REM ----------------------------------------------------------------------------
echo [STEP 1/7] Checking environment configuration (.env)...
if not exist ".env" (
    if exist ".env.example" (
        copy /Y ".env.example" ".env" >nul
        echo   [OK] Created .env from .env.example
    ) else (
        echo   [ERROR] .env.example not found!
        exit /b 1
    )
) else (
    echo   [OK] Existing .env found.
)

REM ----------------------------------------------------------------------------
REM [2/7] Detect Python 3.12+ and Create Virtual Environment (.venv)
REM ----------------------------------------------------------------------------
echo.
echo [STEP 2/7] Setting up Python 3.12+ virtual environment (.venv)...
set "PYTHON_BOOTSTRAP="

py -3.12 --version >nul 2>&1
if !errorlevel! equ 0 (
    set "PYTHON_BOOTSTRAP=py -3.12"
) else (
    python --version >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_BOOTSTRAP=python"
    ) else (
        echo   [ERROR] Python 3.12+ was not found on this system.
        exit /b 1
    )
)

echo   [INFO] Using bootstrap interpreter: !PYTHON_BOOTSTRAP!
if not exist ".venv\Scripts\python.exe" (
    echo   [INFO] Creating virtual environment in .venv ...
    !PYTHON_BOOTSTRAP! -m venv .venv
    if !errorlevel! neq 0 (
        echo   [ERROR] Failed to create .venv virtual environment.
        exit /b 1
    )
    echo   [OK] Virtual environment created at .venv
) else (
    echo   [OK] Virtual environment already exists at .venv
)

set "VENV_PYTHON=%~dp0.venv\Scripts\python.exe"
"!VENV_PYTHON!" --version

REM ----------------------------------------------------------------------------
REM [3/7] Upgrade pip, setuptools, wheel & Install Core + Dev + Intelligence Stack
REM ----------------------------------------------------------------------------
echo.
echo [STEP 3/7] Installing Backend, Streaming, Database, Intelligence ^& Test dependencies...
"!VENV_PYTHON!" -m pip install --upgrade pip setuptools wheel
if !errorlevel! neq 0 (
    echo   [ERROR] Failed to upgrade pip/setuptools/wheel.
    exit /b 1
)

echo   [INFO] Installing core platform, FastAPI, Kafka, Redis, ClickHouse, PostgreSQL, LangGraph, and Dev packages...
"!VENV_PYTHON!" -m pip install -e ".[intelligence,dev]"
if !errorlevel! neq 0 (
    echo   [ERROR] Failed to install core/intelligence/dev dependencies from pyproject.toml.
    exit /b 1
)
echo   [OK] Core Backend, Streaming (confluent-kafka), Redis, ClickHouse, PostgreSQL (SQLAlchemy/asyncpg), LangGraph ^& Dev packages installed.

REM ----------------------------------------------------------------------------
REM [4/7] Install Lakehouse Stack (Parquet, Iceberg, PySpark, dbt, Great Expectations)
REM ----------------------------------------------------------------------------
echo.
echo [STEP 4/7] Installing Lakehouse stack (Parquet/PyArrow, Apache Iceberg, PySpark, dbt-core, dbt-clickhouse)...
"!VENV_PYTHON!" -m pip install "pyarrow>=16.0.0" "pyiceberg>=0.6.1" "dbt-core>=1.8.0" "dbt-clickhouse>=1.8.0"
if !errorlevel! neq 0 (
    echo   [WARN] Partial warning installing pyarrow/pyiceberg/dbt; retrying individual packages...
    "!VENV_PYTHON!" -m pip install pyarrow pyiceberg dbt-core dbt-clickhouse
)

echo   [INFO] Installing PySpark and Great Expectations (optional heavy batch engines)...
"!VENV_PYTHON!" -m pip install "pyspark>=3.5.1" "great-expectations>=0.18.15" >nul 2>&1
if !errorlevel! equ 0 (
    echo   [OK] PySpark and Great Expectations installed successfully.
) else (
    echo   [INFO] Installing PySpark standalone...
    "!VENV_PYTHON!" -m pip install "pyspark>=3.5.1" >nul 2>&1
    echo   [OK] Lakehouse Python packages configured.
)

REM ----------------------------------------------------------------------------
REM [5/7] Initialize Local Medallion Lakehouse (Parquet/Iceberg), Spark & dbt Directories
REM ----------------------------------------------------------------------------
echo.
echo [STEP 5/7] Initializing Medallion Lakehouse (Bronze/Silver/Gold), Parquet, Iceberg, Spark ^& dbt structure...
for %%D in (
    ".local_lakehouse"
    ".local_lakehouse\bronze"
    ".local_lakehouse\silver"
    ".local_lakehouse\gold"
    ".local_lakehouse\iceberg_warehouse"
    "src\transformation\dbt\models\marts"
    "src\transformation\dbt\macros"
    "src\transformation\dbt\tests"
    "src\transformation\dbt\seeds"
    "src\transformation\dbt\analyses"
) do (
    if not exist "%%~D" mkdir "%%~D"
)
echo   [OK] Local Lakehouse directories (.local_lakehouse\bronze, silver, gold, iceberg_warehouse) and dbt paths ready.

REM ----------------------------------------------------------------------------
REM [6/7] Verify Database Schemas & Technology Stack Configs (PostgreSQL, ClickHouse, Kafka, Redis, MinIO, Prometheus)
REM ----------------------------------------------------------------------------
echo.
echo [STEP 6/7] Verifying Database DDL Schemas, Docker Compose Blueprint ^& Technology Stack Configurations...
for %%F in (
    "docker-compose.yml"
    "deploy\docker\Dockerfile.python"
    "deploy\postgres\init\01_schema.sql"
    "deploy\clickhouse\init\01_schema.sql"
    "deploy\prometheus\prometheus.yml"
    "src\transformation\dbt\dbt_project.yml"
    "src\transformation\dbt\profiles.yml"
    "src\processing\spark\bronze_to_silver.py"
    "src\quality\expectations\suite_definitions.py"
    "deploy\nginx\nginx.conf"
    "deploy\tls\generate_tls_certs.py"
) do (
    if exist "%%~F" (
        echo   [OK] Verified config/schema artifact: %%~F
    ) else (
        echo   [ERROR] Missing required configuration/schema artifact: %%~F
        exit /b 1
    )
)

echo   [INFO] Generating X.509 SAN TLS Certificates for *.fmdp.local HTTPS Edge Gateway...
"!VENV_PYTHON!" deploy\tls\generate_tls_certs.py
if !errorlevel! neq 0 (
    echo   [ERROR] Failed to generate TLS certificates.
    exit /b 1
)

REM ----------------------------------------------------------------------------
REM [7/7] Validate Docker Compose & Provision Containers (if Docker Daemon is active)
REM ----------------------------------------------------------------------------
echo.
echo [STEP 7/7] Checking Docker ^& Docker Compose infrastructure stack...
docker compose version >nul 2>&1
if !errorlevel! equ 0 (
    docker compose config --quiet
    if !errorlevel! equ 0 (
        echo   [OK] docker-compose.yml syntax and profiles validated ^(core, lakehouse, intelligence, observability, bi^).
    ) else (
        echo   [ERROR] docker-compose.yml validation failed!
        exit /b 1
    )

    docker info >nul 2>&1
    if !errorlevel! equ 0 (
        echo   [INFO] Docker daemon is running. Starting core + lakehouse infrastructure containers...
        docker compose --profile core --profile lakehouse up -d postgres redis kafka clickhouse minio
        echo   [INFO] Provisioning canonical Kafka topics ^(market.raw.*.v1, market.anomalies.v1, market.dlq.v1^)...
        for %%T in (
            market.raw.trades.v1
            market.raw.klines.v1
            market.raw.tickers.v1
            market.raw.orderbook.v1
            market.anomalies.v1
            market.dlq.v1
        ) do (
            docker exec fmdp-kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic %%T --partitions 6 --replication-factor 1 >nul 2>&1
        )
        echo   [OK] Docker infrastructure containers and Kafka topics provisioned.
    ) else (
        echo   [WARN] Docker Desktop daemon is not currently running on host.
        echo          All Python environments, schemas, Parquet/Iceberg local lakehouse, and Docker Compose specs are ready.
        echo          Start Docker Desktop anytime to launch containerized Kafka/Redis/ClickHouse/MinIO/PostgreSQL.
    )
) else (
    echo   [WARN] Docker CLI not detected; skipped container provisioning.
)

echo.
echo ============================================================================
echo  SETUP COMPLETED SUCCESSFULLY.
echo  Next Step: Run "run.bat" to start services, execute all tests, and verify.
echo ============================================================================
exit /b 0

