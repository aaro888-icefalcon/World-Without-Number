# Phase 6 — Validation

Verify response completeness and correctness before delivering to the player.

## When This Phase Runs
- After state persistence (Phase 5)
- Validation hooks fire automatically on every response

## Mandatory Steps
1. Run the response gate checklist: `skills/response-gate.md`
2. Verify: all mechanics resolved via CLI (not improvised)
3. Verify: state.json updated with all changes
4. Verify: narrative does not contradict mechanical results
5. Verify: response ends with player prompt

## Halt Conditions
- Required CLI script missing or failed
- State validation fails after write
- Narrative contradicts mechanical result
- Action auto-resolved without CLI when command exists

## Manual Validation (On-Demand)
- `python scripts/validate_state.py state.json` — full state schema check
- `python scripts/validate_reference_freshness.py` — reference path check
