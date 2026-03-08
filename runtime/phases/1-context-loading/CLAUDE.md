# Phase 1 — Context Loading

Load game state, scene, lore, and world context before any action interpretation.

## When This Phase Runs
- Start of every turn
- Start of every session
- When setting up a new game

## Mandatory Steps
1. Read `state.json` — character, scene, world, clocks, chronicle
2. Read current scene context from `current_scene` in state
3. Load hard rules and GM protocol (always-load references)
4. Load lore per `skills/lore-loading.md`:
   - Always load: `lore/latter-earth-overview.md`, `lore/history-and-ages.md`
   - Region-specific: `lore/nations/<region_id>.md` based on `current_scene.region_id`
   - Context budget: ~2000 tokens of lore per turn (max 5000)
5. Check `campaign_arcs[].beats` for any triggered beat conditions
6. Check `consequence_tracker` for pending consequences that should fire

## Key Resources
- `references/hard-rules.md` — non-negotiable mechanical contract (10 rules)
- `references/gm-protocol.md` — GM behavioral rules, narrative voice, pacing
- `skills/lore-loading.md` — lore selection and context budget rules
- `lore/` — world setting, geography, nations, languages
- `lore/nations/` — 57 nation files with §-anchored sections

## NYC Campaign — Additional Lore
When `current_scene.region_id` starts with `carven-peaks`, load NYC-specific cross-cutting lore:
- `lore/nyc-factions.md` — internal factions, boroughs, power blocs (always-load for carven-peaks)
- `lore/nyc-situation.md` — dynamic start situation and timeline pressures (session-start load)
- `lore/gallery-system.md` — 9-level gallery dungeon reference (load when in galleries)
- `lore/nyc-magic.md` — magic manifestation and attunement (load for magic scenes)
- `lore/imperator.md` — caged entity and surge dynamics (load for gallery/surge scenes)

## [UNKNOWN] Convention
Lore documents include `[UNKNOWN]` for deliberately unexplained phenomena. When encountering these markers, narrate as genuine mystery — never invent explanations. See `skills/lore-loading.md` for details.
