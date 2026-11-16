---
doc_id: INT-DOM-ORC-001
title: "Domain: Agent Orchestration & Tools"
doc_type: index
plane: intelligence-plane
scope_level: domain
domain: agent-orchestration-and-tools
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
    - "src/intelligence/tools/gateway.py"
related_docs:
  - INT-ROOT-001
  - INT-DOM-ORC-SPEC-001
  - CAP-INT-ORC-DOC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Created Agent Orchestration & Tools domain index."
---

# Domain: Agent Orchestration & Tools

- **Specification**: [domain-specification.md](domain-specification.md) (`INT-DOM-ORC-SPEC-001`)

## Capabilities

| Capability ID | Capability | Risk Tier | `AS-IS` Status |
|---|---|---|---|
| `CAP-INT-ORC-001` | [Market Intelligence Workflow & Tool Gateway](capabilities/market-intelligence-workflow-and-tool-gateway/README.md) | `HIGH_CRITICAL` | `SIMULATED` |

