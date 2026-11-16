# Lifecycle Quality Gates & Status Promotion Rule (`RULE-010`)

| Metadata | Value |
|---|---|
| **Rule ID** | `RULE-010` |
| **Rule Slug** | `quality-gates` |
| **Activation Mode** | `Always Active` |
| **Status** | `APPROVED` |
| **Updated Date** | `2026-11-16` |

---

## 1. Purpose & Scope

Enforces quality gates `QG-1-SCOPE` through `QG-7-OPS` (`docs/governance/quality-gates.md`) and strict separation between `status` (`DRAFT | IN_REVIEW | APPROVED | DEPRECATED`) and `implementation_status` (`PLANNED | NOT_IMPLEMENTED | SIMULATED | PARTIALLY_IMPLEMENTED | IMPLEMENTED | VERIFIED | NOT_APPLICABLE`).

## 2. Mandatory Directives

1. **Respect Decoupled Status Enums**: Never use `APPROVED` as a substitute for `IMPLEMENTED` or `VERIFIED`, and never use retired V1 statuses (`BASELINED`, `PROPOSED`, `REVIEW_REQUIRED`, `SUPERSEDED`).
2. **Approval Hygiene**: Require `scripts/docs/validate_docs.py` exit `0`, zero `TBD`/`TODO`/`[TO BE COMPLETED]`, complete `change_metadata` + `revision_history`, and accountable human/role review before `APPROVED`.
3. **Complete Gate Verification**: Run `scripts/docs/validate_docs.py`, `tools/validators/run_all.py`, and `pytest tests/ -v` according to the change scope.

## 3. Prohibited Actions

- Never self-approve speculative requirements, unverified performance claims, or security risk acceptances on behalf of human owners.
- Never weaken validators or skip failing assertions to turn a gate green.

## 4. Verification Mechanism

- `scripts/docs/validate_docs.py`, `tools/validators/run_all.py`, and `tests/docs/test_validate_docs.py`.
