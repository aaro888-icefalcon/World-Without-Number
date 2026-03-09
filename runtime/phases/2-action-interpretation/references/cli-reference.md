# CLI Reference — emergence_cli.py

Complete command contract for all registered subcommands. Phase 2 uses this to construct correct CLI invocations.

## Global Options

| Option | Type | Description |
|---|---|---|
| `--seed INT` | Optional | Set RNG seed for reproducible output. Record in turn receipt. |

## Commands

### `roll`

Roll dice using standard notation.

```
emergence_cli.py roll <expression> [--seed INT]
```

| Argument | Type | Required | Description |
|---|---|---|---|
| `expression` | positional string | Yes | Dice notation: `1d20+3`, `2d6`, `1d8-1`, `3d6` |

**Output JSON:**
```json
{
  "expression": "1d20+3",
  "rolls": [15],
  "modifier": 3,
  "total": 18,
  "arithmetic_trace": "[15]+3 = 18",
  "seed": 42
}
```

---

### `skill-check`

Make a 2d6 + skill + attribute modifier check against a difficulty target.

```
emergence_cli.py skill-check --attribute-mod INT --skill-level INT --difficulty INT [--seed INT]
```

| Argument | Type | Required | Description |
|---|---|---|---|
| `--attribute-mod` | int | Yes | Attribute modifier (-2 to +2) |
| `--skill-level` | int | Yes | Skill level (-1 unskilled to 4 master) |
| `--difficulty` | int | Yes | Target number (6-14) |

**Output JSON:**
```json
{
  "rolls": [3, 5],
  "modifier": 1,
  "total": 9,
  "arithmetic_trace": "[3+5]+1 = 9",
  "target": 8,
  "success": true,
  "margin": 1,
  "attribute_mod": 0,
  "skill_level": 1,
  "difficulty": 8,
  "seed": 42
}
```

---

### `save`

Make a saving throw (1d20 >= target).

```
emergence_cli.py save --type TYPE --level INT --modifier INT [--seed INT]
```

| Argument | Type | Required | Description |
|---|---|---|---|
| `--type` | choice | Yes | `physical`, `evasion`, or `mental` |
| `--level` | int | Yes | Character level |
| `--modifier` | int | Yes | Best relevant attribute modifier |

Save target = 16 - (level + modifier).

**Output JSON:**
```json
{
  "roll": 14,
  "target": 14,
  "success": true,
  "arithmetic_trace": "d20=[14] vs target 14",
  "save_type": "physical",
  "level": 1,
  "modifier": 1,
  "seed": 42
}
```

---

### `attack`

Resolve a combat attack (hit roll + damage or shock).

```
emergence_cli.py attack --attack-bonus INT --skill-level INT --attribute-mod INT \
    --weapon-damage STR --shock STR --target-ac INT --target-hp INT \
    [--killing-blow INT] [--seed INT]
```

| Argument | Type | Required | Description |
|---|---|---|---|
| `--attack-bonus` | int | Yes | Base attack bonus from class |
| `--skill-level` | int | Yes | Combat skill level (Stab, Shoot, Punch) |
| `--attribute-mod` | int | Yes | Relevant attribute modifier (Str for melee, Dex for ranged) |
| `--weapon-damage` | string | Yes | Damage die notation: `1d8`, `1d6+1` |
| `--shock` | string | No | Shock notation: `2/15` or `none` (default: `none`) |
| `--target-ac` | int | Yes | Defender's armor class |
| `--target-hp` | int | Yes | Defender's current HP |
| `--killing-blow` | int | No | Warrior Killing Blow bonus (default: 0) |

**Output JSON:**
```json
{
  "hit_roll": 15,
  "total_roll": 18,
  "attack_bonus_breakdown": "AB=1 + Skill=1 + Attr=1 = +3",
  "target_ac": 14,
  "natural_20": false,
  "natural_1": false,
  "hit": true,
  "damage": 7,
  "damage_roll": [5],
  "damage_trace": "1d8=5+1(attr)+1(KB) = 7",
  "shock_applied": false,
  "shock_damage": 0,
  "arithmetic_trace": "d20=[15]+3 = 18 → HIT! Damage: 1d8=5+1(attr)+1(KB) = 7",
  "target_hp_before": 8,
  "target_hp_after": 1,
  "target_down": false,
  "seed": 42
}
```

---

### `create-character`

Create a new WWN character.

```
emergence_cli.py create-character --name STR --class CLASS --background INT \
    [--method METHOD] [--seed INT]
```

| Argument | Type | Required | Description |
|---|---|---|---|
| `--name` | string | Yes | Character name |
| `--class` | choice | Yes | `warrior`, `expert`, or `mage` |
| `--background` | int | Yes | Background ID (1-20) |
| `--method` | choice | No | `standard_array` (default) or `roll_3d6` |

**Output JSON:** Complete character dict with all fields required by state.json `character` schema.

---

### `cast-spell`

Cast a spell using the Effort system.

```
emergence_cli.py cast-spell --spell-name STR --caster-level INT --tradition TRADITION \
    --current-effort INT --system-strain INT --system-strain-max INT [--seed INT]
```

| Argument | Type | Required | Description |
|---|---|---|---|
| `--spell-name` | string | Yes | Name of the spell to cast |
| `--caster-level` | int | Yes | Caster's character level |
| `--tradition` | choice | Yes | `high_magic`, `elementalist`, `necromancer`, or `healer` |
| `--current-effort` | int | Yes | Current uncommitted Effort |
| `--system-strain` | int | Yes | Current System Strain |
| `--system-strain-max` | int | Yes | Max System Strain (Constitution score) |

