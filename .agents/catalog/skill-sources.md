# Skill Provenance & Adaptation Register

| Source Repository | Reference Subsystem | Adaptation Status | Exclusion Notes |
|---|---|---|---|
| `DungTran1201/AgentHarnessBuilderTools` | `.agents/skills/*`, `.agents/config/*` | Adapted, sanitized (`16` core documentation/modeling skills), and aligned to Documentation V2 | Excluded AI-Chan product-specific artifacts (`ponytail.md`, VRM companion, Discord bot skills). |
| `DungTran1201/FinancialMarketDataPlatform` (Native) | `.agents/skills/{analytics-engineering-dbt-clickhouse,data-governance-lineage,data-platform-discovery,data-platform-testing-recovery,dataops-observability,financial-data-quality,financial-market-data-ingestion,kafka-event-streaming,lakehouse-medallion}` | Authored natively (`9` financial data-platform skills) and aligned to Documentation V2 | Enforces Three-Plane isolation, exact `Decimal`, UTC timestamps, and `ControlledToolGateway` bounds. |
