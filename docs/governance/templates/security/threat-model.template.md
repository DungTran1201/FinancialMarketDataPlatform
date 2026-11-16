---
doc_id: TPL-SEC-TM-001
title: "Template: Threat Model"
doc_type: template
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: security-architect
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/templates/security/threat-model.template.md"
related_docs:
  - GOV-STD-SEC-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created Threat Model template covering assets, actors, trust boundaries, entry points, attack surfaces, scenarios, risk, mitigations, and residual risks."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Initial V2 threat model template."
---

# Template: Threat Model

Required for `HIGH_CRITICAL` capabilities and any capability touching auth, sensitive data, external exposure, or write-capable Agent tools. **Never include secrets or claim insecure `AS-IS` code is mitigated.**

---

# Threat Model: `<Capability or Plane Name>`

## 1. Assets & Actors `[REQUIRED]`

### Protected Assets
| Asset ID | Asset Name | Classification (`PUBLIC | INTERNAL | CONFIDENTIAL | RESTRICTED`) | Compromise Impact |
|---|---|---|---|
| `AST-001` | `<Signing keys / DB / API>` | `RESTRICTED` | `<Impact>` |

### Actors & Privilege Levels
- `<Untrusted external caller>`, `<Authenticated viewer>`, `<Operator>`, `<Admin>`, `<Autonomous Agent>`

## 2. Trust Boundaries, Entry Points & Attack Surfaces `[REQUIRED]`

- **Trust Boundaries**: `<Edge TLS -> API Gateway -> Internal Network -> Storage Role / Agent Sandbox>`
- **Entry Points & Attack Surfaces**: `<HTTP routes, WS/SSE streams, Kafka topics, LLM prompts/tool inputs>`
- **Threat Diagram**: `[<threat-model-diagram.md>](<threat-model-diagram.md>)`

## 3. Threat Scenarios, Risk Assessment & Mitigations `[REQUIRED]`

| Threat ID | Category (`STRIDE / Abuse`) | Attack Scenario | Inherent Risk | Required Mitigation / Control (`SEC-...`) | `AS-IS` Control Status (`IMPLEMENTED | MISSING | BROKEN`) | Verification Test |
|---|---|---|---|---|---|---|---|
| `THR-<DOM>-001` | `Elevation of Privilege` | `<Concrete abuse path>` | `CRITICAL` | `SEC-<DOM>-001` | `<Honest AS-IS status>` | `TC-<DOM>-001` |

## 4. Residual Risks & Sign-Off `[REQUIRED]`

- `<Explicit residual risks accepted or blockers prohibiting production use>`
