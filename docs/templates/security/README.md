# Security & Threat Modeling Templates (`docs/templates/security/`)

## 1. Directory Purpose

Provides reusable markdown templates for lifecycle phase `10-security`, targeting `docs/product/10-security/` and feature packages in `docs/features/`.

## 2. Scope and Boundaries

- **Belongs in this directory**: Reusable `*.template.md` files for `security` documentation (`security-specification.template.md, threat-model.template.md, STRIDE.template.md, security-control.template.md`).
- **Does NOT belong in this directory**: Populated project documents (which must be saved in `docs/product/10-security/` or `docs/features/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `security-reviewer`; review role: `documentation-auditor`.

## 4. Authoritative Inputs

1. `docs/templates/README.md` — Master template library contract.
2. `docs/product/10-security/README.md` — Target lifecycle phase operating contract.
3. `models/security/threat-model.yaml` — Associated canonical model.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `security-specification.template.md` | Security & Access Control Specification (`SEC-SPEC-[NNN]`) | Required | `docs/templates/security/security-specification.template.md` |
| `threat-model.template.md` | Threat Model & Trust Boundary Specification (`SEC-TM-[NNN]`) | Required | `docs/templates/security/threat-model.template.md` |
| `STRIDE.template.md` | STRIDE Threat Catalog (`SEC-STRIDE-[NNN]`) | Required | `docs/templates/security/STRIDE.template.md` |
| `security-control.template.md` | Security Control & Verification Specification (`SEC-CTRL-[NNN]`) | Required | `docs/templates/security/security-control.template.md` |

## 6. Directory and File Organization

Flat directory `docs/templates/security/` containing `README.md` and 4 `.template.md` files.

## 7. Document Creation Rules

Instantiate templates into the target phase directory, assign a stable ID from `.agents/config/identifier-registry.yaml`, and preserve all `[MANDATORY]` sections.

## 8. Creation Workflow

1. Read `docs/templates/security/README.md` and `docs/product/10-security/README.md`.
2. Inspect authoritative canonical model `models/security/threat-model.yaml`.
3. Copy the selected `.template.md` file to `docs/product/10-security/`.
4. Populate verified facts and explicitly tag assumptions/open questions.
5. Run `tools/validators/validate_templates.py` and `tools/validators/validate_docs.py`.

## 9. Relationships and Dependencies

Mapped to `docs/product/10-security/` in `.agents/config/document-map.yaml`.

## 10. Quality Gate

All templates in this folder pass `validate_templates.py` and `validate_readmes.py` with zero errors.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT edit files inside `docs/templates/security/` to hold feature-specific data.
- Do NOT invent unverified requirements when instantiating these templates.
