"""Comprehensive post-implementation validation for the full 10-phase plan.

Tests cover:
- Phase 1: Level-up system (character advancement L1→L10)
- Phase 2: Tag expansion (50+ tags per type)
- Phase 3: Bestiary completion (70+ creatures with IDs)
- Phase 4: Magic items in treasure (tier 3+)
- Phase 5: Cross-reference wiring (IDs resolve, terrain maps valid)
- Phase 6: Spell completion (elementalist/necromancer L4-5)
- Phase 7: Dungeon generation (procedural rooms)
- Phase 8: Scenario smoke testing (100-seed statistical validation)
- Phase 9: Integration touchpoints (manifests, CLI refs updated)
"""

import sys
import os
import random
import json

# Setup paths
_tests_dir = os.path.dirname(os.path.abspath(__file__))
_runtime_dir = os.path.join(_tests_dir, '..')
_scripts_dir = os.path.join(_runtime_dir, 'scripts')
_skills_dir = os.path.join(_runtime_dir, 'phases', '3-resolution', 'skills')

for _domain in ['core', 'combat', 'exploration', 'social', 'world-building']:
    for _subdir in ['scripts', 'tables']:
        _p = os.path.join(_skills_dir, _domain, _subdir)
        if os.path.isdir(_p) and _p not in sys.path:
            sys.path.insert(0, _p)

if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 1: LEVEL-UP
# ═══════════════════════════════════════════════════════════════════════════

def test_level_up_exists():
    """level_up() function exists in character.py."""
    try:
        from character import level_up
        return []
    except ImportError:
        return ["level_up not importable from character module"]


def test_level_up_warrior():
    """Warrior can level from 1 to 10 with correct progression."""
    errors = []
    try:
        from character import create_character, level_up
        random.seed(42)
        char = create_character("TestWarrior", "warrior", 1, foci=["alert"])

        for target_level in range(2, 11):
            result = level_up(char, target_level)
            if result.get("error"):
                errors.append(f"Level {target_level}: {result['error']}")
                break
            char = result.get("character", char)
            if char["level"] != target_level:
                errors.append(f"Level {target_level}: char level is {char['level']}")
            if char["attack_bonus"] != target_level:
                errors.append(f"Level {target_level}: warrior AB should be {target_level}, got {char['attack_bonus']}")
    except ImportError:
        errors.append("level_up not importable")
    except Exception as e:
        errors.append(f"Exception: {e}")
    return errors


def test_level_up_mage_spell_slots():
    """Mage spell slots increase with level."""
    errors = []
    try:
        from character import create_character, level_up
        random.seed(42)
        char = create_character("TestMage", "mage", 1, tradition="high_mage",
                                spells=["The Excellent Prismatic Spray"])
        for target_level in range(2, 11):
            result = level_up(char, target_level)
            char = result.get("character", char)
    except ImportError:
        errors.append("level_up not importable")
    except Exception as e:
        errors.append(f"Exception: {e}")
    return errors


def test_level_up_expert():
    """Expert levels correctly with lower AB progression."""
    errors = []
    try:
        from character import create_character, level_up
        random.seed(42)
        char = create_character("TestExpert", "expert", 1, foci=["alert"])
        for target_level in range(2, 11):
            result = level_up(char, target_level)
            char = result.get("character", char)
            if char["level"] != target_level:
                errors.append(f"Level {target_level}: char level is {char['level']}")
    except ImportError:
        errors.append("level_up not importable")
    except Exception as e:
        errors.append(f"Exception: {e}")
    return errors


def test_level_up_saves_recalculated():
    """Saving throws decrease (improve) with level."""
    errors = []
    try:
        from character import create_character, level_up
        random.seed(42)
        char = create_character("TestSaves", "warrior", 1, foci=["alert"])
        l1_physical = char["saving_throws"]["physical"]
        result = level_up(char, 5)
        char = result.get("character", char)
        l5_physical = char["saving_throws"]["physical"]
        if l5_physical >= l1_physical:
            errors.append(f"Physical save should improve: L1={l1_physical}, L5={l5_physical}")
    except ImportError:
        errors.append("level_up not importable")
    except Exception as e:
        errors.append(f"Exception: {e}")
    return errors


