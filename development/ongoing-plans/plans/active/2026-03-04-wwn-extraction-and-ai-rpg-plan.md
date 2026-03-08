# Execution Plan: WWN PDF Extraction and AI RPG Implementation

- **Owner:** Development team
- **Status:** Draft
- **Start Date:** 2026-03-04
- **Target Date:** Phased (see milestones)
- **Related Decision Logs:** `analysis/2026-03-04-wwn-pdf-extraction-analysis.md`

---

# PART I: FULL EXTRACTION PLAN

## 1. Extraction Architecture

### Source Material Inventory (621 pages across 5 PDFs)

| PDF | Pages | Content Domain | Extraction Complexity |
|-----|-------|---------------|----------------------|
| WWN 1 | 66 | Core rules (Free Edition): attributes, skills, equipment, combat, travel, magic intro | Low — clean tabular data |
| WWN 2 | 67 | Magic system: 4 traditions, ~200 spells, arts, Workings, campaign setting intro, world-building tools (government, society, religion) | Medium — spell parsing, table interleaving |
| WWN 3 | 133 | Advanced world-building: communities, courts, ruins, wilderness tags, adventure creation, hex mapping, dungeons, treasures | Medium — heavy d-table extraction |
| WWN 4 | 133 | Bestiary (~80+ creatures), magic items, Blighted, demihumans, factions, Heroic classes, Legates, Iterums | Medium — stat block parsing |
| WWN 5 | 222 | Atlas (40+ nations), optional rules, new classes (Accursed, Bard, Mageslayer, Wise), naval combat, character tags, firearms, alchemy | Low-Medium — mostly prose lore |

### Extraction Pipeline

```
PDF → pdftotext -layout → raw .txt → ligature_fix.py → clean .txt → section_split.py → per-chapter .txt → content-type-specific parsers → target formats
```

### Target Formats by Content Type

| Content Type | Target Format | Target Location |
|-------------|--------------|-----------------|
| Rules prose | Markdown (.md) with §section anchors | `phases/*/references/` |
| d-tables (d4-d100) | Python dicts in .py files | `phases/3-resolution/skills/*/tables/` |
| Stat blocks (creatures) | JSON array | `phases/3-resolution/skills/combat/tables/bestiary.py` |
| Spell definitions | JSON objects | `phases/3-resolution/skills/core/tables/spells.py` |
| Equipment tables | Python dicts | `phases/3-resolution/skills/core/tables/equipment.py` |
| Class/progression tables | Python dicts | `phases/3-resolution/skills/core/tables/classes.py` |
| Focus definitions | Python dicts | `phases/3-resolution/skills/core/tables/foci.py` |
| Lore/setting text | Markdown | `phases/1-context-loading/lore/` |
| Tag databases | Python dicts with tag structure | `phases/3-resolution/skills/*/tables/` |
| Nation descriptions | Markdown per-nation | `phases/1-context-loading/lore/nations/` |

## 2. Extraction Steps (All PDFs)

### Step 1: Raw Text Extraction
```bash
for i in 1 2 3 4 5; do
  pdftotext -layout "WWN ${i}.pdf" "extracted/raw/wwn${i}_raw.txt"
done
```

### Step 2: Ligature Fixing
Build `scripts/ligature_fix.py` to handle:
- `#` → `fi` or `fl` (contextual — "a#re" → "afire", "#ght" → "fight", "#ame" → "flame")
- `%` → `ffi` ("di%cult" → "difficult")
- ToC-only number substitutions (decorative font artifacts)

### Step 3: Section Splitting
Split each cleaned file at major chapter boundaries into individual section files for targeted parsing.

### Step 4: Content-Type-Specific Parsing

**4a. Table Parser** — Regex-based extraction of d-tables:
```
Pattern: /^(\d+[-–]\d+|\d+)\s+(.+)$/
```
Outputs Python dicts: `{1: "Result text", 2: "Result text", ...}`

**4b. Stat Block Parser** — Extract creature stat blocks:
```
Pattern: /^(.+?)\s+(\d+)\s+(\d+)\s+([+\d x]+)\s+(.+?)\s+(.+?)\s+(\d+'.*?)\s+(\d+)\s+(\d+)\s+([+\d]+)\s+(\d+\+)$/
```
Outputs: `{"name": ..., "hd": ..., "ac": ..., "atk": ..., "dmg": ..., "shock": ..., "move": ..., "ml": ..., "inst": ..., "skill": ..., "save": ...}`

**4c. Spell Parser** — Extract spell entries:
```
Pattern: Header line with spell name + level, followed by description paragraphs until next spell header
```
Outputs: `{"name": ..., "level": ..., "tradition": ..., "duration": ..., "description": ...}`

**4d. Equipment Parser** — Weapon/armor table row extraction:
Already demonstrated to be excellent quality from WWN 1 analysis.

**4e. Focus Parser** — Level 1/Level 2 structured extraction with prerequisite parsing.

### Step 5: Placement into Phase Architecture

All extracted content placed per the phase-first model:

