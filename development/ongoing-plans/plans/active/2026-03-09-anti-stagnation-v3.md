# Execution Plan: Anti-Stagnation v3 — Scene-Pressure Move System

- **Owner:** Development team
- **Status:** Draft
- **Start Date:** 2026-03-09
- **Target Date:** 2026-03-09
- **Related Decision Logs:** `gm-protocol.md`, `hard-rules.md`, `turn-loop.md`

## Objective

Implement a three-tier GM move system that mechanically prevents play from stagnating. The system tracks turns since the last tier 2 (hard move) and tier 3 (world move), forces escalation when thresholds are reached, and routes all consequences through the existing CLI pipeline. Telegraphed threats create foreshadowed consequences that escalate into binding mechanical events.

### What this solves

Without anti-stagnation, the GM (LLM) tends toward safe, repetitive turns — skill checks that don't bite, combats that don't escalate, a world that waits politely. The move system guarantees:

- Every 5 turns: something bad happens to the PC (tier 2 hard move)
- Every 12 turns: the world acts on its own agenda (tier 3 world move)
- Soft moves (tier 1) telegraph future danger on every failed or marginal roll

## Scope

### In scope:
- `moves.py` (new) — `select_move()` function: source selection, consequence routing, CLI dispatch
- `state.schema.json` — Add `session.turns_since_tier2`, `session.turns_since_tier3`, `current_scene.telegraphed_threats[]`
- `triggers.py` — Extend `check_all_triggers()` to evaluate anti-stagnation thresholds
- `turn-loop.md` — Add move-tier evaluation as a sub-step of step 0
- `gm-protocol.md` — Add §Scene Pressure with tier definitions and narrative directives
- `hard-rules.md` — Add Hard Rule #13: Scene Pressure Is Binding
- Test suite — `test_moves.py`

### Out of scope:
- New CLI subcommands (moves route to existing commands: `attack`, `encounter`, `world-tick`, `faction-turn`, `generate-scene`)
- Combat AI changes (behavior.py unchanged)
- Consequence tracker changes (consequence.py unchanged — moves CREATE consequences through it)
- Phase 4 narrative template changes (moves provide `narrative_directive` text, Phase 4 follows it)

## Architecture

### Tier Definitions

| Tier | Name | What it does | Threshold | Resets |
|------|------|-------------|-----------|--------|
| 1 | Soft Move | Telegraphs future danger. Creates a `telegraphed_threat` entry in scene state. | Every failed/marginal roll | Nothing |
| 2 | Hard Move | A consequence lands on the PC. Exactly one mechanical mutation. | Forced at `turns_since_tier2 >= 5`, or natural from catastrophic failure | `turns_since_tier2` → 0 |
| 3 | World Move | The world acts independently. May involve multiple state changes. | Forced at `turns_since_tier3 >= 12`, or natural from clock completion / faction action | Both counters → 0 |

### Move Flow

