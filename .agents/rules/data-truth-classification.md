# Data Rule — Evidence and Implementation-State Classification (`DATA-RULE-001`)

| Metadata | Value |
|---|---|
| **Rule ID** | `DATA-RULE-001` |
| **Rule Slug** | `data-truth-classification` |
| **Trigger Scope** | Discovery, architecture, implementation reviews, project summaries, release reports, and pipeline readiness statements |
| **Activation Mode** | `Always Active` |
| **Status** | `BASELINED` |
| **Updated Date** | `2026-11-12` |

---

## 1. Purpose & Scope

Enforces strict evidence-backed classification of current runtime behavior (`AS-IS/FACT`) versus documented target architecture (`DOCUMENTED TARGET`), proposals (`PROPOSED`), assumptions (`ASSUMPTION`), decisions (`DECISION`), and open questions (`OPEN QUESTION`).

## 2. Mandatory Directives

1. **Classification Discipline**: Classify material claims as `AS-IS/FACT`, `DOCUMENTED TARGET`, `PROPOSED`, `ASSUMPTION`, `OPEN QUESTION`, or `DECISION`.
2. **Code & Runtime Evidence**: Verify implementation claims directly in `src/`, SQL DDL in `deploy/`, `docker-compose.yml`, `tests/`, or runtime output.
3. **Partial Scaffold Recognition**: Treat worker entrypoints, interfaces, schemas, helper functions, and declarative job specs (`SilverMergeJobSpec`, `QualityExpectationRule`) as partial scaffolds unless the full end-to-end execution path is present.
4. **Prototype Separation**: Keep exploratory notebooks (`notebooks/`) distinct from governed service implementations (`src/`).

## 3. Prohibited Actions

- Do not report an architecture diagram, Compose service declaration, or roadmap as proof of a running production pipeline.
- Do not silently convert assumptions into facts without repository evidence or explicit human confirmation.

## 4. Verification Mechanism

- Review claim-to-evidence references in the active work item/report, cross-check `src/`, `deploy/`, `tests/`, `docker-compose.yml`, and run `tools/validators/run_all.py`.

