# WWN PDF Content Analysis and Extraction Strategy

**Date:** 2026-03-04
**Purpose:** Analyze the five WWN PDFs and recommend extraction strategies that align with the repo's phase-first architecture and development principles.

---

## 1. PDF Inventory

| PDF | Pages | Size | Primary Content |
|-----|-------|------|-----------------|
| WWN 1.pdf | 66 | 15.6 MB | Core rules: character creation, combat, skills, equipment, travel, magic foundations, spell system |
| WWN 2.pdf | 67 | 13.4 MB | Magic traditions (High Mage, Elementalist, Necromancer, Healer, Vowed), spell lists, Workings, magic items, campaign setting lore (Latter Earth history), campaign creation tools |
| WWN 3.pdf | 133 | 10.5 MB | World-building tools: government, society, religion, ruins, communities, courts, wilderness tags, adventure creation, hex mapping |
| WWN 4.pdf | 133 | 11.6 MB | Creatures/bestiary, magic items (weapons, armor, grimoires, calyxes, exemplars), Blighted species, demihumans, factions, Heroic classes, Legates, GM tools |
| WWN 5.pdf | 222 | 24.7 MB | Atlas of the Western Latter Earth: 40+ nations/regions with full lore, new classes (Accursed, Bard, Mageslayer, Wise), optional rules, naval combat, firearms, character tags |

**Total:** 621 pages, ~75.8 MB

---

## 2. Content Categories and Data Types

### 2a. Structured Mechanical Data (high extraction priority)

These are tables, formulas, and stat blocks with regular structure that map directly to CLI scripts and JSON schemas.

| Data Type | Found In | Estimated Count | Target Format |
|-----------|----------|-----------------|---------------|
| Attribute modifiers | WWN 1 | 1 table | JSON lookup / Python dict |
| Skill list + descriptions | WWN 1 | ~30 skills | JSON array |
| Equipment (weapons, armor) | WWN 1 | ~50 items | JSON arrays with properties (dmg, shock, AC, traits) |
| Spell lists (High Magic) | WWN 1, 2 | ~60 spells across 5 levels | JSON per-spell with level, name, description, effects |
| Elementalist spells | WWN 2 | ~55 spells | Same as above |
| Necromancer spells | WWN 2 | ~55 spells | Same as above |
| Creature stat blocks | WWN 4 | ~80+ creatures | JSON with HD, AC, Atk, Dmg, Shock, Move, ML, Inst, Skill, Save |
| Magic item tables | WWN 4 | ~40 tables | JSON lookup tables |
| Background tables | WWN 1 | ~20 backgrounds | JSON with skill grants, equipment |
| Focus (feat) definitions | WWN 1, 5 | ~40+ foci | JSON with level-1 and level-2 effects |
| Random generation tables | WWN 3, 4 | ~200+ d-tables | Python dicts keyed by die range |
| Class progression tables | WWN 1, 4 | ~10 classes | JSON with per-level HD, attack bonus, abilities |
| Faction action tables | WWN 4 | ~20 actions | JSON with cost, requirements, effects |
| Ship stat blocks | WWN 5 | ~15 ships | JSON with hull, crew, weapons, speed |

### 2b. Semi-Structured Reference Text (medium extraction priority)

Prose rules with embedded mechanical specifics. Requires human-guided extraction.

| Data Type | Found In | Target Format |
|-----------|----------|---------------|
| Combat rules (initiative, actions, shock, morale) | WWN 1 | Markdown reference docs with section anchors |
| Magic system rules (preparation, casting, effort, arts) | WWN 1, 2 | Markdown reference docs |
| Travel and exploration rules | WWN 1 | Markdown reference docs |
| Healing, system strain, encumbrance | WWN 1 | Markdown reference docs |
| Working creation rules | WWN 2 | Markdown reference docs |
| Faction turn rules | WWN 4 | Markdown reference docs |
| Mass combat rules | WWN 4 (if present) | Markdown reference docs |

