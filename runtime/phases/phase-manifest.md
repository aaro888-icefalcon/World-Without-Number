# Phase Manifest

Machine-readable mapping of the 6-phase GM pipeline. Schema version 7.5.0.

## PHASE 1: CONTEXT_LOADING
- directory: 1-context-loading/
- cli_commands: (none — this phase reads state and lore files)
- references:
  - `references/hard-rules.md` — non-negotiable mechanical contract
  - `references/gm-protocol.md` — GM behavioral rules and narrative voice
- lore:
  - `lore/latter-earth-overview.md` — world primer (always-load)
  - `lore/history-and-ages.md` — timeline of ages (always-load)
  - `lore/geography.md` — major geographic features
  - `lore/languages.md` — languages of the Latter Earth
  - `lore/nations/*.md` — 57 nation files with §-anchored sections (region-specific load)
  - `lore/nations/carven-peaks.md` — NYC/Carven Peaks primary region (NYC campaign)
  - `lore/nations/manthva.md` — Still Cities on the Gebed Mur (NYC campaign)
  - `lore/nations/mishar.md` — Arena Kingdom, nearest Amundi neighbor (NYC campaign)
  - `lore/nations/nabardura.md` — Fragmented Kingdom (NYC campaign)
  - `lore/nations/fidach.md` — Highland Clans (NYC campaign)
  - `lore/nations/pelegrin.md` — Ascendant Threat (NYC campaign)
  - `lore/nations/qasir.md` — Compromised Kingdom (NYC campaign)
  - `lore/nations/vois.md` — Cautious Republic (NYC campaign)
  - `lore/nations/couront.md` — Monastic Kingdom (NYC campaign)
  - `lore/nations/verdancy.md` — The Verdancy ecological threat (NYC campaign)
  - `lore/nations/black-pact.md` — Black Pact sorcery schools (NYC campaign)
  - `lore/gallery-system.md` — 9-level gallery dungeon reference (NYC campaign, load when in galleries)
  - `lore/nyc-factions.md` — NYC internal power blocs and boroughs (NYC campaign, load when in carven-peaks)
  - `lore/nyc-situation.md` — dynamic start situation and timeline pressures (NYC campaign, session-start load)
  - `lore/nyc-magic.md` — magic manifestation and attunement (NYC campaign, load for magic scenes)
  - `lore/imperator.md` — caged entity and surge dynamics (NYC campaign, load for gallery/surge scenes)
- skills:
  - `skills/lore-loading.md` — lore selection and context budget rules (updated for NYC region-group loading)

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
  - social: NPC generation, reaction rolls, faction turns, diplomacy, consequences
  - world-building: world tick, clock advancement, world pulse, government/society/religion tables
  - downtime: (placeholder — Phase G)
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
  - `level-up --name --class --current-level --target-level --attributes --hp-max --attack-bonus [--tradition] [--partial-classes]` — character level advancement
  - `generate-dungeon --depth [--theme]` — procedural dungeon generation
- references:
  - `skills/combat/references/combat-rules.md` — WWN combat procedures
  - `skills/social/references/npc-reactions.md` — NPC reaction table and modifiers
  - `skills/social/references/faction-rules.md` — faction turn structure and rules
  - `skills/social/references/court-intrigue.md` — court structure and social maneuvering
- tables:
  - `skills/core/tables/attributes.py` — attribute modifiers
  - `skills/core/tables/skills.py` — 22 skill definitions
  - `skills/core/tables/equipment.py` — weapons, armor, gear
  - `skills/core/tables/classes.py` — class progression
  - `skills/core/tables/backgrounds.py` — 20 backgrounds
  - `skills/core/tables/foci.py` — focus definitions
  - `skills/combat/tables/bestiary.py` — creature stat blocks
  - `skills/social/tables/character_tags.py` — d100 NPC character tags
  - `skills/social/tables/court_tags.py` — court intrigue environment tags
  - `skills/social/tables/faction_actions.py` — faction action definitions
  - `skills/world-building/tables/government_tables.py` — government types
  - `skills/world-building/tables/society_tables.py` — society types and features
  - `skills/world-building/tables/religion_tables.py` — religion types and practices
  - `skills/exploration/tables/wilderness_tags.py` — 52+ wilderness environment tags for scene generation
  - `skills/exploration/tables/ruin_tags.py` — 50+ ruin/dungeon environment tags for scene generation
  - `skills/exploration/tables/community_tags.py` — 50+ community/settlement tags for scene generation
  - `skills/core/tables/magic_items.py` — 36 tiered magic items (tier 1-5) for treasure generation
  - `skills/combat/tables/encounter_tables.py` — terrain-based encounter tables with creature ID cross-references
- scripts:
  - `skills/core/scripts/magic.py` — spell casting, Effort, arts, tradition management
  - `skills/combat/scripts/behavior.py` — creature combat AI, behavior trees
  - `skills/combat/scripts/encounter.py` — encounter generation from terrain/threat
  - `skills/exploration/scripts/travel.py` — overland travel, foraging, privation
  - `skills/exploration/scripts/scene.py` — tag-based scene generation
  - `skills/exploration/scripts/treasure.py` — treasure rolls by tier
  - `skills/exploration/scripts/dungeon.py` — procedural dungeon generation
  - `skills/social/scripts/npc.py` — NPC generation with voice cards
  - `skills/social/scripts/faction.py` — faction turn processing
  - `skills/social/scripts/diplomacy.py` — persuasion, negotiation, favor tracking
  - `skills/social/scripts/consequence.py` — consequence tracker, timer checking
  - `skills/world-building/scripts/world_tick.py` — world state advancement

## PHASE 4: NARRATIVE_TRANSLATION
- directory: 4-narrative/
- references:
  - `references/narration-mappings.md` — mechanical-to-narrative translation rules
  - `references/latter-earth-voice.md` — prose style guide (tone, vocabulary, sensory palette)
  - `references/threat-environment-mapping.md` — threat level to environmental description
  - `references/npc-dialogue-protocol.md` — NPC dialogue generation steps
- assets:
  - `assets/character-sheet-template.md` — end-of-turn character sheet display
  - `assets/scene-template.md` — scene rendering template
- tables:
  - `tables/failure_flavors.py` — failure complication flavor text by domain

## PHASE 5: STATE_PERSISTENCE
- directory: 5-persistence/
- cli_commands: validate-state (post-write check)
- references:
  - `schemas/state.schema.json` — state shape contract (v7.5.0)
- skills:
  - `skills/state-persistence.md` — state update procedures and turn receipt

## PHASE 6: VALIDATION
- directory: 6-validation/
- cli_commands: validate-state, validate-reference-freshness, validate-narration-grounding
- skills:
  - `skills/response-gate.md` — turn completeness verification checklist
- validators:
  - `scripts/validate_narration_grounding.py` — narration grounding check (development-time)
