---
doc_id: GOV-STD-REG-001
title: "External Reference Standards Register"
doc_type: standard
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: documentation-architect
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/standards/standards-register.md"
related_docs:
  - GOV-STD-ROOT-001
  - GOV-STD-WRIT-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Verified and recorded all 11 reference engineering standards, versions, official URLs, revision statuses, and project applicability."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: documentation-architect
    summary: "Initial verified standards register (verified 2026-11-16)."
---

# External Reference Standards Register

This register records the external engineering standards referenced by Documentation V2. Reference frameworks are adopted to structure documentation and verification rigor; listing a standard does **not** imply formal third-party compliance certification unless explicitly stated in an approved governance decision.

## 1. Normative vs. Informative Classification

- **Normative**: Rules and structural conventions derived into FMDP standards/templates MUST be followed by authors and validators.
- **Informative**: Conceptual vocabulary and guidance RECOMMENDED to improve clarity without enforcing strict section-for-section conformance.

## 2. Verified Standards Register

| ID | Full Title | Issuing Organization / Maintainers | Pinned / Selected Version (Latest Status) | Official URL | What It Governs | Nature for FMDP | Templates & Rules Using It | Last Verified |
|---|---|---|---|---|---|---|---|---|
| `STD-REQ-29148` | *ISO/IEC/IEEE 29148: Systems and software engineering — Life cycle processes — Requirements engineering* | ISO / IEC / IEEE | **2018 (2nd Edition)** — **Under revision**: 3rd Edition in ISO DIS ballot stage (ISO project 94091) | [IEEE / ISO 29148](https://standards.ieee.org/ieee/29148/6937/) | Requirements quality characteristics, BR/FR/NFR structure, traceability, and validation rules | Normative (adapted) | `requirements-standards.md`, `system-requirements.template.md`, `product-brief.template.md`, `capability-specification.template.md`, `use-case.template.md`, `business-rules.template.md` | `2026-11-16` |
| `STD-ARCH-ARC42` | *arc42 Architecture Documentation Template* | Gernot Starke, Peter Hruschka & Contributors | **9.0 / 9.1** (Latest 9.x line referencing ISO 25010:2023) | [arc42.org](https://arc42.org/) | Modular architecture viewpoints, constraints, context, building blocks, runtime, deployment, cross-cutting concepts, quality, and risks | Normative (adapted per scope; never monolithic) | `architecture-standards.md`, `architecture-description.template.md`, `component-design.template.md` | `2026-11-16` |
| `STD-DIAG-C4` | *The C4 Model for Visualising Software Architecture* | Simon Brown | **Current Living Specification (Levels 1–4)** | [c4model.com](https://c4model.com/) | Hierarchical System Context, Container, Component, and Code diagrams | Normative | `diagram-standards.md`, `c4-diagram.template.md` | `2026-11-16` |
| `STD-PROC-BPMN` | *Business Process Model and Notation (BPMN)* | Object Management Group (OMG) | **2.0.2** (Formal current specification) | [omg.org/spec/BPMN/2.0.2](https://www.omg.org/spec/BPMN/2.0.2/) | Cross-functional business workflows, swimlanes, gateways, and event orchestration | Normative (when workflow notation applies) | `diagram-standards.md`, `workflow-specification.template.md`, `bpmn-diagram.template.md` | `2026-11-16` |
| `STD-MOD-UML` | *OMG Unified Modeling Language (UML)* | Object Management Group (OMG) | **2.5.1** (Latest formal specification) | [omg.org/spec/UML/2.5.1](https://www.omg.org/spec/UML/2.5.1) | Use case, sequence, state machine, and structural class/component diagrams | Normative (for behavior & sequence modeling) | `diagram-standards.md`, `sequence-diagram.template.md`, `state-machine-diagram.template.md`, `use-case.template.md` | `2026-11-16` |
| `STD-API-OPENAPI` | *OpenAPI Specification (OAS)* | OpenAPI Initiative (OAI) | **Selected: 3.1.0** (3.1.x patch 3.1.2; **3.2.1** is latest OAI release). Selected `3.1.0` after tooling review for FastAPI native emission and JSON Schema Draft 2020-12 compatibility | [spec.openapis.org/oas/latest.html](https://spec.openapis.org/oas/latest.html) | HTTP REST request/response contracts, error models, auth schemes, and webhook declarations | Normative | `api-and-event-contract-standards.md`, `openapi.template.yaml` | `2026-11-16` |
| `STD-EVT-ASYNCAPI` | *AsyncAPI Specification* | AsyncAPI Initiative (Linux Foundation) | **3.1.0** (Latest 3.x minor release building on 3.0.0 channel/operation decoupling) | [asyncapi.com](https://www.asyncapi.com/) | Event-driven channels, Kafka topics, WebSocket/SSE message bindings, `send`/`receive` operations, and payload schemas | Normative | `api-and-event-contract-standards.md`, `asyncapi.template.yaml` | `2026-11-16` |
| `STD-DEC-MADR` | *Markdown Architectural Decision Records (MADR)* | ADR / MADR Maintainers | **4.0.0** (Released Sept 2024) | [adr.github.io/madr](https://adr.github.io/madr/) | Structured recording of architectural context, drivers, considered options, decision outcome, and consequences | Normative | `architecture-standards.md`, `adr.template.md` | `2026-11-16` |
| `STD-SEC-ASVS` | *OWASP Application Security Verification Standard (ASVS)* | OWASP Foundation | **5.0.0** | [asvs.owasp.org](https://asvs.owasp.org/) | Security verification controls for authentication, session/JWT handling, access control, validation, cryptography, and API defense | Normative (adapted as control checklist; not formal certification) | `security-standards.md`, `security-requirements.template.md`, `threat-model.template.md`, `authorization-matrix.template.yaml` | `2026-11-16` |
| `STD-SEC-SSDF` | *NIST SP 800-218: Secure Software Development Framework (SSDF)* | National Institute of Standards and Technology (NIST) | **Version 1.1** (Feb 2022, active final) — **Under revision**: SP 800-218 Rev. 1 / Version 1.2 Initial Public Draft (Dec 2025); SP 800-218A addresses GenAI/dual-use models | [csrc.nist.gov/pubs/sp/800/218/final](https://csrc.nist.gov/pubs/sp/800/218/final) | Secure SDLC practices, review gates, secret isolation, vulnerability response, and verification evidence | Informative / Normative for review gates | `security-standards.md`, `quality-gates.md`, `review-and-approval.md` | `2026-11-16` |
| `STD-QA-ISTQB` | *ISTQB Certified Tester Foundation Level (CTFL) Syllabus & Glossary* | International Software Testing Qualifications Board (ISTQB) | **CTFL 4.0** / Living Online Glossary | [glossary.istqb.org](https://glossary.istqb.org) | Consistent QA terminology separating Test Strategy, Test Plan, Test Scenario, Test Case, Test Data, and Verification Evidence | Informative | `qa-and-testing-standards.md`, `test-plan.template.md`, `test-scenarios.template.md`, `test-cases.template.yaml` | `2026-11-16` |
