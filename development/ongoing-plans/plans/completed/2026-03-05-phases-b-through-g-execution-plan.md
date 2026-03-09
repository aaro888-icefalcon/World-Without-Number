# Execution Plan: Phases B through G — Full WWN AI RPG Implementation

- **Owner:** Development team
- **Status:** Draft
- **Start Date:** 2026-03-05
- **Target Date:** Phased (see milestones)
- **Related Decision Logs:** `plans/active/2026-03-04-wwn-extraction-and-ai-rpg-plan.md`
- **Supersedes:** Part V §11 Phases B-G of the parent plan (this plan adds task-level detail, dependency graphs, fail-state analysis, and validation gates)

---

## Key Objective

**Primary formulation:** Build a vertical-slice AI RPG that executes an end-to-end turn loop — player natural language in, deterministic CLI resolution, narrated prose out, validated state persisted — then widen the slice across six phases until the full WWN system is playable.

**Constraint formulation:** Every phase must leave the system in a playable state. No phase may break the turn loop contract. Each phase adds a new *kind* of play (magic, exploration, social, narrative, setting, advanced) while preserving all prior kinds.

---

## Phase A Status Assessment (Baseline)

### Completed
- Core tables: attributes, skills, equipment, classes, backgrounds, foci
- Core scripts: dice.py, character.py, conditions.py
- Combat domain: combat.py, bestiary.py (partial), combat-rules.md
- emergence_cli.py with 5 commands: roll, skill-check, save, attack, create-character
- State schema v7 with WWN character model
- state.json with valid starter character
- Governance: hard-rules.md, gm-protocol.md, all validators, test suite
- validate_extraction.py smoke tests

### Not Yet Completed (Phase A Gaps)
- **A-GAP-1:** Zone-based combat positioning not implemented in combat.py or state schema
- **A-GAP-2:** No end-to-end turn loop test (manual or automated)
- **A-GAP-3:** Phases 2, 4, 5, 6 have CLAUDE.md stubs but no operational content (no skills, no references, no assets)
- **A-GAP-4:** phase-manifest.md not updated with implemented commands/references
- **A-GAP-5:** Script registry (scripts/CLAUDE.md) lists emergence_cli.py commands but domain scripts aren't registered

### Pre-Phase-B Remediation (Required)
Before expanding into new mechanics, the existing foundation must close these gaps. This is "Phase A.5":

- [ ] **A.5-1:** Update phase-manifest.md with all Phase A deliverables (cli_commands, references, domains)
- [ ] **A.5-2:** Wire Phase 2 minimally — create `action-classification.md` reference and `cli-reference.md` listing all 5 commands with argument specs
- [ ] **A.5-3:** Wire Phase 4 minimally — create `narration-mappings.md` with combat/skill-check/save narrative treatment rules
- [ ] **A.5-4:** Wire Phase 5 minimally — create `state-persistence.md` skill documenting the state update procedure
- [ ] **A.5-5:** Wire Phase 6 minimally — create `response-gate.md` skill documenting validation checklist
- [ ] **A.5-6:** Add zone fields to combat state (abstract zones: melee/near/far/distant)
- [ ] **A.5-7:** Run one manual end-to-end turn: player input → Phase 1-6 → validated output. Document gaps found.
- [ ] **A.5-8:** Run all existing tests and validators; fix any failures

**Acceptance:** All 6 phases have at least one operational document. phase-manifest.md reflects reality. Tests pass.

---

## Dependency Graph (Phase Ordering)

```
A.5 (foundation gaps)
 │
 ├──► B (magic + bestiary)
 │     │
 │     └──► C (exploration + world)
 │           │
 │           ├──► D (social + factions)
 │           │     │
 │           │     └──► E (narrative layer) ◄── can start partially after B
 │           │           │
 │           │           └──► F (atlas + setting) ◄── can start extraction during D
 │           │                 │
 │           │                 └──► G (advanced systems)
 │           │
 │           └──► F (extraction can begin in parallel)
 │
 └──► E (partial: narration-mappings for combat can begin immediately)
```

**Critical path:** A.5 → B → C → D → E → G
**Parallelizable:** F extraction can run during C/D. E narration-mappings can start during B.

---

# PHASE B: MAGIC + BESTIARY

## Objective
A mage character can prepare spells, cast them via CLI, expend Effort, and fight creatures that use deterministic behavior trees.

## Extraction Tasks (Data)

- [ ] **B-EXT-1:** Extract High Magic spell list (WWN 2) — all 5 levels, ~50 spells
  - Format: Python list of dicts `{name, level, tradition, duration, description}`
  - Target: `phases/3-resolution/skills/core/tables/spells.py`
  - Validation: count matches source PDF, all required fields non-null

- [ ] **B-EXT-2:** Extract Elementalist arts and spells (WWN 2)
  - Format: same as B-EXT-1 plus `{art_name, art_level, effect}`
  - Target: append to spells.py, new `arts.py` for tradition arts

- [ ] **B-EXT-3:** Extract Necromancer arts and spells (WWN 2)
  - Same format and target as B-EXT-2

- [ ] **B-EXT-4:** Extract Healer arts (WWN 2)
  - Same format and target as B-EXT-2

- [ ] **B-EXT-5:** Expand bestiary — extract remaining creatures from WWN 4 pp.283-321 and WWN 5 pp.148-155
  - Target: expand `combat/tables/bestiary.py`
  - Validation: total creature count matches source; each has HD, AC, Atk, Dmg, Move, ML, Inst, Skill, Save

- [ ] **B-EXT-6:** Extract magic items from WWN 4 (small initial set — 10-15 items)
  - Format: Python list of dicts `{name, type, description, mechanical_effect}`
  - Target: `phases/3-resolution/skills/core/tables/magic_items.py`

## Implementation Tasks (Scripts)

