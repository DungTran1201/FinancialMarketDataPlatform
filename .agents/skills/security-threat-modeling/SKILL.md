---
name: security-threat-modeling
description: Authors capability threat models, SEC-* controls, authorization-matrix.yaml, and threat diagrams.
---

# Skill: STRIDE Threat Modeling & Security Control Design (`SKILL-012`)

## 1. Description

Models trust boundaries, entry points, assets, threat scenarios (`THR-*`), security controls (`SEC-*`), and RBAC authorization matrices (`authorization-matrix.yaml`) in `docs/<plane>/architecture/` and capability `security/` directories.

## 2. Trigger Conditions

- `HIGH_CRITICAL` capabilities, `handles_auth_or_rbac`, `external_exposure`, `agent_write_capable_tools`, or Gate `QG-4-SECURITY` (`security-reviewer`, `security-architect`).

## 3. Authoritative Inputs

- `docs/governance/standards/security-standards.md`, `docs/governance/templates/security/`, `docs/governance/templates/diagrams/threat-model-diagram.template.md`, `src/serving/api/modules/iam/`, `src/shared/security/primitives.py`, `src/intelligence/tools/gateway.py`, `deploy/nginx/nginx.conf`.

## 4. Preconditions

1. Owning `capability.yaml` `risk_signals` checked against `docs/governance/catalog/artifact-applicability-matrix.yaml` (`ART-THREAT-MODEL`, `ART-SEC-REQ`, `ART-AUTHZ-MATRIX`, `ART-DIAG-TM`).

## 5. Execution Procedure

1. Author or update `<capability>/security/threat-model.md` covering all mandatory topics enforced by `validate_docs.py` (`asset`, `trust boundary`, `entry point`, `threat`, `mitigation`, `residual risk`).
2. Author `<capability>/security/security-requirements.md` (`SEC-*` controls) and `security/authorization-matrix.yaml` (`subject x resource x action x condition`).
3. Verify `ControlledToolGateway` isolation (`src/intelligence/tools/gateway.py`), secret hygiene, and honest disclosure of insecure `AS-IS` gaps (`SEC-AUDIT-*`) as `BLOCKED`.
4. Synchronize derived `<capability>/security/threat-model-diagram.md`, update `quality/traceability.yaml`, and run `python scripts/docs/validate_docs.py`.

## 6. Output Artifacts

- `<capability>/security/{threat-model.md,security-requirements.md,authorization-matrix.yaml,threat-model-diagram.md}` and updated `quality/traceability.yaml`.

## 7. Validation

```powershell
python scripts/docs/validate_docs.py
python -m pytest tests/unit/test_security_and_defense.py -v
```

## 8. Failure Handling

- Block Gate `QG-4-SECURITY` and record `blockers` in `capability.yaml` whenever `CRITICAL`/`HIGH` threats lack implemented mitigations or verification tests.

## 9. Restrictions

- Never commit secrets/tokens/PII; never whitewash insecure `AS-IS` auth bypasses; never recreate V1 `models/security/` or `docs/product/10-security/`.

## 10. Related Skills

- `architecture-modeling`, `api-contract`, `test-modeling`
