# Execution Plan: Anti-Stagnation v3 — Scene-Pressure Move System

- **Owner:** Development team
- **Status:** Draft
- **Start Date:** 2026-03-09
- **Target Date:** 2026-03-09
- **Related Decision Logs:** `gm-protocol.md`, `hard-rules.md`, `turn-loop.md`

## Objective

Implement a three-tier GM move system that mechanically prevents play from stagnating. Every player-action turn produces a minimum Tier 1 (soft) move. The system tracks turns since the last hard move, forces escalation when thresholds are reached, and routes all consequences through the existing CLI pipeline. Telegraphed threats create foreshadowed consequences that escalate into binding mechanical events.

### What this solves

Without anti-stagnation, the GM (LLM) tends toward safe, repetitive turns — skill checks that don't bite, combats that don't escalate, a world that waits politely. The move system guarantees:

- **Every turn:** minimum Tier 1 — the world reacts, foreshadows, or reveals
- **Every 5 Tier 1 turns:** forced Tier 2 — a hard consequence lands on the PC
- **Every 8 Tier 1 turns:** forced Tier 3 — the world acts on its own agenda
- **No Tier 0 exits.** No turn is narratively empty. The dispatch table has no path that returns `tier: 0`

### Key design insight (v2→v3)

`select_move` must have a **command-aware dispatch** that handles every primary type differently, not just skill-check. Six of the 21 CLI commands are player-facing primaries that resolve actions, each with different result shapes and different relationships to the move system.

## Scope

### In scope:
- `gm_moves.py` (new) — `select_move()` with 6 command dispatchers, source selection, consequence routing, CLI dispatch
- `gm-move-taxonomy.md` (new) — reference doc for all 6 dispatchers and tier definitions
- `state.schema.json` — Add `session.turns_since_hard_move`, `current_scene.telegraphed_threats[]`
- `triggers.py` — Extend `check_all_triggers()` to evaluate anti-stagnation thresholds
- `turn-loop.md` — Add move-tier evaluation as a full step (step 6)
- Root `CLAUDE.md` — Embed condensed turn loop in Runtime Turn Loop section
- `gm-protocol.md` — Add §Scene Pressure with tier definitions and narrative directives
- `hard-rules.md` — Add Hard Rule #13: Scene Pressure Is Binding
- `narration-mappings.md` — Add move-integration notes to ALL mechanic sections (§save, §combat, §spell, §social, §travel)
- `behavior.py` — Export `get_profile_description()` for attack dispatch foreshadowing
- `chain_registry.py` — Turn loop must pass chain results back (chain_results accumulator)
- Test suite — `test_moves.py`

### Out of scope:
- New CLI subcommands (moves route to existing commands: `attack`, `encounter`, `world-tick`, `faction-turn`, `generate-scene`)
- Consequence tracker changes (consequence.py unchanged — moves CREATE consequences through it)
- Phase 4 narrative template changes (moves provide `narrative_directive` text, Phase 4 follows it)

## Architecture

### Command Classification

All 21 CLI commands fall into exactly one of four categories:

| Category | Commands | Relationship to select_move |
|----------|----------|----------------------------|
| **Player-action primaries** | `skill-check`, `attack`, `save`, `cast-spell`, `reaction-roll`, `travel` | These resolve player-declared actions. `select_move` RUNS on these |
| **World-action commands** | `encounter`, `world-tick`, `faction-turn`, `check-triggers` | GM/world-initiated. These ARE moves already. `select_move` does NOT run |
| **Scene/content generators** | `generate-scene`, `generate-npc`, `generate-dungeon`, `treasure` | Produce content, not outcomes. No move selection needed |
| **Infrastructure/meta** | `roll`, `create-character`, `level-up`, `initialize-game`, `expand-action`, `post-resolution`, `state-snapshot` | Utility. No move selection |

### Tier Definitions (v3 — Tier 1 Floor)

| Tier | Name | What it does | Threshold | Resets |
|------|------|-------------|-----------|--------|
| 1 | Soft Move | Minimum for EVERY player-action turn. Foreshadows danger, reveals information, creates telegraphs, evolves the scene. | Always — no Tier 0 exits | Nothing (increments `turns_since_hard_move`) |
| 2 | Hard Move | A consequence lands on the PC. Exactly one mechanical mutation. | Forced at `turns_since_hard_move >= 5`, or natural from catastrophic failure / hostile reaction | `turns_since_hard_move` → 0 |
| 3 | World Move | The world acts independently. May involve multiple state changes. | Forced at `turns_since_hard_move >= 8` | `turns_since_hard_move` → 0 |

### Escalation Ladder

Single counter: `session.turns_since_hard_move`. Tracks consecutive Tier 1 turns since the last Tier 2+ move.

| Counter value | What fires |
|--------------|-----------|
| 1-4 | Normal Tier 1 turns. Soft moves, telegraphs accumulate |
| 5 | **Force Tier 2** — escalate oldest active telegraph. If none exist, create consequence from clock/faction state |
| 8 | **Force Tier 3** — world-level event. Clock advances, faction acts on-screen, environment fundamentally shifts |

**Guarantee:** Maximum 4 consecutive soft-only turns. Hard consequence by turn 5 of any streak. Natural Tier 2 events (catastrophic failures, hostile reactions) can trigger earlier.

### Per-Command Dispatch Design

#### 1. skill-check

**Result shape:** `{success, margin, total, difficulty}`
**Gate type required:** `--gate-type` (access/discovery/social/survival/combat_setup/pure_test)

| Outcome | Move |
|---------|------|
| Success (any margin) | Tier 1 soft: foreshadow via `GATE_CONSEQUENCES[gate].success_move` + scene_elements draw |
| Fail, margin >= -2 | Tier 1 soft: telegraph from `failure_flavors[domain]` + scene_elements |
| Fail, margin <= -3, telegraph exists | Tier 2 hard: escalate prior telegraph |
| Fail, margin <= -3, no telegraph | Tier 1 soft (record telegraph for next time) |
| Fail, margin <= -5 (catastrophic) | Tier 2 hard regardless of telegraph state |

