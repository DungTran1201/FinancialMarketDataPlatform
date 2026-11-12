# ADR-006: Isolated Agentic Intelligence Plane, LangGraph Orchestration & Deterministic Tool Gateway

- **Status**: Accepted
- **Date**: 2026-11-12
- **Deciders**: System, Backend & AI Architecture Team

---

## 1. Decision Title

Deploy the AI capability as an **Isolated Intelligence Plane** orchestrated by a **Single Stateful LangGraph Orchestrator** that accesses platform data exclusively through a **Read-Only Deterministic Tool Gateway**, supporting both **On-Demand** and **Threshold-Filtered Event-Triggered** execution modes.

---

## 2. Context

The platform integrates AI Agents to perform market analysis, quantitative analysis, anomaly investigation, data quality investigation, and structured report generation. However, LLMs are inherently non-deterministic, prone to arithmetic hallucinations, subject to high latency ($2-30\text{ s}$) and external rate limits, and present security risks (such as SQL injection or unbounded queries) if granted direct database access.

---

## 3. Problem Statement

How do we integrate stateful AI Agent workflows into a financial market data platform such that:
1. All financial and quantitative metrics are 100% mathematically accurate and reproducible,
2. Agents cannot mutate financial data, execute arbitrary SQL, or overload databases,
3. Agent failures or LLM provider outages have zero impact on real-time market ingestion or API serving, and
4. We avoid invoking expensive LLM calls on high-frequency streaming events?

---

## 4. Selected Option

### 4.1. Single LangGraph Orchestrator with Specialized Node Graph
- Start with **one stateful LangGraph workflow orchestrator** (`MarketIntelligenceGraph`) rather than a complex multi-agent swarm.
- The graph consists of explicit deterministic and reasoning nodes:
  `Intake & Guardrail Node` $\rightarrow$ `Context & Tool Planner Node` $\rightarrow$ `Deterministic Tool Execution Node` $\rightarrow$ `Evidence Verification Node` $\rightarrow$ `Structured Report Synthesis Node`.
- Workflow checkpoint state, tool call audit logs, and token consumption are persisted in **PostgreSQL** (`agent_runs`, `agent_tool_invocations`).

### 4.2. Controlled Read-Only Tool Gateway (No Direct DB/SQL Access by LLM)
- The LLM is **never** given raw SQL execution tools or direct database credentials.
- All data retrieval and quantitative calculations pass through the **Tool Gateway**, which exposes 10 strictly typed tools:
  1. `get_latest_price`
  2. `get_market_snapshot`
  3. `get_historical_candles`
  4. `get_market_statistics`
  5. `calculate_returns`
  6. `calculate_volatility`
  7. `calculate_correlation`
  8. `detect_anomalies`
  9. `get_data_freshness`
  10. `generate_analysis_report`
- **Deterministic Computation Rule**: All arithmetic (log/simple returns, annualized realized volatility, Pearson/Spearman correlation, Z-score anomaly thresholds) is computed by deterministic Python/NumPy/ClickHouse SQL routines inside the tools. The LLM's role is strictly to plan tool invocations, synthesize findings, and explain the deterministic evidence.

### 4.3. Dual Triggering Modes with Deterministic Pre-Filtering
1. **On-Demand Mode**: Authenticated users (`analyst`+) submit an asynchronous analysis request via `POST /api/v1/agents/runs` (`202 Accepted`), optionally streaming progress via SSE (`GET /api/v1/agents/runs/{run_id}/events`).
2. **Event-Triggered Mode**: A lightweight deterministic statistical detector evaluates closed candles/metrics and publishes to `market.anomalies.v1` **only when** a threshold is breached and deduplicated over a cooldown window (e.g., max 1 trigger per symbol per 15 minutes). The `agent-worker` consumes `market.anomalies.v1` and runs an automated investigation workflow.

---

## 5. Alternative Options Considered