```
runtime/phases/
├── 1-context-loading/
│   ├── lore/
│   │   ├── latter-earth-overview.md          ← WWN 1 intro + WWN 2 setting
│   │   ├── history-and-ages.md               ← WWN 2, 5 timeline
│   │   ├── geography.md                      ← WWN 5 seas/mountains
│   │   └── nations/                          ← WWN 5 (40+ nation files)
│   │       ├── amundi-kingdoms.md
│   │       ├── atlantis.md
│   │       ├── ... (one per nation)
│   │       └── index.md
│   └── references/
│       ├── hard-rules.md                     ← WWN 1 core resolution
│       ├── gm-protocol.md                    ← WWN 1 GM guidance
│       ├── creation/
│       │   ├── character-creation.md         ← WWN 1 pp. 4-37
│       │   ├── backgrounds.md                ← WWN 1 pp. 11-17
│       │   └── classes.md                    ← WWN 1 pp. 18-21
│       └── species-and-origins.md            ← WWN 4 Blighted/demihumans
│
├── 2-action-interpretation/
│   └── references/
│       ├── action-classification.md          ← derived from combat/skill rules
│       └── cli-reference.md                  ← derived from implemented commands
│
├── 3-resolution/
│   └── skills/
│       ├── core/
│       │   ├── references/
│       │   │   ├── attributes-and-skills.md  ← WWN 1 pp. 8-10, 41
│       │   │   ├── saving-throws.md          ← WWN 1 p. 40
│       │   │   ├── character-advancement.md  ← WWN 1 pp. 54-55
│       │   │   └── magic-system.md           ← WWN 1 pp. 60-64, WWN 2
│       │   ├── scripts/
│       │   │   ├── dice.py                   ← core dice rolling
│       │   │   ├── character.py              ← character creation/advancement
│       │   │   └── conditions.py             ← status effects
│       │   └── tables/
│       │       ├── attributes.py             ← modifier table
│       │       ├── skills.py                 ← skill definitions
│       │       ├── equipment.py              ← weapons, armor, gear
│       │       ├── classes.py                ← progression tables
│       │       ├── backgrounds.py            ← background + skill tables
│       │       ├── foci.py                   ← focus definitions
│       │       └── spells.py                 ← all spell lists
│       │
│       ├── combat/
│       │   ├── references/
│       │   │   ├── combat-rules.md           ← WWN 1 pp. 42-48
│       │   │   ├── morale.md                 ← WWN 1 morale rules
│       │   │   └── mounted-combat.md         ← WWN 5 mounted rules
│       │   ├── scripts/
│       │   │   ├── combat.py                 ← attack resolution
│       │   │   └── behavior.py               ← creature AI/morale
│       │   └── tables/
│       │       ├── bestiary.py               ← all creature stat blocks
│       │       └── combat_actions.py         ← action type definitions
│       │
│       ├── exploration/
│       │   ├── references/
│       │   │   ├── travel-rules.md           ← WWN 1 pp. 49-53
│       │   │   ├── wilderness.md             ← WWN 3 wilderness rules
│       │   │   └── dungeon-crawl.md          ← WWN 3 site exploration
│       │   ├── scripts/
│       │   │   └── scene.py                  ← scene/encounter generation
│       │   └── tables/
│       │       ├── wilderness_tags.py        ← WWN 3 wilderness tags
│       │       ├── encounter_tables.py       ← wandering encounters
│       │       ├── ruin_tags.py              ← WWN 3 ruin tags
│       │       └── treasure_tables.py        ← WWN 3 treasure
│       │
│       ├── social/
│       │   ├── references/
│       │   │   ├── npc-reactions.md          ← WWN 1/4 reaction rules
│       │   │   ├── faction-rules.md          ← WWN 4 faction turn
│       │   │   └── court-intrigue.md         ← WWN 3 court rules
│       │   ├── scripts/
│       │   │   ├── npc.py                    ← NPC generation/reaction
│       │   │   └── faction.py                ← faction turn mechanics
│       │   └── tables/
│       │       ├── character_tags.py         ← WWN 5 character tags (d100)
│       │       ├── court_tags.py             ← WWN 3 court tags
│       │       └── faction_actions.py        ← WWN 4 faction action tables
│       │
│       ├── downtime/
│       │   ├── references/
│       │   │   ├── healing-rules.md          ← WWN 1 p. 48
│       │   │   ├── crafting.md               ← WWN 1 pp. 56-58
│       │   │   └── workings.md               ← WWN 2 Working creation
│       │   └── tables/
│       │       ├── alchemy_recipes.py        ← WWN 5 mundane alchemy
│       │       └── crafting_costs.py         ← WWN 1 crafting tables
│       │
│       └── world-building/
│           ├── references/
│           │   ├── government.md             ← WWN 2 government types
│           │   ├── society.md                ← WWN 2 society construction
│           │   └── religion.md               ← WWN 2 religion generation
│           ├── scripts/
│           │   ├── world_tick.py             ← world state advancement
│           │   └── moves.py                  ← GM moves generator
│           └── tables/
│               ├── government_tables.py      ← WWN 2 government d-tables
│               ├── society_tables.py         ← WWN 2 society d-tables
│               ├── religion_tables.py        ← WWN 2 religion d-tables
│               ├── community_tags.py         ← WWN 3 community tags
│               └── hex_tables.py             ← WWN 3 hex generation
│
├── 4-narrative/
│   ├── references/
│   │   ├── narration-mappings.md             ← derived from WWN tone
│   │   └── latter-earth-voice.md             ← WWN 1, 5 prose style guide
│   └── assets/
│       ├── character-sheet-template.md
│       └── scene-template.md
│
├── 5-persistence/
│   └── (existing state management)
│
└── 6-validation/
    └── (existing validators)
```

## 3. Weakness Analysis — Extraction Plan v1

