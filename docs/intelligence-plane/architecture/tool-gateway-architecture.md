---
doc_id: INT-ARCH-GW-001
title: "Controlled Tool Gateway Architecture"
doc_type: architecture
plane: intelligence-plane
scope_level: plane
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: ai-engineer
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/tools/contracts.py"
    - "src/intelligence/tools/gateway.py"
    - "src/serving/infrastructure/runtime.py"
    - "src/shared/domain/quant.py"
related_docs:
  - INT-ARCH-ROOT-001
  - INT-ARCH-001
  - INT-ARCH-SEC-001
  - INT-CTR-ROOT-001
  - ADR-OVR-003
  - ADR-INT-0001
  - DIAG-INT-GW-001
  - DIAG-INT-ORC-SEQ-002
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Documented all 10 ApprovedAgentTool contracts, gateway validation pipeline, policy vs actual store/side-effect discrepancies, and error propagation gaps."
---

# Controlled Tool Gateway Architecture

Derived diagrams: [tool-gateway-boundaries.md](diagrams/tool-gateway-boundaries.md) (`DIAG-INT-GW-001`) and [tool-invocation-sequence.md](../domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/workflows/tool-invocation-sequence.md) (`DIAG-INT-ORC-SEQ-002`). Authoritative machine-readable schema: [tool-contracts.yaml](../shared-contracts/tool-contracts.yaml).

## 1. Scope and Role

The **Controlled Tool Gateway** (`ControlledToolGateway`, `src/intelligence/tools/gateway.py`) is the single security and determinism firewall between LLM planning/synthesis and platform data stores (`ADR-OVR-003`, `ADR-INT-0001`). Agents NEVER generate SQL, issue direct HTTP/Redis/ClickHouse client calls, or perform arithmetic inside LLM prompts.

## 2. Context: Complete 10-Tool Registry (`Declared Policy` vs `Actual Runtime Implementation`)

`APPROVED_TOOL_POLICIES` (`src/intelligence/tools/contracts.py:38-109`) declares metadata for 10 whitelisted tools (`ApprovedAgentTool`). However, actual `AS-IS` behavior depends on the Python closures registered by `PlatformRuntimeContainer._register_all_ten_deterministic_tools()` (`src/serving/infrastructure/runtime.py:401-553`). **Policy metadata MUST NOT be conflated with live database wiring.**

| # | Tool Name (`ApprovedAgentTool`) | Required Permission | Max Rows / Periods | Timeout (s) | Declared Policy `backing_store` | Actual `AS-IS` Runtime Handler Store | Read / Write & Side Effects (`AS-IS`) |
|---|---|---|---|---|---|---|---|
| 1 | `get_latest_price` | `market:read` | `1` | `1.5` | `redis_with_clickhouse_fallback` | `latest_price_handler.handle("binance", sym)` -> in-memory `HotStateProjector._price_store` fallback to `ClickHouseBatchSink._klines_table` (ignores `provider` param) | **READ_ONLY** |
| 2 | `get_market_snapshot` | `market:read` | `1` | `2.0` | `redis_with_clickhouse_fallback` | `hot_redis_projector.get_hot_snapshot("binance", sym)` -> in-memory `_snapshot_store` **only** (no ClickHouse fallback) | **READ_ONLY** |
| 3 | `get_historical_candles` | `historical:read` | `500` | `5.0` | `clickhouse_agent_ro` | `clickhouse_sink.query_klines("binance", sym, interval, now-7d, now, limit=limit)` -> in-memory `_klines_table` (ignores `start_time`/`end_time`) | **READ_ONLY** |
| 4 | `get_market_statistics` | `analytics:read` | `1` | `5.0` | `clickhouse_mv_agent_ro` | `clickhouse_sink.compute_aggregated_statistics("binance", sym)` -> scans in-memory `_klines_table` (no ClickHouse MV) | **READ_ONLY** |
| 5 | `calculate_returns` | `analytics:read` | `720` | `5.0` | `clickhouse_agent_ro_deterministic_math` | `clickhouse_sink.compute_aggregated_statistics` (hardcoded fallback `[89500.0, 89550.0, 89600.0]`) + `compute_deterministic_log_returns()` (ignores `lookback_periods` slicing) | **READ_ONLY** |
| 6 | `calculate_volatility` | `analytics:read` | `720` | `5.0` | `clickhouse_agent_ro_deterministic_math` | Same in-memory stats + hardcoded fallback + `compute_deterministic_realized_volatility()` (ignores `lookback_periods` slicing) | **READ_ONLY** |
| 7 | `calculate_correlation` | `analytics:read` | `2160` | `8.0` | `clickhouse_agent_ro_deterministic_math` | In-memory stats for 2 symbols (hardcoded fallbacks) + `compute_deterministic_pearson_correlation()` (ignores `lookback_periods`) | **READ_ONLY** |
| 8 | `detect_anomalies` | `analytics:read` | `168` | `5.0` | `clickhouse_agent_ro_deterministic_math` | In-memory stats (hardcoded fallback `[100.0..100.8]`) + `anomaly_detector.evaluate_series("binance", sym, prices)` | **STATE_MUTATING SIDE EFFECT**: Mutates `anomaly_detector._cooldown_registry` (900s suppression) and appends `DetectedMarketAnomaly` to `runtime.detected_anomalies` |
| 9 | `get_data_freshness` | `market:read` | `1` | `3.0` | `redis_and_clickhouse_metadata` | `latest_price_handler.handle("binance", sym)` -> copies identical `dto.age_ms` to both `redis_lag_ms` & `clickhouse_lag_ms` (or `999999`) | **READ_ONLY** |
| 10 | `generate_analysis_report` | `agent:trigger` | `1` | `3.0` | `postgres_agent_rw` | Parses `report` dict into `StructuredAnalysisReport` and writes `runtime.reports[run_id]` in memory | **WRITE SIDE EFFECT**: Mutates `runtime.reports` despite `ToolGovernancePolicy.is_read_only_market_data=True` default |