### 2c. Lore and Narrative Content (lower extraction priority for mechanics, high for context-loading)

| Data Type | Found In | Target Format |
|-----------|----------|---------------|
| Latter Earth setting overview | WWN 1, 2 | Markdown lore docs |
| History (Ages, sorcerer-kings, Outsiders) | WWN 2, 5 | Markdown timeline + lore docs |
| Nation/region descriptions (40+ nations) | WWN 5 | Per-nation markdown files or structured JSON |
| Religion descriptions | WWN 3 | Markdown reference docs |
| Community/court/ruin/wilderness tags | WWN 3 | JSON tag databases with descriptions and effects |
| Blighted species lore | WWN 4 | Markdown lore + JSON stat integration |
| Demihuman descriptions | WWN 4 | Markdown lore + JSON stat integration |

---

## 3. Extraction Quality Assessment

### What `pdftotext` handles well:
- **Prose text**: clean extraction with minor OCR-like artifacts (e.g., `#` for `fi` ligatures, some letter substitutions like `0` for `o` in headers)
- **Simple tables**: one-column d-tables extract readably
- **Stat blocks**: multi-column stat blocks extract with layout mode (`-layout` flag) preserving column alignment
- **Spell summaries**: one-line spell descriptions in table-of-contents format extract cleanly

### What `pdftotext` struggles with:
- **Multi-column layouts**: the two-column page format causes interleaving of left and right columns in default mode; `-layout` mode helps but isn't perfect
- **Complex tables**: multi-column tables with aligned numeric data sometimes merge or misalign
- **Special characters**: `fi`, `fl`, `ff` ligatures render as `#` or other symbols; some diacritics are lost
- **Page headers/footers**: page numbers and section headers inject into the text flow
- **Decorative elements**: sidebar boxes, callout text, and art captions mix into body text

### Character encoding issues observed:
- `#` appears where `fi` or `fl` ligatures should be (e.g., "#ght" = "fight", "#rst" = "first")
- Numbers substitute for letters in some headers (e.g., "Cha,acte, C,eation" = "Character Creation")
- Some special quote marks and dashes render inconsistently

---

## 4. Extraction Strategies

### Strategy A: Batch `pdftotext` + AI Post-Processing (Recommended for Phase 1)

**Approach:** Extract all text via `pdftotext -layout`, then use Claude or similar LLM to clean, structure, and categorize the content into target formats.

**Pros:**
- Fast initial extraction (~90,000 lines total across all 5 PDFs)
- No external dependencies beyond poppler-utils (already installed)
- AI post-processing can fix ligature issues, parse tables, and restructure into JSON/markdown
- Works entirely within the existing repo toolchain

**Cons:**
- Requires manual verification of extracted tables and stat blocks
- Two-column layout interleaving needs careful handling
- Large context windows needed for full-page table extraction

**Steps:**
1. Extract raw text: `pdftotext -layout "WWN X.pdf" wwn-X-raw.txt` for each PDF
2. Split by chapter/section using header patterns
3. AI-assisted cleanup: fix ligatures, parse tables into JSON, structure rules into markdown
4. Human review of mechanical data (stat blocks, spell effects, damage formulas)
5. Place into phase-appropriate directories per repo architecture

### Strategy B: PDF-to-Structured via Python Libraries

**Approach:** Use `pdfplumber` or `camelot` for table-aware extraction, plus `pdftotext` for prose.

**Pros:**
- Better table extraction with cell-level precision
- Can detect and extract tables separately from prose
- Programmatic, repeatable pipeline

**Cons:**
- Requires installing additional Python packages (`pdfplumber`, `pandas`)
- These PDFs are image-heavy RPG books; table detection may be unreliable
- More complex pipeline to build and maintain
- The PDF structure (decorative, two-column, mixed art) may defeat automated table detectors

