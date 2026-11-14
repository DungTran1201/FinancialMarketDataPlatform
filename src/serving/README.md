# Serving Subsystem (`src/serving/`)

Owns **Application & Control Plane (`Plane B`)**: the FastAPI **Modular Monolith**, unified HTTPS/WAF edge gateway, Observatory UI router, optional isolated ASGI microservice entrypoints, and serving dependency injection.

## Structure

| Directory | Architectural Role | Boundary Rule |
|---|---|---|
| `api/main.py` | Modular Monolith FastAPI factory (`create_app()`) & `app` ASGI entrypoint (`--profile core`) | Mounts all 8 Clean Architecture bounded contexts in one process. |
| `api/modules/` | 8 isolated bounded contexts (`market`, `historical`, `analytics`, `catalog`, `iam`, `platform_config`, `agent_api`, `reporting`) | Each follows `domain/` -> `application/` -> `infrastructure/` -> `presentation/`; never imports `ingestion`, `streaming`, `lakehouse`, or `intelligence`. |
| `api/gateway/` | Edge API Gateway (`service.py`), AES-256-GCM masked `MicroserviceRegistry` (`registry.py`), and Real-Time Data Flow UI router (`ui.py`) | Enforces WAF, HTTPS domain policy, sliding-window rate limits, and routing. |
| `api/services/` | Thin optional ASGI microservice factories (`market`, `historical`, `analytics`, `catalog`, `iam`, `intelligence`, `data_plane`) for `--profile microservices` (`DEP-006`) | Wraps bounded context routers without duplicating domain logic. |
| `infrastructure/runtime.py` | Serving DI & composition root (`PlatformRuntimeContainer`) | Wires concrete cache/OLAP/lakehouse/agent adapters into module ports. |