- [ ] **B-IMPL-1:** Create `magic.py` in `phases/3-resolution/skills/core/scripts/`
  - Functions: `prepare_spells(caster, spell_list)`, `cast_spell(caster, spell, target)`, `expend_effort(caster, duration)`, `recover_effort(caster, rest_type)`
  - Must handle: Effort commitment (scene/day/indefinite), System Strain interaction, spell slot tracking
  - Output: JSON with spell effect, effort cost, any target effects, seed

- [ ] **B-IMPL-2:** Create `behavior.py` in `phases/3-resolution/skills/combat/scripts/`
  - Deterministic creature combat AI: decision tree based on creature stats + battlefield state
  - Input: creature entry from bestiary + current combat state (zones, HP, allies)
  - Output: chosen action `{action_type, target, reasoning}`
  - Decision factors: morale (ML), HP threshold, ally count, creature instinct (Inst), zone positions
  - Special behavior tags: "spellcaster," "pack tactics," "ambush predator," "guardian"

- [ ] **B-IMPL-3:** Expand `combat.py` for multi-creature combat
  - Batch resolution: all enemies in one call
  - Initiative: group initiative (side-based, per WWN rules)
  - Round tracking in combat state
  - Zone validation: range checks for attacks and spells

- [ ] **B-IMPL-4:** Create `encounter.py` in `phases/3-resolution/skills/combat/scripts/`
  - Generate random encounters from terrain type + threat level
  - Instantiate creatures from bestiary with HP rolls
  - Output: encounter descriptor JSON with creature list, initial zones, environmental features

## CLI Integration

- [ ] **B-CLI-1:** Add `cast-spell` subcommand to emergence_cli.py
  - Args: `--spell`, `--caster-level`, `--tradition`, `--effort-current`, `--target-save` (optional), `--system-strain`
  - Output: spell resolution JSON

- [ ] **B-CLI-2:** Add `encounter` subcommand
  - Args: `--terrain`, `--threat-level`, `--seed`
  - Output: encounter setup JSON

- [ ] **B-CLI-3:** Add `combat-round` subcommand for batch multi-creature resolution
  - Args: `--state-file` (combat state JSON) or inline `--combatants`
  - Output: full round resolution with all actions + results

## Schema Changes

- [ ] **B-SCHEMA-1:** Add to character state:
  - `spells_prepared: []` — list of prepared spell names
  - `tradition: string` — mage tradition
  - `effort: {current: int, committed_scene: int, committed_day: int, committed_indefinite: int}`
  - `spell_slots: {level_1: int, level_2: int, ...}` — per-level slots
  - **APPROVAL GATE:** Schema version bump 7.0.0 → 7.1.0

- [ ] **B-SCHEMA-2:** Add `combat_state` object to state.json for tracking active combat:
  - `active: bool`, `round: int`, `initiative_order: []`, `zones: {melee: [], near: [], far: [], distant: []}`, `combatants: [{id, hp, conditions, zone}]`

## Integration Touchpoints (per change-integration-checklist.md)

- [ ] **B-INT-1:** Create `phases/3-resolution/skills/core/magic-resolution.md` skill file (9-section format)
- [ ] **B-INT-2:** Update Phase 3 index.md with magic domain
- [ ] **B-INT-3:** Update Phase 3 CLAUDE.md routing table
- [ ] **B-INT-4:** Update phase-manifest.md Phase 3 cli_commands and references
- [ ] **B-INT-5:** Update scripts/CLAUDE.md script registry with cast-spell, encounter, combat-round
- [ ] **B-INT-6:** Update Phase 2 action-classification.md and cli-reference.md with new commands
- [ ] **B-INT-7:** Add magic narrative treatments to Phase 4 narration-mappings.md

## Tests

- [ ] **B-TEST-1:** `test_magic.py` — spell preparation, casting, effort tracking, System Strain interaction
- [ ] **B-TEST-2:** `test_behavior.py` — creature AI produces consistent decisions for same inputs
- [ ] **B-TEST-3:** `test_encounter.py` — encounter generation produces valid creature sets
- [ ] **B-TEST-4:** Expand `test_phase_a.py` → `test_phase_b.py` for Phase B acceptance
- [ ] **B-TEST-5:** Extraction smoke tests for spell counts, art counts, bestiary counts

## Fail States

| ID | Fail State | Probability | Detection | Mitigation |
|----|-----------|-------------|-----------|------------|
| B-F1 | Spell description extraction is too lossy from PDF | High | B-TEST-5 smoke tests + manual spot-check | Store descriptions as full text strings; only extract structured metadata (name, level, tradition). LLM interprets effects at runtime. |
| B-F2 | Effort/System Strain interaction has edge cases not covered | Medium | B-TEST-1 edge case tests | Model exactly per WWN rules: System Strain caps magical healing, Effort recovery happens on rest. Start with strict RAW, loosen only if needed. |
| B-F3 | Behavior tree produces nonsensical creature actions | Medium | B-TEST-2 + playtest | Start with 4 simple behavior profiles (aggressive, cautious, pack, guardian). Add complexity only when needed. |
| B-F4 | Multi-creature combat is too slow (O(n²) interactions) | Low | Performance test with 10+ creatures | Batch by side: all enemies resolve, then player. No cross-creature interaction within same side's turn. |
| B-F5 | Schema migration breaks existing state.json | Medium | B-SCHEMA-1 + validate_state.py | Write migration script that adds new fields with sensible defaults to existing state files. |

## Acceptance Criteria

1. `emergence_cli.py cast-spell --spell "The Coruscating Coffin" --caster-level 3 --tradition "high_magic" --effort-current 1` → valid JSON
2. `emergence_cli.py encounter --terrain forest --threat-level 3 --seed 42` → valid encounter with 1-4 creatures
3. `emergence_cli.py combat-round` with 3 enemies → all enemies choose actions via behavior tree, resolve attacks
4. Behavior tree is deterministic: same inputs → same outputs across runs
5. All spell traditions have correct count of spells matching source PDFs
6. State schema v7.1.0 validates with magic-capable character
7. All tests pass: `python runtime/tests/run_all_tests.py 1`

---