**Steps:**
1. Install: `pip install pdfplumber pandas`
2. Write extraction scripts per content type (tables vs. prose vs. stat blocks)
3. Run and validate per-PDF
4. Post-process into target formats

### Strategy C: Manual Chapter-by-Chapter Extraction (Most Accurate, Most Labor-Intensive)

**Approach:** Read each PDF chapter visually, manually transcribe structured data into target formats, use `pdftotext` only for bulk prose.

**Pros:**
- Highest accuracy for complex tables and stat blocks
- Can make editorial decisions about what to include/exclude in real-time
- No tooling issues

**Cons:**
- Extremely time-consuming for 621 pages
- Not scalable or repeatable
- Prone to transcription errors on large numeric tables

### Strategy D: Hybrid Pipeline (Recommended Overall)

**Approach:** Combine Strategies A and B based on content type.

| Content Type | Extraction Method | Post-Processing |
|-------------|-------------------|-----------------|
| Prose rules/lore | `pdftotext -layout` | AI cleanup (fix ligatures, format as markdown) |
| Simple d-tables (d4, d6, d8, d12, d20) | `pdftotext -layout` | Regex parsing + AI validation |
| Stat block tables | `pdftotext -layout` | AI-assisted parsing into JSON, human verification |
| Spell lists | `pdftotext` (default mode) | AI parsing into per-spell JSON records |
| Complex multi-column tables | `pdfplumber` (if available) or visual reading | Manual verification required |
| Equipment/weapon tables | `pdftotext -layout` | Regex + AI parsing into JSON arrays |

---

## 5. Target Placement (Phase Mapping)

Per the repo's phase-first architecture, extracted content maps to:

### Phase 1 — Context Loading
| Content | Source PDF | Target Path |
|---------|-----------|-------------|
| Latter Earth setting lore | WWN 1 (pp. 94-113), WWN 2 (pp. 55-66), WWN 5 (all) | `phases/1-context-loading/lore/` |
| Hard rules (core resolution, saves, checks) | WWN 1 (pp. 38-57) | `phases/1-context-loading/references/hard-rules.md` |
| GM protocol | WWN 1, WWN 3 | `phases/1-context-loading/references/gm-protocol.md` |
| Character creation rules | WWN 1 (pp. 4-37) | `phases/1-context-loading/references/creation/` |
| Species/ancestry data | WWN 4 (Blighted, Demihumans) | `phases/1-context-loading/references/` |

### Phase 2 — Action Interpretation
| Content | Source PDF | Target Path |
|---------|-----------|-------------|
| Action classification rules | WWN 1 (combat actions, skill checks) | `phases/2-action-interpretation/references/` |
| CLI command mapping | derived from all | `phases/2-action-interpretation/references/cli-reference.md` |

### Phase 3 — Mechanical Resolution (6 Domains)
| Domain | Content | Source PDF | Target Path |
|--------|---------|-----------|-------------|
| **core** | Dice, attributes, skill checks, saves, conditions, character progression | WWN 1 | `skills/core/references/`, `skills/core/scripts/`, `skills/core/tables/` |
| **combat** | Initiative, attack rolls, shock, morale, special actions, creature behavior | WWN 1, WWN 4 | `skills/combat/references/`, `skills/combat/scripts/`, `skills/combat/tables/` |
| **exploration** | Travel, foraging, wandering encounters, dungeon crawling, hex exploration | WWN 1 | `skills/exploration/references/`, `skills/exploration/tables/` |
| **social** | NPC reactions, faction turns, faction actions, morale, diplomacy | WWN 4 | `skills/social/references/`, `skills/social/scripts/`, `skills/social/tables/` |
| **downtime** | Healing, crafting, research, Workings, magic item creation | WWN 1, WWN 2 | `skills/downtime/references/`, `skills/downtime/tables/` |
| **world-building** | Government, society, religion, community, ruin, wilderness generation | WWN 3 | `skills/world-building/tables/`, `skills/world-building/references/` |

