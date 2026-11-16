---
doc_id: TPL-SEC-REQ-001
title: "Template: Security Requirements Specification"
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
    - "docs/governance/templates/security/security-requirements.template.md"
related_docs:
  - GOV-STD-SEC-001
  - GOV-STD-REG-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created OWASP ASVS 5.0.0-informed Security Requirements template."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Initial V2 security requirements template."
---

# Template: Security Requirements Specification

Maps threats (`THR-...`) to testable security requirements (`SEC-...`) informed by **OWASP ASVS 5.0.0**.

---

# Security Requirements: `<Capability Name>`

## 1. Testable Security Controls `[REQUIRED]`

| SEC ID | Control Domain (`AuthN | AuthZ | Validation | Crypto | Secrets | Audit`) | Requirement Statement (`The system MUST...`) | Mitigated Threats | Verification Method / Test Case | Implementation Status |
|---|---|---|---|---|---|
| `SEC-<DOM>-001` | `AuthN` | `<Verifiable security control>` | `THR-<DOM>-001` | `TC-<DOM>-001` | `NOT_IMPLEMENTED` |

## 2. Privacy, Audit Logging & Secret Isolation Rules `[REQUIRED]`

- **Secret Storage**: `<Env/secret manager boundary; zero secrets in VCS/docs/logs>`
- **Audit Events**: `<Who, action, target, decision, timestamp UTC, redacted IP/token>`