# PHASE C: EXPLORATION + WORLD

## Objective
A character can travel between locations, encounter wilderness hazards, explore ruins/dungeons, find treasure, and experience a world that advances between sessions.

## Extraction Tasks

- [ ] **C-EXT-1:** Extract wilderness tags from WWN 3 (~100 tags)
  - Format: `{name, description, enemies, friends, complications, things, places}`
  - Target: `phases/3-resolution/skills/exploration/tables/wilderness_tags.py`

- [ ] **C-EXT-2:** Extract ruin tags from WWN 3 (~100 tags)
  - Same normalized schema as wilderness tags
  - Target: `phases/3-resolution/skills/exploration/tables/ruin_tags.py`

- [ ] **C-EXT-3:** Extract community tags from WWN 3 (~100 tags)
  - Target: `phases/3-resolution/skills/world-building/tables/community_tags.py`

- [ ] **C-EXT-4:** Extract travel/overland rules from WWN 1 pp.49-53
  - Target: `phases/3-resolution/skills/exploration/references/travel-rules.md`
  - Includes: movement rates, foraging DCs, privation rules, supply tracking

- [ ] **C-EXT-5:** Extract dungeon exploration rules from WWN 3
  - Target: `phases/3-resolution/skills/exploration/references/dungeon-crawl.md`

- [ ] **C-EXT-6:** Extract treasure tables from WWN 3
  - Format: Python dicts (tiered by dungeon level/challenge)
  - Target: `phases/3-resolution/skills/exploration/tables/treasure_tables.py`

- [ ] **C-EXT-7:** Extract encounter tables by terrain type from WWN 1/3
  - Target: `phases/3-resolution/skills/exploration/tables/encounter_tables.py`

- [ ] **C-EXT-8:** Extract hex generation tables from WWN 3
  - Target: `phases/3-resolution/skills/world-building/tables/hex_tables.py`

## Implementation Tasks

- [ ] **C-IMPL-1:** Create `exploration/` domain directory under skills/
  - Subdirs: scripts/, tables/, references/

- [ ] **C-IMPL-2:** Create `travel.py` in exploration/scripts/
  - Functions: `calculate_travel(origin, destination, terrain, party_size, supplies)`, `forage(skill_mod, terrain)`, `check_encounter(terrain, threat_level)`, `apply_privation(character)`
  - Output: day-by-day travel log JSON with encounters, foraging results, supply consumption

- [ ] **C-IMPL-3:** Create `scene.py` in exploration/scripts/
  - Functions: `generate_scene(scene_type, tags, threat_level)`, `generate_ruin(ruin_tags, depth_level)`, `generate_wilderness_hex(terrain, tags)`
  - Pulls from tag tables to create scene seeds with NPCs, hazards, treasures, hooks
  - Output: scene descriptor JSON

- [ ] **C-IMPL-4:** Create `treasure.py` in exploration/scripts/
  - Functions: `roll_treasure(tier, context)`, `generate_magic_item(tier)` (uses magic_items table from Phase B)
  - Output: treasure manifest JSON

- [ ] **C-IMPL-5:** Create `world_tick.py` in world-building/scripts/
  - Functions: `advance_world(state, days_elapsed)` — processes all clocks, generates events, updates world pulse
  - Faction clock advancement (simplified — full faction turns in Phase D)
  - Event generation from tables
  - World pulse: news, rumors, trends, arrivals
  - Output: world advancement summary JSON

- [ ] **C-IMPL-6:** Add session summary generation
  - Function in persistence or a utility: `generate_session_summary(chronicle_entries)` → 200-word summary
  - Stored in `campaign.session_summary` in state.json

- [ ] **C-IMPL-7:** Add scene rhythm tracker
  - Track consecutive scene types in `campaign.scene_rhythm: []`
  - If 3+ consecutive scenes of same type, flag for pacing shift

## CLI Integration

- [ ] **C-CLI-1:** Add `travel` subcommand
  - Args: `--terrain`, `--days`, `--supplies`, `--skill-mod`, `--seed`
  - Output: travel resolution JSON

- [ ] **C-CLI-2:** Add `generate-scene` subcommand
  - Args: `--type` (wilderness/ruin/community), `--tags` (count), `--threat-level`, `--seed`
  - Output: scene seed JSON

- [ ] **C-CLI-3:** Add `world-tick` subcommand
  - Args: `--days` (days to advance), `--state-file`
  - Output: world advancement JSON

- [ ] **C-CLI-4:** Add `treasure` subcommand
  - Args: `--tier`, `--context` (dungeon/wilderness/quest), `--seed`
  - Output: treasure JSON

## Schema Changes

- [ ] **C-SCHEMA-1:** Add to state.json:
  - `campaign.scene_rhythm: []` — recent scene type history
  - `campaign.session_summary: string` — last session summary
  - `campaign.supplies: {food: int, water: int, torches: int, tools: int}`
  - `world.explored_hexes: []` — list of explored hex coordinates
  - `world.hex_map: {}` — generated hex data (sparse — only explored hexes)
  - **APPROVAL GATE:** Schema version bump 7.1.0 → 7.2.0

## Integration Touchpoints

- [ ] **C-INT-1:** Create exploration domain directory with index.md
- [ ] **C-INT-2:** Create world-building domain directory with index.md
- [ ] **C-INT-3:** Create skill files for travel, scene generation, treasure, world tick
- [ ] **C-INT-4:** Update Phase 3 index.md + CLAUDE.md with new domains
- [ ] **C-INT-5:** Update phase-manifest.md with new cli_commands and references
- [ ] **C-INT-6:** Update scripts/CLAUDE.md registry
- [ ] **C-INT-7:** Update Phase 2 action-classification.md + cli-reference.md
- [ ] **C-INT-8:** Add exploration/travel narrative treatments to Phase 4 narration-mappings.md

## Tests