### Phase 4 — Narrative Translation
| Content | Source PDF | Target Path |
|---------|-----------|-------------|
| Tone and style (Latter Earth voice) | WWN 1 (intro), WWN 5 | `phases/4-narrative/references/` |
| Narration mappings (mechanical result → narrative) | derived | `phases/4-narrative/references/narration-mappings.md` |

---

## 6. Extraction Priority Order

Based on what the engine needs to become functional:

### Priority 1 — Core Mechanics (enable basic play)
1. Attribute system, modifiers, skill list → `core/tables/`
2. Equipment tables (weapons, armor) → `core/tables/`
3. Combat rules (attack, damage, shock, initiative, actions) → `combat/references/` + `combat/scripts/`
4. Hit dice, saving throws, class progression → `core/tables/`
5. Character creation flow → `1-context-loading/references/creation/`

### Priority 2 — Magic System (enable spellcasting)
6. High Magic spell list (all 5 levels) → `core/tables/` or new `magic/` domain
7. Elementalist + Necromancer spell lists → same
8. Arts (per-tradition abilities) → `core/tables/`
9. Effort and spell preparation rules → `core/references/`

### Priority 3 — World Interaction (enable exploration + social)
10. Creature stat blocks (bestiary) → `combat/tables/`
11. NPC reaction + morale rules → `social/references/`
12. Travel + exploration rules → `exploration/references/`
13. Wandering encounter tables → `exploration/tables/`

### Priority 4 — Generation Tools (enable world-building)
14. Random generation tables (government, society, religion, etc.) → `world-building/tables/`
15. Community/court/ruin/wilderness tags → `world-building/tables/`
16. Faction system → `social/scripts/` + `social/tables/`

### Priority 5 — Lore + Setting (enable immersive play)
17. Latter Earth overview + history → `1-context-loading/lore/`
18. Nation descriptions (WWN 5) → `1-context-loading/lore/`
19. Tone/voice guide for narrative phase → `4-narrative/references/`

### Priority 6 — Advanced/Optional (extend gameplay)
20. Heroic classes, Legates → `core/tables/`
21. Workings (grand magic) → `downtime/references/`
22. Magic item creation rules → `downtime/references/`
23. Naval combat → `combat/references/` (optional sub-domain)
24. Optional rules (firearms, alchemy, etc.) → per-domain

---

## 7. Ligature Fix Map

The following substitutions are needed during post-processing of `pdftotext` output:

| Raw Output | Correct Text |
|-----------|--------------|
| `#` (in word context) | `fi` or `fl` (contextual) |
| `,` (in header context) | various letters (OCR artifact from decorative fonts) |
| `0` (in header context) | `o` (OCR artifact) |
| `%` (in word context) | `ffi` (triple ligature) |

A regex-based cleaner can handle ~90% of these; AI post-processing handles the rest.

---

## 8. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Table extraction errors (wrong numbers in stat blocks) | Broken combat math | Human verification of all numeric tables before integration into scripts |
| Ligature artifacts in rule text | Confusing or incorrect rule references | Automated ligature fixer + manual spot-check |
| Copyright/licensing concerns | Legal risk | Keep extracted content as game-reference material only; do not redistribute raw text |
| Scope explosion (621 pages) | Never-ending extraction | Follow priority order strictly; each priority level is a separate PR |
| Two-column interleaving | Garbled paragraphs | Use `-layout` flag; split pages manually where interleaving occurs |

---

## 9. Recommended Next Steps

1. **Create a `pdftotext` extraction script** that dumps each PDF to raw text with layout preservation
2. **Build a ligature-fixer utility** (Python script, ~20 lines) to clean the most common artifacts
3. **Extract Priority 1 content** (core mechanics) as the first PR — this touches state schema, `core/` domain, and `combat/` domain (2 major surfaces, within scope rules)
4. **Validate extracted tables** against the PDF visually before committing
5. **Wire each extraction batch** into the phase architecture per the change-integration-checklist
