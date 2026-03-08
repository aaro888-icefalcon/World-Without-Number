# Phase 5 — State Persistence

Update state.json with all mechanical changes from the current turn.

## When This Phase Runs
- After narrative (Phase 4) is complete
- Before validation (Phase 6)

## Mandatory Steps
1. Identify all state changes from Phase 3 CLI output
2. Apply changes to state.json (HP, conditions, equipment, scene, time)
3. Append chronicle entry for significant events
4. Update `meta.last_played` and `last_played` timestamps
5. Maintain sync invariants: `current_day == campaign.current_day`, `current_time == campaign.current_time`
6. Write state.json

## Key Resources
- Schema contract: `schemas/state.schema.json` — written state must conform
- Validator: `scripts/validate_state.py` — run after every state write
- Procedure detail: `skills/state-persistence.md`