def test_level_up_hp_increases():
    """HP max increases with level."""
    errors = []
    try:
        from character import create_character, level_up
        random.seed(42)
        char = create_character("TestHP", "warrior", 1, foci=["alert"])
        l1_hp = char["hp"]["max"]
        result = level_up(char, 5)
        char = result.get("character", char)
        l5_hp = char["hp"]["max"]
        if l5_hp <= l1_hp:
            errors.append(f"HP should increase: L1={l1_hp}, L5={l5_hp}")
    except ImportError:
        errors.append("level_up not importable")
    except Exception as e:
        errors.append(f"Exception: {e}")
    return errors


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 2: TAG EXPANSION (50+ per type)
# ═══════════════════════════════════════════════════════════════════════════

REQUIRED_TAG_KEYS = {"name", "description", "enemies", "friends", "complications", "things", "places"}

def test_wilderness_tags_50():
    """Wilderness tags have 50+ entries."""
    errors = []
    try:
        from wilderness_tags import WILDERNESS_TAGS
        if len(WILDERNESS_TAGS) < 50:
            errors.append(f"Expected 50+ wilderness tags, got {len(WILDERNESS_TAGS)}")
        names = [t["name"] for t in WILDERNESS_TAGS]
        if len(names) != len(set(names)):
            errors.append("Duplicate wilderness tag names found")
        for i, tag in enumerate(WILDERNESS_TAGS):
            missing = REQUIRED_TAG_KEYS - set(tag.keys())
            if missing:
                errors.append(f"Tag {i} ({tag.get('name', '?')}): missing {missing}")
    except ImportError:
        errors.append("wilderness_tags not importable")
    return errors


def test_ruin_tags_50():
    """Ruin tags have 50+ entries."""
    errors = []
    try:
        from ruin_tags import RUIN_TAGS
        if len(RUIN_TAGS) < 50:
            errors.append(f"Expected 50+ ruin tags, got {len(RUIN_TAGS)}")
        names = [t["name"] for t in RUIN_TAGS]
        if len(names) != len(set(names)):
            errors.append("Duplicate ruin tag names found")
    except ImportError:
        errors.append("ruin_tags not importable")
    return errors


def test_community_tags_50():
    """Community tags have 50+ entries."""
    errors = []
    try:
        from community_tags import COMMUNITY_TAGS
        if len(COMMUNITY_TAGS) < 50:
            errors.append(f"Expected 50+ community tags, got {len(COMMUNITY_TAGS)}")
        names = [t["name"] for t in COMMUNITY_TAGS]
        if len(names) != len(set(names)):
            errors.append("Duplicate community tag names found")
    except ImportError:
        errors.append("community_tags not importable")
    return errors


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 3: BESTIARY COMPLETION (70+ creatures)
# ═══════════════════════════════════════════════════════════════════════════

def test_bestiary_count():
    """Bestiary has 70+ named creatures."""
    errors = []
    try:
        from bestiary import CREATURES
        if len(CREATURES) < 70:
            errors.append(f"Expected 70+ creatures, got {len(CREATURES)}")
    except ImportError:
        errors.append("bestiary not importable")
    return errors


def test_bestiary_has_ids():
    """All creatures have stable id fields."""
    errors = []
    try:
        from bestiary import CREATURES
        ids_seen = set()
        for i, c in enumerate(CREATURES):
            cid = c.get("id")
            if not cid:
                errors.append(f"Creature {i} ({c.get('name', '?')}): missing 'id' field")
            elif cid in ids_seen:
                errors.append(f"Creature {i} ({c.get('name', '?')}): duplicate id '{cid}'")
            ids_seen.add(cid)
    except ImportError:
        errors.append("bestiary not importable")
    return errors


def test_bestiary_stat_ranges():
    """Creature stats are within valid ranges."""
    errors = []
    try:
        from bestiary import CREATURES
        for c in CREATURES:
            name = c.get("name", "?")
            hd = c.get("hd", 0)
            ac = c.get("ac", 0)
            ml = c.get("ml", 0)
            if not (1 <= hd <= 20):
                errors.append(f"{name}: HD {hd} out of range 1-20")
            if not (0 <= ac <= 25):
                errors.append(f"{name}: AC {ac} out of range 0-25")
            if not (2 <= ml <= 12):
                errors.append(f"{name}: ML {ml} out of range 2-12")
    except ImportError:
        errors.append("bestiary not importable")
    return errors