```
Turn starts
  │
  ├─ Step 0: check-triggers (existing)
  │    └─ NEW: evaluate anti-stagnation counters
  │         ├─ turns_since_tier2 >= 5? → FORCE tier 2
  │         └─ turns_since_tier3 >= 12? → FORCE tier 3
  │
  ├─ Step 1-5: normal turn execution
  │    └─ command dispatch may NATURALLY produce tier 1/2:
  │         ├─ skill-check margin -1 to -4 → tier 1 (telegraph)
  │         ├─ skill-check margin <= -5 → tier 2 (consequence)
  │         ├─ hostile reaction-roll → tier 2
  │         └─ travel privation → tier 2
  │
  ├─ Step 6: persist state
  │    └─ increment turns_since_tier2 and turns_since_tier3
  │       (UNLESS this turn already fired a tier 2 or 3)
  │
  └─ Step 7: post-resolution
       └─ if tier 2/3 fired, its commands appear in post-resolution follow-ups
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
| 1st | Clock completion | Any clock with `status: "active"` and `current` near `max` |
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

**Natural tier 2 from command dispatch — gate-type mapping:**

| Gate type | Tier 2 consequence |
|-----------|-------------------|
| access | Path closes — the thing you tried to access is now harder or impossible |
| discovery | Misinformation — wrong conclusion persisted to state |
| social | NPC hostility — `update_favor()` with negative delta, possible `create_consequence()` |
| survival | Resource loss — supplies, HP, or equipment damaged |
| combat_setup | Ambush reversed — enemies get surprise, `encounter` fires with +2 threat_level |

### Tier 3 — Multi-Mutation Allowed

Unlike tier 2, tier 3 may produce multiple state changes because the world acts at larger scale:

| Source type | CLI commands | State changes |
|------------|-------------|---------------|
| Clock completion | `world-tick --days 0` | Clock → `"completed"`, completion_effect fires, location status changes |
| Faction action | `faction-turn` | Faction assets/goals updated, territory shifts |
| Arc beat trigger | `check-triggers` | Beat status → `"triggered"`, narrative event queued |
| Environment shift | `generate-scene` | `current_scene` replaced, `known_locations[]` updated |

**Clock acceleration:** If a tier 3 is forced and no clock is naturally ready, the nearest-to-completion active clock is advanced to completion. The world does not wait.

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

Stored in `current_scene.telegraphed_threats[]`. When a tier 2 fires and active telegraphs exist, the oldest telegraph escalates — the warning becomes reality.

### select_move() Return Contract

```python
{
    "tier": 2,  # 1, 2, or 3
    "move_type": "telegraph_escalates",  # descriptive tag
    "source": {
        "type": "telegraph",  # telegraph | command_result | clock | faction | arc_beat | environment
        "id": "threat_tunnel_patrol",
        "description": "The patrol you heard earlier",
    },
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
    "requires_cli": "attack",  # CLI command to execute, or null for direct state writes
    "narrative_directive": "The telegraphed patrol arrives. Narrate the ambush with "
        "gravity. The damage is binding. Reference the prior foreshadow.",
    "forced_consequence": True,
    "counter_updates": {"turns_since_tier2": 0},
    "arithmetic_trace": "Tier 2: telegraph 'threat_tunnel_patrol' (created turn 3) "
        "escalated at turn 7. Source: forced (turns_since_tier2=5).",
}
```

## Task Breakdown

### T1: Schema Changes — state.schema.json

- [ ] **T1.1** Add to `session` definition:
  ```json
  "turns_since_tier2": { "type": "integer", "minimum": 0, "description": "Turns since last hard move" },
  "turns_since_tier3": { "type": "integer", "minimum": 0, "description": "Turns since last world move" }
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

### T2: Core Script — moves.py (NEW)

Create `runtime/phases/3-resolution/skills/world-building/scripts/moves.py`.

- [ ] **T2.1** `record_telegraph(description, source_element, current_turn)` → returns telegraph dict
  - Appends to `current_scene.telegraphed_threats[]`
  - Status: `"active"`

- [ ] **T2.2** `select_move(tier, state, command_result=None)` → returns move dict per contract above
  - For tier 1: calls `record_telegraph()`, returns move with `tier: 1`
  - For tier 2: runs source selection priority (telegraph → command_result → clock → faction)
  - For tier 3: runs source selection priority (clock → faction → arc_beat → environment)
  - For forced tier 2/3: skips `command_result` source (there was no command failure)

- [ ] **T2.3** `_select_tier2_source(state)` — internal source selection
  - Check `current_scene.telegraphed_threats` for oldest active
  - Check `clocks` for unfired portent nearest to current
  - Check `human_factions` for goals targeting PC location
  - Return `{type, id, description}` or None

- [ ] **T2.4** `_select_tier3_source(state)` — internal source selection
  - Check `clocks` for nearest-to-completion active clock
  - Check `human_factions` for active goals in PC region
  - Check `campaign_arcs[].beats` for pending beats near threshold
  - Fallback: environment shift
  - Return `{type, id, description}` or None

- [ ] **T2.5** `_build_tier2_mutations(source, state)` — map source to exactly one mutation type
  - Telegraph escalation: `escalate_telegraph` + consequence from telegraph's source_element
  - Clock portent: `create_consequence` from portent's mechanical effect
  - Faction: `update_favor` or `close_path` based on faction goal type
  - No source available: `immediate_resource_cost` (minor environmental hazard)

- [ ] **T2.6** `_build_tier3_mutations(source, state)` — map source to mutation(s)
  - Clock completion: `complete_clock` + location updates + cascading consequences
  - Faction action: faction state updates + territory/access changes
  - Arc beat: beat status update + narrative event
  - Environment: scene replacement

