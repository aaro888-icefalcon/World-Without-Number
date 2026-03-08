# Phase 4 — Narrative Translation

Translate CLI mechanical results into immersive Latter Earth narrative.

## When This Phase Runs
- After CLI execution (Phase 3) returns mechanical results
- Before state persistence (Phase 5)

## Mandatory Steps
1. Read CLI JSON output — these are mechanical facts (binding)
2. Describe the attempt BEFORE revealing the result (tension principle)
3. Translate outcomes into narrative per `references/narration-mappings.md`
4. Apply Latter Earth voice: archaic, melancholy, wondrous, tinged with decay
5. On failure: always narrate a complication, never "nothing happens"
6. On forced consequences: narrate EXACTLY as determined, no softening
7. End with a player prompt ("What do you do?" or equivalent)

## Key References
- `references/narration-mappings.md` — treatment rules by mechanic type, word count guidelines
- `references/latter-earth-voice.md` — tone, vocabulary, sentence rhythm, sensory palette
- `references/threat-environment-mapping.md` — threat level to environmental description mapping
- `references/npc-dialogue-protocol.md` — NPC dialogue generation steps (voice derivation, trust gates, continuity)
- `assets/character-sheet-template.md` — end-of-turn character sheet display format
- `assets/scene-template.md` — scene rendering template (location, threat, NPCs, objectives)
- `tables/failure_flavors.py` — failure complication flavor text by domain

## Word Count Guidelines
- Routine action: ~100 words (max 150)
- Combat round: ~150 words (max 200)
- Major story moment: ~200 words (max 300)
- Transition: ~50 words (max 100)
