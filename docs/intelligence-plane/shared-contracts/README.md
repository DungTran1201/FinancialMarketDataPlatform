---
doc_id: INT-CTR-ROOT-001
title: "Intelligence Plane Shared Contracts Index"
doc_type: index
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
    - "src/intelligence/workflows/investigation.py"
    - "deploy/postgres/init/01_schema.sql"
related_docs:
  - INT-ROOT-001
  - INT-ARCH-GW-001
  - CAP-INT-ORC-DOC-001
  - CAP-INT-ORC-ERR-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Indexed canonical tool-contracts.yaml and data-contract.yaml for Intelligence Plane."
---

# Intelligence Plane Shared Contracts Index

This directory is the **single authoritative owner** of Intelligence Plane internal tool contracts and state/persistence data contracts. Other documents MUST link here rather than duplicating tool input/output schemas.

## 1. Canonical Contract Files

| Contract File | Contract ID | Scope & Ownership | `AS-IS` Status |
|---|---|---|---|
| [tool-contracts.yaml](tool-contracts.yaml) | `TC-INT-TOOLS-001` | All 10 `ApprovedAgentTool` definitions: schemas, permissions, declared vs actual stores, bounds, timeouts, side effects, provenance, and errors | `PARTIALLY_IMPLEMENTED` (runtime closures in-memory; schema validation unimplemented in gateway) |
| [data-contract.yaml](data-contract.yaml) | `DC-INT-STATE-001` | Canonical state & persistence contracts (`AgentWorkflowState`, `ToolExecutionEnvelope`, `StructuredAnalysisReport`, `agent_runs`, `agent_tool_invocations`) | `SIMULATED` (in-memory dicts `AS-IS`; Postgres DDL unwired) |

## 2. Cross-Plane Contract References (Consumed, Not Owned Here)

- **HTTP API Contracts (`/api/v1/agents/*`, `/api/v1/reports/*`)**: Owned by Application Plane `CAP-APP-AGT-001` ([openapi.yaml](../../application-plane/domains/agent-experience-and-reporting/capabilities/agent-run-and-report-portal/contracts/openapi.yaml)).
- **Anomaly Event Schema (`market.anomalies.v1`)**: Owned by Data Plane ([asyncapi.yaml](../../data-plane/shared-contracts/asyncapi.yaml)).

