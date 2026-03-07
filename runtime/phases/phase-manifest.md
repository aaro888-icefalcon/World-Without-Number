# Phase Manifest

Machine-readable mapping of the 6-phase GM pipeline.

## PHASE 1: CONTEXT_LOADING
- directory: 1-context-loading/
- cli_commands: (none — this phase reads state and lore files)
- references:
  - `references/hard-rules.md` — non-negotiable mechanical contract
  - `references/gm-protocol.md` — GM behavioral rules and narrative voice
- lore: (none yet — populate with world setting and region lore)

## PHASE 2: ACTION_INTERPRETATION
- directory: 2-action-interpretation/
- cli_commands: (none — this phase classifies actions, does not execute)
- references:
  - `references/action-classification.md` — intent-to-action classification rules
  - `references/cli-reference.md` — complete CLI command contract and argument specs

## PHASE 3: MECHANICAL_RESOLUTION
- directory: 3-resolution/
- domains:
  - core: dice, character, conditions, magic, attributes, skills, equipment, classes, backgrounds, foci
  - combat: attack resolution, morale, bestiary, zone-based positioning, behavior AI, encounter generation
  - exploration: travel, scene generation, treasure
  - social: NPC generation, reaction rolls, faction turns
  - world-building: world tick, clock advancement, world pulse
- cli_commands:
  - `roll <expression>` — dice roll with arithmetic trace
  - `skill-check --attribute-mod --skill-level --difficulty` — 2d6 skill check
  - `save --type --level --modifier` — saving throw (physical/evasion/mental)
  - `attack --attack-bonus --skill-level --attribute-mod --weapon-damage --shock --target-ac --target-hp` — combat attack
  - `create-character --name --class --background --method` — character creation
  - `cast-spell --spell-name --caster-level --tradition --current-effort --system-strain --system-strain-max` — spellcasting via Effort
  - `encounter --terrain --threat-level` — random encounter generation
  - `travel --terrain --days --supplies [--forage-mod] [--threat-level]` — overland travel resolution
  - `generate-scene --scene-type [--tag-count] [--threat-level]` — tag-based scene generation
  - `treasure --tier` — treasure roll by tier (1-5)
  - `world-tick --days` — advance world clocks and generate world pulse
  - `generate-npc [--importance] [--region] [--tags]` — NPC with voice card
  - `reaction-roll [--modifier]` — 2d6 NPC reaction
  - `faction-turn` — process faction actions from state
- references:
  - `skills/combat/references/combat-rules.md` — WWN combat procedures
- tables:
  - `skills/core/tables/attributes.py` — attribute modifiers
  - `skills/core/tables/skills.py` — 22 skill definitions
  - `skills/core/tables/equipment.py` — weapons, armor, gear
  - `skills/core/tables/classes.py` — class progression
  - `skills/core/tables/backgrounds.py` — 20 backgrounds
  - `skills/core/tables/foci.py` — focus definitions
  - `skills/combat/tables/bestiary.py` — creature stat blocks
- scripts:
  - `skills/core/scripts/magic.py` — spell casting, Effort, arts, tradition management
  - `skills/combat/scripts/behavior.py` — creature combat AI, behavior trees
  - `skills/combat/scripts/encounter.py` — encounter generation from terrain/threat
  - `skills/exploration/scripts/travel.py` — overland travel, foraging, privation
  - `skills/exploration/scripts/scene.py` — tag-based scene generation
  - `skills/exploration/scripts/treasure.py` — treasure rolls by tier
  - `skills/social/scripts/npc.py` — NPC generation with voice cards
  - `skills/social/scripts/faction.py` — faction turn processing
  - `skills/world-building/scripts/world_tick.py` — world state advancement

## PHASE 4: NARRATIVE_TRANSLATION
- directory: 4-narrative/
- references:
  - `references/narration-mappings.md` — mechanical-to-narrative translation rules
- assets: (none yet — populate with display templates)

## PHASE 5: STATE_PERSISTENCE
- directory: 5-persistence/
- cli_commands: validate-state (post-write check)
- references:
  - `schemas/state.schema.json` — state shape contract
- skills:
  - `skills/state-persistence.md` — state update procedures and turn receipt

## PHASE 6: VALIDATION
- directory: 6-validation/
- cli_commands: validate-state, validate-reference-freshness
- skills:
  - `skills/response-gate.md` — turn completeness verification checklist
