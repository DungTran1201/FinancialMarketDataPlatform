---
doc_id: INT-ADR-ROOT-001
title: "Intelligence Plane Architecture Decision Records"
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
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/reporting/validator.py"
related_docs:
  - INT-ARCH-ROOT-001
  - ADR-INT-0001
  - ADR-OVR-003
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Indexed Plane C Architecture Decision Records."
---

# Intelligence Plane Architecture Decision Records

| ADR ID | Decision Title | Doc Status | Implementation Status | Summary |
|---|---|---|---|---|
| `ADR-INT-0001` | [Deterministic Tool Gateway & Citation Provenance Over Freeform LLM SQL/Math](adr-0001-deterministic-gateway-over-freeform-sql.md) | `DRAFT` | `PARTIALLY_IMPLEMENTED` | Restricts LLM data/math access strictly to 10 whitelisted tools (`ControlledToolGateway`) and `ReportValidator` citation checks; records unresolved side-effect & worker-isolation follow-ups. |

Related cross-plane ADRs live in [Overview Decisions](../../../overview/architecture/decisions/README.md) (`ADR-OVR-001`, `ADR-OVR-002`, `ADR-OVR-003`).
