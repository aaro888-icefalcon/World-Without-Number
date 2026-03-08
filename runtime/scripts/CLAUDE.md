# Scripts — Entry Points

Scope: `runtime/scripts/`

## Purpose

Entry point scripts for CLI execution and validation. Domain modules (the actual game logic) live in `phases/3-resolution/skills/<domain>/scripts/`.

## Operating Rules

- Run scripts from repo root (e.g., `python runtime/scripts/emergence_cli.py ...`).
- Treat script output as operational evidence — do not invent outcomes.
- If a script mutates campaign state, re-check `state.json` after it runs.

## Entry Points

| Script | Purpose | Runtime-safe |
|---|---|---|
| `emergence_cli.py` | Unified CLI dispatcher — 14 commands registered (Phases A–D) | Yes |
| `validate_state.py` | State JSON schema validation | Yes |
| `validate_turn_input.py` | Player action provenance validation | Yes |
| `validate_turn_receipt.py` | Turn receipt schema validation | Yes |
| `validate_extraction.py` | Extraction data integrity smoke tests | Development only |
| `validate_reference_freshness.py` | Reference path freshness check | Development only |
| `validate_docs_structure.py` | Documentation structure + schema-doc sync check | Development only |
| `validate_canonical_references.py` | Canonical reference path validator | Development only |
| `validate_narration_grounding.py` | Narration grounding check — flags hallucinated proper nouns | Development only |

## CLI Commands (emergence_cli.py)

| Command | Purpose | Domain |
|---|---|---|
| `roll <expr>` | Dice roll with arithmetic trace | core |
| `skill-check` | 2d6 + skill + attribute vs difficulty | core |
| `save` | Saving throw (physical/evasion/mental) | core |
| `attack` | Combat attack resolution (hit, damage, shock) | combat |
| `create-character` | Generate a new WWN character | core |
| `cast-spell` | Cast a spell using Effort system | core (magic) |
| `encounter` | Generate random encounter by terrain/threat | combat |
| `travel` | Resolve multi-day overland travel | exploration |
| `generate-scene` | Generate scene from tags | exploration |
| `treasure` | Roll treasure by tier | exploration |
| `world-tick` | Advance world state between sessions | world-building |
| `generate-npc` | Generate NPC with voice card | social |
| `reaction-roll` | Roll NPC reaction (2d6) | social |
| `faction-turn` | Run faction turn for all factions | social |

## Domain Module Locations

Domain scripts are physically co-located with their skills in Phase 3:
- `phases/3-resolution/skills/core/scripts/` — dice.py, character.py, conditions.py, magic.py
- `phases/3-resolution/skills/core/tables/` — attributes.py, skills.py, equipment.py, classes.py, backgrounds.py, foci.py
- `phases/3-resolution/skills/combat/scripts/` — combat.py, behavior.py, encounter.py
- `phases/3-resolution/skills/combat/tables/` — bestiary.py
- `phases/3-resolution/skills/exploration/scripts/` — travel.py, scene.py, treasure.py
- `phases/3-resolution/skills/social/scripts/` — npc.py, faction.py, diplomacy.py, consequence.py
- `phases/3-resolution/skills/social/tables/` — character_tags.py, court_tags.py, faction_actions.py
- `phases/3-resolution/skills/world-building/scripts/` — world_tick.py
- `phases/3-resolution/skills/world-building/tables/` — government_tables.py, society_tables.py, religion_tables.py

emergence_cli.py's sys.path includes all domain directories automatically.
