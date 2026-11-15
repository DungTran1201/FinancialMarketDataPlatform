# Operations & SRE Domain (`docs/operations/`)

## 1. Directory Purpose

`docs/operations/` is the authoritative operational, reliability, and Site Reliability Engineering (SRE) portal for the **FinancialMarketDataPlatform**. It provides actionable deployment instructions, Docker Compose profile management, observability dashboards, incident response runbooks, and disaster recovery procedures.

## 2. Scope and Boundaries

- **Belongs in `docs/operations/`**:
  - Container deployment guides (`core` and `microservices` profiles).
  - Health check endpoint catalogs and automated failure recovery procedures.
  - Operational runbooks for Kafka consumer lag, ClickHouse ingestion recovery, and rate limit backoff.
  - Prometheus alerting thresholds and Grafana dashboard documentation.
- **Does NOT belong in `docs/operations/`**:
  - Raw infrastructure compose files or shell scripts (which live in `deploy/`).
  - Architecture theory or decision logs (which live in `docs/architecture/`).
  - Daily developer onboarding instructions (which live in `docs/development/`).

## 3. Agent Role and Responsibilities

- **Primary Owning Role**: `dataops-engineer`.
- **Collaborating Roles**: `data-platform-architect`, `documentation-architect`.
- **Responsibilities**:
  - Maintain current, battle-tested operational runbooks.
  - Ensure deployment documentation matches `deploy/` configurations and `docker-compose.yml`.

## 4. Authoritative Inputs

1. [docker-compose.yml](../../docker-compose.yml) — Production Compose Configuration.
2. [deploy/README.md](../../deploy/README.md) — Deployment Subsystem Contract.
3. [models/deployment/deployment.yaml](../../models/deployment/deployment.yaml) — Canonical Deployment Model.
4. [docs/architecture/11-reliability-and-observability.md](../architecture/11-reliability-and-observability.md) — Reliability Baseline.
5. [docs/architecture/12-deployment-architecture.md](../architecture/12-deployment-architecture.md) — Deployment Baseline.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `README.md` | Domain scope, authoritative inputs, and directory index | Required | `docs/templates/operations/deployment-guide.template.md` |
| `deployment-guide.md` | Step-by-step container deployment guide (`core` & `microservices`) | Required | `docs/templates/operations/deployment-guide.template.md` |
| `operational-runbooks.md` | Incident mitigation runbooks (consumer lag, backfill, alerts) | Required | `docs/templates/operations/runbook.template.md` |

## 6. Directory and File Organization

```text
docs/operations/
├── README.md                 # Domain overview & 12-section contract
├── deployment-guide.md       # Deployment profiles & container management
└── operational-runbooks.md   # Incident recovery and SRE procedures
```

## 7. Document Creation Rules

- All runbooks must follow a standard incident structure: Symptoms, Trigger, Diagnostic Commands, Resolution Steps, and Verification.
- Commands must be executable directly in PowerShell or Bash.

## 8. Creation Workflow

1. Inspect `docker-compose.yml` and `deploy/`.
2. Document verified procedures tested against the actual runtime.
3. Validate links and run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

- **Upstream**: Governed by `deploy/` and `models/deployment/`.
- **Downstream**: Used by on-call engineers, DevOps automations, and CI pipelines.

## 10. Quality Gate

- All operational commands verified to work on Windows PowerShell and Linux Docker environments.
- Zero broken links.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- **Do NOT** publish unverified recovery scripts.
- **Do NOT** specify destructive operations without explicit backup warnings.
