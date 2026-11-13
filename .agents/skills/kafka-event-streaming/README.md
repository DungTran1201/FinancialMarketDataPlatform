# Skill Package: Kafka Event Streaming & Consumer Delivery (`.agents/skills/kafka-event-streaming/`)

## 1. Directory Purpose

Provides the reusable execution procedure for **Kafka Event Streaming & Consumer Delivery** (`SKILL-024`). Designs and implements versioned Kafka event contracts, topic partitioning, producer durability, consumer offset safety, backpressure, DLQ routing, and replay.

## 2. Scope and Boundaries

- **Belongs in this directory**: `SKILL.md` and `README.md` for `kafka-event-streaming`.
- **Does NOT belong in this directory**: Application runtime code, product requirements, or global rules.

## 3. Agent Role and Responsibilities

Primary owning Agent role: `streaming-data-engineer` (`.agents/agents/streaming-data-engineer.md`).

## 4. Authoritative Inputs

1. `AGENTS.md` — Root Agent operating protocol.
2. `.agents/agents/streaming-data-engineer.md` — Owning role definition.
3. `src/shared/contracts/events.py` and `src/consumers/` — Associated event contract and consumer locations.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `SKILL.md` | Executable instruction specification for `kafka-event-streaming` | Required | `.agents/skills/kafka-event-streaming/SKILL.md` |

## 6. Directory and File Organization

Contains `README.md` and `SKILL.md` inside `.agents/skills/kafka-event-streaming/`.

## 7. Document Creation Rules

`SKILL.md` must begin with YAML frontmatter (`name`, `description`) and contain all 10 standard skill sections.

## 8. Creation Workflow

1. Read `.agents/skills/kafka-event-streaming/README.md` and `SKILL.md`.
2. Verify preconditions and authoritative inputs.
3. Execute the numbered procedure in `SKILL.md`.
4. Run `tools/validators/run_all.py` to verify output compliance.

## 9. Relationships and Dependencies

Registered in `.agents/skill-registry.yaml` and `.agents/skills_manifest.json`, and invoked during lifecycle phase `06-architecture`.

## 10. Quality Gate

`SKILL.md` contains valid frontmatter and all required sections, passing `validate_agent_config.py`.

## 11. Validation Commands

```powershell
python tools/validators/validate_agent_config.py
python tools/validators/validate_readmes.py
python tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT bypass target directory `README.md` instructions when executing this skill.
- Do NOT fabricate requirements or mark unverified outputs as `APPROVED`.

