# Phase 2 — Action Interpretation

Classify the player's declared action and select the appropriate CLI command.

## When This Phase Runs
- After context loading, when player declares an action
- Before any CLI execution

## Mandatory Steps
1. Check for `DEVELOPMENT:` prefix — if present, skip to development mode
2. Read the player's declared action
3. Classify intent using `references/action-classification.md` categories
4. Select the correct CLI subcommand and determine arguments using `references/cli-reference.md`
5. Confirm the interpreted action with the player before proceeding to Phase 3
6. DO NOT execute yet — that's Phase 3

## Key References
- `references/action-classification.md` — intent classification rules and difficulty guidelines
- `references/cli-reference.md` — CLI command contracts with argument specs and output JSON

## Fallback Rule
If no specific CLI command matches, fall back to `skill-check` with the most appropriate attribute/skill and a GM-chosen difficulty. Never say "you can't do that" unless physically impossible.

## Every Action Is Mechanical
Every player action MUST map to a CLI command. `skill-check` is the universal fallback. There is no non-mechanical classification. Even passive actions (sitting, thinking, adjusting gear) use `skill-check` with DC 6 to feed the GM move system. See `references/action-classification.md` §Universal Mechanical Classification.