- [ ] **C-TEST-1:** `test_travel.py` — travel resolution, foraging, privation, encounter triggers
- [ ] **C-TEST-2:** `test_scene.py` — scene generation produces valid scenes from tags
- [ ] **C-TEST-3:** `test_world_tick.py` — clock advancement, event generation, world pulse
- [ ] **C-TEST-4:** `test_treasure.py` — treasure rolls produce valid items in expected tier range
- [ ] **C-TEST-5:** Extraction smoke tests for tag counts (wilderness, ruin, community)
- [ ] **C-TEST-6:** `test_phase_c.py` — Phase C acceptance tests

## Fail States

| ID | Fail State | Probability | Detection | Mitigation |
|----|-----------|-------------|-----------|------------|
| C-F1 | Tag extraction misses structure variance (some tags lack enemies/friends fields) | High | C-TEST-5 + field-presence check | Normalize schema: missing fields become `null`, not absent. Validate schema compliance. |
| C-F2 | Travel resolution is boring — just "day 1: nothing, day 2: nothing" | Medium | Playtest | Minimum one event per 3 travel days. Events include non-combat: weather, terrain features, NPCs, landmarks. |
| C-F3 | World tick produces incoherent world pulse (contradictory news) | Medium | C-TEST-3 + manual review | Limit world pulse to factual reports of clock changes. Rumors can be unreliable (marked as such). |
| C-F4 | Scene generation produces bland/repetitive scenes | Medium | Playtest | Tag combination system: 2 tags per scene create emergent combinations. Never use single-tag scenes. |
| C-F5 | Hex map state grows unbounded | Low | Size check on state.json | Cap explored hexes at 100 for MVP. Prune distant/unvisited hexes on session start. |

## Acceptance Criteria

1. `emergence_cli.py travel --terrain forest --days 5 --supplies 10 --seed 42` → 5-day travel log with encounters
2. `emergence_cli.py generate-scene --type ruin --tags 2 --threat-level 4 --seed 42` → playable scene seed
3. `emergence_cli.py world-tick --days 7` → world advancement with clock changes and world pulse
4. Tag databases have correct counts matching source PDFs
5. All tests pass

---

# PHASE D: SOCIAL + FACTIONS

## Objective
NPCs have persistent personalities and voice, factions pursue goals autonomously via faction turns, the player has reputation standing, and campaign arcs provide narrative structure.

## Extraction Tasks

- [ ] **D-EXT-1:** Extract character tags (d100) from WWN 5
  - Target: `phases/3-resolution/skills/social/tables/character_tags.py`

- [ ] **D-EXT-2:** Extract court tags from WWN 3
  - Target: `phases/3-resolution/skills/social/tables/court_tags.py`

- [ ] **D-EXT-3:** Extract faction actions, costs, and requirements from WWN 4
  - Target: `phases/3-resolution/skills/social/tables/faction_actions.py`

- [ ] **D-EXT-4:** Extract NPC reaction rules from WWN 1/4
  - Target: `phases/3-resolution/skills/social/references/npc-reactions.md`

- [ ] **D-EXT-5:** Extract faction rules from WWN 4
  - Target: `phases/3-resolution/skills/social/references/faction-rules.md`

- [ ] **D-EXT-6:** Extract court intrigue rules from WWN 3
  - Target: `phases/3-resolution/skills/social/references/court-intrigue.md`

- [ ] **D-EXT-7:** Extract world-building generation tables from WWN 2 (government, society, religion)
  - Target: `phases/3-resolution/skills/world-building/tables/government_tables.py`, `society_tables.py`, `religion_tables.py`

## Implementation Tasks

- [ ] **D-IMPL-1:** Create `social/` domain directory under skills/

- [ ] **D-IMPL-2:** Create `npc.py` in social/scripts/
  - Functions: `generate_npc(importance, region, tags_count)`, `reaction_roll(npc, context_modifiers)`, `update_relationship(npc_id, delta, reason)`
  - NPC generation includes: name, character tags, personality traits, speech patterns, key phrases, motivation, physical description
  - Voice card: 2-3 sentence prompt for LLM when generating dialogue for this NPC
  - Output: NPC record JSON compatible with `known_npcs` state schema

- [ ] **D-IMPL-3:** Create `faction.py` in social/scripts/
  - Functions: `faction_turn(factions, world_state)`, `execute_faction_action(faction, action, resources)`, `resolve_faction_conflict(faction_a, faction_b)`
  - Processes all factions in one call
  - Each faction: choose action based on goals + resources → execute → update assets/goals
  - Output: faction turn summary JSON (actions taken, results, state changes)

- [ ] **D-IMPL-4:** Add consequence tracker
  - Structure in state.json: `consequence_tracker: [{id, trigger_condition, timer_days, consequence, source_turn}]`
  - Phase 5 checks triggers each turn
  - Consequences can: spawn NPCs, modify faction standing, create events, alter scene properties

- [ ] **D-IMPL-5:** Add arc beats system
  - Structure: `campaign_arcs[].beats: [{beat_name, trigger_condition, status, payoff_description}]`
  - Phase 1 checks beat triggers during context loading
  - When a beat triggers, it queues a narrative event for Phase 4

- [ ] **D-IMPL-6:** Create `diplomacy.py` in social/scripts/ (or extend npc.py)
  - Persuasion/negotiation as structured skill checks with NPC disposition modifiers
  - Bribery cost calculation, favor tracking

## CLI Integration

- [ ] **D-CLI-1:** Add `generate-npc` subcommand
  - Args: `--importance` (minor/major/faction-leader), `--region`, `--tags` (count), `--seed`

- [ ] **D-CLI-2:** Add `reaction-roll` subcommand
  - Args: `--npc-id`, `--context-modifier`, `--seed`

- [ ] **D-CLI-3:** Add `faction-turn` subcommand
  - Args: `--state-file`, `--seed`
  - Output: complete faction turn results for all factions

- [ ] **D-CLI-4:** Add `generate-court` subcommand (optional — if court rules warrant a generator)
  - Args: `--community-type`, `--tags`, `--seed`

## Schema Changes

