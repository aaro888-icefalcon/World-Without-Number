# Execution Plan: Remove Narrative Classification + Seed World State at Init

- **Owner:** Claude
- **Status:** Draft
- **Start Date:** 2026-03-10
- **Target Date:** 2026-03-10
- **Related Decision Logs:** User feedback on turn loop defaulting to narrative; prior fix in commit 4642390

## Objective

1. **Eliminate the `narrative` classification entirely.** Every player action maps to a CLI command — no exceptions. `skill-check` is the universal catch-all.
2. **Seed world state during initialization.** The `initialize-game` command populates factions, NPCs, locations, threats, arcs, relations, and world_pulse from lore data — not left as empty arrays.
3. **Enrich character creation prompt.** The player's initial description provides all character stats/mechanics AND seeds world-state lore (tracked NPCs, starting location details, faction standing).
4. **Derive world state from player description.** Additional flavor/context from the player's character concept feeds into `known_locations`, `known_npcs`, `human_factions`, `world_pulse`, etc.

## Scope

- In scope:
  - Remove `narrative` from action-classification, turn-loop, chain_registry, gm_moves, Phase 2 CLAUDE.md, gm-protocol
  - Make `skill-check` the explicit universal fallback with no exceptions
  - Add NYC seed data to `initialize_game.py` for: `human_factions`, `external_threats`, `known_locations`, `campaign_arcs`, `inter_group_relations`, `pc_standing`, `faction_relationships`, `world_pulse`
  - Expand `game-initialization.md` Step 1 prompt to extract world-relevant info from player description
  - Add `--concept` parameter to `initialize-game` CLI to carry player description into state seeding
  - Update state schema if new required subfields are added to seeded arrays

- Out of scope:
  - New CLI commands (no new subcommands needed)
  - Changes to dice/combat/travel mechanics
  - Schema version bump (arrays already exist, just populated vs empty)
  - Lore file changes (data is extracted FROM existing lore INTO code)

## Milestones

### M1: Remove `narrative` from the turn loop (revert + strengthen prior fix)
### M2: Seed world state in `initialize_game.py` from NYC lore
### M3: Enrich character creation to feed world state from player description

---

## Task Breakdown

### M1: Remove `narrative` — Make everything mechanical

