---
doc_id: ADR-OVR-002
title: "ADR-OVR-002: Modular Monolith Runtime vs. Microservices Decomposition (OPEN)"
doc_type: adr
plane: platform
scope_level: platform
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "0.2.0"
owner_role: system-architect
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/main.py"
    - "src/serving/api/services/"
    - "docker-compose.yml"
related_docs:
  - OVR-ADR-ROOT-001
  - OVR-ARCH-SYS-001
  - GOV-MIG-P2RISK-001
revision_history:
  - version: "0.2.0"
    date: "2026-11-16"
    author_role: system-architect
    summary: "Logged unresolved runtime deployment contradiction ([OPEN]); kept strictly DRAFT awaiting architect & stakeholder sign-off."
---

# ADR-OVR-002: Modular Monolith Runtime vs. Microservices Decomposition `[OPEN]`

> **Status Notice**: This ADR is **DRAFT / UNRESOLVED**. Phase 1 audit uncovered direct contradiction between the single-process Modular Monolith (`backend-api` `main.py`, legacy `ADR-004`) and the 7 standalone microservice wrappers (`docker-compose.yml --profile microservices`, legacy `ADR-007`). Do NOT treat distributed microservice isolation as active until Option B's shared persistence prerequisites are implemented and signed off.

## 1. Context and Problem Statement `[REQUIRED]`

Two competing runtime topologies coexist in the codebase:

1. **Unified Monolith (`src/serving/api/main.py`)**: Mounts all 8 routers, gateway, and observability on one `FastAPI` instance sharing a single in-memory `PlatformRuntimeContainer` (plus mounting 6 in-process sub-apps).
2. **Distributed Microservice Wrappers (`src/serving/api/services/*.py`, `docker-compose.yml:400-563`)**: Defines 7 separate uvicorn container factories (`:8001`–`:8007`) under `--profile microservices`. When invoked standalone (`runtime=None`), each factory constructs its own isolated **in-memory** `PlatformRuntimeContainer()` (`create_iam_microservice_app` also creates its own unshared `JwtSecurityService` and rate-limit dict), meaning containers do not share quotes, instruments, watermarks, agent runs, reports, or revoked tokens.

## 2. Considered Options `[REQUIRED]`

- **Option A — Standardize on Modular Monolith (`backend-api` + Dedicated Background Workers)**: Keep one HTTP/WS gateway (`main.py`) serving all 8 bounded contexts while splitting out `collector-ws`, `collector-rest`, `consumer-*`, and `agent-worker` once backed by live Kafka/Redis/ClickHouse/Postgres. Lowest operational overhead for current scale.
- **Option B — Fully Distributed 8-Microservice Deployment**: Deploy all 7 domain containers independently (`:8001`–`:8007`) behind `svc-api-gateway` (`:8000`). Requires replacing **all** in-memory `PlatformRuntimeContainer` dicts and rate/JWT sets with shared Postgres/Redis/Kafka persistence, implementing missing `/ws/v1/market` routes, and adding defense middleware across all 7 factories.
- **Option C — Hybrid Path**: Run Modular Monolith for MVP / single-host Compose (`core` profile) while keeping ASGI sub-app Clean Architecture seams strictly modular for selective extraction only if scaling bottlenecks justify network hops.

## 3. Decision Outcome `[REQUIRED — OPEN FOR OWNER DECISION]`

**UNRESOLVED (`OPEN`)**: System Architect and human repository owner MUST select Option A, B, or C. Until decided and until shared Postgres/Redis persistence replaces in-memory container state, `backend-api` Modular Monolith remains the only state-consistent runtime (`AS-IS`).

## 4. Consequences `[REQUIRED]`

- **Impact if Left Unresolved**: Running `docker compose --profile microservices up` produces split-brain state across HTTP endpoints (`GAP-ARCH-001`).
- **Required Next Action**: Owner decision on ADR-OVR-002 plus implementing Redis/Postgres persistence for IAM revocation, instruments, watermarks, runs, and reports if moving beyond single-process monolith.