- [ ] **D-SCHEMA-1:** Expand `known_npcs[]` entries:
  - Add: `voice_card: string`, `motivation: string`, `speech_patterns: string`, `key_phrases: []`, `last_interaction_summary: string`, `relationship_arc: string`

- [ ] **D-SCHEMA-2:** Expand `human_factions[]`:
  - Add: `assets: {}`, `goals: []`, `current_action: string`, `resources: {}`, `turn_history: []`

- [ ] **D-SCHEMA-3:** Add:
  - `consequence_tracker: []`
  - `campaign_arcs[].beats: []`
  - `pc_standing[]` entries get `reputation_score: int`, `last_interaction: string`
  - **APPROVAL GATE:** Schema version bump 7.2.0 → 7.3.0

## Integration Touchpoints

- [ ] **D-INT-1:** Create social domain directory with index.md
- [ ] **D-INT-2:** Create skill files for NPC generation, faction turn, reaction roll
- [ ] **D-INT-3:** Update Phase 3 index.md + CLAUDE.md
- [ ] **D-INT-4:** Update phase-manifest.md
- [ ] **D-INT-5:** Update scripts/CLAUDE.md registry
- [ ] **D-INT-6:** Update Phase 2 action-classification.md + cli-reference.md
- [ ] **D-INT-7:** Add social narrative treatments to Phase 4 narration-mappings.md
- [ ] **D-INT-8:** Wire consequence tracker into Phase 5 state-persistence.md
- [ ] **D-INT-9:** Wire arc beats into Phase 1 context loading

## Tests

- [ ] **D-TEST-1:** `test_npc.py` — NPC generation, voice card, reaction rolls
- [ ] **D-TEST-2:** `test_faction.py` — faction turn resolution, action execution, conflict resolution
- [ ] **D-TEST-3:** `test_consequence.py` — consequence trigger checking, timer advancement
- [ ] **D-TEST-4:** Extraction smoke tests for tag counts (character, court, faction actions)
- [ ] **D-TEST-5:** `test_phase_d.py` — Phase D acceptance

## Fail States

| ID | Fail State | Probability | Detection | Mitigation |
|----|-----------|-------------|-----------|------------|
| D-F1 | Faction turn is too complex for single-player game | High | Playtest | Start with 2-3 factions max. Simplified action set. Full complexity is optional. |
| D-F2 | NPC voice cards don't produce distinct dialogue | Medium | Playtest | Include concrete examples in voice card: "Sample dialogue: 'The sea takes what she will, friend.'" |
| D-F3 | Consequence tracker grows unbounded | Medium | Size monitoring | Max 20 active consequences. Oldest expire. Consequences with expired timers auto-resolve. |
| D-F4 | Faction state model is too simplified to feel alive | Medium | Playtest | Start simplified, iterate. Faction "personality" (aggressive/cautious/expansionist) drives action selection. |
| D-F5 | Arc beats feel railroaded | Low | Design review | Beats are SITUATIONS that trigger, not OUTCOMES. The beat creates a scene; player choices determine what happens. |

## Acceptance Criteria

1. `emergence_cli.py generate-npc --importance major --region coastal --tags 3 --seed 42` → NPC with voice card
2. `emergence_cli.py faction-turn` with 3 active factions → all factions take actions, results summarized
3. `emergence_cli.py reaction-roll --npc-id npc_001 --context-modifier 2` → disposition result
4. Consequence tracker fires when trigger condition met
5. All tests pass

---

# PHASE E: NARRATIVE LAYER

## Objective
The LLM-as-GM produces consistently toned, mechanically faithful narration. NPCs speak in distinct voices. The game feels like a Latter Earth story, not a calculator.

## Why This Phase Exists Separately

Phases B-D add *mechanics*. Phase E adds the *presentation layer* — how those mechanics feel to the player. This is the phase where the game becomes an RPG rather than a CLI tool. It is primarily about creating reference documents and validation tooling, not Python scripts.

## Implementation Tasks

- [ ] **E-IMPL-1:** Create `latter-earth-voice.md` in Phase 4 references/
  - Prose style guide extracted from WWN 1 intro + WWN 5 atlas prose
  - Tone: archaic, melancholy, wondrous, tinged with decay
  - Vocabulary guidelines: words to use, words to avoid
  - Sentence rhythm: long descriptive sentences punctuated by short declarative ones
  - Sample passages for each scene type

- [ ] **E-IMPL-2:** Expand `narration-mappings.md` into comprehensive treatment rules
  - Combat hit: how to describe damage at different severity levels
  - Combat miss: always include a consequence or detail (G4: interesting failure)
  - Spell casting: describe the magical effect before revealing mechanical result (T2: tension)
  - Skill check: describe the attempt first, then the outcome
  - Travel: environmental sensory detail per terrain type
  - Social: NPC body language and environmental reactions
  - Forced consequences: BINDING — narrate exactly, with gravity
  - Routine events: cap at ~150 words (G7)
  - Dramatic moments: full narration with sensory detail

- [ ] **E-IMPL-3:** Create character sheet display template in Phase 4 assets/
  - Compact format for end-of-turn display
  - Shows: HP, AC, conditions, key resources, equipped weapons, spells prepared, effort
  - Must be derived from state.json — never hand-composed

- [ ] **E-IMPL-4:** Create scene rendering template in Phase 4 assets/
  - Shows: location, time, weather, threat indicators, visible NPCs, notable features
  - Environmental cues that translate threat level to sensory detail (G5: telegraph danger)

- [ ] **E-IMPL-5:** Create failure consequence flavor tables
  - Per domain: combat miss, skill check failure, spell failure, travel hazard, social gaffe
  - Each entry: brief complication or revelation (never "nothing happens")
  - Format: Python dicts in `phases/4-narrative/tables/failure_flavors.py`
  - These are PROMPTS for the LLM, not complete narrations