- [ ] **action-classification.md**: Delete the "Pure narrative / dialogue / observation" row from the classification table entirely. Remove the §Narrative vs Skill-Check section. Replace with a stronger §Universal Mechanical Classification section that says: "Every player action maps to a CLI command. If no specific command matches, use `skill-check`. There is no non-mechanical classification."
- [ ] **turn-loop.md Step 5**: Remove the "Narrative-only branch" entirely. Step 5 is always the mechanical branch — execute pre_commands → primary → post-chains. Remove `primary == "narrative"?` from the flow diagram.
- [ ] **turn-loop.md Step 6**: Remove the line about `select_move("narrative", {}, ...)` and `_move_narrative_fallback`. All primaries are real CLI commands.
- [ ] **chain_registry.py `expand_action()`**: Remove the narrative early-return block (lines 159-171). All action types go through the standard pre-command/chain expansion.
- [ ] **gm_moves.py**: Keep `_move_narrative_fallback` as the default fallback for unknown commands in `_DISPATCH.get()` (safety net), but it should never be reached in normal operation. Add a comment marking it as a dead-code safety net.
- [ ] **Phase 2 CLAUDE.md**: Remove "Classification Bias: Mechanical First" section (no longer needed — there's no narrative to bias away from). Replace with: "Every player action MUST map to a CLI command. `skill-check` is the universal fallback."
- [ ] **gm-protocol.md**: Remove "Narrative Actions — Mechanical Bias" section. Remove `narrative` from the Command Dispatch list. Add a note: "There is no non-mechanical turn. Every player action produces a CLI execution + GM move."
- [ ] **State-dependent routing in action-classification.md**: Any row that currently says "Narrate from existing..." should instead say "skill-check (DC 6, Notice)" or equivalent. The GM can narrate what the player already knows, but the skill-check still fires to feed the GM move system.
- [ ] **hard-rules.md**: Add Rule 14: "Every Turn Is Mechanical — Every player-action turn executes at least one CLI command. There is no narrative-only classification. If no specific command matches, use `skill-check`."

### M2: Seed world state during initialization

Currently `initialize_game.py` leaves these empty: `human_factions`, `external_threats`, `known_locations`, `campaign_arcs`, `inter_group_relations`, `pc_standing`, `faction_relationships`, `world_pulse.rumors/trends/arrivals`, `known_npcs`.

- [ ] **Add `NYC_INITIAL_FACTIONS` to `initialize_game.py`**: Seed `human_factions` with structured data from `nyc-factions.md`:
  - JDA (military/police), Organized Crime, Labor Unions, Academic Community, Community Orgs
  - Each with: `id`, `name`, `type`, `description`, `disposition_to_pc` (neutral), `power_level`, `goals`, `resources`

- [ ] **Add `NYC_INITIAL_THREATS` to `initialize_game.py`**: Seed `external_threats` from lore:
  - The Verdancy (western biological threat)
  - Gallery Servitors / Imperator (underground dungeon threat)
  - Pelegrinian Empire (geopolitical pressure)
  - Each with: `id`, `name`, `threat_level`, `description`, `status`

- [ ] **Add `NYC_INITIAL_LOCATIONS` to `initialize_game.py`**: Seed `known_locations` with starting locations:
  - Lower Manhattan (starting area), Gallery Mouth (visible from waterfront), Council Chamber, Borough borders
  - Each with: `id`, `name`, `region_id`, `description`, `threat_level`, `discovered_day`

- [ ] **Add `NYC_INITIAL_ARCS` to `initialize_game.py`**: Seed `campaign_arcs` with 2-3 starting arcs from lore:
  - "The Food Crisis" — finding sustainable food supply
  - "The Gallery Below" — understanding and containing the dungeon threat
  - Each with: `id`, `name`, `status`, `beats` (with trigger conditions)

- [ ] **Add `NYC_INITIAL_RELATIONS` to `initialize_game.py`**: Seed `inter_group_relations` and `faction_relationships`:
  - JDA ↔ Council (tense cooperation)
  - Boroughs ↔ Council (fragile federation)
  - NYC ↔ Amundi (nascent trade)

- [ ] **Seed `world_pulse`**: Populate `rumors`, `trends`, `arrivals` with Day 1 content:
  - Rumors: "Something breached the galleries overnight", "The bridges lead to wilderness, not New Jersey"
  - Trends: "Food rationing begins", "Electronics are all dead"
  - Arrivals: none (Day 1)

- [ ] **Seed `pc_standing`**: Initialize PC standing with key factions at 0 (neutral):
  - JDA: 0, Council: 0, Borough (Manhattan): 0

- [ ] **Update `generate_initial_state()`**: Wire all new seed data arrays into the state dict (NYC campaign branch).

### M3: Enrich character creation to feed world state

- [ ] **Expand Step 1 prompt in `game-initialization.md`**: Change the question to also elicit world-relevant info:
  > "Who are you? Describe your character — name, who they are, what they're good at, what matters to them. Where in the city were you when everything changed? Who matters to you here?"

- [ ] **Add `--concept` parameter to `initialize-game` CLI**: Pass the player's full concept text so it can be persisted in `meta` for reference (already partially done via `creation_progress.concept`, but make it survive into final state as `meta.character_concept`).

- [ ] **Add GM extraction instructions to `game-initialization.md`**: After Step 2 (character build), add a Step 2d: "Extract world seeds from concept":
  - Named NPCs mentioned → seed into `known_npcs` with basic voice cards
  - Locations mentioned → seed into `known_locations`
  - Faction affiliations implied → adjust `pc_standing` entries
  - Relationships mentioned → seed into appropriate trackers
  - These are GM-generated from the concept, not additional CLI execution

- [ ] **Update `game-initialization.md` Step 3**: After `initialize-game` runs, the GM applies concept-derived overrides to the generated state before writing `state.json`:
  - Merge concept-extracted NPCs into `known_npcs`
  - Adjust `pc_standing` based on implied affiliations
  - Add concept-mentioned locations to `known_locations`

## Validation

- [ ] All existing tests pass: `python runtime/tests/run_all_tests.py 1`
- [ ] State validator passes on a freshly initialized state: `python runtime/scripts/validate_state.py runtime/state.json`
- [ ] Reference freshness: `python runtime/scripts/validate_reference_freshness.py`
- [ ] Docs structure: `python runtime/scripts/validate_docs_structure.py`
- [ ] Canonical references: `python runtime/scripts/validate_canonical_references.py`
- [ ] `grep -r "narrative" runtime/` returns zero hits in action-classification, turn-loop, Phase 2 CLAUDE.md (only expected in gm_moves.py safety-net comment and gm-protocol.md narrative-voice section which is about writing style, not classification)
- [ ] `expand_action("skill-check", state)` works for the universal fallback case
- [ ] Freshly initialized state has non-empty: `human_factions`, `external_threats`, `known_locations`, `campaign_arcs`, `world_pulse.rumors`, `pc_standing`

## Risks and Mitigations

- **Risk:** Removing narrative breaks the fallback for genuinely zero-stakes actions (player says "I sit down") — **Mitigation:** These become `skill-check` with DC 6 and a generous attribute. The roll always succeeds but still feeds the GM move system. The cost is trivial; the benefit is mechanical consistency.
- **Risk:** Large seed data in `initialize_game.py` makes the file unwieldy — **Mitigation:** Keep entries minimal (id, name, 1-line description, key fields). Full lore stays in markdown files; seed data is just enough for state tracking.
- **Risk:** Schema validation fails on new seed data shapes — **Mitigation:** Verify against `state.schema.json` definitions for each array type before implementing. The schema already defines these array item shapes; we just need to conform.
- **Risk:** Concept extraction (M3) is LLM-dependent, not deterministic — **Mitigation:** The extraction produces state entries, but these are written by the GM to state.json (same as any Phase 5 persistence). The CLI produces the base state; the GM enriches it. This is the existing pattern for post-resolution state updates.

## Exit Criteria

1. No `narrative` classification exists anywhere in the action classification pipeline
2. Every player action that enters the turn loop produces at least one CLI execution
3. A freshly initialized NYC game has populated (non-empty) factions, threats, locations, arcs, relations, and world_pulse
4. The character creation flow extracts world-relevant info from the player's concept and seeds it into state
5. All validators pass
