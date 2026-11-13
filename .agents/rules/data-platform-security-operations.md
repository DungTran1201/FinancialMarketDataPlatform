# Data Rule — Data Platform Security and Destructive Operations (`DATA-RULE-011`)

| Metadata | Value |
|---|---|
| **Rule ID** | `DATA-RULE-011` |
| **Rule Slug** | `data-platform-security-operations` |
| **Trigger Scope** | Secrets, exchange credentials, network exposure, RBAC, object storage, database access, retention, offset resets, and recovery operations |
| **Activation Mode** | `Always Active` |
| **Status** | `BASELINED` |
| **Updated Date** | `2026-11-12` |

---

## 1. Purpose & Scope

Enforces secret isolation, least-privilege database/storage credentials, read-only Agent Tool Gateway guardrails, and safety gates around destructive data operations.

## 2. Mandatory Directives

1. **Secret Management**: Inject credentials via environment variables (`.env.example` template only in VCS) and redact secrets in logs, traces, and error payloads.
2. **Least-Privilege Access**: Separate writer and reader credentials across Kafka, ClickHouse (`fmdp_ingest_writer` vs. read-only query roles), PostgreSQL (`fmdp_pg_admin` vs. service roles), and MinIO.
3. **Controlled Tool Gateway Isolation**: Restrict `agent-worker` to the 10 whitelisted read-only tools in `ControlledToolGateway` (`src/agent/tools/gateway.py`) with enforced RBAC permissions, row caps, and execution timeouts.
4. **Destructive Operation Approval**: Require dry-run analysis, impact assessment, and explicit human approval before executing destructive DDL, Kafka offset resets, bulk overwrites, or snapshot expiration.

## 3. Prohibited Actions

- Do not commit `.env` secrets, private keys, or live exchange API credentials to the repository.
- Do not bypass RBAC, `ControlledToolGateway`, or data-quality gates.
- Do not execute destructive storage or broker recovery commands without human approval.

## 4. Verification Mechanism

- Security threat model review (`models/security/threat-model.yaml`), `PreToolUse` command guard (`tools/hooks/pre_command_guard.py`), Tool Gateway unit tests, and `tools/validators/run_all.py`.