- [ ] **E-IMPL-6:** Drama budget system
  - Add `session.drama_budget: int` to state (starts at 3 per session)
  - Dramatic escalations (life-threatening combat, betrayal, major revelation) cost 1 point
  - When budget=0, remaining encounters are lower-stakes
  - Phase 5 tracks budget; Phase 2 considers budget when classifying action intensity

- [ ] **E-IMPL-7:** Create threat-level-to-environment mapping reference
  - Threat 0 (safe): warm light, birdsong, clean air
  - Threat 1-2 (mild): subtle wrongness, distant sounds, animals behaving oddly
  - Threat 3-4 (dangerous): visible damage, signs of conflict, NPC warnings
  - Threat 5+ (lethal): active hazards, corpses, distorted reality

- [ ] **E-IMPL-8:** Create NPC dialogue protocol skill in Phase 4
  - Step 1: Load NPC voice card from known_npcs
  - Step 2: Generate dialogue that matches speech_patterns and personality_traits
  - Step 3: Include at least one key_phrase per extended conversation
  - Step 4: Reference last_interaction_summary for continuity

- [ ] **E-IMPL-9:** Create `validate-narration-grounding.py` validator (Phase 6)
  - Checks: are there proper nouns in narration that don't appear in loaded context?
  - Flags potential hallucinations for review
  - This is a development-time tool, not a turn-loop blocker

## Schema Changes

- [ ] **E-SCHEMA-1:** Add:
  - `session.drama_budget: int`
  - `session.drama_events: []` — log of dramatic moments this session
  - **APPROVAL GATE:** Schema version bump 7.3.0 → 7.4.0

## Integration Touchpoints

- [ ] **E-INT-1:** Phase 4 CLAUDE.md rewritten from stub to full operational instructions
- [ ] **E-INT-2:** Phase 4 index.md updated with all new assets and references
- [ ] **E-INT-3:** phase-manifest.md Phase 4 section populated
- [ ] **E-INT-4:** Phase 6 CLAUDE.md updated with narration grounding check
- [ ] **E-INT-5:** Hard rules updated: "Narrative must follow the Latter Earth voice guide"
- [ ] **E-INT-6:** GM protocol updated with drama budget rules

## Tests

- [ ] **E-TEST-1:** `test_failure_flavors.py` — all domains have failure tables, all entries are non-empty strings
- [ ] **E-TEST-2:** `test_narration_grounding.py` — validator catches hallucinated proper nouns in test narration
- [ ] **E-TEST-3:** `test_phase_e.py` — all Phase E reference files exist and have required sections

## Fail States

| ID | Fail State | Probability | Detection | Mitigation |
|----|-----------|-------------|-----------|------------|
| E-F1 | Narration mappings are too prescriptive, produce formulaic prose | Medium | Playtest | Mappings define CONSTRAINTS, not templates. "Describe the hit with physical impact" not "Say 'Your blade strikes true.'" |
| E-F2 | Drama budget feels artificial/gamey | Medium | Playtest | Budget is invisible to player. GM adjusts encounter intensity naturally. Budget is a GUIDELINE for the LLM, not a hard gate. |
| E-F3 | Latter Earth voice guide is ignored by LLM in practice | High | Playtest | Include voice guide in Phase 1 always-load context. Short (500 words max). Sample sentences the LLM can pattern-match from. |
| E-F4 | Narration grounding validator has too many false positives | Medium | E-TEST-2 | Whitelist common English proper nouns. Only flag nouns that look like WWN-specific names (capitalized multi-word phrases, non-English roots). |

## Acceptance Criteria

1. Phase 4 has complete operational instructions, voice guide, narration mappings, templates
2. Each mechanic domain (combat, magic, exploration, social) has narration treatment rules
3. Failure flavor tables cover all domains with 5+ entries each
4. Narration grounding validator runs without errors on clean narration
5. Character sheet template renders correctly from state.json data

---

# PHASE F: ATLAS + FULL SETTING

## Objective
The complete Latter Earth setting is extractable and loadable. Any canonical WWN location can serve as a game setting with region-appropriate lore, culture, and encounter context.

## Extraction Tasks (This Phase Is Primarily Extraction)

- [ ] **F-EXT-1:** Extract all 40+ nation descriptions from WWN 5
  - Target: `phases/1-context-loading/lore/nations/` (one .md file per nation)
  - Each file must include: history, geography, government, culture, cultural implications, sensory palette, voice notes (how NPCs from here speak), adventure hooks
  - Format: Markdown with §anchors for sub-sections

- [ ] **F-EXT-2:** Extract history/timeline from WWN 2 + WWN 5
  - Target: `phases/1-context-loading/lore/history-and-ages.md`
  - Covers: the ages of the Latter Earth, rise and fall of empires, the Legacy

- [ ] **F-EXT-3:** Extract geographic reference from WWN 5
  - Target: `phases/1-context-loading/lore/geography.md`
  - Covers: seas, mountain ranges, major rivers, climate zones

- [ ] **F-EXT-4:** Extract Latter Earth overview/setting intro from WWN 1 + WWN 2
  - Target: `phases/1-context-loading/lore/latter-earth-overview.md`

- [ ] **F-EXT-5:** Extract language/culture reference
  - Target: `phases/1-context-loading/lore/languages.md`

- [ ] **F-EXT-6:** Create region-specific encounter table overlays
  - Modify encounter_tables.py to support region-specific variants
  - Some regions have unique creatures/hazards

## Implementation Tasks

- [ ] **F-IMPL-1:** Create lore/ directory structure with index.md and nations/ subdirectory

- [ ] **F-IMPL-2:** Create tiered context loading logic documentation
  - Phase 1 skill: `lore-loading.md` — how to select which lore to load based on current_scene.region
  - Rule: load nation file for current region + geography for adjacent regions + overview always
  - Context budget: ~2000 tokens of lore per turn (L1 mitigation)

- [ ] **F-IMPL-3:** Create `[UNKNOWN]` marker convention
  - Lore docs include `[UNKNOWN]` for deliberately unexplained phenomena
  - Phase 4 narration: when encountering `[UNKNOWN]`, narrate as genuine mystery — never invent explanations (T7)

