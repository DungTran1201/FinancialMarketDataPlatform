# Single Source-of-Truth & Conflict Resolution Rule (`RULE-007`)

| Metadata | Value |
|---|---|
| **Rule ID** | `RULE-007` |
| **Rule Slug** | `source-of-truth` |
| **Activation Mode** | `Always Active` |
| **Status** | `APPROVED` |
| **Updated Date** | `2026-11-16` |

---

## 1. Purpose & Scope

Operationalizes `docs/governance/source-of-truth-policy.md`, defining authoritative precedence between `docs/governance/`, approved specs/ADRs (`TARGET`), runtime code/DDL/tests (`AS-IS`), and derived views.

## 2. Mandatory Directives

1. **Respect Precedence**:
   - `docs/governance/` governs documentation rules and schemas.
   - `APPROVED` specifications, contracts (`openapi.yaml`, `asyncapi.yaml`, `data-contract.yaml`), and ADRs govern **`TARGET`** intent.
   - Inspected code (`src/`, `frontend/`), DDL/IaC (`deploy/`, `docker-compose.yml`), and executed tests (`tests/`) govern **`AS-IS`** reality.
2. **Log Conflicts Explicitly**: When code contradicts an approved spec or two specs disagree, record the gap in `capability.yaml` (`open_questions` / `blockers`) and `AS-IS vs. TARGET` tables, and escalate per `docs/governance/roles-and-raci.md`.
3. **Derived Source Declaration**: Every derived summary or diagram MUST set `source_of_truth.is_authoritative: false` and link its upstream authoritative paths.

## 3. Prohibited Actions

- Never silently pick a winner when two authoritative documents disagree.
- Never infer `AS-IS` implemented behavior from legacy docs, filenames, or target diagrams alone.

## 4. Verification Mechanism

- `scripts/docs/validate_docs.py` (`VAL-LINK-001`, `VAL-DIAG-SOT-001`) and human review per `docs/governance/review-and-approval.md`.