- [ ] **T2.7** `_determine_requires_cli(tier, source, mutations)` — which CLI command(s) to fire
  - Tier 2 with combat source → `"attack"` or `"encounter"`
  - Tier 2 with trap/hazard → `"save"`
  - Tier 2 with social → None (direct state write)
  - Tier 3 with clock → `["world-tick"]`
  - Tier 3 with faction → `["faction-turn"]`
  - Tier 3 with environment → `["generate-scene"]`

- [ ] **T2.8** `check_stagnation_counters(session)` → returns `{force_tier2: bool, force_tier3: bool}`
  - `force_tier2 = session.turns_since_tier2 >= 5`
  - `force_tier3 = session.turns_since_tier3 >= 12`

- [ ] **T2.9** `move_for_skill_check(margin, gate_type)` → returns tier (1, 2, or None)
  - margin -1 to -4: tier 1
  - margin <= -5: tier 2
  - margin >= 0: None (success, no move)

### T3: Trigger Integration — triggers.py (EDIT)

- [ ] **T3.1** Add `check_stagnation()` to `check_all_triggers()`:
  - Read `session.turns_since_tier2` and `session.turns_since_tier3`
  - If either threshold met, append to `commands_to_fire`:
    ```python
    {
        "command": "select-move",
        "args": {"tier": 2},  # or 3
        "reason": f"Anti-stagnation: turns_since_tier2={n} (threshold: 5)",
        "source": "anti_stagnation",
        "priority": "high",
    }
    ```
- [ ] **T3.2** Add stagnation counters to `arithmetic_trace` output

### T4: Turn Loop Integration — turn-loop.md (EDIT)

- [ ] **T4.1** Add to step 0 (after existing trigger checks):
  ```
  0b. **Scene pressure — anti-stagnation check**
      - Read `session.turns_since_tier2` and `session.turns_since_tier3`.
      - If tier 2 threshold (5) reached: call `select_move(tier=2, state)`.
        Execute `requires_cli` command(s) from the result. Apply `suggested_mutations`.
        Narrate per `narrative_directive`. Reset counter.
      - If tier 3 threshold (12) reached: call `select_move(tier=3, state)`.
        Execute `requires_cli` command(s). Apply mutations. Narrate with full
        dramatic treatment (200-300 words, costs 1 drama_budget). Reset both counters.
      - Forced moves fire BEFORE the player's turn — the world acts first.
  ```
- [ ] **T4.2** Add to step 6 (persist):
  ```
  6b. **Increment stagnation counters**
      - If no tier 2 fired this turn: `session.turns_since_tier2 += 1`
      - If no tier 3 fired this turn: `session.turns_since_tier3 += 1`
      - If tier 2 fired: `session.turns_since_tier2 = 0`
      - If tier 3 fired: `session.turns_since_tier2 = 0`, `session.turns_since_tier3 = 0`
  ```
- [ ] **T4.3** Add to step 5 (after command dispatch):
  ```
  5b. **Natural move evaluation**
      - If command was skill-check with margin -1 to -4: fire tier 1 (record_telegraph)
      - If command was skill-check with margin <= -5: fire tier 2 (select_move)
      - If command was reaction-roll with hostile result: fire tier 2
      - If command was travel with privation: fire tier 2
  ```

### T5: GM Protocol — gm-protocol.md (EDIT)

- [ ] **T5.1** Add §Scene Pressure section:
  ```markdown
  ## Scene Pressure

  The move system prevents play from stagnating. Three tiers of GM response
  ensure consequences accumulate and the world stays dangerous.

  ### Tier 1 — Soft Move (Telegraph)
  On every failed or marginal roll, foreshadow future danger. Create a
  `telegraphed_threat` in the current scene. Describe the warning through
  sensory detail — sounds, smells, environmental signs. The player should
  feel that something is coming.

  Narration: ~50 words. Woven into the skill-check narration, not a separate block.

  ### Tier 2 — Hard Move (Consequence)
  A consequence lands on the PC. This fires naturally from catastrophic
  failures or is forced every 5 turns. Exactly one mechanical mutation.
  If active telegraphs exist, the oldest one escalates — the foreshadowed
  threat becomes real.

  Narration: §consequence treatment (~150 words). Reference the prior
  telegraph if one existed. The consequence is BINDING (Hard Rule #13).

  ### Tier 3 — World Move (The World Acts)
  The world pursues its own agenda. Fires naturally from clock completions
  and faction actions, or forced every 12 turns. May produce multiple state
  changes. This is NOT directed at the PC — it is something that happens
  in the world that the PC witnesses or hears about.

  Narration: §dramatic-moments treatment (200-300 words). Costs 1 drama_budget.
  The world moved — narrate it with gravity and scale.

  ### Counter Rules
  - Tier 2 resets `turns_since_tier2` to 0
  - Tier 3 resets BOTH counters to 0
  - Counters increment by 1 at end of any turn where no tier 2/3 fired
  - Counters reset to 0 at session start
  ```

