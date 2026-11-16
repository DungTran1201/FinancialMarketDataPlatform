---
doc_id: ADR-OVR-003
title: "ADR-OVR-003: Fixed-Point Decimal Financial Math & Deterministic Tool Gateway"
doc_type: adr
plane: platform
scope_level: platform
status: IN_REVIEW
implementation_status: IMPLEMENTED
version: "2.0.0"
owner_role: data-architect
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/shared/domain/primitives.py"
    - "src/shared/domain/quant.py"
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/reporting/validator.py"
related_docs:
  - OVR-ADR-ROOT-001
  - OVR-REQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Recorded financial precision and AI determinism constraints implemented across shared domain and tool gateway."
---

# ADR-OVR-003: Fixed-Point Decimal Financial Math & Deterministic Tool Gateway

## 1. Context and Problem Statement `[REQUIRED]`

Financial price aggregation (OHLCV, VWAP, returns, liquidity) suffers silent rounding drift under binary IEEE-754 floats, while LLM-generated market narratives risk hallucinated metrics, SQL injection, or unverified arithmetic if models query stores or compute numbers in prompt text.

## 2. Considered Options `[REQUIRED]`

1. **Float JSON + Direct LLM SQL/Math**: Accept `float` prices and grant the LLM SQL read access to compute metrics.
2. **Fixed-Point `Decimal` Storage/Wire + Deterministic Tool Gateway**: Enforce `DecimalPrice` / string decimals (`Decimal128(18)` in ClickHouse DDL) and restrict all LLM data/math access exclusively through whitelisted deterministic Python tools with mandatory UUID provenance validation.

## 3. Decision Outcome `[REQUIRED]`

Adopt **Option 2**:

- Prices, volumes, and Gold OHLCV/liquidity metrics MUST serialize as decimal strings and compute in `Decimal` (note: `compute_deterministic_log_returns`, `compute_deterministic_realized_volatility`, and `GoldLayerMartEngine.materialize_realized_volatility_mart` convert ratios via `math.log`/`math.sqrt` floats for transcendental steps only).
- AI Agents MUST obtain every quantitative fact exclusively via `ControlledToolGateway` (`ApprovedAgentTool`) and pass `ReportValidator.validate_report()` verifying non-empty matching `invocation_id` citations.

## 4. Consequences `[REQUIRED]`

- **Positive**: Reproducible OHLCV/VWAP values and verifiable provenance audit trail (`test_contracts_and_guardrails.py`, `test_medallion_quality_gates.py`).
- **Residual Caveat**: `ReportValidator` currently verifies `invocation_id` existence in `evidence_trail`, not deep numeric equality between prose strings and tool output payloads (`GAP-INT`).
