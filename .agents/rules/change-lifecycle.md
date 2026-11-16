# Documentation V2 Change Lifecycle & PR Rule (`RULE-008`)

| Metadata | Value |
|---|---|
| **Rule ID** | `RULE-008` |
| **Rule Slug** | `change-lifecycle` |
| **Activation Mode** | `Always Active` |
| **Status** | `APPROVED` |
| **Updated Date** | `2026-11-16` |

---

## 1. Purpose & Scope

Aligns Agent workflows with the 9-stage Documentation V2 lifecycle (`docs/governance/documentation-lifecycle.md`) and pull-request change procedure (`docs/governance/change-management.md`).

## 2. Mandatory Directives

1. **Scope Before Edit**: Follow the 10-step Agent discovery workflow (`docs/governance/standards/ai-agent-and-discovery-standards.md`), inspecting `capability.yaml` and `docs/governance/catalog/artifact-applicability-matrix.yaml` before authoring.
2. **Metadata Synchronization**: On every meaningful document change, bump SemVer `version`, set ISO-8601 `updated_at`, append `revision_history`, and update `change_metadata` if `status: APPROVED`.
3. **PR-Driven Delivery & Retirement**: Deliver changes on dedicated branches via PRs; deprecate with `status: DEPRECATED` + `superseded_by` and retire deleted specs cleanly via Git history rather than creating `docs/archive/`.

## 3. Prohibited Actions

- Never commit directly to `main` or recreate retired V1 `work-items/` workflows without explicit project authorization.
- Never modify unrelated application source code (`src/`, `frontend/`) during documentation-only tasks.

## 4. Verification Mechanism

- `scripts/docs/validate_docs.py`, `tools/validators/run_all.py`, and PR review gates in `docs/governance/review-and-approval.md`.