**Gate-type → consequence mapping (natural Tier 2):**

| Gate | Consequence |
|------|------------|
| access | Path closes |
| discovery | Misinformation persisted |
| social | NPC hostility + possible consequence |
| survival | Resource loss |
| combat_setup | Ambush reversed (+2 threat_level) |

#### 2. attack

**Result shape:** `{hit, damage, target_down, shock_applied, roll, target_ac}`

**Key constraint:** During active multi-round combat, move selection operates at Tier 1 minimum (battlefield evolution) — it does NOT suppress. Every round, the battlefield changes.

| Outcome | Move |
|---------|------|
| Hit or miss (combat continues) | Tier 1: battlefield evolves — terrain shifts, enemy reveals capability, environment reacts, position changes. Draw from `scene_elements.complications` + `behavior.py` profile |
| Target down, enemies remain | Tier 1: foreshadow via behavior profile of next alive enemy. `get_profile_for_creature(next_enemy)`: aggressive → "press attack", cautious → "reassess", ambush → "melt into shadow" |
| Target down, ALL enemies down (combat ends) | Tier 1: aftermath — foreshadow what the scene holds beyond combat. Draw from scene_elements |
| PC drops to 0 HP (from enemy turn) | Tier 2: death/incapacitation consequence. Hard rules handle persistence, select_move flags for tracking |

**Integration with behavior.py:** `select_move` for attack reads `combat_state` parameter (from snapshot) to check remaining enemies and query behavior profiles for foreshadow flavor.

#### 3. save

**Result shape:** `{success, roll, save_target, save_type, margin}`

**Key insight:** Saves are REACTIVE. The GM already made a move (the threat that forced the save). The save resolves that prior move. But no turn exits silent.

