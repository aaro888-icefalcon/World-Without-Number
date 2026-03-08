# Lore Loading — Context Selection Skill

This skill governs how lore is loaded during Phase 1 based on the current scene context.

## When This Runs

- Every turn during Phase 1 (Context Loading)
- When the current scene's region changes
- At session start

## Loading Rules

### Always Load (Core Context)

These files are loaded every turn as background context:
- `lore/latter-earth-overview.md` — world primer
- `lore/history-and-ages.md` — timeline and ages (summary only)

### Region-Specific Loading

Based on `current_scene.region_id` in state.json:

1. **Primary region**: Load `lore/nations/<region_id>.md` — full content
2. **Adjacent regions**: If the narrative references a neighboring region, load its `§sensory-palette` and `§voice-notes` sections only
3. **Unknown regions**: If `region_id` is not recognized or file doesn't exist, use generic Latter Earth description

### Context Budget

- **Target**: ~2000 tokens of lore per turn
- **Maximum**: 5000 tokens (only for lore-heavy scenes like first arrival in a new region)
- If context exceeds budget, prioritize: sensory palette > culture > history > geography

### Loading Procedure

```
1. Read current_scene.region_id from state.json
2. Load always-load files
3. If region_id maps to a nation file:
   a. Load the full nation file
   b. Extract §sensory-palette for narrative voice
   c. Extract §voice-notes for NPC dialogue
4. If region_id is unknown:
   a. Use generic Latter Earth description
   b. Mark narration with [UNKNOWN] where specific details would go
5. Check world.known_regions[] — player has visited these, may reference them
```

## [UNKNOWN] Marker Convention

Lore documents include `[UNKNOWN]` for deliberately unexplained phenomena:
- When the GM encounters `[UNKNOWN]`, narrate as genuine mystery
- Never invent explanations for `[UNKNOWN]` elements
- In-world responses: "None can say," "The scholars disagree," "That knowledge was lost with the Prior Ages"
- The mystery IS the content — preserving it is more important than filling gaps

## Lore Grounding (Hard Rule #10)

The LLM may only reference lore loaded in Phase 1 context:
- If a player asks about something not in loaded context → "Your character doesn't know"
- If a player asks about something marked [UNKNOWN] → "Rumors suggest..." or "None living can say"
- Never hallucinate setting details — the world is defined by its documents
