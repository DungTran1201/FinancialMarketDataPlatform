---
doc_id: GOV-STD-AGENT-001
title: "AI/Agent Documentation Standards & Agent Discovery Workflow"
doc_type: standard
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: ai-engineer
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/standards/ai-agent-and-discovery-standards.md"
related_docs:
  - DOC-ROOT-001
  - GOV-STD-SEC-001
  - GOV-POL-TRAC-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Defined Intelligence Plane AI/Agent documentation rules (tools, permissions, side effects, evals, observability) and the 10-step Agent documentation discovery workflow."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Initial Documentation V2 AI/Agent and discovery standards."
---

# AI/Agent Documentation Standards & Agent Discovery Workflow

## Part A: AI & Agent System Documentation Conventions (Intelligence Plane)

All Intelligence Plane capabilities, LLM integrations, orchestrators, and Agent tools MUST document the following explicitly:

1. **Agent Runtime & LLM Integration**:
   - Separate the deterministic orchestration runtime from external or mock LLM provider adapters (`AS-IS` mock vs `TARGET` external LLM).
   - Document model invocation boundaries, timeouts, token budgets, iteration caps, and deterministic fallback behavior on LLM outage or rate limits.
2. **Tool Contracts, Permissions & Side Effects**:
   - Every Agent-callable tool MUST have an explicit contract specifying: `tool_name`, input schema with strict row/time bounds, timeout, required RBAC permissions, backing store (read-only vs. write), and side effects.
   - Any tool with **write or irreversible side effects** MUST document idempotency, rate/blast-radius caps, human approval gates, and dedicated safety tests in accordance with [artifact-applicability-matrix.yaml](../catalog/artifact-applicability-matrix.yaml).
3. **Workflow Orchestration & State Transitions**:
   - Document all orchestrator graph nodes, conditional edges, loop termination bounds, persisted state schema, and failure states (using an Agent Workflow Diagram and/or State Machine diagram).
4. **Memory & State Persistence**:
   - Distinguish ephemeral per-run working state, durable checkpoint/audit logs, and long-term knowledge stores; document retention, isolation, and PII/secret redaction rules.
5. **Evaluation, Provenance & Observability**:
   - Document deterministic verification rules (such as citation/provenance validation preventing fabricated tool IDs or unverified LLM arithmetic), evaluation datasets/metrics, token/latency telemetry, and audit logging.
6. **Fact Integrity Prohibition**:
   - AI-generated summaries, inferences, or model outputs MUST NEVER be recorded as verified system facts or approved requirements without deterministic evidence or explicit human review.
   - Intelligence Plane specifications MUST maintain traceability across: `Agent Requirement (FR/SEC)` -> `Workflow Design` -> `Tool Contract` -> `Safety & Evaluation Tests`.

---

## Part B: Agent Documentation Discovery Workflow

Documentation V2 is structured so an AI Agent can locate and modify a single capability without reading the entire repository.

### 1. Discovery Chain

1. [AGENTS.md](../../../AGENTS.md) — Concise repository entrypoint pointing to Documentation V2.
2. [docs/README.md](../../README.md) & [docs/docs-index.yaml](../../docs-index.yaml) — Root index mapping Planes and governance files.
3. `docs/<plane>/README.md` — Plane index listing Domains and plane-level architecture/contracts.
4. `docs/<plane>/domains/<domain>/README.md` — Domain index listing Capabilities.
5. `docs/<plane>/domains/<domain>/capabilities/<capability>/README.md` & `capability.yaml` — Capability manifest defining exact scope, risk tier, dependencies, authoritative docs, contracts, required artifacts, document status, implementation status, open questions, and blockers.

### 2. Mandatory 10-Step Agent Reading & Execution Order

When working on any task, an Agent MUST follow this exact order:

1. **Read root documentation instructions**: Read `AGENTS.md`, `docs/README.md`, and `docs/docs-index.yaml`.
2. **Resolve the task's Plane**: Determine whether the task belongs to `data-plane`, `application-plane`, `intelligence-plane`, `overview`, or `governance`.
3. **Resolve Domain and Capability**: Navigate via the Plane and Domain `README.md` files (never scan unrelated capabilities).
4. **Read the relevant Capability Manifest (`capability.yaml`)**: Check `risk_tier`, `scope`, `in_scope`/`out_of_scope`, `required_artifacts`, `document_status`, `implementation_status`, and `open_questions`/`blockers`.
5. **Read authoritative requirements and dependencies**: Inspect only the upstream requirements, business rules, and dependent capabilities referenced by `capability.yaml`.
6. **Read related diagrams, contracts, and design artifacts**: Inspect only scoped diagrams and contracts linked from the capability.
7. **Inspect relevant source code and tests**: Read actual implementation (`src/`, `frontend/`), infrastructure (`deploy/`), and automated tests (`tests/`) to verify `AS-IS` reality.
8. **Perform impact analysis before modification**: Trace affected upstream/downstream IDs and contracts per [traceability-and-impact-analysis.md](../traceability-and-impact-analysis.md).
9. **Update affected artifacts**: Keep changes scoped to owned files, update `revision_history` and `implementation_status` accurately, and preserve unresolved questions.
10. **Validate documents and traceability**: Run `python scripts/docs/validate_docs.py` (plus code/test suites if code changed under separate authorization).

### 3. Handling Missing, Contradictory, or Unapproved Specifications

If any required authoritative specification is **missing**, **contradictory** across sources, or **`DRAFT` / unapproved**:

- The Agent **MUST STOP** and report the blocker explicitly (including affected `doc_id`/paths and conflicting statements).
- The Agent **MUST record** the gap in `capability.yaml` (`open_questions` / `blockers`).
- The Agent **MUST NOT** silently invent a business rule, requirement, SLA target, or architecture decision to unblock itself.
