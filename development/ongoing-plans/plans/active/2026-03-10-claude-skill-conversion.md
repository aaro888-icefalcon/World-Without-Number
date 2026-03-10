# Execution Plan: Convert WWN Engine to Claude Code Skill

- **Owner:** Development
- **Status:** Draft
- **Start Date:** 2026-03-10
- **Target Date:** TBD
- **Related Decision Logs:** N/A

## Objective

Convert the World Without Number RPG engine from a CLAUDE.md-driven project into a proper Claude Code skill (custom slash command). This gives the game a clean `/play` invocation, explicit mode switching between development and play, dynamic state injection at startup, auto-approved tool permissions for game scripts, and a path toward shareability as a standalone skill package.

## Background: Current vs. Target Architecture

### Current Architecture

The game runs via implicit CLAUDE.md loading:
1. User opens Claude Code in this repo
2. Root `CLAUDE.md` loads automatically, describes two modes (development/runtime)
3. User says something like "let's play" — Claude reads `runtime/CLAUDE.md`
4. Claude manually loads phase CLAUDE.md files, lore, state, etc. on each turn
5. No formal entry point — mode switching is conversational

### Target Architecture

The game runs via explicit skill invocation:
1. User types `/play` — SKILL.md loads GM instructions + dynamically injects current state
2. User types `/wwn-init` — SKILL.md loads character creation protocol
3. Supporting non-user-invocable skills provide rules, voice, and lore context on demand
4. `allowed-tools` auto-approves `emergence_cli.py` execution (no per-turn permission prompts)
5. Root CLAUDE.md remains for development mode only

## Scope

- In scope:
  - Create `/play` skill — main game loop entry point
  - Create `/wwn-init` skill — game initialization / character creation
  - Create supporting reference skills (rules, voice, lore) — non-user-invocable
  - Configure `allowed-tools` for game script execution
  - Use dynamic context injection (`!`command``) for state loading
  - Update root CLAUDE.md to reference skills instead of runtime/CLAUDE.md for play mode
  - Update `.claude/settings.json` if needed
  - Preserve all existing runtime functionality (scripts, phases, state management)
- Out of scope:
  - Changes to the Python scripts or game mechanics
  - Schema changes
  - New lore content
  - Making the skill work outside this repository (future goal)
  - Removing runtime/CLAUDE.md (kept as authoritative reference; skill distills it)

## Design

### Skill Architecture

```
.claude/skills/
├── play/                          # Main game skill
│   └── SKILL.md                   # GM instructions + dynamic state injection
├── wwn-init/                      # Character creation skill
│   └── SKILL.md                   # Interactive initialization protocol
├── wwn-rules/                     # Hard rules + GM protocol (reference)
│   └── SKILL.md                   # Non-user-invocable; Claude loads when needed
├── wwn-voice/                     # Narrative voice guide (reference)
│   └── SKILL.md                   # Non-user-invocable; Latter Earth voice
└── wwn-lore/                      # Lore loading instructions (reference)
    └── SKILL.md                   # Non-user-invocable; lore discovery protocol
```

### Skill 1: `/play` (Main Game Loop)

```yaml
---
name: play
description: Start or resume a World Without Number RPG session. Use when the player wants to play the game, take a turn, or continue an adventure.
allowed-tools: Bash(python runtime/scripts/emergence_cli.py *), Read, Glob, Grep
---
```

**Content includes:**
- Core GM identity and fidelity pledges (distilled from runtime/CLAUDE.md)
- Truth hierarchy (state.json > CLI output > hard rules > GM protocol)
- The 11-step turn loop (condensed but complete)
- Dynamic state injection via `!`python runtime/scripts/emergence_cli.py state-snapshot``
- References to supporting skills for rules, voice, and lore
- Anti-stagnation / scene pressure summary
- Phase pipeline summary with file paths for deeper loading

