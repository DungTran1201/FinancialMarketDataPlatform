# Data Rule — Evidence and Implementation-State Classification (`DATA-RULE-001`)

| Metadata | Value |
|---|---|
| **Rule ID** | `DATA-RULE-001` |
| **Rule Slug** | `data-truth-classification` |
| **Trigger Scope** | Discovery, architecture, implementation reviews, project summaries, release reports, and pipeline readiness statements |
| **Activation Mode** | `Always Active` |
| **Status** | `APPROVED` |
| **Updated Date** | `2026-11-16` |

---

## 1. Purpose & Scope

Enforces strict evidence-backed classification of current runtime behavior (`AS-IS`) versus target intended architecture (`TARGET`), decoupled `implementation_status` enums (`PLANNED | NOT_IMPLEMENTED | SIMULATED | PARTIALLY_IMPLEMENTED | IMPLEMENTED | VERIFIED`), `[ASSUMPTION]` tags, and `[OPEN]` / `BLOCKED` registers per `docs/governance/source-of-truth-policy.md` and `docs/governance/versioning-and-status.md`.

## 2. Mandatory Directives

1. **Classification Discipline**: Separate `AS-IS` verified reality from `TARGET` design, tag unconfirmed hypotheses `[ASSUMPTION]`, and log unresolved gaps as `[OPEN]` or `BLOCKED` in `capability.yaml`.
2. **Code & Runtime Evidence**: Verify implementation claims directly in `src/`, SQL DDL in `deploy/`, `docker-compose.yml`, `tests/`, or runtime output.
3. **Partial Scaffold Recognition**: Treat worker entrypoints, interfaces, schemas, helper functions, and declarative job specs (`SilverMergeJobSpec`, `QualityExpectationRule`) as `SIMULATED` or `PARTIALLY_IMPLEMENTED` unless the full end-to-end execution path is present.
4. **Prototype Separation**: Keep exploratory notebooks (`notebooks/`) distinct from governed service implementations (`src/`).

## 3. Prohibited Actions

- Do not report an architecture diagram, Compose service declaration, or roadmap as proof of a running production pipeline.
- Do not silently convert assumptions into facts without repository evidence or explicit human confirmation.

## 4. Verification Mechanism

- Review claim-to-evidence references in `capability.yaml` and capability specs, cross-check `src/`, `deploy/`, `tests/`, `docker-compose.yml`, and run `scripts/docs/validate_docs.py` (`tools/validators/run_all.py`).
