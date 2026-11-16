---
doc_id: ADR-INT-0001
title: "ADR-INT-0001: Deterministic Tool Gateway & Provenance Validation Over Freeform LLM SQL/Math"
doc_type: adr
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
    - "src/intelligence/reporting/validator.py"
    - "src/shared/domain/quant.py"
related_docs:
  - INT-ADR-ROOT-001
  - INT-ARCH-GW-001
  - ADR-OVR-003
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Documented MADR 4.0 decision for ControlledToolGateway and ReportValidator aligned with ADR-OVR-003."
---

# ADR-INT-0001: Deterministic Tool Gateway & Provenance Validation Over Freeform LLM SQL/Math

## 1. Context and Problem Statement

Quantitative market investigations require accurate OHLCV retrieval, log-return/volatility/correlation math, anomaly checks, and auditable provenance. Allowing an LLM to generate raw ClickHouse/PostgreSQL SQL or compute financial math inside token generation introduces SQL injection risks, unbounded query scans, floating-point drift, and fabricated numbers.

## 2. Considered Options

1. **Option 1 — Text-to-SQL + Prompt-Based Math**: Provide database schema descriptions to the LLM and allow read-only SQL generation plus inline LLM arithmetic.
2. **Option 2 — Whitelisted Deterministic Tool Gateway + Provenance Citations**: Restrict all Agent actions to an enumerated registry (`ApprovedAgentTool`) mediated by `ControlledToolGateway`, run all financial math in Python (`src/shared/domain/quant.py`), attach UUID `ToolProvenanceMetadata`, and enforce `ReportValidator.validate_report()`.

## 3. Decision Outcome

Adopt **Option 2** (consistent with platform-wide `ADR-OVR-003`):

- All Agent tool calls MUST pass through `ControlledToolGateway.execute_tool()` enforcing whitelist membership, RBAC capability checks, `max_rows_or_periods` caps, and `asyncio.wait_for` timeouts.
- All synthesized reports MUST cite `invocation_id`s verified against `state.evidence_trail` via `ReportValidator`.
- State-mutating actions (`generate_analysis_report`, `detect_anomalies` cooldown/list appends) MUST be explicitly classified and controlled rather than masked under read-only framing.

## 4. Consequences

- **Positive (`AS-IS` Verified)**: Unapproved tool names and excessive row limits are blocked deterministically (`test_contracts_and_guardrails.py`, `test_three_planes_framework.py`), and fabricated `invocation_id`s fail `ReportValidator`.
- **Negative / Remaining Gaps (`OPEN`)**:
  - `ToolGovernancePolicy.is_read_only_market_data` currently defaults to `True` even for `generate_analysis_report` and `detect_anomalies` side effects.
  - `MarketIntelligenceGraph` hardcodes `_agent_permissions` instead of propagating caller RBAC claims.
  - `ReportValidator` checks `invocation_id` existence only and does not validate numeric equality in prose narratives.