- [ ] **F-IMPL-4:** Add lore grounding protocol to Phase 1
  - Hard rule: LLM may only reference lore loaded in Phase 1 context
  - If player asks about something not in loaded context, in-world answer: "Your character doesn't know" or "Rumors suggest..." (with `[UNKNOWN]` marker)

## Schema Changes

- [ ] **F-SCHEMA-1:** Add:
  - `current_scene.region_id: string` — links to nation/region lore file
  - `world.known_regions: []` — regions the PC has visited or heard about
  - **APPROVAL GATE:** Schema version bump 7.4.0 → 7.5.0

## Integration Touchpoints

- [ ] **F-INT-1:** Create `phases/1-context-loading/lore/index.md` — master lore inventory
- [ ] **F-INT-2:** Create `phases/1-context-loading/lore/nations/index.md` — nation file listing
- [ ] **F-INT-3:** Create lore-loading skill in Phase 1
- [ ] **F-INT-4:** Update Phase 1 CLAUDE.md with lore loading instructions
- [ ] **F-INT-5:** Update Phase 1 index.md
- [ ] **F-INT-6:** Update phase-manifest.md Phase 1 section with lore references

## Tests

- [ ] **F-TEST-1:** Extraction smoke tests: nation count matches source, each file has required §sections
- [ ] **F-TEST-2:** `test_lore_loading.py` — verify lore files are well-formed and loadable
- [ ] **F-TEST-3:** `test_phase_f.py` — all lore files exist, index.md is accurate

## Fail States

| ID | Fail State | Probability | Detection | Mitigation |
|----|-----------|-------------|-----------|------------|
| F-F1 | 40+ nation files bloat the repo significantly | Low | File size audit | These are text files; even at 2KB each, total is ~80KB. Manageable. |
| F-F2 | Lore extraction from PDF prose is messy (paragraph boundaries, page breaks mid-sentence) | High | F-TEST-1 + manual review | Extract as-is, then hand-clean the most important nations first. Iteratively improve. |
| F-F3 | Context budget (2000 tokens) is too small for rich lore | Medium | Playtest | 2000 is a starting point. Measure actual context usage. Increase if needed without exceeding ~5000. |
| F-F4 | Regions feel interchangeable despite different lore files | Medium | Playtest | Sensory palettes and voice notes are the key differentiators. Short, vivid, unique per nation. |

## Acceptance Criteria

1. `phases/1-context-loading/lore/nations/` contains 40+ nation files
2. Each nation file has: history, geography, culture, sensory palette, voice notes
3. Phase 1 can load appropriate lore for any canonical location
4. Latter Earth overview, history, and geography references exist
5. All lore files have `[UNKNOWN]` markers where appropriate

---

# PHASE G: ADVANCED SYSTEMS

## Objective
Extend the game with optional content for experienced play: new classes, heroic-tier play, naval combat, alchemy, and firearms.

## Extraction Tasks

- [ ] **G-EXT-1:** Extract optional classes from WWN 5: Accursed, Bard, Mageslayer, Wise
  - Target: expand `classes.py` + create class-specific skill references
  - Each class needs: progression table, class abilities, skill interactions

- [ ] **G-EXT-2:** Extract heroic classes from WWN 4: Heroic Warrior, Heroic Expert, Heroic Mage, Legates, Iterums
  - Target: expand `classes.py` + heroic progression tables

- [ ] **G-EXT-3:** Extract naval combat rules from WWN 5
  - Target: `phases/3-resolution/skills/combat/references/naval-combat.md`
  - Ship stat blocks, crew mechanics, boarding, weather

- [ ] **G-EXT-4:** Extract mundane alchemy from WWN 5
  - Target: `phases/3-resolution/skills/downtime/tables/alchemy_recipes.py`
  - Recipes, costs, skill requirements, effects

- [ ] **G-EXT-5:** Extract primitive firearms from WWN 5
  - Target: expand `equipment.py` with firearm weapons
  - Add firearm-specific combat rules to combat-rules.md

- [ ] **G-EXT-6:** Extract Workings (grand magic) from WWN 2
  - Target: `phases/3-resolution/skills/downtime/references/workings.md`
  - Working creation rules, sample Workings

## Implementation Tasks

- [ ] **G-IMPL-1:** Create `downtime/` domain directory under skills/

- [ ] **G-IMPL-2:** Expand `character.py` to support optional and heroic classes
  - Additional class choices in creation
  - Heroic-tier advancement (levels 11+)
  - Class ability interactions

- [ ] **G-IMPL-3:** Create `naval.py` in combat/scripts/ (if naval combat warrants its own script)
  - Ship-to-ship combat resolution
  - Crew management
  - Weather effects on naval actions

- [ ] **G-IMPL-4:** Create `crafting.py` in downtime/scripts/
  - Alchemy recipe resolution
  - Working creation mechanics
  - General crafting from WWN 1

- [ ] **G-IMPL-5:** Expand combat.py for firearms
  - Firearm-specific attack resolution (reload, misfire, range)

- [ ] **G-IMPL-6:** Create low/no-magic campaign variant config
  - Configuration flag in state.json that disables/limits magic
  - Affects character creation (no mage class), encounter generation (no magical creatures), treasure (no magic items)

## CLI Integration

- [ ] **G-CLI-1:** Expand `create-character` with optional/heroic class choices
- [ ] **G-CLI-2:** Add `naval-combat` subcommand (if warranted)
- [ ] **G-CLI-3:** Add `craft` subcommand for alchemy/crafting
- [ ] **G-CLI-4:** Expand `attack` to handle firearms

## Schema Changes

- [ ] **G-SCHEMA-1:** Add:
  - `character.heroic_abilities: []` — heroic class features
  - `campaign.variant_rules: {low_magic: bool, firearms: bool, naval: bool}` — optional rule toggles
  - `world.ships: []` — if naval combat is implemented
  - **APPROVAL GATE:** Schema version bump 7.5.0 → 7.6.0

