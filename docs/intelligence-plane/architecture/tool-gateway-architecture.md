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
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/tools/contracts.py"
    - "src/intelligence/tools/gateway.py"
    - "src/serving/infrastructure/runtime.py"
related_docs:
  - INT-ARCH-ROOT-001
  - INT-ARCH-001
  - INT-ARCH-SEC-001
  - INT-CTR-ROOT-001
  - DIAG-INT-GW-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Documented all 10 tools, invocation lifecycle, validation gaps, policy vs actual backing store discrepancies, and side-effect audit."
---

# Controlled Tool Gateway Architecture

Derived trust boundary diagram: [tool-gateway-boundaries.md](diagrams/tool-gateway-boundaries.md) (`DIAG-INT-GW-001`). Canonical machine-readable registry: [tool-contracts.yaml](../shared-contracts/tool-contracts.yaml).

## 1. Approved Tool Registry & Policy vs. Actual Reality

`ControlledToolGateway` (`src/intelligence/tools/gateway.py`) mediates every tool call via `ApprovedAgentTool` and `APPROVED_TOOL_POLICIES` (`src/intelligence/tools/contracts.py`). Concrete handlers are registered by `PlatformRuntimeContainer._register_all_ten_deterministic_tools()` (`src/serving/infrastructure/runtime.py:401-553`).

| # | Tool Name | Policy Permission | Policy Declared `backing_store` | Actual `AS-IS` Backing Store (`runtime.py`) | Max Rows / Periods | Timeout (s) | Actual Side Effects (`AS-IS`) |
|---|---|---|---|---|---|---|---|
| 1 | `get_latest_price` | `market:read` | `redis_with_clickhouse_fallback` | `self.latest_price_handler` (in-memory Hot/OLAP fallback) | 1 | 1.5 | None (Read-only) |
| 2 | `get_market_snapshot` | `market:read` | `redis_with_clickhouse_fallback` | `self.hot_redis_projector.get_hot_snapshot()` (in-memory dict) | 1 | 2.0 | None (Read-only) |
| 3 | `get_historical_candles` | `historical:read` | `clickhouse_agent_ro` | `self.clickhouse_sink.query_klines()` (in-memory OLAP sink) | 500 | 5.0 | None (Read-only) |
| 4 | `get_market_statistics` | `analytics:read` | `clickhouse_mv_agent_ro` | `self.clickhouse_sink.compute_aggregated_statistics()` | 1 | 5.0 | None (Read-only) |
| 5 | `calculate_returns` | `analytics:read` | `clickhouse_agent_ro_deterministic_math` | `clickhouse_sink` + `compute_deterministic_log_returns()` | 720 | 5.0 | None (Read-only) |
| 6 | `calculate_volatility` | `analytics:read` | `clickhouse_agent_ro_deterministic_math` | `clickhouse_sink` + `compute_deterministic_realized_volatility()` | 720 | 5.0 | None (Read-only) |
| 7 | `calculate_correlation` | `analytics:read` | `clickhouse_agent_ro_deterministic_math` | `clickhouse_sink` + `compute_deterministic_pearson_correlation()` | 2160 | 8.0 | None (Read-only) |
| 8 | `detect_anomalies` | `analytics:read` | `clickhouse_agent_ro_deterministic_math` | `clickhouse_sink` + `self.anomaly_detector.evaluate_series()` | 168 | 5.0 | **WRITE**: Appends to `self.detected_anomalies` + updates detector cooldown state |
| 9 | `get_data_freshness` | `market:read` | `redis_and_clickhouse_metadata` | `self.latest_price_handler.handle()` lag check | 1 | 3.0 | None (Read-only) |
| 10 | `generate_analysis_report` | `agent:trigger` | `postgres_agent_rw` | `self.reports[run_id] = StructuredAnalysisReport(...)` (in-memory dict) | 1 | 3.0 | **WRITE**: Mutates `runtime.reports[run_id]` (Policy flag `is_read_only_market_data` erroneously defaults to `True`) |

## 2. Tool Invocation Lifecycle

1. **Whitelist Validation**: `ApprovedAgentTool(tool_name)` raises `UnauthorizedToolAccessError` for any unknown tool name.
2. **Permission Check**: Checks `policy.required_permission in granted_permissions`; raises `UnauthorizedToolAccessError` on mismatch.
3. **Query Bounds Check**: Computes `requested_limit = int(params.get("limit") or params.get("lookback_periods") or 1)` and raises `ToolQueryLimitExceededError` if `requested_limit > policy.max_rows_or_periods`.
   - *Gap*: Negative/zero limits, invalid `symbols` array lengths, and full JSON schema validation of `params` are **not** enforced by the gateway.
4. **Handler Dispatch & Timeout**: Looks up `self._handlers.get(approved_tool)`. If missing, returns `{"status": "stub_ok", "tool": ...}`. Otherwise awaits `asyncio.wait_for(handler(params), timeout=policy.timeout_seconds)`.
5. **Provenance & Normalization**: Wraps output in `ToolExecutionEnvelope(status="SUCCESS", data=result_data, provenance=ToolProvenanceMetadata(...))` with a freshly generated `uuid.uuid4()` `invocation_id`.
6. **Audit Behavior**: Appends `envelope` to in-memory `self._audit_log`. It is **not** persisted to PostgreSQL `agent_tool_invocations` (`AS-IS`).

## 3. Error Propagation & Side-Effect Classification

- `UnauthorizedToolAccessError`, `ToolQueryLimitExceededError`, and `asyncio.TimeoutError` propagate directly to the caller; `ToolExecutionEnvelope` statuses `TIMEOUT`, `VALIDATION_ERROR`, and `PERMISSION_DENIED` are declared in comments (`contracts.py:130`) but are **never constructed** in `gateway.py`.
- **Read-Only vs. Write-Capable**: Tools 1–7 and 9 are read-only. Tool 10 (`generate_analysis_report`) is explicitly write-capable (`postgres_agent_rw` target), and Tool 8 (`detect_anomalies`) has stateful side effects (`self.detected_anomalies.append()`), creating a policy metadata mismatch (`is_read_only_market_data=True` by default).

