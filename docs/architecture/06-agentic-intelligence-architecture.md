# 06 — Agentic Intelligence Architecture

## 1. Intelligence Plane Design Philosophy

The **Intelligence Plane** integrates AI Agents into the platform to perform market analysis, quantitative research, anomaly investigation, data quality diagnostics, and structured report generation while upholding four non-negotiable engineering invariants:
1. **Zero Data Plane Dependency**: The core Data Plane and Market/Historical/Analytics APIs operate with 100% availability even if all LLM providers are offline or `agent-worker` is stopped.
2. **Deterministic Math Only**: LLMs never compute financial metrics (returns, volatility, correlations, Z-scores) via prompt arithmetic. All quantitative calculations are executed by deterministic Python/SQL tools.
3. **No Unrestricted Database or SQL Access**: The LLM cannot execute raw SQL or mutate any market data. Every data access goes through the **Controlled Tool Gateway**.
4. **Evidence-Backed Provenance**: Every figure and claim in an Agent report must reference a recorded deterministic tool execution (`invocation_id`, `source_table`, `symbol`, `time_range`, `row_count`).

See also:
- [Diagram 12: Agentic Intelligence Architecture](../diagrams/agent/12-agentic-intelligence-architecture.md)
- [Diagram 13: Agent Workflow Sequence Diagram](../diagrams/agent/13-agent-workflow-sequence.md)
- [Diagram 14: Agent Tool Access Diagram](../diagrams/agent/14-agent-tool-access.md)

---

## 2. Deployment Model & Single-Orchestrator Topology

In accordance with Section `8.1` and `8.2`, the Intelligence Plane starts with **one stateful LangGraph orchestrator (`MarketIntelligenceGraph`)** deployed inside the `agent-worker` service, rather than premature multi-agent swarms.

### 2.1. LangGraph State Machine Nodes (`MarketIntelligenceGraph`)

| Graph Node | Type | Responsibility | Failure / Guardrail Behavior |
|---|---|---|---|
| **1. `intake_and_guardrail_node`** | Deterministic | Validates input symbol(s), time window bounds, trigger type (`ON_DEMAND` vs `EVENT_TRIGGERED`), caller permissions, and initializes token/step budgets (`max_steps=6`, `max_tokens=8000`). | Immediately aborts with `VALIDATION_ERROR` if symbol is unmonitored or window exceeds limits. |
| **2. `investigation_planner_node`** | LLM + Structured Output | Inspects the user request or anomaly payload plus accumulated evidence and selects which deterministic tools to invoke next. | Uses strict JSON schema tool-calling; if LLM fails or times out ($30\text{ s}$), falls back to a deterministic default tool sequence for the anomaly type. |
| **3. `tool_gateway_executor_node`** | Deterministic | Executes the requested tools through the `ControlledToolGateway`, enforcing RBAC, timeouts ($5\text{ s}$), row caps, and recording audit rows in `agent_tool_invocations`. | Tool errors or timeouts are captured as structured tool error observations without crashing the workflow. |
| **4. `evidence_verifier_node`** | Deterministic | Checks whether sufficient quantitative and data-freshness evidence has been gathered or if another planner iteration is required (up to `max_steps=6`). | Forces transition to `report_synthesizer_node` once `step_count >= max_steps` or token budget reaches $80\%$. |
| **5. `report_synthesizer_node`** | LLM + Deterministic Validator | Synthesizes the `StructuredAnalysisReport` JSON and verifies that all cited metrics and `invocation_id` references match recorded tool outputs. | If LLM synthesis fails while deterministic tool outputs succeeded, emits a `DEGRADED_DETERMINISTIC_ONLY` report containing the exact quantitative tables without narrative prose. |

---

## 3. Controlled Tool Gateway & Catalog of 10 Deterministic Tools

All Agent data access passes through `ControlledToolGateway` (`src/agent/tools/gateway.py`).

