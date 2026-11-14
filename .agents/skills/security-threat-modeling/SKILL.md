---
name: security-threat-modeling
description: STRIDE threats (THR-###), controls (CTRL-###), and trust boundaries.
---

# Skill: STRIDE Threat Modeling & Security Control Design (`SKILL-012`)

## 1. Description

Models trust boundaries, STRIDE threats (`THR-###`), and mitigating controls (`CTRL-###`) in `models/security/` and `docs/product/10-security/`.

## 2. Trigger Conditions

- Phase `10-security` or `SEC` work items touching authentication, RBAC, secrets, network zones, or Agent Tool Gateway (`security-reviewer`).

## 3. Authoritative Inputs

- `models/security/security.yaml`, `threats.yaml`, `docs/architecture/10-security-and-governance.md`, `src/agent/tools/gateway.py`, `docs/templates/security/`.

## 4. Preconditions

1. Target `README.md` read; network zones (`frontend_net`, `app_control_net`, `data_plane_net`) and plane boundaries verified.

## 5. Execution Procedure

1. Update `models/security/security.yaml` and `threats.yaml` first with `THR-###` and `CTRL-###` IDs mapped to components (`COMP-###`) and test cases (`TC-###`).
2. Verify Zero-Direct-DB access for `Plane C` (`ControlledToolGateway` whitelist) and secret isolation (`RULE-009`, `DATA-RULE-011`).
3. Synchronize `docs/product/10-security/` from `docs/templates/security/` and `docs/diagrams/security/`.
4. Run `python tools/validators/run_all.py`.

## 6. Output Artifacts

- `models/security/*.yaml`, `docs/product/10-security/*.md`, `docs/diagrams/security/*.md`.

## 7. Validation

```powershell
python tools/validators/run_all.py
```

## 8. Failure Handling

- Block gate `G3_DESIGN` / `G5_VERIFY` if any `HIGH`/`CRITICAL` threat lacks a linked `CTRL-###` and `TC-###`.

## 9. Restrictions

- Never commit secrets/tokens; never permit `Plane C` LLM direct SQL, shell, or write access to `Plane A`/`Plane B` stores.

## 10. Related Skills

- `architecture-modeling`, `api-contract`, `test-modeling`
