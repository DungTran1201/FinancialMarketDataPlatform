---
doc_id: GOV-STD-WRIT-001
title: "Documentation Writing, Formatting & Metadata Standards"
doc_type: standard
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: documentation-tooling-engineer
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/standards/writing-standards.md"
related_docs:
  - GOV-STD-ROOT-001
  - GOV-STD-REG-001
  - GOV-POL-VER-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Established normative keywords, canonical English language rule, Markdown structure, naming, IDs, frontmatter metadata, and assumption/open-question tagging."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: documentation-tooling-engineer
    summary: "Initial Documentation V2 writing and metadata standards."
---

# Documentation Writing, Formatting & Metadata Standards

## 1. Normative Keywords

All Documentation V2 governance documents, standards, templates, and specifications MUST use the following RFC-aligned normative terms consistently:

- **MUST**: Mandatory requirement without exception unless a formal waiver is recorded in an approved decision.
- **MUST NOT**: Strictly prohibited behavior.
- **SHOULD**: Strongly recommended practice; deviations MUST be justified with documented rationale.
- **SHOULD NOT**: Discouraged behavior unless an approved exception exists.
- **MAY**: Truly optional behavior left to the owner's discretion.

## 2. Canonical Language & Terminology

1. **Canonical Documentation Language**: All repository identifiers, filenames, schemas, contracts, and engineering specifications MUST be authored in clear, concise **English** (matching existing source code, schemas, and specifications in this repository).
2. **No Duplicated Translations**: Authors MUST NOT maintain parallel English and Vietnamese copies of the same specification; duplicated translations create drift and split the source of truth.
3. **Ubiquitous Terms**: Domain terms MUST align with the Domain glossary entry definitions and source-code symbol names (`UpperCamelCase` classes, `snake_case` Python modules/fields, `UPPER_SNAKE_CASE` constants).

## 3. Markdown Formatting & Heading Hierarchy

1. Every Markdown document MUST contain YAML frontmatter delimited by `---` at line 1, followed by exactly one top-level H1 heading (`# <Title>`).
2. Headings MUST follow strict sequential hierarchy (`#` -> `##` -> `###` -> `####`); skipping heading levels (e.g., `#` directly to `###`) MUST NOT occur.
3. Structured comparisons, mappings, registers, and inventories SHOULD use GitHub-Flavored Markdown tables with explicit column headers.
4. Bullet lists SHOULD use `-` consistently and fenced code blocks MUST declare a language identifier (`yaml`, `json`, `mermaid`, `python`, `sql`, `bash`, `text`).
5. Documents MUST avoid filler prose and oversized monolithic walls of text; split by capability or concern when a document becomes multi-concern.

## 4. File Naming & Identifier Conventions

1. **Filenames**: Directories and filenames MUST use lowercase `kebab-case` (e.g., `capability-specification.md`, `adr-0001-topic.md`), except standard repository filenames (`README.md`, `AGENTS.md`) and machine-readable files (`capability.yaml`, `openapi.yaml`, `asyncapi.yaml`, `data-contract.yaml`).
2. **Document IDs (`doc_id`)**: Every Markdown specification MUST carry a globally unique uppercase `doc_id` matching `^[A-Z][A-Z0-9-]*[A-Z0-9]$` (for example: `GOV-STD-WRIT-001`, `DP-ING-SPEC-001`, `APP-MKT-UC-001`).
3. **Requirement & Artifact IDs**: Stable semantic IDs MUST NEVER be renumbered once referenced:
   - Business Requirement: `BR-<DOMAIN>-NNN`
   - Functional Requirement: `FR-<DOMAIN>-NNN`
   - Non-Functional Requirement: `NFR-<DOMAIN>-NNN`
   - Business Rule: `RULE-<DOMAIN>-NNN`
   - Use Case: `UC-<DOMAIN>-NNN`
   - Acceptance Criteria: `AC-<DOMAIN>-NNN`
   - Architecture Decision Record: `ADR-<SCOPE>-NNN`
   - Diagram: `DIAG-<SCOPE>-NNN`
   - Threat / Security Control: `THR-<SCOPE>-NNN` / `SEC-<SCOPE>-NNN`
   - Test Scenario / Test Case: `TS-<SCOPE>-NNN` / `TC-<SCOPE>-NNN`

## 5. Document Metadata (YAML Frontmatter)

Every Markdown document under `docs/` MUST conform to [document-frontmatter.schema.json](../schemas/document-frontmatter.schema.json), instantiated from [document-frontmatter.template.yaml](../templates/common/document-frontmatter.template.yaml). Required fields include:

- `doc_id`, `title`, `doc_type`, `plane`, `scope_level`
- `status` (`DRAFT | IN_REVIEW | APPROVED | DEPRECATED`)
- `implementation_status` (`PLANNED | NOT_IMPLEMENTED | SIMULATED | PARTIALLY_IMPLEMENTED | IMPLEMENTED | VERIFIED | NOT_APPLICABLE`)
- `version` (SemVer `X.Y.Z`), `owner_role`, `accountable_role`
- `created_at`, `updated_at`
- `source_of_truth` (`is_authoritative`, `authoritative_source`)
- `related_docs`
- `change_metadata` (`approved_by`, `approved_at`, `change_summary` — mandatory when `status: APPROVED`)
- `revision_history` (mandatory matching entry when `status: APPROVED`)

## 6. Dates, Timezones & Links

1. All dates MUST use ISO-8601 `YYYY-MM-DD` (or UTC timestamp `YYYY-MM-DDTHH:MM:SSZ`). Local ambiguous date formats (e.g., `11/12/26`) MUST NOT be used.
2. Local cross-references MUST use valid relative Markdown links (`[label](relative/path.md)`). Broken local links or references to non-existent files MUST fail automated validation.
3. Diagrams referenced by a document MUST be linked using their file path and `diagram_id` (`DIAG-...`), and the referenced diagram MUST reside in the scope folder or adjacent `diagrams/` folder.

## 7. Revision History, Status, Assumptions & Open Questions

1. Every approved specification change MUST bump `version`, update `updated_at`, and append a `revision_history` entry.
2. `status: APPROVED` MUST NOT be granted if the document contains `[TO BE COMPLETED]`, `TBD`, `TODO`, or unlogged assumptions.
3. Unconfirmed working hypotheses MUST be explicitly tagged `[ASSUMPTION]` with owner and validation plan, and MUST NOT be written as approved requirements or implemented behavior.
4. Unresolved business or architectural choices MUST be tagged `[OPEN]` / `NEEDS_CLARIFICATION` / `BLOCKED` in an explicit Open Questions register with owner and impact; Agents MUST NOT invent answers to resolve them.