---

### `encounter`

Generate a random encounter for given terrain and threat level.

```
emergence_cli.py encounter --terrain TERRAIN --threat-level INT [--seed INT]
```

| Argument | Type | Required | Description |
|---|---|---|---|
| `--terrain` | choice | Yes | `forest`, `plains`, `mountains`, `desert`, `swamp`, `coast`, `ruins`, `urban`, `dungeon`, `wilderness` |
| `--threat-level` | int | Yes | Area threat level (1-10) |

---

### `travel`

Resolve multi-day overland travel with per-day events.

```
emergence_cli.py travel --terrain TERRAIN --days INT --supplies INT \
    [--forage-mod INT] [--threat-level INT] [--seed INT]
```

| Argument | Type | Required | Description |
|---|---|---|---|
| `--terrain` | choice | Yes | `road`, `plains`, `forest`, `hills`, `mountains`, `desert`, `swamp`, `coast`, `jungle` |
| `--days` | int | Yes | Number of days to travel |
| `--supplies` | int | Yes | Current ration count |
| `--forage-mod` | int | No | Wis/Survive modifier for foraging (default: 0) |
| `--threat-level` | int | No | Area threat level (default: 3) |

---

### `generate-scene`

Generate a playable scene seed from tags.

```
emergence_cli.py generate-scene --scene-type TYPE [--tag-count INT] [--threat-level INT] [--seed INT]
```

| Argument | Type | Required | Description |
|---|---|---|---|
| `--scene-type` | choice | Yes | `wilderness`, `ruin`, or `community` |
| `--tag-count` | int | No | Number of tags to combine (default: 2) |
| `--threat-level` | int | No | Overall threat level (default: 3) |

---

### `treasure`

Roll treasure by tier.

```
emergence_cli.py treasure --tier INT [--seed INT]
```

| Argument | Type | Required | Description |
|---|---|---|---|
| `--tier` | int | Yes | Treasure tier 1-5 |

---

### `world-tick`

Advance world state between sessions: process clocks, generate world pulse.

```
emergence_cli.py world-tick --days INT [--seed INT]
```

| Argument | Type | Required | Description |
|---|---|---|---|
| `--days` | int | Yes | Number of in-game days elapsed |

Reads `clocks` and `factions` from state.json automatically.

---

### `generate-npc`

Generate an NPC with voice card and personality.

```
emergence_cli.py generate-npc [--importance LEVEL] [--region STR] [--tags INT] [--seed INT]
```

| Argument | Type | Required | Description |
|---|---|---|---|
| `--importance` | choice | No | `minor` (default), `major`, or `faction_leader` |
| `--region` | string | No | Region name for flavor (default: `unknown`) |
| `--tags` | int | No | Number of character tags (default: 1) |

---

### `reaction-roll`

Roll NPC reaction (2d6 + modifier).

```
emergence_cli.py reaction-roll [--modifier INT] [--seed INT]
```

| Argument | Type | Required | Description |
|---|---|---|---|
| `--modifier` | int | No | Reaction modifier (default: 0) |

---

### `faction-turn`

Run a faction turn for all active factions in state.json.

```
emergence_cli.py faction-turn [--seed INT]
```

Reads factions from state.json automatically. Each faction selects an action based on archetype and power level, then rolls 2d6+power bonus to resolve.

---

### `level-up`

Advance a character to a target level.

```
emergence_cli.py level-up --name STR --class CLASS --current-level INT --target-level INT \
    --attributes JSON --hp-max INT --attack-bonus INT \
    [--tradition STR] [--partial-classes STR [STR ...]] [--seed INT]
```

| Argument | Type | Required | Description |
|---|---|---|---|
| `--name` | string | Yes | Character name |
| `--class` | choice | Yes | `warrior`, `expert`, `mage`, or `adventurer` |
| `--current-level` | int | Yes | Current character level |
| `--target-level` | int | Yes | Target level (2-10) |
| `--attributes` | JSON string | Yes | JSON dict of attribute scores |
| `--hp-max` | int | Yes | Current max HP |
| `--attack-bonus` | int | Yes | Current attack bonus |
| `--tradition` | string | No | Spellcasting tradition (for mages/partial mages) |
| `--partial-classes` | string list | No | Adventurer partial classes (e.g., `warrior mage`) |

**Output JSON:**
```json
{
  "character": { "...updated character dict..." },
  "changes": ["Level 2: gained 4 HP, AB now +1", "..."],
  "focus_picks_available": 1,
  "spell_advancement": null,
  "seed": 42
}
```

---

### `generate-dungeon`

Generate a procedural dungeon with rooms, encounters, and treasure.

```
emergence_cli.py generate-dungeon --depth INT [--theme STR] [--seed INT]
```

| Argument | Type | Required | Description |
|---|---|---|---|
| `--depth` | int | Yes | Dungeon depth level (1-5) |
| `--theme` | string | No | Dungeon theme (e.g., `tomb`, `mine`, `temple`, `sewer`) |

**Output JSON:**
```json
{
  "theme": "tomb",
  "depth": 3,
  "rooms": [
    {
      "id": 1,
      "type": "corridor",
      "encounter": null,
      "hazard": null,
      "treasure": null,
      "connections": [2],
      "is_boss": false
    }
  ],
  "room_count": 7,
  "seed": 42
}
```