> [!WARNING]
> **Critical Policy Metadata Defect (`contracts.py:35`)**: `ToolGovernancePolicy.is_read_only_market_data` defaults to `True` on **all 10 policies**, including `GENERATE_ANALYSIS_REPORT` (`postgres_agent_rw`) and `DETECT_ANOMALIES` (`runtime.detected_anomalies` mutation). Gateway code does not enforce read-only vs write separation or human approval gates (`OPEN` remediation item).

## 3. Building Blocks: Invocation Lifecycle & Guardrails

`ControlledToolGateway.execute_tool(tool_name, params, granted_permissions)` (`src/intelligence/tools/gateway.py:44-97`) executes these steps in order:

1. **Whitelist Validation**: Parses `ApprovedAgentTool(tool_name)`. Unknown tool names (e.g., `execute_raw_sql`) immediately raise `UnauthorizedToolAccessError`.
2. **RBAC Permission Check**: Verifies `policy.required_permission in granted_permissions`. Missing permission raises `UnauthorizedToolAccessError`.
   - **`AS-IS` Limitation**: `MarketIntelligenceGraph` injects a fixed set `frozenset({"market:read", "historical:read", "analytics:read", "agent:trigger"})`, bypassing per-user authorization (`INT-ARCH-SEC-001`).
3. **Query Bounds Enforcement**: Computes `requested_limit = int(params.get("limit") or params.get("lookback_periods") or 1)` and checks `requested_limit > policy.max_rows_or_periods` -> raises `ToolQueryLimitExceededError`.
   - **Input Schema Gap**: No Pydantic/JSON Schema validation exists on `params`. Non-numeric `limit` raises raw `ValueError`/`TypeError`; negative/zero limits (`<= 0`) pass the `>` check; `interval`, `symbol` format, and `report` nested keys are unvalidated by the gateway.
4. **Timeout Enforcement**: Looks up handler in `self._handlers`:
   - If handler is **registered**: runs `await asyncio.wait_for(handler(params), timeout=policy.timeout_seconds)`.
   - If handler is **missing (`None`)**: returns synthetic stub `{"status": "stub_ok", "tool": approved_tool.value}` rather than failing closed (`GAP`).
5. **Result Normalization & Provenance Metadata**: Generates `invocation_id = str(uuid.uuid4())`, captures `now_utc = datetime.now(UTC)`, and builds `ToolProvenanceMetadata(invocation_id, tool_name, source_store=policy.backing_store, symbol, window_start=params.get("start_time", now_utc), window_end=params.get("end_time", now_utc), row_count=int(result_data.get("row_count", 1)), executed_at=now_utc)`.
   - **Provenance Window Gap**: `window_start` and `window_end` default to `now_utc` even when `get_historical_candles` queries `now - timedelta(days=7)` (`runtime.py:429`), and passed strings are not coerced to `datetime`.
6. **Audit Recording & Error Propagation**:
   - Appends `ToolExecutionEnvelope(status="SUCCESS", data=result_data, provenance=provenance)` to `self._audit_log` and returns it.
   - **Error Propagation Gap**: Although `ToolExecutionEnvelope.status` comment (`contracts.py:130`) lists `SUCCESS | TIMEOUT | VALIDATION_ERROR | PERMISSION_DENIED`, `ControlledToolGateway` never constructs non-`SUCCESS` envelopes and does **not** record denied, timed-out, or failed invocations in `_audit_log` (exceptions propagate directly out of `execute_tool()`).