**Key design decisions:**
- SKILL.md stays under 500 lines — detailed reference stays in runtime/ phase files
- Dynamic context injection loads current state at invocation time, not stale
- `allowed-tools` eliminates per-turn permission prompts for CLI execution
- Claude still reads phase CLAUDE.md files as needed during turns (the skill doesn't replace phases, it bootstraps them)

### Skill 2: `/wwn-init` (Game Initialization)

```yaml
---
name: wwn-init
description: Create a new World Without Number character and start a new game. Use when starting fresh or creating a new character.
disable-model-invocation: true
allowed-tools: Bash(python runtime/scripts/emergence_cli.py *), Read, Write
---
```

**Content includes:**
- Interactive character creation protocol (from game-initialization.md)
- `query-chargen-options` integration for valid choices
- Step-by-step flow: concept → class/background → attributes → execute
- State template initialization
- Opening scene generation

### Skill 3: `wwn-rules` (Reference — Non-User-Invocable)

```yaml
---
name: wwn-rules
description: World Without Number hard rules, GM protocol, and action classification. Core mechanical reference for the RPG engine.
user-invocable: false
---
```

**Content includes:**
- All 13 hard rules (from hard-rules.md)
- GM protocol behavioral rules (from gm-protocol.md)
- Action classification routing table (from action-classification.md)
- Difficulty guidelines
- Combat, save, and skill check rules

### Skill 4: `wwn-voice` (Reference — Non-User-Invocable)

```yaml
---
name: wwn-voice
description: Latter Earth narrative voice guide for World Without Number. Tone, vocabulary, sensory palette, and word count rules.
user-invocable: false
---
```

**Content includes:**
- Latter Earth voice guide (from latter-earth-voice.md)
- Vocabulary preferences and avoidances
- Sentence rhythm rules
- Sensory palette
- Word count limits per action type

### Skill 5: `wwn-lore` (Reference — Non-User-Invocable)

```yaml
---
name: wwn-lore
description: Lore loading protocol for World Without Number. How to discover and load setting lore, nations, NPCs, and world state.
user-invocable: false
---
```

**Content includes:**
- Lore file discovery protocol (paths to lore directories)
- How to load contextual lore for current scene/region
- [UNKNOWN] element handling rules
- NPC voice card loading protocol
- Campaign-specific lore references

### Dynamic Context Injection

The `/play` skill uses backtick injection to load live state:

```markdown
## Current Game State
!`python runtime/scripts/emergence_cli.py state-snapshot 2>/dev/null || echo "No active game state — run /wwn-init to start"`
```

This gives Claude the current state snapshot every time `/play` is invoked, without manual file reading.

### CLAUDE.md Updates

Root CLAUDE.md gets a new section:

```markdown
## Play Mode

To play the game, use `/play`. To create a new character, use `/wwn-init`.
These skills load the full GM pipeline. Do not manually read runtime/CLAUDE.md for play sessions — the skills handle context loading.
```

The development mode instructions remain unchanged.

## Milestones

1. **M1: Core play skill** — `/play` SKILL.md created with GM instructions, turn loop, dynamic state injection
2. **M2: Init skill** — `/wwn-init` SKILL.md created with character creation protocol
3. **M3: Reference skills** — `wwn-rules`, `wwn-voice`, `wwn-lore` created as non-user-invocable references
4. **M4: Integration** — Root CLAUDE.md updated, settings.json updated if needed
5. **M5: Validation** — Skills load correctly, game plays through turn loop, existing tests pass

## Task Breakdown

- [ ] Create `.claude/skills/play/SKILL.md` — main game loop skill
- [ ] Create `.claude/skills/wwn-init/SKILL.md` — initialization skill
- [ ] Create `.claude/skills/wwn-rules/SKILL.md` — hard rules + GM protocol reference
- [ ] Create `.claude/skills/wwn-voice/SKILL.md` — narrative voice reference
- [ ] Create `.claude/skills/wwn-lore/SKILL.md` — lore loading reference
- [ ] Update root `CLAUDE.md` — add play mode skill references
- [ ] Update `.claude/settings.json` — add skill-related permissions if needed
- [ ] Verify dynamic context injection works (`state-snapshot` backtick execution)
- [ ] Smoke test: invoke `/play`, take a turn, verify turn loop executes correctly
- [ ] Smoke test: invoke `/wwn-init`, create a character, verify valid state.json
- [ ] Run existing tests: `python runtime/tests/run_all_tests.py 1`

## Validation

1. `/play` invocation loads GM context and current state without manual file reading
2. Turn loop executes all 11 steps correctly through the skill
3. `/wwn-init` produces schema-valid state.json via interactive flow
4. Reference skills are auto-loaded by Claude when relevant (not visible in `/` menu)
5. `emergence_cli.py` commands execute without per-turn permission prompts (via `allowed-tools`)
6. All existing tests pass (`python runtime/tests/run_all_tests.py 1`)
7. Development mode (root CLAUDE.md) still works independently of skills

## Risks and Mitigations

- **Risk:** SKILL.md exceeds 500-line recommendation, causing context bloat — **Mitigation:** Keep `/play` SKILL.md to essential GM instructions (~300 lines); delegate detailed rules to `wwn-rules` reference skill; Claude loads phase files on-demand during turns
- **Risk:** Dynamic context injection (`!`command``) fails or produces too much output — **Mitigation:** Use `state-snapshot` (compact format) rather than raw state.json; add `2>/dev/null` fallback for missing state
- **Risk:** Reference skills (non-user-invocable) not auto-loading when needed — **Mitigation:** Explicit cross-references in `/play` SKILL.md ("load wwn-rules for hard rules"); test auto-invocation with natural prompts
- **Risk:** `allowed-tools` pattern too permissive or too restrictive — **Mitigation:** Scope to exact `emergence_cli.py` pattern; test edge cases (validate scripts, state writes)
- **Risk:** Skill description budget exceeded with 5 skills — **Mitigation:** Keep descriptions concise; monitor with `/context`; reference skills have short descriptions
- **Risk:** Breaking existing development workflow — **Mitigation:** Root CLAUDE.md development mode unchanged; skills are additive, not replacing existing files

## Exit Criteria

1. Five skill files exist in `.claude/skills/` with correct frontmatter
2. `/play` loads GM context, injects state, and executes turn loop without manual file reading
3. `/wwn-init` creates valid characters through interactive flow
4. No per-turn permission prompts for `emergence_cli.py` during play
5. All existing tests pass
6. Root CLAUDE.md references skills for play mode
