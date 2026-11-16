# Security, Secret Isolation & Agent Safety Rule (`RULE-009`)

| Metadata | Value |
|---|---|
| **Rule ID** | `RULE-009` |
| **Rule Slug** | `security` |
| **Activation Mode** | `Always Active` |
| **Status** | `APPROVED` |
| **Updated Date** | `2026-11-16` |

---

## 1. Purpose & Scope

Enforces `docs/governance/standards/security-standards.md`, prohibiting real secrets or PII in docs/tests, forbidding security whitewashing, and preserving `ControlledToolGateway` isolation for the Intelligence Plane.

## 2. Mandatory Directives

1. **Zero Secrets or PII**: Never place real secrets, API keys, JWT signing secrets, private keys, or PII in docs, examples, or tests; keep `.env.example` placeholder-only.
2. **No Security Whitewashing**: Report verified insecure `AS-IS` behaviors (such as `SEC-AUDIT-001..005` in IAM routers or hardcoded default keys) explicitly as `CRITICAL`/`HIGH` gaps and `BLOCKED` controls—never describe them as approved controls.
3. **High-Risk Security Gate (`QG-4-SECURITY`)**: Any capability with `handles_auth_or_rbac`, `external_exposure`, or `agent_write_capable_tools` MUST maintain `threat-model.md`, `security-requirements.md`, threat model diagram, and `authorization-matrix.yaml` (per `artifact-applicability-matrix.yaml`).
4. **Intelligence Plane Sandbox**: Keep LLM/Agent access bounded to `ControlledToolGateway` with RBAC checks, row caps, timeouts, and zero arbitrary SQL or unapproved writes.

## 3. Prohibited Actions

- Never weaken or silently waive `HIGH`/`CRITICAL` security findings without `security-architect` / human owner sign-off.
- Never execute destructive repository or infrastructure commands bypassing `.agents/hooks.json` (`pre_command_guard.py`).

## 4. Verification Mechanism

- `scripts/docs/validate_docs.py` (threat model topic checks & applicability), `tests/unit/test_security_and_defense.py`, and `QG-4-SECURITY` review.