### T6: Hard Rules — hard-rules.md (EDIT)

- [ ] **T6.1** Add Hard Rule #13:
  ```markdown
  ## 13. Scene Pressure Is Binding
  When `select_move` returns a forced tier 2 or tier 3 consequence, it fires.
  It cannot be softened, delayed, or narratively circumvented. The
  `suggested_mutations` are applied to state. The `requires_cli` command
  executes with binding results. Telegraphed threats that escalate become
  real mechanical events, not narrative flavor.
  ```

### T7: Tests — test_moves.py (NEW)

Create `runtime/tests/test_moves.py`.

- [ ] **T7.1** Test `record_telegraph()` produces valid telegraph dict with required fields
- [ ] **T7.2** Test `check_stagnation_counters()`:
  - `turns_since_tier2=4` → `{force_tier2: False, force_tier3: False}`
  - `turns_since_tier2=5` → `{force_tier2: True, force_tier3: False}`
  - `turns_since_tier3=12` → `{force_tier2: False, force_tier3: True}`
  - Both at threshold → both True
- [ ] **T7.3** Test `move_for_skill_check()`:
  - margin 0 → None
  - margin -2 → 1
  - margin -5 → 2
  - margin -8 → 2
- [ ] **T7.4** Test `select_move(tier=2)` with active telegraph → escalates oldest
- [ ] **T7.5** Test `select_move(tier=2)` with no telegraph → falls through to clock/faction
- [ ] **T7.6** Test `select_move(tier=2)` with no sources → produces environmental hazard
- [ ] **T7.7** Test `select_move(tier=3)` with near-completion clock → clock acceleration
- [ ] **T7.8** Test `select_move(tier=3)` with no clock → faction fallback
- [ ] **T7.9** Test `select_move(tier=3)` environment shift fallback (no clocks, no factions)
- [ ] **T7.10** Test tier 2 mutation types: exactly one primary mutation per move
- [ ] **T7.11** Test tier 3 mutation types: allows multiple mutations
- [ ] **T7.12** Test `_determine_requires_cli()` returns correct commands per source type
- [ ] **T7.13** Test counter_updates: tier 2 resets tier2 only, tier 3 resets both
- [ ] **T7.14** Test arithmetic_trace is present and non-empty on all moves
- [ ] **T7.15** Test schema validation passes with new session fields and telegraphed_threats
- [ ] **T7.16** Determinism: same state + same seed → same move selection

### T8: State Update — state.json (EDIT)

- [ ] **T8.1** Add to `session` object:
  ```json
  "turns_since_tier2": 0,
  "turns_since_tier3": 0
  ```
- [ ] **T8.2** Add to `current_scene`:
  ```json
  "telegraphed_threats": []
  ```
- [ ] **T8.3** Run `validate-state` to confirm schema compliance

## Implementation Order

1. T1 — Schema changes (defines the contract)
2. T7 — Write tests first (validates completion criteria)
3. T2 — Core `moves.py` script (the engine)
4. T3 — Wire into triggers.py (discovery)
5. T5, T6 — Update governance docs (gm-protocol, hard-rules)
6. T4 — Update turn-loop.md (integration)
7. T8 — Update state.json with new fields
8. Run all tests, fix issues
9. Run existing test suite (regression check)

## Modified Files Summary

| File | Change Type | Surfaces Touched |
|------|-------------|------------------|
| `schemas/state.schema.json` | Edit | State schema |
| `skills/world-building/scripts/moves.py` | New | Rules logic |
| `skills/world-building/scripts/triggers.py` | Edit | Rules logic |
| `turn-loop.md` | Edit | Turn loop contract |
| `phases/1-context-loading/references/gm-protocol.md` | Edit | GM protocol |
| `phases/1-context-loading/references/hard-rules.md` | Edit | Hard rules |
| `tests/test_moves.py` | New | Validation |
| `state.json` | Edit | State data |

