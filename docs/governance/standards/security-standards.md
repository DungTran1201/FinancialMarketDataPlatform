---
doc_id: GOV-STD-SEC-001
title: "Security, Privacy & Threat Modeling Documentation Standards"
doc_type: standard
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
    - "docs/governance/standards/security-standards.md"
related_docs:
  - GOV-STD-REG-001
  - GOV-CAT-MAT-001
  - GOV-STD-AGENT-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Established minimum threat model structure, authorization matrix standard, secret/PII prohibition, and security verification rules aligned with OWASP ASVS 5.0.0 and NIST SSDF 1.1."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Initial Documentation V2 security documentation standard."
---

# Security, Privacy & Threat Modeling Documentation Standards

Informed by **OWASP ASVS 5.0.0** and **NIST SSDF 1.1 (SP 800-218)** as recorded in [standards-register.md](standards-register.md).

## 1. Mandatory Threat Model Structure

Any `HIGH`/`CRITICAL` capability, or any capability handling authentication, authorization, external ingestion, user input, secrets, or write-capable Agent tools MUST produce a Threat Model ([threat-model.template.md](../templates/security/threat-model.template.md)) containing:

1. **Assets**: Data stores, credentials, keys, business state, and availability targets requiring protection.
2. **Actors & Privilege Levels**: Human personas, automated services, external providers, and untrusted callers.
3. **Trust Boundaries**: Explicit network, process, storage-role, and sandbox boundaries.
4. **Entry Points & Attack Surfaces**: HTTP/WS/SSE routes, broker topics, CLI/worker inputs, file parsers, and LLM prompts/tools.
5. **Threat & Abuse Scenarios**: Structured threat scenarios (e.g., STRIDE / abuse cases covering auth bypass, privilege escalation, injection, SSRF, DoS, prompt injection, and data tampering).
6. **Risk Assessment**: Likelihood, impact, and inherent risk rating per threat.
7. **Mitigations & Controls**: Concrete preventive/detective controls mapped to [security-requirements.template.md](../templates/security/security-requirements.template.md) (`SEC-...`) and verified code mechanisms.
8. **Residual Risks**: Remaining risk after controls, requiring explicit owner sign-off (never hidden).
9. **Security Verification Mapping**: Automated tests or security checks verifying each control.

## 2. Authorization Matrix Standard

Capabilities exposing operations or protected resources MUST maintain an Authorization Matrix ([authorization-matrix.template.yaml](../templates/security/authorization-matrix.template.yaml)) specifying for every rule:

- `subject` (role, service identity, or principal class)
- `resource` (endpoint pattern, dataset, tool name, or admin action)
- `action` (`read | write | execute | admin | revoke`)
- `condition` (e.g., IP binding, ownership match, read-only DB role, token scope)
- `expected_decision` (`ALLOW | DENY`)

## 3. Non-Negotiable Security Integrity & Secret Rules

1. **Zero Secrets or Sensitive Data in Docs**: Real API keys, passwords, private keys, certificates, JWT signing secrets, session tokens, internal non-public endpoints, and real user PII MUST NOT appear in any documentation, example, or test fixture. Use non-secret placeholder tokens (`<SECRET_IN_ENV>`) and synthetic test data only.
2. **No Whitewashing Insecure Behavior**: Insecure current code behavior (such as unauthenticated endpoints, self-verified login routes, client-supplied roles, or missing RBAC checks) MUST be explicitly documented as an **unmitigated security finding / gap** in `AS-IS` sections and MUST NOT be described as an approved security control.
3. **Security Review Gate**: High/Critical capabilities MUST obtain explicit `security-architect` sign-off before transitioning security specifications to `APPROVED` or marking implementation `VERIFIED`.
