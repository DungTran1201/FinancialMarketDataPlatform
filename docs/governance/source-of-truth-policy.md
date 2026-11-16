---
doc_id: GOV-POL-SOT-001
title: "Single Source-of-Truth Policy & Conflict Resolution"
doc_type: governance
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: documentation-architect
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/source-of-truth-policy.md"
related_docs:
  - GOV-ARCH-001
  - GOV-POL-RACI-001
  - GOV-STD-AGENT-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Established single-owner source-of-truth precedence for intended vs implemented behavior and conflict logging rules."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: documentation-architect
    summary: "Initial Documentation V2 source-of-truth policy."
---

# Single Source-of-Truth Policy & Conflict Resolution

## 1. Authoritative Source by Engineering Dimension

Every fact or specification MUST have **one** authoritative home; all other references MUST link to it instead of duplicating content:

| Dimension | Authoritative Source of Truth | Derived Views (Must Reference Only) |
|---|---|---|
| **Documentation Governance & Rules** | `docs/governance/` | `AGENTS.md`, `docs/README.md`, templates |
| **Business / Functional / NFR Intent** | `APPROVED` capability `requirements/` & `use-cases/` | Summaries in `README.md`, test scenarios, release notes |
| **Architectural Decisions** | `APPROVED` MADR 4.0.0 ADRs at owning scope | Architecture descriptions, diagrams |
| **HTTP / Event Contracts** | Canonical `openapi.yaml`, `asyncapi.yaml`, `data-contract.yaml` | Prose endpoint summaries, sequence diagrams |
| **Current Runtime Behavior (`AS-IS`)** | Actual source code (`src/`, `frontend/`), DDL/IaC (`deploy/`, `docker-compose.yml`), and test runs (`tests/`) | `AS-IS` sections in architecture/inventory docs |
| **Verification Proof** | Executed test logs and verification reports | `implementation_status: VERIFIED` badges |
| **Visual Diagrams** | Never authoritative (`is_authoritative: false`) | Always derived from upstream specs/contracts |

## 2. Conflict Resolution Protocol

When two sources disagree (for example, an older ADR conflicts with a newer ADR, a doc contradicts source code, or frontend service paths mismatch backend routers):

1. **Do Not Silently Pick a Winner**: Neither an AI Agent nor an individual contributor MAY silently alter an approved requirement or invent a new architecture decision to hide a conflict.
2. **Code vs. Approved Specification**:
   - Code is the sole truth for **`AS-IS` current behavior**.
   - Approved specifications/ADRs remain the truth for **`TARGET` intended behavior**.
   - The gap MUST be logged in `capability.yaml` (`blockers` / `open_questions`) and the `AS-IS vs. TARGET` table.
3. **Document vs. Document**: Escalate to the accountable owner in [roles-and-raci.md](roles-and-raci.md) (or `documentation-architect` for cross-plane conflicts), mark conflicting claims `BLOCKED` / `OPEN`, and resolve via an explicit ADR or specification revision.
4. **Frontmatter Declaration**: Derived documents and diagrams MUST set `source_of_truth.is_authoritative: false` and list exact upstream `source_of_truth.authoritative_source` files.
