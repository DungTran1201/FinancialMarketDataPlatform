# Capability Manifests, Contracts & Schema Rule (`RULE-003`)

| Metadata | Value |
|---|---|
| **Rule ID** | `RULE-003` |
| **Rule Slug** | `models` |
| **Activation Mode** | `Always Active` |
| **Status** | `APPROVED` |
| **Updated Date** | `2026-11-16` |

---

## 1. Purpose & Scope

Governs machine-readable capability manifests (`capability.yaml`), API/event/data contracts (`openapi.yaml`, `asyncapi.yaml`, `data-contract.yaml`), authorization matrices (`authorization-matrix.yaml`), test cases (`test-cases.yaml`), and traceability matrices (`traceability.yaml`) across Documentation V2.

## 2. Mandatory Directives

1. **Capability-Owned Structured Artifacts**: Maintain machine-readable specifications at their canonical Plane (`docs/<plane>/shared-contracts/`) or Capability (`docs/<plane>/domains/<domain>/capabilities/<capability>/`) location per `docs/governance/documentation-architecture.md`.
2. **Schema & Applicability Conformance**: Validate `capability.yaml` against `docs/governance/schemas/capability-manifest.schema.json` and `traceability.yaml` against `docs/governance/schemas/traceability.schema.json`.
3. **Contract-First Synchronization**: Update canonical `openapi.yaml`, `asyncapi.yaml`, and `data-contract.yaml` before regenerating derived prose summaries or diagrams.
4. **Explicit Not-Applicable Reasons**: Record a concrete `not_applicable_reason` in `capability.yaml` whenever an artifact is `NOT_APPLICABLE_WITH_REASON`.

## 3. Prohibited Actions

- Never recreate a separate top-level `models/` tree duplicating capability manifests and contracts.
- Never copy raw OpenAPI or AsyncAPI schemas inline into Markdown when a canonical contract file owns them.
- Never omit required artifacts mandated by active `risk_signals` in `docs/governance/catalog/artifact-applicability-matrix.yaml`.

## 4. Verification Mechanism

- `scripts/docs/validate_docs.py` (JSON Schema, OpenAPI 3.x, AsyncAPI 3.x, and applicability matrix enforcement).
