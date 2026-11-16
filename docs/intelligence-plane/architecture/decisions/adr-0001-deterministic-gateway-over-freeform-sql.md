---
doc_id: ADR-INT-0001
title: "ADR-INT-0001: Deterministic Controlled Tool Gateway Over Freeform LLM SQL"
doc_type: adr
plane: intelligence-plane
scope_level: plane
status: DRAFT
implementation_status: IMPLEMENTED
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
related_docs:
  - INT-ADR-ROOT-001
  - INT-ARCH-001
  - INT-ARCH-GW-001
  - ADR-OVR-003
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Documented MADR 4.0.0 decision enforcing ControlledToolGateway whitelist over free-form SQL or prompt arithmetic."
---

# ADR-INT-0001: Deterministic Controlled Tool Gateway Over Freeform LLM SQL

## 1. Context and Problem Statement `[REQUIRED]`

Allowing an LLM to generate raw SQL against ClickHouse/PostgreSQL or perform floating-point financial calculations in prompt text introduces SQL injection, unbounded table-scan DoS, silent IEEE-754 rounding drift, and unverifiable hallucinated numbers.

## 2. Decision Drivers `[REQUIRED]`

- Prevent arbitrary query execution and unapproved data access.
- Guarantee deterministic quantitative metrics (log returns, realized volatility, Pearson correlation, Z-score anomalies).
- Attach verifiable `invocation_id` provenance to every data point used in reports.

## 3. Considered Options `[REQUIRED]`

1. **Free-form LLM SQL + Prompt Math**: Provide ClickHouse/Postgres read-only credentials to an LLM SQL tool.
2. **Whitelisted Deterministic `ControlledToolGateway`**: Restrict the orchestrator to 10 enumerated `ApprovedAgentTool` contracts mediated by `ControlledToolGateway` with RBAC, row caps, timeouts, and `ReportValidator`.

## 4. Decision Outcome `[REQUIRED]`

Adopt **Option 2 (`ControlledToolGateway`)**, reinforcing platform-level [ADR-OVR-003](../../../overview/architecture/decisions/adr-0003-decimal-precision-and-deterministic-tool-gateway.md):
- Every tool call MUST pass `ApprovedAgentTool` enum validation, `required_permission` check, `max_rows_or_periods` check, and `asyncio.wait_for` timeout.
- Every report MUST pass `ReportValidator.validate_report()` verifying non-empty `provenance_citations` matching `evidence_trail` `invocation_id`s.

## 5. Consequences `[REQUIRED]`

- **Positive**: Deterministic quant math, zero raw SQL exposure, verified in `tests/contract/test_contracts_and_guardrails.py` and `tests/integration/test_three_planes_framework.py`.
- **Negative / Residual Gaps**: Requires explicit handler registration per tool; `ReportValidator` does not yet cross-check numeric values in narrative prose (`GAP-INT-006`), and `generate_analysis_report` / `detect_anomalies` have write side effects despite read-only framing (`GAP-INT-005`).

