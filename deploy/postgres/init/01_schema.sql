-- =============================================================================
-- PostgreSQL Control Plane & Intelligence State Schema Initialization
-- Strictly stores control metadata, IAM, watermarks, and Agent execution trails.
-- High-frequency market tick data is NEVER stored in PostgreSQL.
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY,
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    role            VARCHAR(32) NOT NULL CHECK (role IN ('viewer', 'analyst', 'operator', 'admin', 'service')),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS monitored_instruments (
    instrument_id   UUID PRIMARY KEY,
    provider        VARCHAR(32) NOT NULL,
    symbol          VARCHAR(32) NOT NULL,
    base_asset      VARCHAR(16) NOT NULL,
    quote_asset     VARCHAR(16) NOT NULL,
    status          VARCHAR(32) NOT NULL CHECK (status IN ('TRADING', 'HALTED', 'INACTIVE')),
    enabled_streams JSONB NOT NULL DEFAULT '["trade", "kline_1m", "ticker", "depth20"]'::jsonb,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (provider, symbol)
);

CREATE TABLE IF NOT EXISTS ingestion_watermarks (
    watermark_id            UUID PRIMARY KEY,
    provider                VARCHAR(32) NOT NULL,
    symbol                  VARCHAR(32) NOT NULL,
    dataset                 VARCHAR(64) NOT NULL,
    last_synced_timestamp   TIMESTAMPTZ NOT NULL,
    status                  VARCHAR(32) NOT NULL CHECK (status IN ('IDLE', 'RUNNING', 'FAILED', 'COMPLETED')),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (provider, symbol, dataset)
);

CREATE TABLE IF NOT EXISTS agent_runs (
    run_id              UUID PRIMARY KEY,
    trigger_mode        VARCHAR(32) NOT NULL CHECK (trigger_mode IN ('ON_DEMAND', 'EVENT_TRIGGERED')),
    requested_by        UUID NULL REFERENCES users(id),
    symbol              VARCHAR(32) NOT NULL,
    status              VARCHAR(32) NOT NULL CHECK (status IN ('QUEUED', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED')),
    prompt_summary      TEXT NOT NULL,
    structured_report   JSONB NULL,
    token_usage         JSONB NOT NULL DEFAULT '{"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}'::jsonb,
    started_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at        TIMESTAMPTZ NULL
);

CREATE INDEX IF NOT EXISTS idx_agent_runs_status_started ON agent_runs (status, started_at DESC);

CREATE TABLE IF NOT EXISTS agent_tool_invocations (
    invocation_id   UUID PRIMARY KEY,
    run_id          UUID NOT NULL REFERENCES agent_runs(run_id) ON DELETE CASCADE,
    tool_name       VARCHAR(64) NOT NULL,
    input_params    JSONB NOT NULL,
    output_metadata JSONB NOT NULL,
    status          VARCHAR(32) NOT NULL CHECK (status IN ('SUCCESS', 'TIMEOUT', 'VALIDATION_ERROR', 'SOURCE_ERROR')),
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_tools_run_id ON agent_tool_invocations (run_id, started_at ASC);