## Validation

1. `python runtime/tests/test_moves.py` — new tests pass
2. `python runtime/tests/run_all_tests.py 1` — existing tests pass (no regression)
3. `python runtime/scripts/validate_state.py runtime/state.json` — state validates with new fields
4. Manual trace: simulate 5 turns with no tier 2 → forced tier 2 fires with correct source selection
5. Manual trace: simulate 12 turns with no tier 3 → forced tier 3 fires, clock accelerated
6. Determinism: same seed produces same move selection

## Risks and Mitigations

- **Risk:** Schema version bump breaks existing state files — **Mitigation:** Additive only (new optional fields with defaults). Migration: add `turns_since_tier2: 0`, `turns_since_tier3: 0` to session, `telegraphed_threats: []` to current_scene.
- **Risk:** Forced tier 2 at turn 5 feels arbitrary — **Mitigation:** Source selection preferring telegraphed threats makes forced moves feel foreshadowed, not random. The player saw the warning.
- **Risk:** Clock acceleration in tier 3 bypasses intended pacing — **Mitigation:** Only accelerates the nearest-to-completion clock, not an arbitrary one. If no clock is above 50% progress, environment shift fallback fires instead (no acceleration).
- **Risk:** `select_move()` has no source material to draw from (empty state) — **Mitigation:** Environmental hazard fallback for tier 2, environment shift for tier 3. These are generic but always available.
- **Risk:** Turn loop becomes too complex with move evaluation at three points (steps 0, 5, 6) — **Mitigation:** Step 0 handles forced moves only. Step 5 handles natural moves only. Step 6 just increments counters. Each touch point has a single responsibility.

## Analysis Pass 1 — Weaknesses Found and Fixed

**W1 (FIXED): Telegraphs don't persist across scenes.** Telegraphed threats live in `current_scene`. When the scene changes, they're lost. FIXED: This is correct behavior — telegraphs are scene-local. A warning about "boots above" doesn't follow you to a different location. Scene changes naturally clear them.

**W2 (FIXED): Tier 3 clock acceleration could fire on a clock at 1/8.** Accelerating a barely-started clock feels wrong. FIXED: Add 50% threshold — only clocks at `current >= max/2` are eligible for acceleration. Below 50%, fall through to faction/environment sources.

**W3 (FIXED): Dual forced (tier 2 at 5 AND tier 3 at 12 on same turn).** Both thresholds met simultaneously. FIXED: Tier 3 takes priority (it resets both counters). Only one forced move per turn. Tier 3 subsumes tier 2.

**W4 (FIXED): Natural tier 2 from command + forced tier 2 on same turn.** If a skill check naturally produces tier 2, the forced tier 2 is redundant. FIXED: Natural tier 2 resets the counter. If a natural tier 2 fires during step 5, the forced check in step 0 won't have fired (it checked before the command). The counter reset in step 6 prevents double-counting.

**W5 (FIXED): No gate_type on existing skill-check output.** The `move_for_skill_check` function needs a gate_type to determine consequence flavor, but skill-check CLI output doesn't include one. FIXED: `gate_type` is a Phase 2 classification detail, not a CLI output. `select_move` receives it from the action interpretation context, not from CLI JSON.

**W6 (FIXED): Consequence tracker max 20 — tier 2 creating consequences could overflow.** FIXED: `select_move` checks `len(consequence_tracker)` before choosing `create_consequence` mutation. If at cap, uses `immediate_resource_cost` instead (instant effect, no tracker entry).

## Exit Criteria

1. `select_move(tier=1)` creates valid telegraph in scene state
2. `select_move(tier=2)` with active telegraph → escalates oldest, produces exactly one mutation
3. `select_move(tier=2)` with no telegraph → falls through to clock/faction/environmental sources
4. `select_move(tier=3)` with near-complete clock → accelerates clock, fires completion effect
5. `select_move(tier=3)` with no clock → faction or environment fallback
6. `check_stagnation_counters()` correctly evaluates thresholds (5 and 12)
7. Counters increment on non-move turns, reset on move turns
8. Tier 3 resets both counters; tier 2 resets only its own
9. Schema validates with new fields
10. All existing tests pass (no regression)
11. `arithmetic_trace` present on all move outputs
12. Same seed + same state → deterministic move selection