| Outcome | Move |
|---------|------|
| Success | Tier 1: threat averted, but the event leaves a mark. Draw from scene_elements — "You dodged the collapse, but the tremor loosened something deeper." |
| Failure | Tier 1: forced consequence lands (Hard Rule #5, binding) PLUS telegraph what caused it or what comes next |
| Failure + margin <= -3 | Tier 2: severe consequence + telegraph |

**Why minimum Tier 1 (not Tier 0)?** The save was triggered by something. Even when averted, the event changed the scene. Double-moving (save fails AND new complication) would feel punitive at Tier 2 — so standard failure stays at Tier 1 with the forced consequence as the content.

**Exception — environmental chain:** If the save was triggered by environment AND failure is severe (margin <= -3), escalate to Tier 2.

#### 4. cast-spell

**Result shape:** `{success, spell_name, effort_type, effort_committed, system_strain_added, effect}`

**Key insight:** Spells have built-in costs (effort, system strain). Don't double-tax. But magic is loud — it attracts attention.

| Outcome | Move |
|---------|------|
| Success (effort committed) | Tier 1: the world notices. Draw from `scene_elements.complications` — "your spell succeeds, but the discharge causes [complication element] to stir." Not punishment — consequence in a low-magic world |
| Success (in active combat) | Tier 1: spell effect ripples — enemies reposition, terrain altered, collateral occurs. (combat_state.active guard: no scene_elements draw during combat) |
| Failure (fizzle/strain overload) | Tier 1: the attempt itself was noticed. Arcane discharge, residue, attention drawn. The world reacts to magical intent, not just success |

#### 5. reaction-roll

**Result shape:** `{total, modifier, disposition, reaction_text}`

**Key insight:** The reaction roll result IS the move. The NPC's disposition directly determines what happens.

| Outcome | Move |
|---------|------|
| Hostile (2-3) | Tier 2 hard: NPC acts against PC. `update_favor(npc, -2, "hostile reaction")`. `create_consequence()` if NPC has power |
| Unfriendly (4-5) | Tier 1: NPC obstructs, telegraph leverage. `update_favor(npc, -1, "cold reception")` |
| Neutral (6-8) | Tier 1: NPC gives information — rumor from `world_pulse`, location detail, observation about recent events. Transactional doesn't mean empty |
| Friendly (9-11) | Tier 1: opportunity — NPC offers something. `update_favor(npc, +1, "warm reception")`. Draw from scene_elements or `world_pulse.rumors` |
| Enthusiastic (12+) | Tier 1: strong opportunity, active help. `update_favor(npc, +2, "enthusiastic")`. May offer quest hook from `campaign_arcs` |

**Integration with diplomacy.py:** For hostile/unfriendly results, `select_move` calls `update_favor(npc_id, favor_delta, reason)` as suggested mutation.

**Breakpoint B10:** NPC might not exist yet in `known_npcs` (reaction-roll has a pre-command chain that generates the NPC). Fix: `select_move` accepts optional `pre_command_results` dict for NPC data from `generate-npc` pre-command.

#### 6. travel

**Result shape:** `{travel_log: [{day, events, encounter_check, travel_event, has_encounter}], encounters, supplies_end}`

**Key insight:** `travel.py` already generates per-day events. Don't add MORE events — pick the most significant and classify it for Phase 4 emphasis.

| Outcome | Move |
|---------|------|
| Clock portent (from world-tick chain) | Tier 1 or 2: portent IS the featured move. Portents outrank travel events |
| Encounter triggered | Tier 0 exception: encounter command handles it (the encounter IS the move) |
| Privation (supplies_end == 0) | Tier 2 hard: resource consequence. `apply_privation()` already computed damage |
| Notable travel event (landmark, remains, traveler) | Tier 1: promote most dramatic `TRAVEL_EVENT` as featured beat |
| Uneventful | Tier 1: `world_pulse` rumor as featured beat. If world_pulse also empty → stagnation flag |

**Breakpoint B11:** `world-tick` is a post-chain — its results aren't in `command_result`. Fix: `select_move` accepts `chain_results` parameter keyed by chain command name → result.

### Updated select_move() Signature

```python
def select_move(
    command_name,        # which primary just ran
    command_result,      # its JSON output
    gate_type=None,      # only for skill-check
    scene_elements=None, # current scene's element menu
    telegraphed_threats=None,  # active telegraphs
    combat_state=None,   # for attack suppression / spell context
    chain_results=None,  # results from post-chains (e.g., world-tick after travel)
    pre_command_results=None,  # results from pre-commands (e.g., generate-npc before reaction-roll)
):
    """Select a GM move based on the primary command's result.

    Returns:
        dict with tier, move_type, narrative_directive, source_elements,
        suggested_mutations, suggested_chain, forced_consequence,
        counter_update, arithmetic_trace
    """
    dispatch = {
        "skill-check": _move_for_skill_check,
        "attack": _move_for_attack,
        "save": _move_for_save,
        "cast-spell": _move_for_cast_spell,
        "reaction-roll": _move_for_reaction_roll,
        "travel": _move_for_travel,
    }
    handler = dispatch.get(command_name, _move_narrative_fallback)
    return handler(command_result, gate_type, scene_elements,
                    telegraphed_threats, combat_state, chain_results,
                    pre_command_results)
```

### select_move() Return Contract

```python
{
    "tier": 2,  # 1, 2, or 3 — NEVER 0
    "move_type": "telegraph_escalates",  # descriptive tag
    "source": {
        "type": "telegraph",  # telegraph | command_result | clock | faction | arc_beat | environment | behavior_profile | world_pulse
        "id": "threat_tunnel_patrol",
        "description": "The patrol you heard earlier",
    },
    "source_elements": ["enemies.patrol_squad"],  # which scene_elements were drawn on
    "suggested_mutations": [
        {
            "type": "immediate_resource_cost",
            "target": "character.hp",
            "value": -4,
            "reason": "Ambush from tunnel patrol — damage via attack command",
        },
        {
            "type": "escalate_telegraph",
            "telegraph_id": "threat_tunnel_patrol",
            "new_status": "escalated",
        },
    ],
    "suggested_chain": "attack",  # additional CLI command to execute, or null
    "narrative_directive": "The telegraphed patrol arrives. Narrate the ambush with "
        "gravity. The damage is binding. Reference the prior foreshadow.",
    "forced_consequence": True,
    "counter_update": {
        "action": "reset",  # "reset" for tier 2+, "increment" for tier 1
        "turns_since_hard_move": 0,
    },
    "arithmetic_trace": "Tier 2: telegraph 'threat_tunnel_patrol' (created turn 3) "
        "escalated at turn 7. Source: forced (turns_since_hard_move=5).",
}
```

### Source Selection Priority

**Tier 2 sources (in priority order):**

| Priority | Source | When available |
|----------|--------|---------------|
| 1st | Telegraph escalation | Active `telegraphed_threats` exist (oldest by `turn_created`) |
| 2nd | Natural command result | Command dispatch produced tier 2 directly (catastrophic failure, hostile reaction) |
| 3rd | Clock portent | First active clock with an unfired portent nearest to current value |
| 4th | Faction fallback | First faction with a goal targeting PC's current location |

**Tier 3 sources (in priority order):**

| Priority | Source | When available |
|----------|--------|---------------|
| 1st | Clock completion | Any clock with `status: "active"` and `current >= max/2` (accelerated to completion if forced) |
| 2nd | Faction action | Any faction with an active goal targeting PC's region |
| 3rd | Campaign arc beat | Any beat with `status: "pending"` and evaluable trigger near threshold |
| 4th | Environment shift | Fallback — scene transforms (new arrivals, weather, terrain shift) |

### Tier 2 — Mutation Types

Each tier 2 produces exactly ONE of these:

| Mutation | State changed | Example |
|----------|--------------|---------|
| `immediate_resource_cost` | `character.hp`, `character.equipment[]`, `campaign.supplies`, `character.system_strain` | Ambush damage, equipment destroyed, supplies lost |
| `create_consequence` | Appends to `consequence_tracker[]` | "Faction retaliates in 3 days" |
| `update_favor` | `known_npcs[].favor` → derived `standing` | NPC disposition drops |
| `close_path` | `current_scene.accessible_paths[]` or `known_locations[].status` | Route blocked, door locked |
| `add_condition` | `character.conditions[]` | Poisoned, exhausted, cursed |
| `escalate_telegraph` | `telegraphed_threats[].status` → `"escalated"` | Warning becomes reality |

### Tier 3 — Multi-Mutation Allowed

| Source type | CLI commands | State changes |
|------------|-------------|---------------|
| Clock completion | `world-tick --days 0` | Clock → `"completed"`, completion_effect fires, location status changes |
| Faction action | `faction-turn` | Faction assets/goals updated, territory shifts |
| Arc beat trigger | `check-triggers` | Beat status → `"triggered"`, narrative event queued |
| Environment shift | `generate-scene` | `current_scene` replaced, `known_locations[]` updated |

**Clock acceleration:** If a tier 3 is forced and no clock is naturally ready, the nearest-to-completion active clock (>= 50% progress) is advanced to completion.

### Telegraphed Threats (Tier 1 Output)

```python
{
    "id": "telegraph_<source>_<turn>",
    "description": "Boots echo from the level above",
    "turn_created": 3,
    "source_element": "enemies.patrol_squad",  # or clock, faction, environment
    "status": "active",  # active → escalated → resolved
}
```

Stored in `current_scene.telegraphed_threats[]`. Scene-local — cleared on scene transition (W1). When a tier 2 fires and active telegraphs exist, the oldest telegraph escalates.

### Narrative Treatment by Tier

| Tier | Treatment | Word count | Budget cost |
|------|-----------|------------|-------------|
| 1 | Woven into command narration per existing §mappings + move source | ~50 words | None |
| 2 | §consequence treatment. Reference prior telegraph if escalation. Binding | ~150 words | None |
| 3 | §dramatic-moments treatment. Full gravity and scale | 200-300 words | 1 drama_budget |

## Breakpoints (Integration Issues)

### B9: attack — behavior.py needs enemy list from combat_state, not command result

The attack command returns `{hit, damage, target_down}` but not the remaining enemy list. `select_move` needs `combat_state.enemies` (from the snapshot) to check if ALL enemies are down and to query behavior profiles.

**Fix:** `select_move` for attack reads `combat_state` parameter (passed from snapshot). If `target_down`, check `combat_state.enemies` for remaining alive enemies. If none → combat ends. If some → get their profiles for foreshadow.

### B10: reaction-roll — NPC might not exist yet in known_npcs

The reaction-roll has a pre-command chain that generates the NPC if unknown. But `select_move` needs the NPC's importance/faction for `update_favor()`. The NPC was JUST generated — it's in the `generate-npc` pre-command result, not in `command_result`.

**Fix:** `select_move` for reaction-roll accepts optional `pre_command_results` dict. If `generate-npc` was a pre-command, its result provides the NPC data. Otherwise, look up from `known_npcs` in state.

### B11: travel — world-tick is a post-chain, its results aren't in command_result

Travel's `select_move` needs to know if a clock portent fired during the world-tick chain. But `command_result` is travel's output, not world-tick's.

**Fix:** `select_move` accepts `chain_results` parameter — a dict keyed by chain command name → result. The turn loop passes this after executing all post-chains. Travel's dispatch handler checks `chain_results.get("world-tick", {}).get("triggered_events", [])`.

### B12: cast-spell — spell success in combat shouldn't draw scene_elements

A successful spell during active combat shouldn't cause "the ruins stir" — combat is its own context. Scene-element draws should only happen outside combat.

**Fix:** Same `combat_state.active` guard as attack. If combat is active, successful cast-spell returns Tier 1 with combat-contextual ripple (enemy reposition, terrain altered). Scene-element draws only happen in exploration/social contexts.

## Safeguards (Weaknesses Found and Fixed)

**W1 (FIXED): Telegraphs don't persist across scenes.** Telegraphed threats live in `current_scene`. When the scene changes, they're lost. This is correct behavior — telegraphs are scene-local. A warning about "boots above" doesn't follow you to a different location.

**W2 (FIXED): Tier 3 clock acceleration could fire on a clock at 1/8.** Only clocks at `current >= max/2` are eligible for acceleration. Below 50%, fall through to faction/environment sources.

**W3 (FIXED): Dual forced (tier 2 at 5 AND tier 3 at 8 on same turn).** Tier 3 takes priority (it resets the counter). Only one forced move per turn. Tier 3 subsumes tier 2.

**W4 (FIXED): Natural tier 2 from command + forced tier 2 on same turn.** Natural tier 2 resets the counter. If a natural tier 2 fires during step 6, the forced check in step 0b won't have fired (it checked before the command). The counter reset prevents double-counting.

**W5 (FIXED): No gate_type on existing skill-check output.** `gate_type` is a Phase 2 classification detail, not a CLI output. `select_move` receives it from the action interpretation context.

**W6 (FIXED): Consequence tracker max 20 — tier 2 creating consequences could overflow.** `select_move` checks `len(consequence_tracker)` before choosing `create_consequence` mutation. If at cap, uses `immediate_resource_cost` instead.

## Task Breakdown

### T1: Schema Changes — state.schema.json

- [ ] **T1.1** Add to `session` definition:
  ```json
  "turns_since_hard_move": { "type": "integer", "minimum": 0, "description": "Consecutive Tier 1 turns since last Tier 2+ move" }
  ```
- [ ] **T1.2** Add `telegraphed_threats` to `current_scene`:
  ```json
  "telegraphed_threats": {
      "type": "array",
      "items": {
          "type": "object",
          "required": ["id", "description", "turn_created", "status"],
          "properties": {
              "id": { "type": "string" },
              "description": { "type": "string" },
              "turn_created": { "type": "integer" },
              "source_element": { "type": "string" },
              "status": { "type": "string", "enum": ["active", "escalated", "resolved"] }
          }
      },
      "description": "Tier 1 soft-move foreshadowing — telegraphed dangers in current scene"
  }
  ```
- [ ] **T1.3** Bump schema version from `7.5.0` to `7.6.0`
  - **APPROVAL GATE:** Schema version bump

### T2: Core Script — gm_moves.py (NEW)

Create `runtime/phases/3-resolution/skills/world-building/scripts/gm_moves.py`.

- [ ] **T2.1** `record_telegraph(description, source_element, current_turn)` → returns telegraph dict
- [ ] **T2.2** `select_move()` with 6-handler dispatch table (signature above)
- [ ] **T2.3** `_move_for_skill_check()` — gate-type aware, margin thresholds, telegraph escalation
- [ ] **T2.4** `_move_for_attack()` — combat_state aware, behavior profile foreshadow, battlefield evolution every round
- [ ] **T2.5** `_move_for_save()` — reactive (prior move resolves), Tier 1 floor, severe failure escalation
- [ ] **T2.6** `_move_for_cast_spell()` — no double-tax, combat_state guard for scene_elements, magic ripple
- [ ] **T2.7** `_move_for_reaction_roll()` — disposition mapping, diplomacy.py integration, pre_command_results for new NPCs
- [ ] **T2.8** `_move_for_travel()` — chain_results for world-tick, portent priority, privation detection
- [ ] **T2.9** `_move_narrative_fallback()` — for "narrative" pseudo-commands (no CLI). Tier 1: world breathes. Draw from scene_elements or world_pulse
- [ ] **T2.10** `_select_tier2_source(state)` — telegraph → clock portent → faction → environmental hazard
- [ ] **T2.11** `_select_tier3_source(state)` — clock completion → faction → arc beat → environment shift
- [ ] **T2.12** `_build_tier2_mutations(source, state)` — map source to exactly one mutation type
- [ ] **T2.13** `_build_tier3_mutations(source, state)` — map source to mutation(s), multi-mutation allowed
- [ ] **T2.14** `check_escalation(turns_since_hard_move, telegraphed_threats, clocks, factions)` → returns forced tier dict or None
  - `>= 8` → force Tier 3
  - `>= 5` → force Tier 2 (escalate oldest telegraph, or create from clock/faction)
  - `< 5` → None

### T3: Trigger Integration — triggers.py (EDIT)

- [ ] **T3.1** Add `check_stagnation()` to `check_all_triggers()`:
  - Read `session.turns_since_hard_move`
  - If threshold met (5 or 8), append to `commands_to_fire` with `source: "anti_stagnation"`
- [ ] **T3.2** Add stagnation counter to `arithmetic_trace` output

### T4: Turn Loop Integration — turn-loop.md (EDIT) + Root CLAUDE.md (EDIT)

- [ ] **T4.1** Embed condensed turn loop in root CLAUDE.md (new §Runtime Turn Loop section between Runtime Surfaces and Repository Map):
  ```markdown
  ## Runtime Turn Loop (Mandatory Sequence)

  Every game turn follows this sequence. No steps may be skipped or reordered.

  0. **World preamble** — `check-triggers`. Fire high-priority commands.
  1. **Capture + classify** — Player intent → CLI command via `action-classification.md`.
     If "no mechanic" → classify as `narrative` pseudo-command (still enters the loop).
  2. **Expand** — `expand-action` → pre-commands + primary + declared chains.
  3. **Validate input** — Provenance check.
  4. **Snapshot** — `state-snapshot` (for delta detection).
  5. **Execute** — pre-commands → primary → post-chains. Track `executed_commands`.
  6. **★ Select GM move** — `select-move` on primary result.
     - EVERY player-action turn produces minimum Tier 1.
     - Tier 1: soft move (foreshadow, telegraph, opportunity, information).
     - Tier 2: hard move (consequence lands, telegraph escalates). Forced after 5 Tier 1 turns.
     - Tier 3: world move (clock/faction/environment shift). Forced after 8 Tier 1 turns.
     - Source: `gm-move-taxonomy.md`. Script: `gm_moves.py`.
  7. **Narrate** — Phase 4, informed by move selection output.
  8. **Persist** — Phase 5. Includes move mutations (telegraphs, escalations, element usage, counter updates).
  9. **Post-resolution** — `post-resolution` safety net. Up to 3 iterations.
  10. **Validate** — `validate-state`.
  11. **Receipt** — Log full command sequence + move selection + seeds.

  Detail: `runtime/turn-loop.md`. Phase instructions: `runtime/phases/<N>/CLAUDE.md`.
  ```
- [ ] **T4.2** Renumber `runtime/turn-loop.md` to match root CLAUDE.md version. Step 6 is a full step (not 5.5). Flow diagram updated.
- [ ] **T4.3** Add escalation check to step 0b (forced moves fire BEFORE player's turn)
- [ ] **T4.4** Add natural move evaluation to step 6 (after command dispatch)
- [ ] **T4.5** Add counter update to step 8 (persist phase)
- [ ] **T4.6** Update `runtime/CLAUDE.md` — remove duplicate governance, point to root CLAUDE.md for turn loop

### T5: GM Protocol — gm-protocol.md (EDIT)

- [ ] **T5.1** Add §Scene Pressure section with all three tier definitions
- [ ] **T5.2** Include Tier 1 floor principle — "No turn is narratively empty"
- [ ] **T5.3** Include escalation ladder (5/8 thresholds)

### T6: Hard Rules — hard-rules.md (EDIT)

- [ ] **T6.1** Add Hard Rule #13: Scene Pressure Is Binding
  ```markdown
  ## 13. Scene Pressure Is Binding
  When `select_move` returns a forced tier 2 or tier 3 consequence, it fires.
  It cannot be softened, delayed, or narratively circumvented. The
  `suggested_mutations` are applied to state. The `requires_cli` command
  executes with binding results. Telegraphed threats that escalate become
  real mechanical events, not narrative flavor.
  ```

### T7: Reference Doc — gm-move-taxonomy.md (NEW)

- [ ] **T7.1** Create `runtime/phases/1-context-loading/references/gm-move-taxonomy.md`
- [ ] **T7.2** Document all 6 command dispatchers with outcome → tier mapping tables
- [ ] **T7.3** Document escalation ladder, source selection priority, mutation types

### T8: Narration Mappings — narration-mappings.md (EDIT)

- [ ] **T8.1** Add move-integration notes to §skill-check section
- [ ] **T8.2** Add move-integration notes to §combat/attack section
- [ ] **T8.3** Add move-integration notes to §save section
- [ ] **T8.4** Add move-integration notes to §spell/cast-spell section
- [ ] **T8.5** Add move-integration notes to §social/reaction-roll section
- [ ] **T8.6** Add move-integration notes to §travel section

### T9: Behavior Integration — behavior.py (EDIT)

- [ ] **T9.1** Export `get_profile_description(creature_type)` → returns foreshadow text string
  - aggressive: "press attack with renewed fury"
  - cautious/pack: "hesitate, reassessing"
  - ambush: "melt back into shadow"

### T10: Chain Results Accumulator — chain_registry.py (EDIT)

- [ ] **T10.1** Turn loop must pass chain results back to select_move
  - New `chain_results` dict accumulator in expand/execute cycle
  - Keyed by chain command name → result

### T11: Tests — test_moves.py (NEW)

Create `runtime/tests/test_moves.py`.

- [ ] **T11.1** Test `record_telegraph()` produces valid telegraph dict
- [ ] **T11.2** Test `check_escalation()`:
  - `turns_since_hard_move=4` → None
  - `turns_since_hard_move=5` → forced Tier 2
  - `turns_since_hard_move=8` → forced Tier 3
- [ ] **T11.3** Test each of the 6 command dispatchers returns minimum Tier 1
- [ ] **T11.4** Test `_move_for_skill_check()` margin thresholds
- [ ] **T11.5** Test `_move_for_attack()` with combat_state variations (mid-combat, combat ends)
- [ ] **T11.6** Test `_move_for_save()` success/failure/severe failure
- [ ] **T11.7** Test `_move_for_cast_spell()` success/failure, combat_state guard
- [ ] **T11.8** Test `_move_for_reaction_roll()` all 5 disposition tiers
- [ ] **T11.9** Test `_move_for_travel()` with chain_results (portent, privation, uneventful)
- [ ] **T11.10** Test `select_move(tier=2)` with active telegraph → escalates oldest
- [ ] **T11.11** Test `select_move(tier=2)` with no sources → environmental hazard
- [ ] **T11.12** Test `select_move(tier=3)` with near-completion clock → acceleration
- [ ] **T11.13** Test tier 2 mutation count: exactly one per move
- [ ] **T11.14** Test tier 3 mutation count: allows multiple
- [ ] **T11.15** Test counter updates: tier 1 increments, tier 2+ resets
- [ ] **T11.16** Test arithmetic_trace present on all outputs
- [ ] **T11.17** Test schema validation with new fields
- [ ] **T11.18** Determinism: same state + same seed → same selection

### T12: State Update — state.json (EDIT)

- [ ] **T12.1** Add `"turns_since_hard_move": 0` to `session`
- [ ] **T12.2** Add `"telegraphed_threats": []` to `current_scene`
- [ ] **T12.3** Run `validate-state` to confirm schema compliance

## Implementation Order

1. T1 — Schema changes (defines the contract)
2. T11 — Write tests first (validates completion criteria)
3. T2 — Core `gm_moves.py` (the engine — 6 dispatchers)
4. T9 — behavior.py export (needed by attack dispatcher)
5. T10 — chain_registry.py accumulator (needed by travel dispatcher)
6. T3 — Wire into triggers.py (discovery)
7. T7 — Reference doc (gm-move-taxonomy.md)
8. T5, T6 — Update governance docs (gm-protocol, hard-rules)
9. T8 — Update narration-mappings.md (all sections)
10. T4 — Update turn-loop.md + root CLAUDE.md (integration)
11. T12 — Update state.json with new fields
12. Run all tests, fix issues
13. Run existing test suite (regression check)

## Modified Files Summary

| File | Change Type | Surfaces Touched |
|------|-------------|------------------|
| `CLAUDE.md` (root) | Edit | Turn loop contract (new §Runtime Turn Loop) |
| `runtime/CLAUDE.md` | Edit | Governance (point to root for turn loop) |
| `runtime/schemas/state.schema.json` | Edit | State schema |
| `runtime/phases/3-resolution/skills/world-building/scripts/gm_moves.py` | New | Rules logic (6 dispatchers) |
| `runtime/phases/3-resolution/skills/world-building/scripts/triggers.py` | Edit | Rules logic |
| `runtime/phases/3-resolution/skills/combat/scripts/behavior.py` | Edit | Rules logic (export) |
| `runtime/phases/2-action-interpretation/chain_registry.py` | Edit | Chain execution |
| `runtime/turn-loop.md` | Edit | Turn loop contract |
| `runtime/phases/1-context-loading/references/gm-protocol.md` | Edit | GM protocol |
| `runtime/phases/1-context-loading/references/hard-rules.md` | Edit | Hard rules |
| `runtime/phases/1-context-loading/references/gm-move-taxonomy.md` | New | Reference doc |
| `runtime/phases/4-narrative/narration-mappings.md` | Edit | Narration rules |
| `runtime/tests/test_moves.py` | New | Validation |
| `runtime/state.json` | Edit | State data |

**Total: 14 files (3 new, 11 edited)**

## Flowchart (Final — v3)

```
PLAYER DECLARES ACTION (or narrative with no mechanic)
         │
         ▼
┌────────────────────────────────────────────────────┐
│  STEP 1: CLASSIFY INTENT                            │
│                                                    │
│  ┌─ skill-check (+ gate_type annotation)           │
│  ├─ attack                                         │
│  ├─ save                                           │
│  ├─ cast-spell                                     │
│  ├─ reaction-roll                                  │
│  ├─ travel                                         │
│  └─ narrative (no CLI — STILL enters loop)          │
│                                                    │
│  gate_type required for skill-check (no default)   │
└──────────┬─────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────────────────┐
│  STEPS 2-5: EXPAND → VALIDATE → SNAPSHOT → EXECUTE │
│                                                    │
│  chain_registry.py expands action                  │
│  state-snapshot captures pre-state                 │
│  Execute: pre → primary → post-chains              │
│  Accumulate: executed_commands, chain_results       │
└──────────┬─────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────────┐
│  ★ STEP 6: SELECT GM MOVE                                           │
│                                                                      │
│  ┌─ ESCALATION CHECK (runs first) ─────────────────────────────────┐│
│  │                                                                  ││
│  │  Read session.turns_since_hard_move                              ││
│  │  ├─ >= 8 → FORCE TIER 3: world event                            ││
│  │  │   Clock advances, faction acts on-screen, environment shifts  ││
│  │  │   Reset counter to 0                                         ││
│  │  │                                                               ││
│  │  ├─ >= 5 → FORCE TIER 2: hard consequence                       ││
│  │  │   Escalate oldest telegraph, or create from clock/faction     ││
│  │  │   Reset counter to 0                                         ││
│  │  │                                                               ││
│  │  └─ < 5 → proceed to command dispatch                            ││
│  └──────────────────────────────────────────────────────────────────┘│
│                                                                      │
│  ┌─ COMMAND DISPATCH (Tier 1 floor — no Tier 0 exits) ─────────────┐│
│  │                                                                  ││
│  │  ┌─ SKILL-CHECK ──────────────────────────────────────────────┐  ││
│  │  │ success → Tier 1: foreshadow via GATE_CONSEQUENCES[gate]   │  ││
│  │  │ fail, margin >= -2 → Tier 1: telegraph from scene_elements │  ││
│  │  │ fail, margin <= -3 + telegraph → Tier 2: escalate          │  ││
│  │  │ fail, margin <= -3 no telegraph → Tier 1: record first     │  ││
│  │  │ fail, margin <= -5 → Tier 2: catastrophic regardless       │  ││
│  │  └────────────────────────────────────────────────────────────┘  ││
│  │                                                                  ││
│  │  ┌─ ATTACK ──────────────────────────────────────────────────┐   ││
│  │  │ EVERY round → Tier 1: battlefield evolves                 │   ││
│  │  │   Draw: terrain shift, enemy reveal, environment react    │   ││
│  │  │   Source: scene_elements.complications + behavior profile  │   ││
│  │  │                                                           │   ││
│  │  │ target_down + enemies remain → Tier 1: profile foreshadow │   ││
│  │  │   behavior.py: "The [cautious] survivors pull back..."    │   ││
│  │  │                                                           │   ││
│  │  │ target_down + all enemies down → Tier 1: aftermath        │   ││
│  │  │   Source: scene_elements (what's beyond combat)           │   ││
│  │  │                                                           │   ││
│  │  │ PC drops to 0 HP → Tier 2: death/incapacitation          │   ││
│  │  └───────────────────────────────────────────────────────────┘   ││
│  │                                                                  ││
│  │  ┌─ SAVE ────────────────────────────────────────────────────┐   ││
│  │  │ success → Tier 1: threat averted, event leaves a mark     │   ││
│  │  │   Draw: scene_elements — what changed because of the event│   ││
│  │  │                                                           │   ││
│  │  │ failure → Tier 1: forced consequence + telegraph           │   ││
│  │  │   Hard Rule #5 binds the consequence                      │   ││
│  │  │   PLUS: telegraph what caused it or what comes next       │   ││
│  │  │                                                           │   ││
│  │  │ failure + margin <= -3 → Tier 2: severe + telegraph        │   ││
│  │  └───────────────────────────────────────────────────────────┘   ││
│  │                                                                  ││
│  │  ┌─ CAST-SPELL ──────────────────────────────────────────────┐   ││
│  │  │ success → Tier 1: magic ripples                           │   ││
│  │  │   Outside combat: scene_elements.complications            │   ││
│  │  │   In combat: spell effect ripples (combat context)        │   ││
│  │  │                                                           │   ││
│  │  │ failure → Tier 1: attempt noticed                          │   ││
│  │  │   Arcane discharge / attention drawn / residue             │   ││
│  │  └───────────────────────────────────────────────────────────┘   ││
│  │                                                                  ││
│  │  ┌─ REACTION-ROLL ──────────────────────────────────────────┐    ││
│  │  │ hostile (2-3) → Tier 2: NPC acts against PC              │    ││
│  │  │   mutation: update_favor(npc, -2)                        │    ││
│  │  │   chain: create_consequence() if NPC has power           │    ││
│  │  │                                                          │    ││
│  │  │ unfriendly (4-5) → Tier 1: NPC obstructs + telegraph     │    ││
│  │  │ neutral (6-8) → Tier 1: NPC gives information             │    ││
│  │  │   Draw: world_pulse.rumors or location detail            │    ││
│  │  │ friendly (9-11) → Tier 1: NPC offers opportunity          │    ││
│  │  │ enthusiastic (12+) → Tier 1: active help + quest hook     │    ││
│  │  └──────────────────────────────────────────────────────────┘    ││
│  │                                                                  ││
│  │  ┌─ TRAVEL ─────────────────────────────────────────────────┐    ││
│  │  │ clock portent (from chain_results) → Tier 1 or 2         │    ││
│  │  │   Portents outrank travel events                         │    ││
│  │  │ privation (supplies_end == 0) → Tier 2: resource cost     │    ││
│  │  │ encounter → handled by encounter command (is the move)    │    ││
│  │  │ notable event → Tier 1: promote as featured beat          │    ││
│  │  │ uneventful → Tier 1: world_pulse rumor as featured beat   │    ││
│  │  └──────────────────────────────────────────────────────────┘    ││
│  │                                                                  ││
│  │  ┌─ NARRATIVE (no CLI) ─────────────────────────────────────┐    ││
│  │  │ Always Tier 1: world breathes                             │    ││
│  │  │ Draw: scene_elements sensory detail or world_pulse rumor │    ││
│  │  └──────────────────────────────────────────────────────────┘    ││
│  └──────────────────────────────────────────────────────────────────┘│
│                                                                      │
│  OUTPUT:                                                             │
│  ├── tier (1, 2, or 3 — never 0)                                    │
│  ├── move_type, narrative_directive, source_elements                 │
│  ├── suggested_mutations (telegraphs, favors, consequences, used[])  │
│  ├── counter_update:                                                 │
│  │   tier 1 → turns_since_hard_move += 1                             │
│  │   tier 2+ → turns_since_hard_move = 0                             │
│  └── arithmetic_trace                                                │
└───────────────────────┬──────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│  STEP 7: NARRATE (Phase 4)                                    │
│                                                              │
│  Read select-move output:                                    │
│  ├── Tier 1: weave soft move into narration                  │
│  │   Source elements ground the foreshadow in the scene      │
│  │   Telegraph without resolving                             │
│  │                                                           │
│  ├── Tier 2: narrate hard consequence with gravity           │
│  │   Reference prior telegraph if escalation                 │
│  │   Forced consequences are binding (no softening)          │
│  │                                                           │
│  └── Tier 3: world-level event narration                     │
│      Full treatment (~200-300 words)                         │
│      "The world does not wait"                               │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  STEP 8: PERSIST (Phase 5)                                    │
│                                                              │
│  Standard state mutations PLUS move mutations:               │
│  ├── record_telegraph → telegraphed_threats[]                │
│  ├── escalate_telegraph → status="escalated" + consequence   │
│  ├── mark_element_used → scene_elements.used[]               │
│  ├── update_favor → known_npcs[].favor (diplomacy.py)        │
│  ├── create_consequence → consequence_tracker[]              │
│  ├── turns_since_hard_move update                            │
│  │                                                           │
│  Scene transition guard:                                     │
│  ├── expire_scene_telegraphs(old) BEFORE new scene           │
│  └── all elements used? → force scene transition/generate    │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  STEPS 9-11: POST-RESOLUTION → VALIDATE → RECEIPT            │
│                                                              │
│  Post-resolution (step 9):                                   │
│  ├── Delta detection (day, location, combat, XP)             │
│  ├── scene_elements exhaustion → force generate-scene        │
│  ├── stagnation safety net:                                  │
│  │   └── zero deltas + tier 1 → stagnation warning           │
│  └── Up to 3 iterations                                      │
│                                                              │
│  Validate (step 10): validate-state                          │
│  Receipt (step 11): log commands + move + seeds              │
└──────────────────────────────────────────────────────────────┘
```

### Guarantee: No Static Path Exists

| Turns | What happens |
|-------|-------------|
| Turn 1 | Tier 1 minimum. Soft move introduces new element |
| Turn 2 | Tier 1 minimum. Another soft move, possibly telegraphing |
| Turn 3 | Tier 1 minimum. Telegraphs accumulate |
| Turn 4 | Tier 1 minimum. Tension building |
| Turn 5 | **Forced Tier 2.** Oldest telegraph escalates. Counter resets |
| Turn 6-8 | Tier 1 minimum again. New telegraphs accumulate |
| Turn 9 | **Forced Tier 2 again** (5 since last hard move) |
| ... | |
| Turn 13 | If somehow 8 consecutive Tier 1 since last reset: **Forced Tier 3. World event.** (Impossible in practice since Tier 2 forces at 5) |

Maximum consecutive soft-only turns: **4**. Natural Tier 2 events (catastrophic failures, hostile reactions, privation) make the actual cadence even more dynamic.

### Concrete Example Trace

**Turn 1:** Player fails Sneak check (margin -2). Tier 1 fires. Telegraph created: `{id: "telegraph_patrol_1", description: "Boots echo from the level above", status: "active"}`. Counter: `turns_since_hard_move=1`.

**Turn 2:** Player succeeds. Tier 1: foreshadow via gate success_move. Counter: `turns_since_hard_move=2`.

**Turn 3:** Player fails Know check (margin -3). Tier 1 (no existing telegraph to escalate for this source — record new telegraph): `{id: "telegraph_unstable_3", description: "Dust sifts from a crack in the ceiling"}`. Counter: `turns_since_hard_move=3`.

**Turn 4:** Player succeeds. Tier 1 minimum. Counter: `turns_since_hard_move=4`.

**Turn 5:** Escalation check: `turns_since_hard_move=5`. **Forced Tier 2.** `check_escalation()` finds oldest telegraph (`telegraph_patrol_1`, turn 1). Escalates it. `suggested_chain: "encounter"`. The patrol arrives. Telegraph status → `"escalated"`. Counter resets: `turns_since_hard_move=0`.

**Turns 6-9:** Normal play. Counter reaches 4 by turn 9.

**Turn 10:** `turns_since_hard_move=5` again. Another forced Tier 2 — escalates `telegraph_unstable_3` or uses clock/faction.

## Validation

1. `python runtime/tests/test_moves.py` — new tests pass
2. `python runtime/tests/run_all_tests.py 1` — existing tests pass (no regression)
3. `python runtime/scripts/validate_state.py runtime/state.json` — state validates with new fields
4. Manual trace: simulate 5 turns with all Tier 1 → forced Tier 2 fires with correct source selection
5. Manual trace: simulate 8 turns with all Tier 1 → forced Tier 3 fires, clock accelerated
6. Determinism: same seed produces same move selection
7. Each of 6 dispatchers returns minimum Tier 1 for all result paths

## Risks and Mitigations

- **Risk:** Schema version bump breaks existing state files — **Mitigation:** Additive only (new optional fields with defaults). Migration: add `turns_since_hard_move: 0` to session, `telegraphed_threats: []` to current_scene.
- **Risk:** Forced Tier 2 at turn 5 feels arbitrary — **Mitigation:** Source selection preferring telegraphed threats makes forced moves feel foreshadowed, not random.
- **Risk:** Clock acceleration in Tier 3 bypasses intended pacing — **Mitigation:** Only clocks at >= 50% progress eligible. Below 50%, fall through to faction/environment.
- **Risk:** `select_move()` has no source material (empty state) — **Mitigation:** Environmental hazard fallback for Tier 2, environment shift for Tier 3.
- **Risk:** Tier 1 floor makes every turn feel over-narrated — **Mitigation:** Tier 1 soft moves are ~50 words woven into existing narration, not separate blocks. "The door opens... and something shifts in the dark beyond" is a Tier 1, not a paragraph.
- **Risk:** Combat rounds become bloated with battlefield-evolves Tier 1 — **Mitigation:** Combat Tier 1 draws from scene_elements.complications (finite, curated per scene). When exhausted, suggests scene transition.

## Exit Criteria

1. `select_move()` returns minimum Tier 1 for ALL 6 command dispatchers (no Tier 0 paths)
2. `select_move(tier=2)` with active telegraph → escalates oldest, produces exactly one mutation
3. `select_move(tier=2)` with no telegraph → falls through to clock/faction/environmental sources
4. `select_move(tier=3)` with near-complete clock → accelerates clock, fires completion effect
5. `check_escalation()` correctly evaluates thresholds (5 for Tier 2, 8 for Tier 3)
6. Single counter `turns_since_hard_move` increments on Tier 1, resets on Tier 2+
7. Schema validates with new fields
8. All existing tests pass (no regression)
9. `arithmetic_trace` present on all move outputs
10. Same seed + same state → deterministic move selection
11. Root CLAUDE.md contains embedded turn loop
12. All 6 narration-mappings sections have move-integration notes
13. `behavior.py` exports `get_profile_description()` for attack dispatcher