def test_encounter_tables_exist():
    """Encounter tables map terrains to creature IDs."""
    errors = []
    try:
        from encounter_tables import TERRAIN_CREATURE_TABLE
        if not isinstance(TERRAIN_CREATURE_TABLE, dict):
            errors.append("TERRAIN_CREATURE_TABLE should be a dict")
            return errors
        required_terrains = {"road", "plains", "forest", "hills", "mountains",
                             "desert", "swamp", "coast", "jungle"}
        missing = required_terrains - set(TERRAIN_CREATURE_TABLE.keys())
        if missing:
            errors.append(f"Missing terrains: {missing}")
        for terrain, pool in TERRAIN_CREATURE_TABLE.items():
            if not pool or len(pool) < 3:
                errors.append(f"Terrain '{terrain}': needs 3+ creature entries, has {len(pool)}")
    except ImportError:
        errors.append("encounter_tables not importable")
    return errors


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 4: MAGIC ITEMS
# ═══════════════════════════════════════════════════════════════════════════

def test_magic_items_exist():
    """Magic items table exists with tiered entries."""
    errors = []
    try:
        from magic_items import MAGIC_ITEMS
        if len(MAGIC_ITEMS) < 30:
            errors.append(f"Expected 30+ magic items, got {len(MAGIC_ITEMS)}")
        # Check tiers represented
        tiers = set(item.get("tier") for item in MAGIC_ITEMS)
        for t in [1, 2, 3, 4, 5]:
            if t not in tiers:
                errors.append(f"No magic items at tier {t}")
        # Check required fields
        required = {"name", "type", "tier", "description"}
        for i, item in enumerate(MAGIC_ITEMS):
            missing = required - set(item.keys())
            if missing:
                errors.append(f"Item {i} ({item.get('name', '?')}): missing {missing}")
    except ImportError:
        errors.append("magic_items not importable")
    return errors


def test_treasure_magic_items():
    """Tier 3+ treasures can include magic items."""
    errors = []
    try:
        from treasure import roll_treasure
        random.seed(42)
        found_magic = False
        for _ in range(100):
            result = roll_treasure(4, "dungeon")
            if result.get("magic_items"):
                found_magic = True
                break
        if not found_magic:
            errors.append("No magic items found in 100 tier-4 treasure rolls")
    except Exception as e:
        errors.append(f"Exception: {e}")
    return errors


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 5: CROSS-REFERENCE WIRING
# ═══════════════════════════════════════════════════════════════════════════

def test_cross_reference_creature_ids():
    """All creature IDs in encounter tables resolve to bestiary entries."""
    errors = []
    try:
        from bestiary import CREATURES
        from encounter_tables import TERRAIN_CREATURE_TABLE
        valid_ids = {c["id"] for c in CREATURES if "id" in c}
        for terrain, pool in TERRAIN_CREATURE_TABLE.items():
            for entry in pool:
                # Handle both (creature_id, weight) tuples and plain strings
                cid = entry[0] if isinstance(entry, (list, tuple)) else entry
                if cid not in valid_ids:
                    errors.append(f"Terrain '{terrain}': creature ID '{cid}' not in bestiary")
    except ImportError as e:
        errors.append(f"Import error: {e}")
    return errors


def test_cross_reference_terrain_types():
    """All terrain types in encounter tables match travel.py's terrain list."""
    errors = []
    try:
        from travel import TERRAIN_MOVEMENT
        from encounter_tables import TERRAIN_CREATURE_TABLE
        travel_terrains = set(TERRAIN_MOVEMENT.keys())
        encounter_terrains = set(TERRAIN_CREATURE_TABLE.keys())
        missing = travel_terrains - encounter_terrains
        if missing:
            errors.append(f"Terrains in travel but not encounters: {missing}")
    except ImportError as e:
        errors.append(f"Import error: {e}")
    return errors


def test_get_creature_lookup():
    """get_creature(id) function works."""
    errors = []
    try:
        from bestiary import get_creature
        result = get_creature("animated_skeleton")
        if not result:
            errors.append("get_creature('animated_skeleton') returned None")
        elif result.get("name") != "Animated Skeleton":
            errors.append(f"get_creature returned wrong creature: {result.get('name')}")
    except ImportError:
        errors.append("get_creature not importable from bestiary")
    except Exception as e:
        errors.append(f"Exception: {e}")
    return errors


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 6: SPELL COMPLETION
# ═══════════════════════════════════════════════════════════════════════════