## Integration Touchpoints

- [ ] **G-INT-1:** Create downtime domain directory with index.md
- [ ] **G-INT-2:** Update all Phase 3 indexes and CLAUDE.md
- [ ] **G-INT-3:** Update phase-manifest.md
- [ ] **G-INT-4:** Update scripts/CLAUDE.md
- [ ] **G-INT-5:** Update Phase 2 action-classification.md + cli-reference.md
- [ ] **G-INT-6:** Update character creation references in Phase 1

## Tests

- [ ] **G-TEST-1:** `test_optional_classes.py` — all optional classes can be created
- [ ] **G-TEST-2:** `test_heroic.py` — heroic advancement works
- [ ] **G-TEST-3:** `test_crafting.py` — alchemy, crafting resolution
- [ ] **G-TEST-4:** `test_firearms.py` — firearm attack resolution
- [ ] **G-TEST-5:** `test_phase_g.py` — Phase G acceptance
- [ ] **G-TEST-6:** Regression: all prior phase tests still pass with new content

## Fail States

| ID | Fail State | Probability | Detection | Mitigation |
|----|-----------|-------------|-----------|------------|
| G-F1 | Optional classes interact badly with existing mechanics | Medium | G-TEST-1 + playtest | Test each class through character creation AND one combat encounter. Class abilities that modify core mechanics need careful validation. |
| G-F2 | Naval combat is a whole separate game — too much scope | High | Scope assessment before starting | Naval combat is OPTIONAL. If scope exceeds 2 days of work, defer to a future plan. Prioritize alchemy/classes over naval. |
| G-F3 | Heroic-tier play breaks balance assumptions | Medium | G-TEST-2 + balance review | Heroic play is inherently high-power. Accept that balance is looser. Focus on "does it run" not "is it balanced." |
| G-F4 | Variant rule toggles create combinatorial testing burden | Medium | Test matrix | Test each variant independently. Don't test all combinations. Document known interactions. |

## Acceptance Criteria

1. All optional classes can be created via `emergence_cli.py create-character`
2. Heroic advancement works for levels 11+
3. At least alchemy crafting resolves via CLI
4. Firearms attack resolution works
5. Variant rule toggles function (low-magic mode disables magic)
6. All prior phase tests still pass (regression)

---

# CROSS-CUTTING CONCERNS

## Governance Overhead Management

The 7-touchpoint integration checklist is designed for a mature system. During Phases B-C (bootstrapping new domains), apply it progressively:

- **Always required:** Skill file, Phase 3 index.md, phase-manifest.md, script registry, tests
- **Wire after mechanics work:** Phase 2 classification, Phase 4 narration mappings
- **Don't block implementation on documentation completeness** — code first, wire second, document third

## Schema Version Strategy

Batch schema changes per phase rather than per feature:
- Phase B: v7.0.0 → v7.1.0 (magic + combat state)
- Phase C: v7.1.0 → v7.2.0 (exploration + world)
- Phase D: v7.2.0 → v7.3.0 (social + factions)
- Phase E: v7.3.0 → v7.4.0 (narrative features)
- Phase F: v7.4.0 → v7.5.0 (lore/region)
- Phase G: v7.5.0 → v7.6.0 (advanced systems)

Each bump includes a migration path (add new fields with defaults to existing state files).

## Testing Strategy

- **Per-phase acceptance tests:** `test_phase_X.py` validates all deliverables
- **Regression:** Each phase runs ALL prior phase tests. Failures block the phase.
- **Extraction smoke tests:** Count-based validation for all extracted data tables
- **Manual playtest:** At least one end-to-end turn after each phase. Document results.
- **CI integration:** Add new tests to existing CI jobs (smoke-balance, state-validators)

## Context Window Budget

The system must stay within usable context limits. Budget per phase:
- Phase 1 (context loading): ~3000 tokens — state (~1000) + scene (~500) + relevant lore (~1500)
- Phase 2 (action interpretation): ~500 tokens — action classification reference
- Phase 3 (resolution): ~200 tokens — CLI command + JSON result
- Phase 4 (narrative): ~1500 tokens — voice guide (~500) + narration mappings (~500) + templates (~500)
- Phase 5 (persistence): ~200 tokens — state update procedure
- Phase 6 (validation): ~100 tokens — validation checklist
- **Total governance overhead per turn:** ~5500 tokens
- **Remaining for conversation history:** depends on model context window

## Risk Register (Cross-Phase)

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Governance overhead kills velocity | High | High | Progressive wiring. Don't block code on docs. Batch integration touchpoint updates per phase. |
| Schema churn cascades break state files | Medium | High | One schema bump per phase. Migration scripts. State backup at phase boundaries. |
| Extraction quality varies by PDF section | High | Medium | Accept imperfection. Flag known-bad extractions. Iteratively improve. |
| Phases become too large to implement in one PR | Medium | Medium | Split phases into sub-PRs: extraction, implementation, integration. Each sub-PR is independently mergeable. |
| Turn loop is never tested end-to-end | High | Critical | Manual end-to-end test at Phase A.5 and after each subsequent phase. Automated E2E test by Phase E. |
| Single-player focus limits design options | Low | Low | Design for single player. Multi-player is out of scope. |

## Exit Criteria (Full Project)

1. A player can create a WWN character through AI-guided character creation
2. Combat with multiple enemies resolves deterministically and narrates fluidly
3. Spellcasting works for at least High Magic tradition
4. Overland travel between settlements generates encounters and manages resources
5. NPCs have consistent personalities across sessions
6. Faction clocks advance the world between sessions
7. The Latter Earth setting is narrated with consistent voice and accurate lore
8. State can be rolled back to any session-start snapshot
9. All mechanical outcomes come from CLI, never LLM improvisation
10. A 5-session playtest campaign completes without state corruption
11. All 6 pipeline phases have operational content (not just stubs)
12. All tests pass across all phases with no regressions
