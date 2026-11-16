# External Skill Evaluation & Quarantine Policy

## 1. Admission Criteria

Before any external skill can be added to `.agents/skills/` and activated in `.agents/skill-registry.yaml`:
1. **Path Sanitization**: All directory references must match `FinancialMarketDataPlatform` Documentation V2 (`docs/overview/`, `docs/data-plane/`, `docs/application-plane/`, `docs/intelligence-plane/`, `docs/governance/`, `src/`, `frontend/`, `deploy/`, `tests/`).
2. **Domain Decontamination**: Remove any product-specific domain assumptions from the source project.
3. **Security Review**: Verify that the skill does not execute arbitrary network calls, bypass `.agents/rules/security.md` or `docs/governance/standards/security-standards.md`, or weaken the `ControlledToolGateway`.
4. **Governance Alignment**: Ensure the skill respects `AGENTS.md`, `docs/docs-index.yaml`, and `docs/governance/source-of-truth-policy.md`.
