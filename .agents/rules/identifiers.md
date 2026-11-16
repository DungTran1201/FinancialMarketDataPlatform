# Identifier Allocation & Preservation Rule (`RULE-006`)

| Metadata | Value |
|---|---|
| **Rule ID** | `RULE-006` |
| **Rule Slug** | `identifiers` |
| **Activation Mode** | `Always Active` |
| **Status** | `APPROVED` |
| **Updated Date** | `2026-11-16` |

---

## 1. Purpose & Scope

Enforces globally unique `doc_id` and `capability_id` values alongside stable semantic requirement, rule, use case, ADR, diagram, security, and test identifiers per `.agents/config/identifier-registry.yaml` and `docs/governance/standards/writing-standards.md`.

## 2. Mandatory Directives

1. **Global Uniqueness**: Assign every Markdown file under `docs/` a unique uppercase `doc_id` and every capability a unique `capability_id` (`CAP-*`).
2. **Canonical Semantic Prefixes**: Format requirement and specification table IDs using `BR/FR/NFR/RULE/UC/AC/CON/THR/SEC/TS/TC-<DOMAIN>-NNN` as enforced by `scripts/docs/validate_docs.py`.
3. **ID Preservation**: Never renumber or reuse retired/existing identifiers for cosmetic continuity.

## 3. Prohibited Actions

- Never assign duplicate `doc_id`, `capability_id`, or requirement IDs across `docs/`.
- Never alter historical identifiers referenced in ADRs, traceability matrices, or tests without an approved deprecation notice.

## 4. Verification Mechanism

- `scripts/docs/validate_docs.py` (`VAL-ID-UNIQUE-001`, `VAL-FM-001`, `VAL-CAP-SCHEMA-001`).
