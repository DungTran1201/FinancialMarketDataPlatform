---
doc_id: INT-ARCH-LLM-001
title: "Model Integration Architecture"
doc_type: architecture
plane: intelligence-plane
scope_level: plane
status: DRAFT
implementation_status: SIMULATED
version: "2.0.0"
owner_role: ai-engineer
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/orchestrator/graph.py"
    - "src/intelligence/workflows/investigation.py"
    - ".env.example"
related_docs:
  - INT-ARCH-ROOT-001
  - INT-ARCH-001
  - INT-ARCH-RT-001
  - INT-ARCH-SEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Documented DeterministicMockLLMAdapter AS-IS behavior vs TARGET external LLM provider adapter boundary, token accounting, timeouts, retries, and secret handling."
---

# Model Integration Architecture

## 1. Model Adapter Interface & Responsibilities (`AS-IS`)

`MarketIntelligenceGraph.__init__` accepts `llm_adapter: DeterministicMockLLMAdapter | None = None` (`src/intelligence/orchestrator/graph.py:105`). There is no formal Python `Protocol` or abstract base class yet; the implicit contract requires two synchronous methods:

1. **`plan_tool_sequence(state: AgentWorkflowState) -> tuple[list[dict[str, Any]], int]`**:
   - Returns `(planned_tools, tokens_consumed)`.
   - `DeterministicMockLLMAdapter` (`AS-IS`): On `current_iteration == 0`, returns a fixed list of **7 read/analytics tool calls** (`get_latest_price`, `get_market_snapshot`, `get_historical_candles`, `calculate_returns`, `calculate_volatility`, `detect_anomalies`, `get_data_freshness`) and `420` tokens. On any subsequent iteration, returns `([], 110)`.
   - **Important**: `DeterministicMockLLMAdapter` ignores `state.prompt_summary` entirely.
2. **`synthesize_narrative(state: AgentWorkflowState) -> tuple[dict[str, Any], int]`**:
   - Iterates over `state.evidence_trail`, maps each `ToolExecutionEnvelope` into `quantitative_evidence[tool_name]`, extracts anomaly alerts when `detect_anomalies` returns `anomaly_detected=True`, builds `provenance_citations` from `ToolProvenanceMetadata`, and returns `(report_dict, 540)`.

## 2. Mock Adapter vs. External Provider Adapters (`TARGET`)

| Capability | `AS-IS` (`DeterministicMockLLMAdapter`) | `TARGET` (External LLM Provider Adapter) |
|---|---|---|
| **Provider Configuration** | `.env.example` declares `LLM_PROVIDER=mock`, `LLM_API_KEY=...`; **neither is read by `PlatformConfig`** | `PlatformConfig` loads provider name, model ID, and secret API key at runtime |
| **SDK Dependencies** | Zero external LLM SDKs in `pyproject.toml` | Dedicated async HTTP/SDK adapter behind an explicit `ModelAdapterPort` `Protocol` |
| **Prompt Construction** | Not constructed (`prompt_summary` unused) | Structured system prompt + sanitized `symbol`/`prompt_summary` + tool JSON schemas |
| **Planner Output** | Hardcoded 7-tool plan | Structured tool-calling output validated against `ApprovedAgentTool` |
| **Narrative Synthesis** | Fixed template string (`"Deterministic market intelligence report..."`) | LLM-synthesized narrative constrained to cited `evidence_trail` facts |

## 3. Prompt Construction Boundary (`TARGET`)

When external LLMs are introduced, prompt construction MUST enforce strict separation between:
- **Trusted System Instructions**: Role, tool whitelist, prohibition on inventing metrics.
- **Untrusted User Input**: `prompt_summary` (validated/length-bounded in Plane B, delimited in prompt).
- **Untrusted Market/Exchange Text**: Any string fields returned from external feeds or tool payloads MUST be treated as data, never executable instructions.

## 4. Token Usage, Timeouts, Rate Limiting & Error Handling

- **Token Accounting**:
  - `AS-IS`: Fixed `420` (plan) + `540` (synthesis) = `960` tokens per standard 1-iteration run. No prompt/completion split.
  - `TARGET`: Capture actual `prompt_tokens` and `completion_tokens` from provider usage metadata and persist to `agent_runs.token_usage` (`deploy/postgres/init/01_schema.sql`).
- **Provider Timeout, Rate Limiting & Retry/Fallback**:
  - `AS-IS`: Synchronous in-memory calls with zero network latency; no provider timeout, rate limiter, retry, or fallback exists.
  - `TARGET`: Per-LLM-call timeout, exponential backoff with jitter on `429`/`5xx`, circuit breaker, and deterministic fallback to `DeterministicMockLLMAdapter` or graceful `FAILED` state.
- **Data Privacy & Secret Handling**:
  - `AS-IS`: No external egress occurs; `LLM_API_KEY` in `.env.example` is a placeholder.
  - `TARGET`: API keys MUST never be logged, serialized into `AgentWorkflowState`, or returned in `StructuredAnalysisReport`; PII/internal credentials MUST be stripped before any external LLM payload leaves Plane C.

