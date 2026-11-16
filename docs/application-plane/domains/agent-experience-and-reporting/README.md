---
doc_id: APP-DOM-AGT-001
title: "Domain: Agent Experience & Analytical Reporting"
doc_type: index
plane: application-plane
scope_level: domain
domain: agent-experience-and-reporting
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: ai-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/agent_api/presentation/router.py"
    - "src/serving/api/modules/reporting/presentation/router.py"
    - "frontend/src/modules/ai-workspace/AiWorkspaceModule.ts"
    - "frontend/src/services/api/agent.service.ts"
related_docs:
  - APP-ROOT-001
  - APP-DOM-AGT-SPEC-001
  - APP-DOM-AGT-GLOSS-001
  - CAP-APP-AGT-DOC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Created Agent Experience & Reporting domain bridging UI/REST/SSE clients to Intelligence Plane CAP-INT-ORC-001."
---

# Domain: Agent Experience & Analytical Reporting

## 1. Domain Documentation

- [domain-specification.md](domain-specification.md) (`APP-DOM-AGT-SPEC-001`)
- [glossary.md](glossary.md) (`APP-DOM-AGT-GLOSS-001`)

## 2. Capabilities

- [CAP-APP-AGT-001 — Agent Run & Report Portal](capabilities/agent-run-and-report-portal/README.md) (`IN_REVIEW` / `MEDIUM`)
