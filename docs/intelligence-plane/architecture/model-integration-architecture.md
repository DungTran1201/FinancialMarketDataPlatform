---
doc_id: INT-ARCH-LLM-001
title: "Model Integration & Prompt Boundary Architecture"
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
    - "src/shared/config/settings.py"
    - ".env.example"
related_docs:
  - INT-ARCH-ROOT-001
  - INT-ARCH-001
  - INT-ARCH-RT-001
  - INT-ARCH-SEC-001
  - ADR-OVR-003
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Documented DeterministicMockLLMAdapter AS-IS behavior vs TARGET external LLM adapter contract, prompt boundaries, rate limits, timeouts, and secret handling."
---

# Model Integration & Prompt Boundary Architecture

## 1. Scope and Adapter Abstraction (`AS-IS` vs `TARGET`)

### 1.1 Scope

This document specifies how the Intelligence Plane interfaces with Language Model (LLM) providers for tool planning and narrative report synthesis, while prohibiting direct model access to databases or financial math (`ADR-OVR-003`).

### 1.2 Adapter Boundary (`AS-IS` Reality)

In `src/intelligence/orchestrator/graph.py:14-97` and `105`:

- **Explicit Interface Gap (`AS-IS`)**: There is **no** formal Python `Protocol` or abstract base class for LLM adapters yet (`MarketIntelligenceGraph.__init__` accepts `llm_adapter: DeterministicMockLLMAdapter | None = None`).
- **Single Concrete Adapter**: Only `DeterministicMockLLMAdapter` exists. It exposes two synchronous methods:
  1. `plan_tool_sequence(state: AgentWorkflowState) -> tuple[list[dict[str, Any]], int]`
  2. `synthesize_narrative(state: AgentWorkflowState) -> tuple[dict[str, Any], int]`
- **Unwired Environment Configuration**: `.env.example:86-90` declares `LLM_PROVIDER=mock`, `LLM_MODEL_NAME=gpt-4o-mini`, and `LLM_API_KEY=`, but `src/shared/config/settings.py` does not load any of these three environment variables, and `pyproject.toml` contains zero external LLM SDK dependencies (`openai`, `anthropic`, `google-genai`, `langchain-*`).

## 2. Context: Planner vs Narrative Synthesis Responsibilities

| Capability | Planner Role (`plan_tool_sequence`) | Synthesizer Role (`synthesize_narrative`) |
|---|---|---|
| **`AS-IS` (`DeterministicMockLLMAdapter`)** | On `current_iteration == 0`, returns a fixed list of **7** tool calls (`get_latest_price`, `get_market_snapshot`, `get_historical_candles(interval="1m", limit=60)`, `calculate_returns(lookback_periods=30)`, `calculate_volatility(lookback_periods=30)`, `detect_anomalies(lookback_periods=24)`, `get_data_freshness`) and fixed token cost `420`. On `current_iteration > 0`, returns `([], 110)`. Completely ignores `state.prompt_summary`. | Iterates over `state.evidence_trail`, maps tool results into `quantitative_evidence`, extracts anomaly alert strings when `detect_anomalies` returns `anomaly_detected=True`, maps all envelopes into `provenance_citations`, sets static `"data_quality_status": "HEALTHY"`, formats `"summary"`, appends `limitations_disclaimer` mentioning `LLM narrative adapter=mock`, and charges fixed `540` tokens. |
| **`TARGET` (External Provider Adapter)** | Inspects `state.prompt_summary`, `state.symbol`, prior `evidence_trail`, and remaining budget; selects a bounded next batch of whitelisted tools (`ApprovedAgentTool` + schema-valid params) via structured tool-calling / JSON mode. | Synthesizes analytical markdown/narrative strictly grounded in `evidence_trail` JSON payloads, citing exact `invocation_id`s without recomputing math or altering tool numbers. |

## 3. Building Blocks: External Provider Requirements (`TARGET`)

Before enabling any non-mock `LLM_PROVIDER` (`openai`, `anthropic`, `gemini`, or self-hosted vLLM), the following boundaries MUST be implemented (`OPEN` architectural tasks):

### 3.1 Formal Adapter Protocol & Provider Isolation

- Define an async `LLMAdapterPort` (`Protocol`) inside `src/intelligence/orchestrator/` separating planner and synthesizer invocations, keeping external HTTP/SDK clients isolated in a provider adapter module so `MarketIntelligenceGraph` remains provider-agnostic.

### 3.2 Prompt Construction & Injection Boundary

- **Data-Plane Isolation**: Market strings or `prompt_summary` inputs injected into LLM prompts MUST be delimited as untrusted user/external data (`<user_request>`, `<tool_evidence>`) separate from immutable system instructions.
- **No Raw Secret or Internal Topology Leakage**: Prompts MUST NEVER include `JWT_SECRET_KEY`, database credentials, `LLM_API_KEY`, or internal container hostnames/IPs.

### 3.3 Token Usage, Provider Timeouts, Rate Limiting & Retries

| Control | `AS-IS` State | `TARGET` Requirement |
|---|---|---|
| **Token Accounting** | Fixed synthetic integers (`420`, `110`, `540`); total typical run = `960` tokens. | Record real provider `prompt_tokens` + `completion_tokens` into `AgentWorkflowState.tokens_consumed` and Postgres `agent_runs.token_usage` JSONB (`prompt_tokens`, `completion_tokens`, `total_tokens`). |
| **Provider Call Timeout** | Synchronous CPU dict assembly (`<1ms`); no network timeout. | Explicit per-LLM HTTP request timeout bounded within `AGENT_RUN_TIMEOUT_SECONDS` (`90s` in `.env.example`, exact per-call split `OPEN`). |
| **Provider Rate Limiting & Retries** | None (`AS-IS` offline). | Bounded exponential backoff with jitter on `HTTP 429` / transient `5xx` only; respect `token_budget` and run timeout before retrying. |
| **Fallback & Outage Handling** | Always succeeds offline (`mock`). | On external LLM outage, timeout, or malformed JSON output after bounded retries, MUST degrade safely either to deterministic template summary (clearly flagged in `limitations_disclaimer`) or transition `AgentWorkflowState.status = "FAILED"` with explicit error metadata — never fabricating metrics. |

### 3.4 Data Privacy and Secret Handling (`LLM_API_KEY`)

- **Public Market Data Only (`AS-IS`)**: `evidence_trail` contains public spot market quotes/candles/analytics and zero PII.
- **User Prompt Sensitivity**: Analyst `prompt_summary` text sent to third-party LLM APIs MAY carry proprietary trading hypotheses; deployment policy for external data retention / zero-data-retention agreements is **`OPEN`** pending stakeholder provider selection (`BR-SYS-003` in `OVR-REQ-001`).
- **Secret Hygiene**: `LLM_API_KEY` MUST be injected solely via environment/secret manager, excluded from logs, exception tracebacks, `limitations_disclaimer`, and Postgres `agent_runs` columns.

