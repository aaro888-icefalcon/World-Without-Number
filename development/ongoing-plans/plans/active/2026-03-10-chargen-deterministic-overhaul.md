# Execution Plan: Character Creation — Deterministic Overhaul

- **Owner:** Claude
- **Status:** In Progress
- **Start Date:** 2026-03-10
- **Target Date:** 2026-03-10
- **Related Decision Logs:** User feedback on character creation UX

## Objective

Fix character creation so it: (1) uses Python tables as source of truth instead of hallucinating from markdown, (2) GM picks everything based on character concept instead of presenting menus, (3) saves progress incrementally, (4) uses character concept to seed world state info, (5) stops reprinting long lists across compressed conversation turns.

## Scope

- In scope:
  - New `query-chargen-options` CLI command that exposes Python table data
  - `--known-arts` and `--class-ability-overrides` params on `initialize-game`
  - Rewrite `game-initialization.md` to a 3-step GM-picks flow
  - Incremental concept save (write partial data to state.json after concept step)
  - Update CLI docs (scripts CLAUDE.md)

- Out of scope:
  - Schema version bump (no new required fields)
  - Changes to validation scripts
  - Changes to the turn loop or runtime pipeline

## Milestones

1. `query-chargen-options` CLI command — returns filtered foci, arts, class abilities, backgrounds from Python tables
2. `initialize-game` accepts `--known-arts` and `--class-ability-overrides` to override auto-picks
3. `game-initialization.md` rewritten: 3 steps (concept → GM build → confirm)
4. Incremental saves: concept stored in `state.json` meta after step 1

## Task Breakdown

- [ ] Add `query-chargen-options` command to emergence_cli.py + handler function
- [ ] Add `--known-arts` param to initialize-game / create_character
- [ ] Add `--class-ability-overrides` param to allow dropping abilities (e.g., no Veteran's Luck)
- [ ] Rewrite game-initialization.md to 3-step flow
- [ ] Add incremental save instructions (write concept to state.json meta)
- [ ] Update scripts/CLAUDE.md with new command
- [ ] Run tests

## Validation

- `python runtime/tests/run_all_tests.py 1` passes
- `query-chargen-options` returns correct filtered results for test cases
- `initialize-game` with `--known-arts` produces valid state
- `validate_state.py` passes on generated state

## Risks and Mitigations

- **Risk:** Query command returns stale data if tables change — **Mitigation:** Command reads directly from imported table modules, no caching
- **Risk:** game-initialization.md references removed steps — **Mitigation:** Full rewrite, not incremental edit

## Exit Criteria

1. `query-chargen-options --class adventurer --partial-classes accursed,warrior` returns valid foci and arts from Python tables
2. `initialize-game` with `--known-arts "night_black_eyes,accursed_blade"` works
3. game-initialization.md describes 3-step flow with GM-picks-for-you pattern
4. Concept data saved incrementally to state.json
