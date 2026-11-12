# External Skill Evaluation & Quarantine Policy

## 1. Admission Criteria

Before any external skill can be added to `.agents/skills/` and activated in `.agents/skill-registry.yaml`:
1. **Path Sanitization**: All directory references must match `FinancialMarketDataPlatform` (`docs/product/`, `docs/architecture/`, `models/`, `work-items/`).
2. **Domain Decontamination**: Remove any product-specific domain assumptions from the source project.
3. **Security Review**: Verify that the skill does not execute arbitrary network calls, bypass `.agents/rules/security.md`, or weaken the Controlled Tool Gateway.
