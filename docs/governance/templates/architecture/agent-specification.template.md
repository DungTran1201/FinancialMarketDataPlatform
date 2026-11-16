---
doc_id: TPL-ARCH-AGENT-001
title: "Template: AI Agent Runtime, Tooling & Safety Specification"
doc_type: template
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: ai-engineer
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/templates/architecture/agent-specification.template.md"
related_docs:
  - GOV-STD-AGENT-001
  - GOV-STD-SEC-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created Intelligence Plane AI/Agent specification template covering runtime, LLM bounds, tool permissions, side effects, memory, and evaluation."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Initial V2 AI Agent specification template."
---

# Template: AI Agent Runtime, Tooling & Safety Specification

Required for Intelligence Plane capabilities per [ai-agent-and-discovery-standards.md](../../standards/ai-agent-and-discovery-standards.md).

---

# AI Agent Specification: `<Agent Capability Name>`

## 1. Agent Runtime & LLM Integration `[REQUIRED]`

- **Orchestrator & Runtime**: `<Graph engine / worker entrypoint>`
- **LLM Adapter (`AS-IS` vs `TARGET`)**: `<Mock/deterministic vs external LLM provider>`
- **Execution Caps**: `max_iterations`, `token_budget`, `run_timeout_seconds`, fallback mode on LLM failure.

## 2. Workflow Graph & State Transitions `[REQUIRED]`

| Node ID | Responsibility | Allowed State Transitions | Loop / Exit Guard |
|---|---|---|---|
| `<node_1>` | `<Action>` | `<Next node(s)>` | `<Budget or validation check>` |

## 3. Tool Contracts, Permissions & Side-Effect Controls `[REQUIRED]`

| Tool Name | Mode (`READ_ONLY | WRITE`) | Required RBAC Permission | Hard Bounds (`Max Rows / Timeout`) | Side Effects & Human Approval Gate | Backing Store |
|---|---|---|---|---|---|---|
| `<tool_name>` | `READ_ONLY` | `<permission>` | `<max_rows / timeout_s>` | `None (or explicit approval rule if WRITE)` | `<store>` |

## 4. Memory, Provenance & Hallucination Controls `[REQUIRED]`

- **State & Audit Persistence**: `<Where run state & tool invocations are persisted>`
- **Provenance Enforcement**: `<How numeric calculations & report citations are deterministically validated>`

## 5. Evaluation, Observability & Safety Testing `[REQUIRED]`

- **Evaluation Criteria**: `<Deterministic checks, citation integrity, latency/token metrics>`
- **Abuse / Safety Tests**: `<Prompt injection, unauthorized tool call denial, timeout tests>`
