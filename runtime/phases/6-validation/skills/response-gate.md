# Response Gate — Turn Completeness Verification

This skill runs as the final check before a turn response is delivered to the player.

## When This Runs
- After Phase 5 state persistence
- Before the response is shown to the player

## Verification Checklist

### 1. Mechanical Fidelity
- [ ] All player actions that required dice/mechanics were resolved via CLI (not improvised)
- [ ] CLI output JSON was parsed and used — not ignored or overridden
- [ ] If a forced consequence was returned, it was narrated exactly as given
- [ ] RNG seed was recorded (if any CLI command was executed)

### 2. State Consistency
- [ ] `state.json` was updated with all mechanical changes from this turn
- [ ] `character.hp.current` is between 0 and `character.hp.max`
- [ ] `character.system_strain.current` is between 0 and `character.system_strain.max`
- [ ] `current_day == campaign.current_day` (sync invariant)
- [ ] `current_time == campaign.current_time` (sync invariant)
- [ ] `meta.last_played` was updated

### 3. Narrative Completeness
- [ ] The turn includes narrative description of the action outcome
- [ ] Narrative does not contradict CLI mechanical results
- [ ] Turn ends with a player prompt ("What do you do?" or equivalent)

### 4. No Hallucination
- [ ] Narration references only lore loaded in Phase 1 context
- [ ] No invented NPC names, locations, or world facts that aren't in state or loaded lore
- [ ] Spell effects, creature abilities, and item properties come from extracted data tables
- [ ] NPC dialogue follows voice card from `known_npcs[]` (speech_patterns, key_phrases)
- [ ] Region descriptions match loaded nation lore file

### 5. Social & Narrative Integrity
- [ ] If NPC interaction occurred, `known_npcs[].last_interaction_summary` updated
- [ ] If dramatic event occurred, `session.drama_budget` decremented
- [ ] If scene type changed, `campaign.scene_rhythm` updated
- [ ] If consequence should have triggered (timer expired), it was checked
- [ ] Latter Earth voice maintained (per `references/latter-earth-voice.md`)

## Halt Conditions

If ANY of the following are true, HALT the turn and report the error:
- A required CLI script was missing or failed with non-zero exit
- State validation (`validate_state.py`) fails after the state write
- The narrative contradicts a mechanical result (e.g., narrating a hit when CLI said miss)
- An action was auto-resolved without CLI when a CLI command exists for that action type

## Post-Validation

After passing all checks:
1. Deliver the narrative response to the player
2. The turn is considered complete
3. Wait for the next player input before starting a new turn cycle