| # | Tool Name | Backing Store | Input Schema Summary | Output Schema & Provenance | Max Window / Row Cap | Timeout |
|---|---|---|---|---|---|---|
| **1** | `get_latest_price` | Redis (Fallback: CH) | `provider: str`, `symbol: str` | `last_price`, `exchange_event_time`, `age_ms`, `is_stale`, `provenance` | 1 row | `1.5s` |
| **2** | `get_market_snapshot` | Redis (Fallback: CH) | `provider: str`, `symbol: str` | 24h `high`, `low`, `vwap`, `price_change_pct`, `best_bid`, `best_ask`, `spread_bps`, `provenance` | 1 snapshot | `2.0s` |
| **3** | `get_historical_candles` | ClickHouse (`agent_ro`) | `provider: str`, `symbol: str`, `interval: Enum`, `start_time: datetime`, `end_time: datetime`, `limit: int <= 500` | Downsampled/bounded OHLCV summary + min/max/first/last candle + `provenance` | Max `500` candles | `5.0s` |
| **4** | `get_market_statistics` | ClickHouse MV (`agent_ro`) | `provider: str`, `symbol: str`, `window: Enum['1h','24h','7d','30d']` | `vwap`, `total_base_volume`, `total_quote_volume`, `trade_count`, `taker_buy_ratio`, `provenance` | Aggregated summary | `5.0s` |
| **5** | `calculate_returns` | ClickHouse + Python Decimal/NumPy | `provider: str`, `symbol: str`, `interval: Enum`, `lookback_periods: int <= 720` | Deterministic simple & log returns, cumulative return, mean, skew, min/max drawdown + `provenance` | Max `720` periods | `5.0s` |
| **6** | `calculate_volatility` | ClickHouse + Python NumPy | `provider: str`, `symbol: str`, `interval: Enum`, `lookback_periods: int <= 720`, `annualize: bool` | Realized volatility, Parkinson high-low volatility, rolling volatility percentiles + `provenance` | Max `720` periods | `5.0s` |
| **7** | `calculate_correlation` | ClickHouse + Python NumPy | `provider: str`, `symbols: list[str] (2..10)`, `interval: Enum`, `lookback_days: int <= 90` | Pairwise Pearson & Spearman return correlation matrix, sample size `n_aligned_bars` + `provenance` | Max `10` symbols, `90` days | `8.0s` |
| **8** | `detect_anomalies` | ClickHouse (`agent_ro`) | `provider: str`, `symbol: str`, `interval: Enum`, `lookback_hours: int <= 168`, `zscore_threshold: float = 3.0` | List of deterministic return/volume/spread Z-score breaches with exact timestamps and magnitudes + `provenance` | Max `168` hours | `5.0s` |
| **9** | `get_data_freshness` | Redis + ClickHouse + PG | `provider: str`, `symbol: str` | `redis_lag_ms`, `clickhouse_lag_ms`, `last_kline_open_time`, `missing_candle_count_24h`, `status` + `provenance` | Diagnostic metadata | `3.0s` |
| **10** | `generate_analysis_report` | PostgreSQL (`agent_rw`) | `StructuredAnalysisReport` payload citing valid `invocation_id`s | Persisted report record with verified provenance citations and disclaimer | 1 report per run | `3.0s` |

---

## 4. Dual Triggering Modes & Storm Prevention

### 4.1. Mode 1 — On-Demand Analysis
- **Flow**: `Authenticated Analyst -> POST /api/v1/agents/runs -> PostgreSQL (QUEUED) -> Redis Queue -> agent-worker -> LangGraph -> Tool Gateway -> Structured Report`.
- **Guardrails**: Requires `analyst`, `operator`, or `admin` role; rate-limited to `5 requests / minute` per user; supports `Idempotency-Key` header to prevent duplicate submissions.

### 4.2. Mode 2 — Event-Triggered Anomaly Investigation
- **Flow**: `Kafka (klines/tickers) -> StatisticalAnomalyDetector (Deterministic Z-Score > 3.5 or Freshness Gap > 60s) -> Redis Cooldown Check -> Kafka (market.anomalies.v1) -> agent-worker -> Investigation Workflow -> Report / Alert`.
- **Anti-Storm Policies (Never Invoke LLM per Market Event)**:
  1. **Deterministic Pre-Filter**: Only closed candles (`is_closed = true`) or periodic 10-second statistical windows are evaluated by `StatisticalAnomalyDetector`.
  2. **Per-Symbol Cooldown Deduplication**: Before emitting to `market.anomalies.v1`, the detector sets `SET agent:cooldown:{provider}:{symbol}:{detector_name} 1 NX EX 900` (15-minute cooldown). Subsequent breaches within those 15 minutes increment a Prometheus counter without triggering additional LLM runs.
  3. **Global Concurrency & Daily Token Cap**: `agent-worker` enforces `MAX_CONCURRENT_AGENT_RUNS = 2` and a daily token circuit breaker (`AGENT_DAILY_TOKEN_BUDGET`).