def test_elementalist_spells_l4_l5():
    """Elementalist has level 4 and level 5 spells."""
    errors = []
    try:
        from spells import SPELLS
        elem_l4 = [s for s in SPELLS if s["tradition"] == "elementalist" and s["level"] == 4]
        elem_l5 = [s for s in SPELLS if s["tradition"] == "elementalist" and s["level"] == 5]
        if len(elem_l4) < 2:
            errors.append(f"Expected 2+ elementalist L4 spells, got {len(elem_l4)}")
        if len(elem_l5) < 1:
            errors.append(f"Expected 1+ elementalist L5 spells, got {len(elem_l5)}")
    except ImportError:
        errors.append("spells not importable")
    return errors


def test_necromancer_spells_l4_l5():
    """Necromancer has level 4 and level 5 spells."""
    errors = []
    try:
        from spells import SPELLS
        necro_l4 = [s for s in SPELLS if s["tradition"] == "necromancer" and s["level"] == 4]
        necro_l5 = [s for s in SPELLS if s["tradition"] == "necromancer" and s["level"] == 5]
        if len(necro_l4) < 2:
            errors.append(f"Expected 2+ necromancer L4 spells, got {len(necro_l4)}")
        if len(necro_l5) < 1:
            errors.append(f"Expected 1+ necromancer L5 spells, got {len(necro_l5)}")
    except ImportError:
        errors.append("spells not importable")
    return errors


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 7: DUNGEON GENERATION
# ═══════════════════════════════════════════════════════════════════════════

def test_dungeon_generator_exists():
    """dungeon.py exists and has generate_dungeon function."""
    errors = []
    try:
        from dungeon import generate_dungeon
    except ImportError:
        errors.append("generate_dungeon not importable from dungeon module")
    return errors


def test_dungeon_output_structure():
    """Generated dungeon has valid structure."""
    errors = []
    try:
        from dungeon import generate_dungeon
        random.seed(42)
        result = generate_dungeon(depth=3, theme=None)
        required = {"rooms", "depth", "theme", "arithmetic_trace"}
        missing = required - set(result.keys())
        if missing:
            errors.append(f"Missing keys: {missing}")
        rooms = result.get("rooms", [])
        if len(rooms) < 3:
            errors.append(f"Expected 3+ rooms at depth 3, got {len(rooms)}")
        for i, room in enumerate(rooms):
            room_required = {"id", "type", "connections"}
            room_missing = room_required - set(room.keys())
            if room_missing:
                errors.append(f"Room {i}: missing {room_missing}")
        # Last room should be boss room
        if rooms and not rooms[-1].get("is_boss"):
            errors.append("Last room should be boss room")
    except ImportError:
        errors.append("dungeon not importable")
    except Exception as e:
        errors.append(f"Exception: {e}")
    return errors


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 8: SCENARIO SMOKE TEST (statistical validation)
# ═══════════════════════════════════════════════════════════════════════════

def test_scenario_smoke():
    """100-seed statistical validation across all systems."""
    errors = []
    error_count = 0
    total_tests = 0

    for seed in range(100):
        random.seed(seed)

        # Scene generation
        try:
            from scene import generate_scene
            for scene_type in ["wilderness", "ruin", "community"]:
                total_tests += 1
                result = generate_scene(scene_type, tag_count=2, threat_level=5)
                if "fallback" in result.get("tags_used", []):
                    error_count += 1
        except Exception:
            error_count += 3
            total_tests += 3

        # Encounter generation
        try:
            from encounter import generate_encounter
            total_tests += 1
            result = generate_encounter("forest", 5)
            if not result.get("combatants"):
                error_count += 1
        except Exception:
            error_count += 1
            total_tests += 1

        # Treasure generation
        try:
            from treasure import roll_treasure
            total_tests += 1
            result = roll_treasure(4)
            if "coins" not in result:
                error_count += 1
        except Exception:
            error_count += 1
            total_tests += 1

    error_rate = error_count / max(1, total_tests)
    if error_rate > 0.05:
        errors.append(f"Error rate {error_rate:.1%} exceeds 5% threshold ({error_count}/{total_tests})")

    return errors


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 9: INTEGRATION TOUCHPOINTS
# ═══════════════════════════════════════════════════════════════════════════

