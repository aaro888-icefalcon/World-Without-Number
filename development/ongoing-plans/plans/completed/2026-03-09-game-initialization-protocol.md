# Execution Plan: Game Initialization Protocol

- **Owner:** Development
- **Status:** Complete
- **Completion Date:** 2026-03-09
- **Start Date:** 2026-03-09
- **Target Date:** 2026-03-09
- **Related Decision Logs:** N/A

## Objective

Create a codified initialization protocol that governs game startup, streamlined character creation, and opening scene setting. The protocol must be discoverable by runtime Claude through existing CLAUDE.md and skill files, and must produce a valid, playable state.json from a blank template through an interactive player-facing flow.

## Scope

- In scope:
  - New Phase 0 (game-initialization) skill file with step-by-step interactive protocol
  - `initialize-game` CLI command to generate seeded initial state.json
  - Updates to runtime/CLAUDE.md to add initialization as a pre-turn-loop entry point
  - Updates to Phase 1 CLAUDE.md for session-start vs game-start distinction
  - Updates to phase-manifest.md and scripts/CLAUDE.md registries
  - Validation test for the initialization protocol
- Out of scope:
  - Schema changes (state.schema.json is sufficient as-is)
  - New lore content
  - Changes to the turn loop contract itself

## Milestones

1. Initialization protocol skill file created and wired into Phase 1
2. `initialize-game` CLI command implemented and registered
3. Runtime CLAUDE.md updated with game-start entry point
4. Validation test passes
5. Existing tests still pass

## Task Breakdown

- [x] Research current codebase (game setting, character creation, scene setting, state schema)
- [x] Create `runtime/phases/1-context-loading/skills/game-initialization.md` — the protocol skill
- [x] Create `runtime/scripts/initialize_game.py` — CLI script to generate initial state
- [x] Add `initialize-game` command to `emergence_cli.py`
- [x] Update `runtime/CLAUDE.md` — add initialization entry point before turn loop
- [x] Update `runtime/phases/1-context-loading/CLAUDE.md` — game-start context
- [x] Update `runtime/phases/phase-manifest.md` — register new skill and command
- [x] Update `runtime/scripts/CLAUDE.md` — register new script
- [x] Update `runtime/phases/1-context-loading/index.md` — register new skill
- [x] Create `runtime/tests/test_game_initialization.py` — validation test
- [x] Run all existing tests to verify no regressions (63/63 pass)

## Validation

1. `python runtime/scripts/emergence_cli.py initialize-game --name "Test" --class warrior --background 1 --seed 42` produces valid JSON
2. Output JSON passes `python runtime/scripts/validate_state.py`
3. `python runtime/tests/test_game_initialization.py` passes
4. `python runtime/tests/run_all_tests.py 1` passes (no regressions)

## Risks and Mitigations

- **Risk:** Protocol is too rigid, doesn't allow player agency in character creation choices — **Mitigation:** Protocol is interactive; Claude presents options at each step and waits for player input
- **Risk:** Generated state doesn't pass validation — **Mitigation:** Test explicitly validates output against schema
- **Risk:** NYC-specific initialization clocks/factions make the protocol too campaign-specific — **Mitigation:** Base protocol is campaign-agnostic; NYC seeding is an optional campaign module

## Exit Criteria

1. `initialize-game` CLI command produces schema-valid state.json
2. Protocol skill file is discoverable in Phase 1 CLAUDE.md and phase-manifest.md
3. Runtime CLAUDE.md documents the game-start entry point
4. All tests pass (new + existing)
