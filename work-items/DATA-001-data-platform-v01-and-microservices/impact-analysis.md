# Impact Analysis — `DATA-001`

## 1. Affected Subsystems

1. **Data Plane (`src/collectors/`, `src/processing/`, `src/quality/`)**: Upgraded to zero-mock 12-stage Data Platform v0.1.
2. **Microservices Runtime (`src/microservices/`, `src/backend/runtime.py`, `src/backend/main.py`, `docker-compose.yml`)**: Added 8 domain microservices and `--profile microservices` (`DEP-006`).
3. **Canonical Models (`models/`)**: Updated `architecture.yaml`, `components.yaml`, `deployment.yaml`, `api.yaml`, and `testing.yaml`.
4. **Documentation & Diagrams (`docs/architecture/`, `docs/diagrams/`)**: Added `ADR-007`, `14-data-platform-v01-and-microservices-architecture.md`, `DIAG-DATA-008`, `DIAG-DATA-009`, `DIAG-C4-017`, and `DIAG-DEP-018`.