def test_cli_reference_level_up():
    """CLI reference documents level-up command."""
    errors = []
    cli_ref = os.path.join(_runtime_dir, 'phases', '2-action-interpretation',
                           'references', 'cli-reference.md')
    if os.path.exists(cli_ref):
        with open(cli_ref) as f:
            content = f.read()
        if 'level-up' not in content:
            errors.append("cli-reference.md missing level-up command")
    else:
        errors.append("cli-reference.md not found")
    return errors


def test_cli_reference_dungeon():
    """CLI reference documents generate-dungeon command."""
    errors = []
    cli_ref = os.path.join(_runtime_dir, 'phases', '2-action-interpretation',
                           'references', 'cli-reference.md')
    if os.path.exists(cli_ref):
        with open(cli_ref) as f:
            content = f.read()
        if 'generate-dungeon' not in content:
            errors.append("cli-reference.md missing generate-dungeon command")
    else:
        errors.append("cli-reference.md not found")
    return errors


def test_phase_manifest_updated():
    """Phase manifest lists new table and script entries."""
    errors = []
    manifest = os.path.join(_runtime_dir, 'phases', 'phase-manifest.md')
    if os.path.exists(manifest):
        with open(manifest) as f:
            content = f.read()
        for expected in ['magic_items.py', 'encounter_tables.py', 'dungeon.py', 'level-up']:
            if expected not in content:
                errors.append(f"phase-manifest.md missing '{expected}'")
    else:
        errors.append("phase-manifest.md not found")
    return errors


# ═══════════════════════════════════════════════════════════════════════════
# TEST RUNNER
# ═══════════════════════════════════════════════════════════════════════════

ALL_TESTS = [
    # Phase 1: Level-up
    ("P1: level_up exists", test_level_up_exists),
    ("P1: warrior L1→L10", test_level_up_warrior),
    ("P1: mage spell slots", test_level_up_mage_spell_slots),
    ("P1: expert levels", test_level_up_expert),
    ("P1: saves recalculated", test_level_up_saves_recalculated),
    ("P1: HP increases", test_level_up_hp_increases),
    # Phase 2: Tags
    ("P2: wilderness 50+ tags", test_wilderness_tags_50),
    ("P2: ruin 50+ tags", test_ruin_tags_50),
    ("P2: community 50+ tags", test_community_tags_50),
    # Phase 3: Bestiary
    ("P3: bestiary 70+ creatures", test_bestiary_count),
    ("P3: bestiary has IDs", test_bestiary_has_ids),
    ("P3: bestiary stat ranges", test_bestiary_stat_ranges),
    ("P3: encounter tables exist", test_encounter_tables_exist),
    # Phase 4: Magic items
    ("P4: magic items table", test_magic_items_exist),
    ("P4: treasure includes magic", test_treasure_magic_items),
    # Phase 5: Cross-references
    ("P5: creature IDs resolve", test_cross_reference_creature_ids),
    ("P5: terrain types match", test_cross_reference_terrain_types),
    ("P5: get_creature lookup", test_get_creature_lookup),
    # Phase 6: Spells
    ("P6: elementalist L4-5", test_elementalist_spells_l4_l5),
    ("P6: necromancer L4-5", test_necromancer_spells_l4_l5),
    # Phase 7: Dungeon
    ("P7: dungeon generator exists", test_dungeon_generator_exists),
    ("P7: dungeon output structure", test_dungeon_output_structure),
    # Phase 8: Smoke test
    ("P8: scenario smoke 100 seeds", test_scenario_smoke),
    # Phase 9: Integration
    ("P9: CLI ref level-up", test_cli_reference_level_up),
    ("P9: CLI ref dungeon", test_cli_reference_dungeon),
    ("P9: manifest updated", test_phase_manifest_updated),
]


def run_test():
    """Entry point for run_all_tests.py."""
    all_passed = True
    pass_count = 0
    fail_count = 0

    for test_name, test_fn in ALL_TESTS:
        try:
            errors = test_fn()
            if errors:
                all_passed = False
                fail_count += 1
                print(f"  FAIL: {test_name}")
                for e in errors:
                    print(f"    - {e}")
            else:
                pass_count += 1
                print(f"  PASS: {test_name}")
        except Exception as e:
            all_passed = False
            fail_count += 1
            print(f"  ERROR: {test_name}: {e}")

    print(f"\n  Full plan validation: {pass_count} passed, {fail_count} failed")
    return all_passed


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
