---
doc_id: CAP-INT-ORC-REQ-001
title: "Capability Specification: Market Intelligence Workflow & Tool Gateway"
doc_type: specification
plane: intelligence-plane
scope_level: capability
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
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
    - "src/intelligence/tools/contracts.py"
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/reporting/validator.py"
related_docs:
  - CAP-INT-ORC-DOC-001
  - CAP-INT-ORC-NFR-001
  - CAP-INT-ORC-COMP-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Authored functional requirements and business rules grounded in src/intelligence/ AS-IS and TARGET contracts."
---

# Capability Specification: Market Intelligence Workflow & Tool Gateway (`CAP-INT-ORC-001`)

## 1. Business Rules

| Rule ID | Rule Statement | `AS-IS` Status | Code Reference |
|---|---|---|---|
| `BR-INT-001` | Investigations MUST be restricted to monitored catalog symbols. | `PARTIALLY_IMPLEMENTED` (hardcoded 5-symbol tuple) | `graph.py:106-112` |
| `BR-INT-002` | All quantitative metrics MUST be computed by deterministic tools, never in LLM prompt text. | `IMPLEMENTED` | `ADR-OVR-003`, `runtime.py` |
| `BR-INT-003` | Every tool call MUST pass whitelist, permission, row-limit, and timeout checks. | `IMPLEMENTED` | `gateway.py:44-97` |
| `BR-INT-004` | Every synthesized report MUST cite at least one valid `invocation_id` from `evidence_trail`. | `IMPLEMENTED` | `validator.py:19-31` |
| `BR-INT-005` | Planning loops MUST terminate at `max_iterations` (`6`) or `80%` of `token_budget` (`6400`). | `PARTIALLY_IMPLEMENTED` (Node 5 runs post-budget) | `investigation.py:37-43` |

## 2. Functional Requirements

| Req ID | Requirement | `AS-IS` Implementation | Target Expectation |
|---|---|---|---|
| `FR-INT-001` | Execute a 5-node market investigation workflow (`intake_and_guardrail` -> `investigation_planner` -> `tool_gateway_executor` -> `evidence_verifier` -> `report_synthesizer`). | `IMPLEMENTED` (pure Python `while` loop) | Stateful LangGraph execution in isolated `agent-worker` |
| `FR-INT-002` | Dispatch all 10 `ApprovedAgentTool` operations through `ControlledToolGateway` with `ToolProvenanceMetadata`. | `IMPLEMENTED` (in-memory stores) | Real Redis, ClickHouse, and PostgreSQL store bindings |
| `FR-INT-003` | Validate synthesized reports via `ReportValidator.validate_report()` before marking run `COMPLETED`. | `IMPLEMENTED` (citation ID check only) | Add numeric consistency check between prose and tool payloads |
| `FR-INT-004` | Persist `StructuredAnalysisReport` via `generate_analysis_report` keyed by `run_id`. | `SIMULATED` (in-memory `runtime.reports` dict) | Durable PostgreSQL `agent_runs.structured_report` JSONB |
| `FR-INT-005` | Reject unmonitored symbols cleanly with `status="FAILED"` and error payload. | `IMPLEMENTED` | Dynamic lookup against `monitored_instruments` catalog |
| `FR-INT-006` | Support `EVENT_TRIGGERED` investigations from Kafka `market.anomalies.v1`. | `NOT_IMPLEMENTED` | Autonomous `agent-worker` Kafka consumer with cooldown |