| # | Weakness | Severity | Root Cause |
|---|----------|----------|------------|
| W1 | **Ligature fixing is lossy** — `#` could be `fi` or `fl`; automated fixing will produce errors in edge cases ("re#ne" could be "refine" or "refline") | Medium | PDF encoding strips ligature metadata |
| W2 | **Two-column interleaving** — even with `-layout`, some pages merge columns, producing garbled paragraphs | Medium | pdftotext layout heuristics break on decorative RPG layouts |
| W3 | **Spell parsing accuracy** — spell effects often contain conditional logic and duration clauses that resist regex extraction | High | Natural language complexity |
| W4 | **No validation pipeline** — extracted data has no automated check against source | High | Missing verification tooling |
| W5 | **Scope too broad** — extracting all 621 pages before implementing any CLI commands means nothing is playable for a long time | High | Waterfall extraction approach |
| W6 | **Free vs Deluxe edition gap** — WWN 1 only has 64 pages of the full ~400-page core rules; many systems referenced in ToC are absent | Critical | Edition limitation |
| W7 | **Tag structures vary** — community tags, court tags, ruin tags, wilderness tags all have different internal structures (some have Enemies/Friends/Complications/Things/Places, others don't) | Medium | Inconsistent source format |
| W8 | **No incremental testing** — no way to verify extracted tables work until scripts are built | Medium | Tooling gap |

## 4. Fixed Extraction Plan v2

### Fixes Applied

| Weakness | Fix |
|----------|-----|
| W1 (ligatures) | Use dictionary-based ligature replacement: maintain a wordlist of known RPG/WWN terms; only replace `#` when the resulting word is in the dictionary. Flag ambiguous cases for human review. |
| W2 (columns) | Extract once with `-layout`, once without. Compare outputs. For pages where `-layout` garbles, use the non-layout version. Build a per-page quality score. |
| W3 (spell parsing) | Don't regex-parse spell effects. Store spell descriptions as full-text strings in JSON. The LLM can interpret spell effects at runtime — that's what it's good at. Only extract structured metadata (name, level, tradition, duration keyword). |
| W4 (no validation) | Build `validate_extraction.py` that counts expected items per table and verifies key fields are non-null. Cross-reference total counts against known PDF content (e.g., "22 skills expected, 22 found"). |
| W5 (scope too broad) | **Vertical slice approach**: extract one complete playable slice first (core mechanics + 1 scene type + basic combat), make it functional, then expand. |
| W6 (Free Edition gap) | WWN 2-5 ARE the Deluxe content. The full rules are spread across all 5 PDFs. WWN 1 (Free) covers character creation + core rules, which is the most critical extraction target. Higher-level spells, bestiary, factions, etc. are in WWN 2-4. No gap. |
| W7 (tag structures) | Normalize all tag types to a common schema: `{name, description, enemies, friends, complications, things, places}`. Omit fields that don't apply rather than force-fitting. |
| W8 (no incremental testing) | Each extraction batch comes with a smoke test: `python -c "from tables.equipment import WEAPONS; assert len(WEAPONS) == 28"` |

### Revised Extraction Order (Vertical Slice)

**Slice 1: "First Combat"** (makes basic play possible)
1. Core tables: attributes, skills, equipment, classes, backgrounds, foci
2. Combat rules reference doc
3. Basic combat scripts: dice.py, combat.py (attack resolution)
4. State schema v7: add WWN character attributes
5. Character creation script
6. 10 basic creatures from bestiary

**Slice 2: "First Spell"** (adds magic)
7. All spell lists (High Magic, Elementalist, Necromancer, Healer)
8. Arts definitions
9. Effort/System Strain mechanics
10. Magic system reference doc

**Slice 3: "First Journey"** (adds exploration)
11. Travel rules + overland encounter tables
12. Wilderness tags (full extraction)
13. Scene generation script
14. Site/dungeon exploration rules
15. Treasure tables

**Slice 4: "First Kingdom"** (adds social/political layer)
16. Faction system rules + faction action tables
17. NPC generation + character tags
18. Court tags
19. Community tags
20. World-building generation tables (government, society, religion)

**Slice 5: "The World"** (adds full setting)
21. All nation descriptions (40+ nations from WWN 5)
22. History/timeline
23. Geography
24. Remaining bestiary

**Slice 6: "Advanced Play"**
25. Optional classes (Accursed, Bard, Mageslayer, Wise)
26. Heroic classes + Legates
27. Naval combat
28. Mundane alchemy + firearms
29. Workings (grand magic)

---

# PART II: IMPLEMENTATION OF EXTRACTION (SLICE 1)

## Implemented Artifacts

The following extraction artifacts are created as part of this plan execution:

1. `extracted/raw/` — raw text dumps from all 5 PDFs
2. `runtime/phases/3-resolution/skills/core/tables/attributes.py` — attribute modifier table
3. `runtime/phases/3-resolution/skills/core/tables/skills.py` — 22 skills with descriptions
4. `runtime/phases/3-resolution/skills/core/tables/equipment.py` — weapons, armor, gear
5. `runtime/phases/3-resolution/skills/core/tables/classes.py` — class progression tables
6. `runtime/phases/3-resolution/skills/core/tables/backgrounds.py` — 20 backgrounds with growth/learning tables
7. `runtime/phases/3-resolution/skills/core/tables/foci.py` — all focus definitions
8. `runtime/phases/1-context-loading/references/hard-rules.md` — core resolution rules
9. `runtime/phases/3-resolution/skills/combat/references/combat-rules.md` — combat procedure

---

# PART III: INTEGRATED AI RPG IMPLEMENTATION PLAN

## 1. Vision

Transform the extracted WWN content into a fully functional AI-driven RPG where an LLM serves as Game Master, using the 6-phase deterministic pipeline to ensure mechanical fidelity while delivering rich narrative experiences.

## 2. Architecture Overview

```
Player Input (natural language)
    │
    ▼
┌──────────────────────────────────────────────────────┐
│ Phase 1: CONTEXT LOADING                              │
│  • Load state.json (character, world, scene)          │
│  • Load relevant lore/references for current region   │
│  • Load active faction clocks and world pulse         │
└──────────────┬───────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────┐
│ Phase 2: ACTION INTERPRETATION                        │
│  • LLM classifies player intent                       │
│  • Maps to CLI command(s): attack, skill_check,       │
│    cast_spell, travel, faction_turn, etc.              │
│  • Validates action is legal given current state       │
└──────────────┬───────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────┐
│ Phase 3: MECHANICAL RESOLUTION (deterministic)        │
│  • Execute emergence_cli.py subcommand                │
│  • Python scripts roll dice, calculate damage,        │
│    resolve skill checks, determine loot, etc.          │
│  • Output: structured JSON with all results           │
│  • Seeds recorded for reproducibility                 │
└──────────────┬───────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────┐
│ Phase 4: NARRATIVE TRANSLATION (LLM creative)        │
│  • LLM receives mechanical results as structured JSON │
│  • Translates into vivid prose matching Latter Earth   │
│    voice: archaic, melancholy, wondrous               │
│  • Forced consequences narrated exactly as given      │
│  • Player character sheet and scene rendered           │
└──────────────┬───────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────┐
│ Phase 5: STATE PERSISTENCE                            │
│  • Update state.json with all changes                 │
│  • Advance clocks per events                          │
│  • Record turn receipt                                │
└──────────────┬───────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────┐
│ Phase 6: VALIDATION                                   │
│  • Validate state.json against schema                 │
│  • Verify turn receipt completeness                   │
│  • Response gate: ensure all required elements present │
└──────────────────────────────────────────────────────┘
```

## 3. Core Implementation Milestones

### M1: Deterministic Engine Core
- `emergence_cli.py` with subcommands: `roll`, `attack`, `skill-check`, `save`, `damage`
- `dice.py` with seedable RNG
- `combat.py` with full attack resolution (hit roll, damage, shock, morale)
- `character.py` with creation and advancement
- State schema v7 with WWN character attributes

### M2: Magic System
- Spell preparation/casting commands
- Effort tracking
- Arts execution
- All tradition spell lists loaded

### M3: Exploration Engine
- Travel mechanics (time, encounters, foraging)
- Scene/encounter generation from tables
- Dungeon/site crawl system
- Treasure determination

### M4: Social/Faction System
- NPC generation and reaction rolls
- Faction turn automation
- Court intrigue mechanics
- Diplomacy and standing tracking

### M5: World Simulation
- World tick (between-session world advancement)
- Clock system integration (faction clocks, threat clocks, meta clocks)
- Event generation from tables
- News/rumor generation for world pulse

### M6: Narrative Layer
- Latter Earth voice guide
- Narration mappings (mechanical result → narrative treatment)
- Scene rendering templates
- Character sheet display format

## 4. Weakness Analysis — AI RPG Plan v1

| # | Weakness | Severity | Impact |
|---|----------|----------|--------|
| P1 | **Context window pressure** — loading full state + lore + rules + spell lists for every turn will exceed LLM context limits | Critical | Turns fail or context truncated, losing critical state |
| P2 | **Action interpretation ambiguity** — player intent mapping to CLI commands is the hardest AI task; "I want to sneak past the guards" could be Sneak check, Exert check, or complex multi-step sequence | High | Wrong mechanics applied, breaking player trust |
| P3 | **Narrative consistency** — LLM has no long-term memory beyond state.json; NPCs will behave inconsistently across sessions | High | Immersion breaking, world feels random |
| P4 | **Combat pacing** — deterministic combat with individual initiative and per-round resolution will be extremely slow when narrated by LLM | Medium | Tedious combat encounters |
| P5 | **Faction turn automation** — WWN faction turns happen between sessions with complex multi-faction interactions; automating this is a significant engineering challenge | Medium | Faction system unusable |
| P6 | **Player agency vs. determinism tension** — rigid CLI execution may feel overly mechanical; players expect some narrative flexibility | Medium | Game feels like a calculator, not an RPG |
| P7 | **Error recovery** — when state.json becomes inconsistent (and it will), there's no rollback mechanism | High | Corrupted game state, campaign lost |
| P8 | **Lore hallucination** — LLM will "know" things about WWN from training data that contradict the extracted canonical references | High | Incorrect world details narrated |

## 5. Fixed AI RPG Plan v2

| Weakness | Fix |
|----------|-----|
| P1 (context pressure) | **Tiered context loading**: Phase 1 loads only relevant subset — current scene's region lore, active NPC data, applicable rules for scene type. Use `index.md` files as routing tables. Cap Phase 1 context to ~2000 tokens of lore + current state. Spell lists stay on disk; only load when casting. |
| P2 (action ambiguity) | **Intent confirmation loop**: After Phase 2 classification, present the interpreted action back to the player: "You want to make a Dex/Sneak check (difficulty 8) to slip past the guards. Confirm?" Player confirms or corrects before Phase 3 executes. |
| P3 (narrative consistency) | **NPC memory in state.json**: Each `known_npc` entry gets `personality_traits`, `speech_patterns`, `last_interaction_summary`, `relationship_arc` fields. LLM reads these before generating NPC dialogue. |
| P4 (combat pacing) | **Batch combat resolution**: For multi-enemy fights, resolve all enemy actions in a single CLI call. Present results as one narrative block. Only pause for player input between rounds, not between individual enemy turns. |
| P5 (faction turns) | **Simplified faction tick**: Run faction turns as a single CLI command that processes all factions, outputs a summary of changes. LLM narrates the results as rumors/news in the world pulse. |
| P6 (agency vs. determinism) | **Narrative latitude zones**: Phase 4 has explicit latitude rules — flavor text and scene description are LLM-creative; mechanical outcomes (damage numbers, status effects, death) are BINDING. The LLM has creative freedom in HOW it describes the hit, not WHETHER the hit lands. |
| P7 (error recovery) | **State snapshots**: Auto-backup state.json at session start and every 10 turns. `emergence_cli.py rollback <snapshot>` command for recovery. Turn receipts serve as audit trail. |
| P8 (lore hallucination) | **Lore grounding protocol**: Phase 1 loads canonical lore text; Phase 4 narration must reference only loaded lore. Hard rule: "If a fact is not in the loaded context, do not assert it. Say the character doesn't know." |

---

# PART IV: TENETS AND CONSTRAINTS

## 6. Key Tenets of Narrative and Good Story

### T1: Consequences Matter
Every player choice must have meaningful downstream effects. The world remembers. An insulted noble becomes a future antagonist. A saved village sends aid later. State.json's chronicle and clocks are the mechanism — they ensure consequences persist.

### T2: Tension Requires Uncertainty
Good stories need moments where the outcome is genuinely unknown. The deterministic dice system provides this — the LLM must NOT pre-determine outcomes or telegraph results. Build tension in narration BEFORE revealing the mechanical result.

### T3: The World Has Its Own Agenda
The world does not exist to serve the player. Factions pursue their goals. NPCs have motivations independent of the PC. The clock system and world pulse ensure the world moves forward even when the player does nothing. This creates urgency and the feeling of a living world.

### T4: Show, Don't Tell
Narration should reveal world state through sensory detail, NPC behavior, and environmental cues — not exposition dumps. "The market stalls are half-empty and the merchants eye you with suspicion" is better than "The town's prosperity rating is Low."

### T5: Pacing Is Structure
A good session alternates tension and release: exploration → discovery → danger → resolution → reflection. The scene type system (combat/exploration/social/downtime/travel) should naturally cycle. Don't let the player stay in one mode too long without prompting a shift.

### T6: Characters Are Defined by What They Do Under Pressure
The most memorable RPG moments come from hard choices. Present genuine dilemmas where mechanical optimization conflicts with narrative/moral considerations. "You can take the treasure, but the village will starve."

### T7: Mystery Drives Engagement
The Latter Earth is ancient and unknowable. Not everything should be explained. Ruins should hold unanswered questions. Creature origins should be ambiguous. This creates the drive to explore.

### Plan Adjustments for Narrative Tenets

| Tenet | Implementation Change |
|-------|----------------------|
| T1 (consequences) | Add `consequence_tracker` to state.json: array of pending consequences with trigger conditions and timers. Phase 5 checks triggers each turn. |
| T2 (tension) | Phase 4 narration protocol: describe the attempt BEFORE revealing the mechanical result. "You leap across the chasm, fingers reaching for the far edge—" [then reveal success/failure]. |
| T3 (world agenda) | World tick runs at session start AND every in-game week. Faction clocks advance automatically. World pulse generates news. Hidden clocks create events the player hasn't anticipated. |
| T4 (show don't tell) | Narration mappings must translate mechanical states into sensory descriptions. Threat levels become environmental descriptions. HP loss becomes visible injuries. Economy stats become market descriptions. |
| T5 (pacing) | Add `scene_rhythm` tracker to campaign state. If 3+ consecutive scenes are the same type, generate a narrative prompt to shift mode (e.g., after 3 combats, create a social/rest opportunity). |
| T6 (hard choices) | Adventure generation includes dilemma templates. Each dungeon/quest should include at least one genuine moral choice with mechanical trade-offs on both sides. |
| T7 (mystery) | Lore docs include `[UNKNOWN]` markers for deliberately unexplained phenomena. LLM narrates these as genuine mysteries, never inventing explanations. |

## 7. Key Tenets of Good Game Mastering

### G1: Be a Fan of the Player Character
The GM is not the player's adversary. Root for the PC to succeed — but let the dice be honest. Present challenges that are tough but fair. Celebrate player creativity.

### G2: Say "Yes, and..." When Possible
If a player's proposed action is creative and plausible, find a way to adjudicate it even if no exact rule exists. Use the skill check system as the universal resolver. Only say "no" to actions that are physically impossible or would break the game.

### G3: Prepare Situations, Not Plots
Don't script a narrative railroad. Set up a situation (factions in conflict, dungeon full of treasure, NPC with a problem) and let the player's choices determine what happens. Clocks drive the world; the player drives the story.

### G4: Make Failure Interesting
A failed roll should never result in "nothing happens." Failed skill checks should introduce complications, reveal information, or create new problems. A failed combat isn't just "you miss" — it's "your blade slides off the creature's carapace and sparks illuminate a passage behind it."

### G5: Telegraph Danger
Never surprise-kill the player. If a situation is lethal, give warning signs: bones scattered outside the cave, NPCs who tried and failed, environmental hazards that hint at danger. The player should be able to make an informed choice about risk.

### G6: The Rule of Three
Offer roughly three options/directions at any major decision point. One obvious, one creative, one dangerous. This prevents paralysis while preserving agency.

### G7: Keep the Pace Moving
Don't over-describe. Don't belabor transitions. Get to the interesting part. If the player says "I go to the market," don't narrate the walk there unless something happens on the way.

### Plan Adjustments for GM Tenets

| Tenet | Implementation Change |
|-------|----------------------|
| G1 (be a fan) | GM protocol in Phase 1 references explicitly sets the LLM's disposition as "enthusiastic but honest narrator." Never punish creative play. |
| G2 (yes, and) | Phase 2 action interpretation: if no CLI command matches, fall back to generic `skill-check` with GM-chosen difficulty. Never respond with "you can't do that" unless physically impossible. |
| G3 (situations, not plots) | Campaign arcs in state.json define SITUATIONS (faction goals, threats, ticking clocks), never scripted plot beats. The LLM must not railroad toward predetermined outcomes. |
| G4 (interesting failure) | Add `failure_consequences` table to each skill domain. Combat miss → flavor text plus minor complication. Skill check failure → partial information or new obstacle. Never "nothing happens." |
| G5 (telegraph danger) | Threat levels in scenes must be narrated as environmental cues before combat begins. Creature difficulty ratings translate to sensory warnings. |
| G6 (rule of three) | Phase 4 narration: when presenting an open scene, always suggest at least 2-3 visible options/directions through environmental description. |
| G7 (keep pace) | Hard rule: narration blocks capped at ~150 words for routine events. Full-length narration only for combat outcomes, dramatic moments, and scene transitions. |

## 8. Key Tenets of World-Building

### W1: Internal Consistency Over Novelty
The world must follow its own rules. If magic requires Effort, that applies to everyone — PCs and NPCs. If a nation is poor, its soldiers have poor equipment. Consistency builds trust.

### W2: History Creates Geography Creates Culture
Every nation's culture should flow logically from its geography and history. Coastal nations trade and build ships. Nations near the Anak Wastes are militaristic. Former colonies resent their parent empire. The WWN setting already embodies this — preserve it.

### W3: Scale Creates Wonder
The Latter Earth is inconceivably old. Empires have risen and fallen so many times that their ruins form geological strata. This scale is what makes exploration compelling — every ruin could contain technology from a completely alien civilization.

### W4: Scarcity Drives Conflict
Resources, knowledge, and safety are scarce in the Latter Earth. This scarcity is what motivates adventuring. Don't undermine it with easy access to healing, wealth, or information.

### W5: Every Place Should Feel Distinct
Nations and regions need personality. The Amundi Kingdoms feel different from Atlantis which feels different from the Scarlet Princes. Use language, naming conventions, cultural values, and physical description to make each place memorable.

### W6: The Map Has Blank Spaces
Not everything is known. The wilderness between settlements is genuinely dangerous and unknown. This creates space for discovery and adventure.

### Plan Adjustments for World-Building Tenets

| Tenet | Implementation Change |
|-------|----------------------|
| W1 (consistency) | NPC stat blocks use the same class/skill system as PCs. Magic rules apply universally. Economy uses the same silver-piece standard everywhere. |
| W2 (history→culture) | Nation files in `lore/nations/` include a "Cultural Implications" section linking geography/history to present culture. LLM references this when narrating. |
| W3 (scale) | Ruin generation tables include era tags (First Age, Second Age, etc.) that determine technology level and aesthetic. Narration treats ancient ruins with appropriate awe. |
| W4 (scarcity) | Healing is slow (System Strain limits magical healing). Treasure is rare but valuable. Shops have limited inventory. Encumbrance matters. Don't hand-wave logistics. |
| W5 (distinct places) | Each nation file includes: voice notes (how NPCs from here speak), sensory palette (what the region looks/smells/sounds like), cultural dos/don'ts. Phase 4 loads these when narrating scenes in that region. |
| W6 (blank spaces) | Hex map generation leaves ~40% of hexes as "unexplored." Wilderness encounters are generated procedurally, not pre-scripted. |

## 9. Limitations of AI in Running Games — Analysis and Adjustments

### L1: Context Window Limits
**Limitation:** LLMs can only process ~100-200K tokens at once. A full game state + rules + lore + conversation history will eventually exceed this.

**Impact:** Loss of earlier events, inconsistent behavior, forgotten NPCs and plot threads.

**Mitigation:**
- State.json is the persistent memory. Everything important goes into structured state.
- Chronicle entries summarize past events so the LLM doesn't need to remember conversation history.
- Tiered context loading: only load what's relevant to the current scene.
- Session summaries generated at session end and stored in state.json.
- **New plan element:** Add `session_summary` field to campaign state. At session end, LLM generates a 200-word summary that captures key events, decisions, and unresolved threads. This is loaded at next session start.

### L2: No True Reasoning About Game State
**Limitation:** LLMs approximate reasoning but make logical errors, especially with complex multi-step chains (e.g., "if the enemy is bloodied AND has morale < 7 AND allies are dead, then they flee").

**Impact:** Incorrect tactical decisions, wrong rule applications, missed trigger conditions.

**Mitigation:**
- This is exactly why the CLI exists. ALL conditional logic lives in Python scripts, not in the LLM's "reasoning."
- Complex NPC behavior trees are deterministic code, not LLM improvisation.
- Morale checks, reaction rolls, and trigger conditions are CLI commands.
- **New plan element:** Build `behavior.py` with a decision tree engine for creature combat AI. Input: creature stats + battlefield state. Output: chosen action. The LLM never decides what enemies do tactically.

### L3: Hallucination of Facts
**Limitation:** LLMs confidently assert false information, including "facts" about game worlds they've been trained on.

**Impact:** Contradicts canonical setting, introduces nonexistent spells/items/locations, breaks immersion for players who know the source material.

**Mitigation:**
- Lore grounding protocol (see P8 fix above).
- Hard rule: LLM may only reference lore loaded in Phase 1 context. If asked about something not in context, the in-world answer is "Your character doesn't know."
- All spell effects, item properties, and creature abilities come from extracted data tables, not LLM knowledge.
- **New plan element:** Add a Phase 6 validation step: `validate-narration-grounding` that flags any proper nouns in the narration that don't appear in the loaded context.

### L4: Poor Numerical Reasoning
**Limitation:** LLMs are unreliable at arithmetic, probability estimation, and tracking multiple simultaneous numerical values.

**Impact:** Wrong damage calculations, incorrect HP tracking, bad resource management.

**Mitigation:**
- ALL arithmetic happens in Python. The LLM never adds, subtracts, or compares numbers directly.
- State.json tracks all numerical values; the LLM reads but never manually calculates them.
- CLI output includes pre-computed values: "Target takes 7 damage (1d8+2=7). HP: 15→8."
- **New plan element:** CLI output format standardized: always include human-readable arithmetic trace so the LLM can narrate the exact numbers.

### L5: Difficulty with Long-Term Planning
**Limitation:** LLMs can't maintain a coherent multi-session narrative arc without external structure.

**Impact:** Stories feel episodic and disconnected. Foreshadowing doesn't pay off. Villain plans don't escalate logically.

**Mitigation:**
- Campaign arcs defined in state.json with structured beats and progress markers.
- Clock system provides mechanical structure for long-term plot progression.
- Faction goals and methods persist in state, creating emergent long-term narrative.
- **New plan element:** Add `arc_beats` array to campaign_arcs: `[{beat_name, trigger_condition, status, payoff_description}]`. Phase 1 loads the current arc and checks if any beat trigger conditions are met.

### L6: Inconsistent Character Voice
**Limitation:** LLMs struggle to maintain distinct voices for multiple NPCs across conversations.

**Impact:** All NPCs sound the same. Recurring characters feel like strangers.

**Mitigation:**
- Each known_npc entry includes `speech_patterns` (e.g., "speaks in third person, uses nautical metaphors"), `personality_traits` (e.g., "cautious, dry humor"), and `key_phrases` (1-2 signature expressions).
- Phase 4 narration explicitly loads NPC voice data before generating dialogue.
- **New plan element:** NPC voice cards: each NPC gets a 2-3 sentence voice prompt loaded into context when they speak.

### L7: Tendency Toward Dramatic Escalation
**Limitation:** LLMs are trained on fiction that trends toward dramatic climaxes. Left unchecked, every session escalates to world-ending stakes.

**Impact:** Scope creep, loss of groundedness, player fatigue.

**Mitigation:**
- GM protocol explicitly caps threat escalation per session.
- Scene rhythm tracker prevents consecutive high-drama scenes.
- Most encounters should be mundane challenges (bandits, terrain, resource management), not cosmic threats.
- **New plan element:** Add `drama_budget` to session state. Each "dramatic escalation" costs points. When budget is spent, remaining encounters are lower-stakes until next session.

### L8: Cannot Track Spatial Relationships
**Limitation:** LLMs have no spatial reasoning. They can't track who is where on a battle map, how far apart things are, or whether a character has line of sight.

**Impact:** Incoherent combat descriptions, impossible physical actions, spatial contradictions.

**Mitigation:**
- Combat state tracks positions abstractly using zones (melee, ranged, cover) rather than grid positions.
- CLI manages zone membership and validates movement/range.
- **New plan element:** Define 4 abstract combat zones: `melee` (adjacent), `near` (30'), `far` (100'), `distant` (300'+). Creatures are in zones. Movement actions change zones. Range checks are zone-based.

---

# PART V: OPTIMIZED FINAL PLAN

## 10. Constraint Integration Matrix

Every plan element must satisfy constraints from ALL four tenet categories. Here's the cross-reference:

| Plan Element | Narrative | GM | World-Building | AI Limitation |
|-------------|-----------|-----|----------------|---------------|
| Deterministic CLI | T2 (honest uncertainty) | G1 (fair dice) | W1 (consistency) | L2, L4 (offload reasoning/math) |
| Tiered context loading | T4 (relevant detail) | G7 (keep pace) | W5 (distinct places) | L1 (context limits) |
| Intent confirmation | T6 (informed choice) | G2 (yes and) | — | L2 (prevent misinterpretation) |
| NPC voice cards | T4 (show don't tell) | G1 (be a fan) | W5 (distinct places) | L6 (consistent voice) |
| Clock system | T3 (world agenda) | G3 (situations) | W4 (scarcity) | L5 (long-term structure) |
| Zone-based combat | T2 (tactical tension) | G5 (telegraph danger) | — | L8 (no spatial reasoning) |
| Consequence tracker | T1 (consequences matter) | G4 (interesting failure) | W1 (consistency) | L1 (persistent memory) |
| Session summaries | — | — | W2 (historical continuity) | L1 (context), L5 (long-term) |
| Behavior trees | T3 (world agenda) | G1 (fair enemies) | W1 (consistency) | L2 (deterministic AI) |
| Drama budget | T5 (pacing) | G7 (keep pace) | W4 (grounded stakes) | L7 (prevent escalation) |
| Lore grounding | T7 (mystery) | G5 (honest info) | W6 (blank spaces) | L3 (prevent hallucination) |
| Batch combat | T5 (pacing) | G7 (keep pace) | — | L4 (reduce math) |

## 11. Final Optimized Implementation Plan

### Phase A: Foundation (Extraction + Engine Core)

**Goal:** Extract WWN core data, build deterministic engine, create first playable character.

**Deliverables:**
1. All core tables extracted: attributes, skills, equipment, classes, backgrounds, foci
2. `dice.py` — seedable dice roller
3. `character.py` — character creation (attribute generation, background, class, focus selection)
4. `combat.py` — attack resolution (hit roll, damage, shock, morale check)
5. `conditions.py` — status effects and System Strain
6. State schema v7 — WWN character (6 attributes, HP, AC, attack bonus, skills, equipment, effort, system strain, class features)
7. `hard-rules.md` — core resolution mechanics (skill checks, saves, combat flow)
8. `gm-protocol.md` — GM behavioral rules (be a fan, yes-and, telegraph danger, interesting failure)
9. `validate_extraction.py` — smoke tests for extracted data integrity
10. Zone-based combat position tracking in combat state

**Acceptance criteria:**
- `emergence_cli.py roll 1d20+3` works with seed
- `emergence_cli.py create-character` generates a valid WWN character
- `emergence_cli.py attack --attacker X --defender Y` resolves fully
- `validate_state.py` passes on a state.json with a created character
- All extracted tables have smoke test counts matching expected values

### Phase B: Magic + Bestiary

**Goal:** Extract all spell data, implement spellcasting, populate bestiary.

**Deliverables:**
1. All spell lists extracted: High Magic (5 levels), Elementalist, Necromancer, Healer arts
2. `magic.py` — spell preparation, casting, effort management
3. `bestiary.py` — full creature stat block database with behavior trees
4. `behavior.py` — deterministic creature combat AI (decision tree: flee/attack/special/defend based on stats + battlefield state)
5. Combat expanded: multi-creature resolution, batch enemy turns
6. Encounter generation: random encounter from tables + creature instantiation

**Acceptance criteria:**
- `emergence_cli.py cast-spell --spell "The Coruscating Coffin" --caster X --target Y` resolves
- `emergence_cli.py encounter --terrain forest --threat 3` generates valid encounter
- Behavior tree produces consistent actions for same inputs

### Phase C: Exploration + World

**Goal:** Build travel system, extract exploration tables, create living world.

**Deliverables:**
1. Travel rules: overland movement, foraging, privation, supply tracking
2. Wilderness tags, ruin tags, community tags extracted as Python table databases
3. `scene.py` — scene generation from tags + encounter tables
4. `world_tick.py` — between-session world advancement (faction clocks, event generation, world pulse)
5. Treasure tables extracted and wired to dungeon/ruin exploration
6. Hex exploration system: reveal hexes, track explored vs. unexplored
7. Session summary generation (auto-generated at session end, stored in state)
8. Scene rhythm tracker to manage pacing

**Acceptance criteria:**
- `emergence_cli.py travel --from A --to B --days 3` resolves with encounters, foraging, time tracking
- `emergence_cli.py world-tick` advances all faction clocks and generates world pulse
- `emergence_cli.py generate-scene --type ruin --tags 2` produces playable scene seed

### Phase D: Social + Factions

**Goal:** Build NPC system, faction turn, social mechanics.

**Deliverables:**
1. NPC generation with character tags (d100 table), voice cards, motivation
2. Reaction roll system
3. Faction turn system (all faction actions, costs, requirements, outcomes)
4. Court intrigue mechanics
5. PC standing tracking (reputation per faction)
6. Consequence tracker in state.json
7. Diplomacy/persuasion skill check framework
8. Arc beats system for campaign narrative structure

**Acceptance criteria:**
- `emergence_cli.py generate-npc --importance major` creates NPC with voice card, tags, motivation
- `emergence_cli.py faction-turn` processes all active factions
- `emergence_cli.py reaction-roll --npc X` resolves NPC disposition

### Phase E: Narrative Layer

**Goal:** Build the LLM-facing layer that translates mechanics to story.

**Deliverables:**
1. `latter-earth-voice.md` — prose style guide extracted from WWN 1/5 narrative voice
2. `narration-mappings.md` — mechanical result → narrative treatment rules
3. Character sheet display template
4. Scene rendering template
5. NPC dialogue protocol (load voice card → generate in-character speech)
6. Failure consequence flavor tables per domain
7. Drama budget system
8. Narration grounding validator (Phase 6)
9. Threat level → environmental description mappings

**Acceptance criteria:**
- Phase 4 produces consistently toned narration for combat, exploration, social scenes
- NPC dialogue uses loaded voice card patterns
- Narration grounding check catches hallucinated proper nouns

### Phase F: Atlas + Full Setting

**Goal:** Extract and integrate the complete Latter Earth setting.

**Deliverables:**
1. 40+ nation files in `lore/nations/` with: history, culture, geography, sensory palette, voice notes, adventure hooks
2. History/timeline document
3. Geographic reference (seas, mountains, regions)
4. Languages reference
5. Region-specific encounter tables
6. Cultural knowledge base for LLM context loading

**Acceptance criteria:**
- Phase 1 can load appropriate nation lore for any canonical location
- Narration reflects regional cultural distinctions

### Phase G: Advanced Systems

**Goal:** Extend with optional content.

**Deliverables:**
1. Optional classes: Accursed, Bard, Mageslayer, Wise
2. Heroic classes + Legates (high-level play)
3. Naval combat system
4. Mundane alchemy + primitive firearms
5. Workings (grand magic)
6. Low/no-magic campaign variant rules

**Acceptance criteria:**
- All optional classes can be created and used in play
- Naval combat resolves through CLI

---

## 12. Summary of All Plan Adjustments

### Changes from Narrative Tenets:
- Added consequence_tracker to state.json
- Phase 4 narration reveals results AFTER describing the attempt
- World tick runs proactively to create living world feel
- Narration mappings translate stats to sensory descriptions
- Scene rhythm tracker manages pacing
- Adventure generation includes dilemma templates
- `[UNKNOWN]` markers in lore preserve mystery

### Changes from GM Tenets:
- GM protocol sets LLM disposition as "enthusiastic but honest"
- Generic skill-check fallback for unmapped actions
- Campaign arcs define situations, never scripted plots
- Failure consequence tables ensure "failure is interesting"
- Threat levels narrated as environmental cues
- Narration suggests 2-3 options through environmental description
- Routine narration capped at ~150 words

### Changes from World-Building Tenets:
- NPCs use same mechanical system as PCs
- Nation files include Cultural Implications section
- Ruin generation tags include era markers
- Healing is mechanically slow (System Strain)
- Region-specific sensory palettes and voice notes
- 40% of hex map left unexplored for discovery

### Changes from AI Limitations:
- Tiered context loading (cap at ~2000 tokens lore per turn)
- Session summaries for memory persistence
- Behavior tree engine for creature AI (no LLM tactical decisions)
- Lore grounding validator catches hallucinated content
- ALL math in Python, never LLM
- Arc beats provide long-term narrative structure
- NPC voice cards maintain character consistency
- Drama budget prevents escalation
- Zone-based abstract combat replaces grid positioning
- CLI output includes arithmetic traces for narration

---

## 13. Risk Register

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Extraction errors in spell/stat data | High | Medium | Smoke test counts + human spot-check of 10% sample |
| State schema grows too complex | Medium | High | Keep schema versioned; only add fields when implementing the feature that needs them |
| Combat feels too slow/mechanical | Medium | High | Batch resolution + narration pacing rules; playtest early |
| Faction system too complex for single-player | Medium | Medium | Start with simplified faction tick; add complexity only if needed |
| LLM narration quality degrades with long sessions | High | Medium | Session summaries + context pruning; encourage natural session breaks |
| Player finds deterministic system too rigid | Medium | High | Intent confirmation loop gives player agency; "yes, and" fallback |

## 14. Exit Criteria (Full Project)

1. A player can create a WWN character through AI-guided character creation
2. Combat with multiple enemies resolves deterministically and narrates fluidly
3. Spellcasting works for at least High Magic tradition
4. Overland travel between settlements generates encounters and manages resources
5. NPCs have consistent personalities across sessions
6. Faction clocks advance the world between sessions
7. The Latter Earth setting is narrated with consistent voice and accurate lore
8. State can be rolled back to any session-start snapshot
9. All mechanical outcomes come from CLI, never LLM improvisation
10. A 5-session playtest campaign completes without state corruption