### Alternative A: Text-to-SQL Agent with Direct ClickHouse / PostgreSQL Execution
- **Description**: Allow the LLM to write and execute arbitrary `SELECT` queries against ClickHouse and PostgreSQL.
- **Rejection Reason**: Violates Section 8.3 and 8.4 ("The LLM must not have unrestricted database access. It must not execute arbitrary unrestricted SQL"). Text-to-SQL risks full-table scans, syntax errors, schema leakage, and inconsistent metric definitions (e.g., inconsistent volatility annualization factors).

### Alternative B: Multi-Agent Swarm (Separate Autonomous Agents for Market, Quant, Anomaly, Data Quality, and Writer)
- **Description**: Deploy 5 independent LLM agents communicating via natural language messages.
- **Rejection Reason**: Violates Section 8.2 ("Do not create multiple independent Agents without a clear specialization or isolation requirement. Start with one orchestrator and well-defined analytical capabilities"). Multi-agent chat loops multiply token consumption and latency by $3\times - 5\times$ while reducing determinism.

### Alternative C: Synchronous Agent Execution Inside FastAPI Request Handlers
- **Description**: Execute the LangGraph workflow synchronously during `POST /api/v1/agents/analyze` and return the final report in the HTTP response.
- **Rejection Reason**: Violates Section 7.4 and 8.4. Multi-step LLM and analytical workflows take $4-35\text{ seconds}$, causing HTTP gateway timeouts, holding open connection pools, and making workflow recovery impossible on client disconnect.

---

## 6. Decision Rationale

- **LangGraph** provides explicit state schema definition, conditional edges, bounded retry loops, and checkpoint persistence without opaque prompt-chaining magic.
- **The Tool Gateway** acts as a security, cost, and correctness firewall: every tool validates inputs via Pydantic, enforces hard row/time-window limits, executes with a strict timeout ($3-8\text{ s}$), uses a dedicated read-only database user (`agent_ro`), and attaches **Data Provenance Metadata** (`source_table`, `symbol`, `start_time`, `end_time`, `row_count`, `query_hash`) to every tool output.

---

## 7. Benefits

- **Zero Hallucinated Math**: Financial figures in every report trace directly to deterministic tool outputs recorded in `agent_tool_invocations`.
- **Complete Plane Isolation**: If the LLM API key is missing, rate-limited, or timing out, only `agent-worker` tasks fail gracefully; real-time ingestion and API serving are completely untouched.
- **Full Auditability**: Every prompt, tool input, tool output provenance, latency, and token count is logged in PostgreSQL and exposed to Prometheus.

---

## 8. Drawbacks

- Adding a new analytical capability requires writing and testing a deterministic tool in Python/SQL rather than letting the LLM improvise arbitrary queries.
- Asynchronous execution requires clients to poll `/api/v1/agents/runs/{run_id}` or subscribe to the SSE progress endpoint.

---

## 9. Architectural Limitations

- Narrative explanations generated by the LLM remain probabilistic interpretations and must always carry a structured provenance footer citing the exact deterministic tool calls and time ranges used.
- External LLM provider latency and availability are outside platform control; workflows enforce a hard max step count (`max_iterations = 6`) and total run timeout (`90s`).

---

## 10. Operational Implications

- Configure rate limits and token budget circuit breakers (`AGENT_MAX_TOKENS_PER_RUN=8000`, `AGENT_ANOMALY_COOLDOWN_SECONDS=900`).
- Provide a deterministic `MockLLMProviderAdapter` / offline fallback mode so local integration tests and CI pipelines can verify the entire LangGraph orchestration and Tool Gateway without spending external LLM tokens.

---

## 11. Consequences

- All Agent reports must conform to the `StructuredAnalysisReport` schema containing `summary`, `quantitative_evidence[]`, `anomalies_detected[]`, `data_quality_status`, `provenance_citations[]`, and `limitations_disclaimer`.

---

## 12. Conditions That Could Invalidate This Decision

1. If distinct regulatory or organizational teams require separate security clearances and completely disjoint tool catalogs (e.g., an internal Infrastructure Ops Agent vs. an external Client Research Agent), the single orchestrator can be split into two isolated LangGraph graphs sharing the same Tool Gateway framework.

