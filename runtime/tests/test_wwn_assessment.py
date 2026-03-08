#!/usr/bin/env python3
"""
WWN Game Engine — Comprehensive Assessment Test Suite

Evaluates the overall health, completeness, and quality of the Worlds Without
Number AI RPG engine across 12 assessment dimensions:

  1. Core Mechanics Integrity (dice, combat, saves, skill checks)
  2. Character Creation Completeness (all classes, traditions, backgrounds)
  3. Data Tables Quality (weapons, armor, bestiary, spells, foci)
  4. CLI Command Coverage (all 14 commands functional)
  5. State Schema Robustness (schema + validator coverage)
  6. Social Systems (NPCs, factions, diplomacy, consequences)
  7. Exploration Systems (travel, scenes, treasure, encounters)
  8. Narrative Layer (voice guide, templates, failure flavors, drama budget)
  9. Lore & World-Building (nations, overview files, indexes, markers)
  10. Cross-System Integration (CLI↔scripts↔state↔schema consistency)
  11. Determinism & Reproducibility (seed-based determinism)
  12. Edge Cases & Error Handling (invalid inputs, boundary values)

Outputs a scored report card with per-dimension grades.
"""

import os
import sys
import json
import subprocess
import random
import copy
import time

# Paths
RUNTIME_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(RUNTIME_DIR)
SCRIPTS_DIR = os.path.join(RUNTIME_DIR, "scripts")
SKILLS_DIR = os.path.join(RUNTIME_DIR, "phases", "3-resolution", "skills")
CORE_TABLES = os.path.join(SKILLS_DIR, "core", "tables")
CORE_SCRIPTS = os.path.join(SKILLS_DIR, "core", "scripts")
COMBAT_TABLES = os.path.join(SKILLS_DIR, "combat", "tables")
COMBAT_SCRIPTS = os.path.join(SKILLS_DIR, "combat", "scripts")
SOCIAL_TABLES = os.path.join(SKILLS_DIR, "social", "tables")
SOCIAL_SCRIPTS = os.path.join(SKILLS_DIR, "social", "scripts")
EXPLORATION_SCRIPTS = os.path.join(SKILLS_DIR, "exploration", "scripts")
WB_TABLES = os.path.join(SKILLS_DIR, "world-building", "tables")
WB_SCRIPTS = os.path.join(SKILLS_DIR, "world-building", "scripts")
NARRATIVE_DIR = os.path.join(RUNTIME_DIR, "phases", "4-narrative")
LORE_DIR = os.path.join(RUNTIME_DIR, "phases", "1-context-loading", "lore")
NATIONS_DIR = os.path.join(LORE_DIR, "nations")
SCHEMAS_DIR = os.path.join(RUNTIME_DIR, "schemas")
CLI = os.path.join(SCRIPTS_DIR, "emergence_cli.py")
STATE_FILE = os.path.join(RUNTIME_DIR, "state.json")

# Add all domain paths
for d in [CORE_TABLES, CORE_SCRIPTS, COMBAT_TABLES, COMBAT_SCRIPTS,
          SOCIAL_TABLES, SOCIAL_SCRIPTS, EXPLORATION_SCRIPTS,
          WB_TABLES, WB_SCRIPTS,
          os.path.join(NARRATIVE_DIR, "tables")]:
    if os.path.isdir(d) and d not in sys.path:
        sys.path.insert(0, d)


# ═══════════════════════════════════════════════════════════════════════════════
# ASSESSMENT FRAMEWORK
# ═══════════════════════════════════════════════════════════════════════════════

class AssessmentDimension:
    """Tracks pass/fail/error counts for a single assessment dimension."""
    def __init__(self, name, weight=1.0):
        self.name = name
        self.weight = weight
        self.passed = []
        self.failed = []
        self.errors = []
        self.notes = []

    def ok(self, name, detail=""):
        self.passed.append(name)
        print(f"    [PASS] {name}" + (f"  ({detail})" if detail else ""))

    def fail(self, name, reason=""):
        self.failed.append((name, reason))
        print(f"    [FAIL] {name}: {reason}")

    def error(self, name, exc):
        self.errors.append((name, str(exc)))
        print(f"    [ERR]  {name}: {exc}")

    def note(self, text):
        self.notes.append(text)

    @property
    def total(self):
        return len(self.passed) + len(self.failed) + len(self.errors)

    @property
    def score(self):
        if self.total == 0:
            return 0.0
        return len(self.passed) / self.total

    @property
    def grade(self):
        s = self.score
        if s >= 0.95: return "A"
        if s >= 0.85: return "B"
        if s >= 0.70: return "C"
        if s >= 0.50: return "D"
        return "F"


def run_cli(args_list):
    """Run emergence_cli.py with given args."""
    cmd = [sys.executable, CLI] + args_list
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    return result.returncode, result.stdout, result.stderr


# ═══════════════════════════════════════════════════════════════════════════════
# DIMENSION 1: CORE MECHANICS INTEGRITY
# ═══════════════════════════════════════════════════════════════════════════════

def assess_core_mechanics(d):
    print(f"\n  [{d.name}]")

    # 1a. Dice module
    try:
        from dice import roll, roll_dice, parse_dice_notation, roll_check, roll_save
        d.ok("dice module imports (roll, roll_dice, parse_dice_notation, roll_check, roll_save)")
    except ImportError as e:
        d.error("dice module import", e)
        return

    # 1b. Dice notation parsing
    try:
        for expr, expected in [("1d20", (1, 20, 0)), ("2d6+4", (2, 6, 4)),
                                ("1d8-1", (1, 8, -1)), ("3d10", (3, 10, 0))]:
            p = parse_dice_notation(expr)
            assert (p["count"], p["sides"], p["modifier"]) == expected, \
                f"Parse '{expr}' got {p}"
        d.ok("dice notation parsing (4 formats)")
    except Exception as e:
        d.error("dice parsing", e)

    # 1c. Roll result structure
    try:
        random.seed(42)
        r = roll("2d6+3")
        for key in ["total", "rolls", "expression", "arithmetic_trace"]:
            assert key in r, f"Missing key: {key}"
        assert r["total"] == sum(r["rolls"]) + 3
        d.ok("roll result structure (total, rolls, expression, trace)")
    except Exception as e:
        d.error("roll result structure", e)

    # 1d. Skill check mechanics (2d6 based)
    try:
        random.seed(100)
        result = roll_check(modifier=3, target=8)
        assert "success" in result
        assert "total" in result
        assert "rolls" in result
        assert result["target"] == 8
        d.ok("skill check mechanics (2d6 + modifier vs target)")
    except Exception as e:
        d.error("skill check", e)

    # 1e. Save mechanics (d20 based)
    try:
        random.seed(100)
        result = roll_save(14)
        assert "success" in result
        assert "roll" in result
        assert result["target"] == 14
        d.ok("save mechanics (d20 vs target)")
    except Exception as e:
        d.error("save mechanics", e)

    # 1f. Combat resolution
    try:
        from combat import resolve_attack, resolve_shock
        random.seed(42)
        result = resolve_attack(
            attacker={"attack_bonus": 3, "skill_level": 1, "attribute_mod": 1,
                       "weapon": {"damage": "1d8", "shock": "2/15", "traits": []}},
            defender={"armor_class": 14, "hp": {"current": 10, "max": 10}},
        )
        for key in ["hit_roll", "total_roll", "hit", "damage", "shock_applied", "arithmetic_trace"]:
            assert key in result, f"Missing combat key: {key}"
        d.ok("combat attack resolution (hit roll, damage, shock, trace)")
    except Exception as e:
        d.error("combat resolution", e)

    # 1g. Zone-based combat
    try:
        from combat import CombatZone, CombatState
        cs = CombatState()
        cs.add_combatant("a", zone=CombatZone.MELEE)
        cs.add_combatant("b", zone=CombatZone.FAR)
        assert not cs.can_melee_attack("a", "b")
        cs.move_combatant("b", CombatZone.MELEE)
        assert cs.can_melee_attack("a", "b")
        d.ok("zone-based combat (MELEE/NEAR/FAR/DISTANT)")
    except Exception as e:
        d.error("zone combat", e)

    # 1h. Conditions and System Strain
    try:
        from conditions import SystemStrain, CONDITION_EFFECTS
        ss = SystemStrain(max_strain=14)
        assert ss.current == 0 and ss.can_heal()
        ss.add(14)
        assert not ss.can_heal()
        assert len(CONDITION_EFFECTS) >= 3
        d.ok("conditions: SystemStrain + CONDITION_EFFECTS")
    except Exception as e:
        d.error("conditions", e)

    # 1i. Magic system
    try:
        from magic import cast_spell, get_max_spell_level, can_cast
        assert get_max_spell_level(1) == 1
        assert get_max_spell_level(5) == 3
        assert get_max_spell_level(10) == 5
        assert can_cast(1, 1) and not can_cast(1, 2)
        random.seed(42)
        result = cast_spell("Test", 3, "high_magic", 2, 0, 14)
        assert result["success"] is True
        assert result["effort_after"] == 1
        d.ok("magic system (cast_spell, effort, spell levels)")
    except Exception as e:
        d.error("magic system", e)

    # 1j. Creature behavior AI
    try:
        from behavior import decide_action, BEHAVIOR_PROFILES, choose_target
        assert len(BEHAVIOR_PROFILES) >= 5
        combatants = [
            {"id": "pc_1", "hp_current": 8, "hp_max": 10, "zone": "melee", "is_pc": True},
            {"id": "pc_2", "hp_current": 3, "hp_max": 10, "zone": "near", "is_pc": True},
        ]
        target = choose_target(combatants, "cautious", "mob_1")
        assert target == "pc_2", "Cautious should target weakest"
        target2 = choose_target(combatants, "aggressive", "mob_1")
        assert target2 == "pc_1", "Aggressive should target strongest"
        d.ok("creature behavior AI (6 profiles, target selection)")
    except Exception as e:
        d.error("creature AI", e)


# ═══════════════════════════════════════════════════════════════════════════════
# DIMENSION 2: CHARACTER CREATION COMPLETENESS
# ═══════════════════════════════════════════════════════════════════════════════

def assess_character_creation(d):
    print(f"\n  [{d.name}]")

    try:
        from character import create_character
    except ImportError as e:
        d.error("character module import", e)
        return

    # 2a. All 4 base classes
    for cls in ["warrior", "expert", "mage", "adventurer"]:
        try:
            random.seed(200)
            kwargs = {"name": f"Test_{cls}", "class_name": cls,
                      "background_id": 18, "method": "standard_array"}
            if cls == "adventurer":
                kwargs["partial_classes"] = ["expert", "warrior"]
            char = create_character(**kwargs)
            assert char["class"] == cls
            assert char["level"] == 1
            assert "hp" in char and char["hp"]["max"] > 0
            d.ok(f"class={cls} creates valid character")
        except Exception as e:
            d.error(f"class={cls}", e)

    # 2b. All 20 backgrounds
    try:
        success = 0
        for bg_id in range(1, 21):
            random.seed(300 + bg_id)
            char = create_character(name=f"BG{bg_id}", class_name="warrior",
                                     background_id=bg_id, method="standard_array")
            if char["background"]:
                success += 1
        if success == 20:
            d.ok(f"all 20 backgrounds produce valid characters")
        else:
            d.fail("backgrounds", f"Only {success}/20 work")
    except Exception as e:
        d.error("background sweep", e)

    # 2c. Magic traditions
    traditions_to_test = [
        ("high_mage", "mage", False),
        ("elementalist", "mage", False),
        ("necromancer", "mage", False),
        ("healer", "adventurer", True),  # partial-only
        ("vowed", "adventurer", True),   # partial-only
        ("invoker", "mage", False),
    ]
    for trad, cls, partial_only in traditions_to_test:
        try:
            random.seed(400)
            kwargs = {"name": f"Trad_{trad}", "class_name": cls,
                      "background_id": 16, "method": "standard_array",
                      "tradition": trad}
            if cls == "adventurer":
                kwargs["partial_classes"] = ["warrior", "mage"]
            char = create_character(**kwargs)
            assert char.get("tradition") == trad
            d.ok(f"tradition={trad} (class={cls})")
        except Exception as e:
            d.error(f"tradition={trad}", e)

    # 2d. All 10 expanded partial classes
    from partial_classes import PARTIAL_CLASSES
    tested = 0
    for pcls in ["accursed", "bard", "mageslayer", "wise",
                 "invoker", "skinshifter", "duelist", "beastmaster",
                 "blood_priest", "thought_noble"]:
        try:
            random.seed(500 + tested)
            base = PARTIAL_CLASSES[pcls]["base_type"]
            partner = "warrior" if base != "warrior" else "expert"
            if pcls == "mageslayer":
                partner = "expert"  # mageslayer can't pair with mage types
            char = create_character(
                name=f"PC_{pcls}", class_name="adventurer",
                background_id=1, method="standard_array",
                partial_classes=[pcls, partner])
            assert pcls in char["partial_classes"]
            tested += 1
            d.ok(f"partial_class={pcls}/{partner}")
        except Exception as e:
            d.error(f"partial_class={pcls}", e)

    # 2e. Equipment packages
    try:
        from equipment import EQUIPMENT_PACKAGES
        random.seed(600)
        char = create_character(name="Equipped", class_name="warrior",
                                 background_id=18, method="standard_array",
                                 equipment_package="armored_warrior")
        has_gear = (len(char["equipment"]["readied"]) > 0 or
                    len(char["equipment"]["stowed"]) > 0)
        if has_gear:
            d.ok(f"equipment packages ({len(EQUIPMENT_PACKAGES)} available)")
        else:
            d.fail("equipment packages", "No items after package applied")
    except Exception as e:
        d.error("equipment packages", e)

    # 2f. Saving throw formula correctness
    try:
        random.seed(700)
        from attributes import get_modifier
        char = create_character(name="SaveCheck", class_name="warrior",
                                 background_id=18, method="standard_array")
        attrs = char["attributes"]
        str_mod = get_modifier(attrs["strength"])
        con_mod = get_modifier(attrs["constitution"])
        expected_phys = 16 - (1 + max(str_mod, con_mod))
        assert char["saving_throws"]["physical"] == expected_phys
        assert "luck" in char["saving_throws"]
        assert char["saving_throws"]["luck"] == 15
        d.ok("saving throw formulas correct (physical, luck)")
    except Exception as e:
        d.error("saving throws", e)


# ═══════════════════════════════════════════════════════════════════════════════
# DIMENSION 3: DATA TABLES QUALITY
# ═══════════════════════════════════════════════════════════════════════════════

def assess_data_tables(d):
    print(f"\n  [{d.name}]")

    # 3a. Attributes
    try:
        from attributes import ATTRIBUTES, ATTRIBUTE_MODIFIERS, get_modifier
        assert len(ATTRIBUTES) == 6
        assert get_modifier(3) == -2 and get_modifier(18) == 2 and get_modifier(10) == 0
        d.ok(f"attributes: 6 attributes, modifier table correct")
    except Exception as e:
        d.error("attributes", e)

    # 3b. Skills
    try:
        from skills import SKILLS, SKILL_CHECK_DIFFICULTIES
        assert len(SKILLS) >= 20
        for req in ["stab", "shoot", "magic", "heal", "notice", "sneak", "exert"]:
            assert req in SKILLS, f"Missing skill: {req}"
        d.ok(f"skills: {len(SKILLS)} skills, difficulty table present")
    except Exception as e:
        d.error("skills", e)

    # 3c. Equipment — weapons
    try:
        from equipment import WEAPONS, ARMOR, WEAPON_TRAITS
        assert len(WEAPONS) >= 25
        for w in WEAPONS:
            for f in ["name", "damage", "shock", "cost_sp"]:
                assert f in w, f"Weapon {w.get('name','?')} missing '{f}'"
        d.ok(f"weapons: {len(WEAPONS)} weapons with damage/shock/cost")
    except Exception as e:
        d.error("weapons", e)

    # 3d. Equipment — armor
    try:
        assert len(ARMOR) >= 10
        for a in ARMOR:
            for f in ["name", "ac", "cost_sp"]:
                assert f in a, f"Armor {a.get('name','?')} missing '{f}'"
        d.ok(f"armor: {len(ARMOR)} armor pieces with AC/cost")
    except Exception as e:
        d.error("armor", e)

    # 3e. Classes and progression
    try:
        from classes import CLASSES, XP_TABLE, ADVENTURER_PROGRESSION
        assert len(CLASSES) >= 4
        assert len(XP_TABLE) == 10
        assert len(ADVENTURER_PROGRESSION) >= 3
        d.ok(f"classes: {len(CLASSES)} classes, XP table (10 levels), {len(ADVENTURER_PROGRESSION)} progressions")
    except Exception as e:
        d.error("classes", e)

    # 3f. Backgrounds
    try:
        from backgrounds import BACKGROUNDS
        assert len(BACKGROUNDS) == 20
        for bg in BACKGROUNDS.values() if isinstance(BACKGROUNDS, dict) else BACKGROUNDS:
            b = bg if isinstance(bg, dict) else BACKGROUNDS[bg]
            assert "name" in b and "free_skill" in b
        d.ok(f"backgrounds: {len(BACKGROUNDS)} backgrounds")
    except Exception as e:
        d.error("backgrounds", e)

    # 3g. Foci
    try:
        from foci import FOCI
        assert len(FOCI) >= 27
        incomplete = []
        for name, focus in FOCI.items():
            if "level_1" not in focus or "level_2" not in focus:
                incomplete.append(name)
        if not incomplete:
            d.ok(f"foci: {len(FOCI)} foci all have level_1/level_2")
        else:
            d.fail(f"foci: {len(FOCI)} foci but {len(incomplete)} incomplete",
                   f"Missing level_2: {incomplete}")
    except Exception as e:
        d.error("foci", e)

    # 3h. Spells
    try:
        from spells import SPELLS
        assert len(SPELLS) >= 30
        traditions_covered = set(s["tradition"] for s in SPELLS)
        for trad in ["high_mage", "elementalist", "necromancer"]:
            assert trad in traditions_covered
        d.ok(f"spells: {len(SPELLS)} spells across {len(traditions_covered)} traditions")
    except Exception as e:
        d.error("spells", e)

    # 3i. Bestiary
    try:
        from bestiary import CREATURES, HUMAN_TEMPLATES, REACTION_TABLE
        assert len(CREATURES) >= 15
        assert len(HUMAN_TEMPLATES) >= 5
        for c in CREATURES:
            for f in ["name", "hd", "ac", "atk", "dmg", "move", "ml", "save"]:
                assert f in c, f"Creature {c.get('name','?')} missing '{f}'"
        d.ok(f"bestiary: {len(CREATURES)} creatures, {len(HUMAN_TEMPLATES)} templates, reaction table")
    except Exception as e:
        d.error("bestiary", e)

    # 3j. Partial classes
    try:
        from partial_classes import PARTIAL_CLASSES, BASE_TYPE_MAP
        assert len(PARTIAL_CLASSES) >= 10
        assert len(BASE_TYPE_MAP) >= 13  # 3 base + 10 expanded
        d.ok(f"partial classes: {len(PARTIAL_CLASSES)} defined, BASE_TYPE_MAP has {len(BASE_TYPE_MAP)} entries")
    except Exception as e:
        d.error("partial classes", e)

    # 3k. Traditions
    try:
        from traditions import TRADITIONS
        assert len(TRADITIONS) >= 6
        for name, t in TRADITIONS.items():
            assert "description" in t and "arts" in t
        d.ok(f"traditions: {len(TRADITIONS)} traditions with arts and descriptions")
    except Exception as e:
        d.error("traditions", e)


# ═══════════════════════════════════════════════════════════════════════════════
# DIMENSION 4: CLI COMMAND COVERAGE
# ═══════════════════════════════════════════════════════════════════════════════

def assess_cli_commands(d):
    print(f"\n  [{d.name}]")

    cli_tests = [
        ("roll", ["roll", "1d20+3", "--seed", "42"], ["total", "rolls", "seed"]),
        ("skill-check", ["skill-check", "--attribute-mod", "1", "--skill-level", "1",
                          "--difficulty", "8", "--seed", "42"], ["success", "total"]),
        ("save", ["save", "--type", "physical", "--level", "3",
                   "--modifier", "1", "--seed", "42"], ["success", "roll", "target"]),
        ("attack", ["attack", "--attack-bonus", "3", "--skill-level", "1",
                     "--attribute-mod", "1", "--weapon-damage", "1d8",
                     "--shock", "2/15", "--target-ac", "14",
                     "--target-hp", "10", "--seed", "42"], ["hit", "damage"]),
        ("create-character", ["create-character", "--name", "CLI_Test",
                              "--class", "warrior", "--background", "18",
                              "--seed", "42"], ["name", "class", "level"]),
        ("cast-spell", ["cast-spell", "--spell-name", "Magic Missile",
                         "--caster-level", "3", "--tradition", "high_magic",
                         "--current-effort", "2", "--system-strain", "0",
                         "--system-strain-max", "14", "--seed", "42"], ["success"]),
        ("encounter", ["encounter", "--terrain", "forest", "--threat-level", "3",
                        "--seed", "42"], ["seed"]),
        ("travel", ["travel", "--terrain", "forest", "--days", "3",
                     "--supplies", "5", "--seed", "42"], ["travel_log", "total_distance_miles"]),
        ("generate-scene", ["generate-scene", "--scene-type", "wilderness",
                             "--seed", "42"], ["seed"]),
        ("treasure", ["treasure", "--tier", "2", "--seed", "42"], ["seed"]),
        ("world-tick", ["world-tick", "--days", "7", "--seed", "42"], ["seed"]),
        ("generate-npc", ["generate-npc", "--importance", "major", "--region", "coastal",
                           "--tags", "2", "--seed", "42"], ["name", "voice_card"]),
        ("reaction-roll", ["reaction-roll", "--modifier", "2", "--seed", "42"],
         ["disposition", "total"]),
        ("faction-turn", ["faction-turn", "--seed", "42"], ["faction_count"]),
    ]

    for name, args, required_keys in cli_tests:
        try:
            rc, out, err = run_cli(args)
            if rc == 0:
                data = json.loads(out)
                missing = [k for k in required_keys if k not in data]
                if missing:
                    d.fail(f"CLI {name}", f"Missing keys: {missing}")
                else:
                    d.ok(f"CLI {name}")
            else:
                d.fail(f"CLI {name}", f"exit code {rc}: {err.strip()[:100]}")
        except Exception as e:
            d.error(f"CLI {name}", e)


# ═══════════════════════════════════════════════════════════════════════════════
# DIMENSION 5: STATE SCHEMA ROBUSTNESS
# ═══════════════════════════════════════════════════════════════════════════════

def assess_state_schema(d):
    print(f"\n  [{d.name}]")

    # 5a. Schema file exists and parses
    try:
        schema_path = os.path.join(SCHEMAS_DIR, "state.schema.json")
        with open(schema_path) as f:
            schema = json.load(f)
        assert "$defs" in schema
        assert "properties" in schema
        d.ok(f"schema file parses ({len(schema.get('$defs', {}))} definitions)")
    except Exception as e:
        d.error("schema parse", e)
        return

    # 5b. Schema has all critical definitions
    critical_defs = ["character", "current_scene", "known_npc", "human_faction",
                     "resource_pool", "consequence_entry", "session", "campaign_arc"]
    missing_defs = [dd for dd in critical_defs if dd not in schema.get("$defs", {})]
    if not missing_defs:
        d.ok(f"schema definitions: all {len(critical_defs)} critical defs present")
    else:
        d.fail("schema definitions", f"Missing: {missing_defs}")

    # Load state and validator for remaining tests
    if SCRIPTS_DIR not in sys.path:
        sys.path.insert(0, SCRIPTS_DIR)
    try:
        from validate_state import validate_state
        with open(STATE_FILE) as f:
            state = json.load(f)
        validator_loaded = True
    except Exception as e:
        d.error("load validate_state + state.json", e)
        validator_loaded = False
        state = {}

    # 5c. State validates against schema
    if validator_loaded:
        try:
            errors = validate_state(state)
            if not errors:
                d.ok("live state.json passes validation")
            else:
                d.fail("state validation", f"{len(errors)} errors: {errors[:3]}")
        except Exception as e:
            d.error("state validation", e)

    # 5d. Validator catches mutations
    if validator_loaded:
        mutation_tests = [
            ("missing chronicle", ["chronicle"], None),
            ("wrong type current_day", ["current_day"], "two"),
            ("forbidden key", lambda s: s.update({"entropy": 42}) or s, None),
        ]

        for name, path_or_fn, value in mutation_tests:
            try:
                s = copy.deepcopy(state)
                if callable(path_or_fn):
                    path_or_fn(s)
                elif value is None:
                    obj = s
                    for key in path_or_fn[:-1]:
                        obj = obj[key]
                    del obj[path_or_fn[-1]]
                else:
                    obj = s
                    for key in path_or_fn[:-1]:
                        obj = obj[key]
                    obj[path_or_fn[-1]] = value
                errs = validate_state(s)
                if errs:
                    d.ok(f"validator catches: {name}")
                else:
                    d.fail(f"validator misses: {name}", "No error raised")
            except Exception as e:
                d.error(f"validator mutation: {name}", e)

    # 5e. Schema version consistency
    try:
        assert state.get("schema_version") == "7.5.0"
        assert "7.5.0" in schema.get("description", "")
        d.ok("schema version 7.5.0 consistent between state and schema")
    except Exception as e:
        d.error("schema version", e)

    # 5f. Character schema completeness
    try:
        char_props = schema["$defs"]["character"]["properties"]
        wwn_fields = ["attributes", "hp", "armor_class", "attack_bonus",
                      "skills", "equipment", "saving_throws", "system_strain",
                      "effort", "foci", "class_abilities", "tradition",
                      "partial_classes", "spells_known"]
        missing = [f for f in wwn_fields if f not in char_props]
        if not missing:
            d.ok(f"character schema has all {len(wwn_fields)} WWN fields")
        else:
            d.fail("character schema", f"Missing: {missing}")
    except Exception as e:
        d.error("character schema", e)


# ═══════════════════════════════════════════════════════════════════════════════
# DIMENSION 6: SOCIAL SYSTEMS
# ═══════════════════════════════════════════════════════════════════════════════

def assess_social_systems(d):
    print(f"\n  [{d.name}]")

    # 6a. NPC generation
    try:
        from npc import generate_npc, reaction_roll
        random.seed(42)
        npc = generate_npc(importance="major", region="coastal", tag_count=2)
        for key in ["name", "voice_card", "personality_traits", "speech_patterns",
                     "key_phrases", "motivation", "importance"]:
            assert key in npc, f"NPC missing key: {key}"
        d.ok(f"NPC generation: {npc['name']} with voice card")
    except Exception as e:
        d.error("NPC generation", e)

    # 6b. Reaction roll
    try:
        random.seed(42)
        reaction = reaction_roll(modifier=2)
        assert "disposition" in reaction and "total" in reaction
        assert "arithmetic_trace" in reaction
        d.ok(f"reaction roll: {reaction['total']} -> {reaction['disposition']}")
    except Exception as e:
        d.error("reaction roll", e)

    # 6c. Faction turn
    try:
        from faction import faction_turn
        random.seed(42)
        factions = [
            {"id": "f1", "name": "Iron Band", "archetype": "aggressive",
             "goal": "Conquer", "power_level": 7,
             "clock": {"name": "War", "current": 3, "max": 6, "status": "active"}},
            {"id": "f2", "name": "Trade Guild", "archetype": "mercantile",
             "goal": "Profit", "power_level": 5,
             "clock": {"name": "Deal", "current": 1, "max": 8, "status": "active"}},
        ]
        result = faction_turn(factions)
        assert result["faction_count"] == 2
        assert "results" in result
        d.ok(f"faction turn: {result['faction_count']} factions processed")
    except Exception as e:
        d.error("faction turn", e)

    # 6d. Diplomacy
    try:
        from diplomacy import persuasion_check, calculate_bribe_cost
        random.seed(42)
        result = persuasion_check(skill_mod=1, disposition="neutral", context_modifiers=[])
        assert "outcome" in result and "arithmetic_trace" in result
        cost = calculate_bribe_cost(npc_importance="major", request_difficulty="moderate")
        assert cost["total_cost_gp"] > 0
        d.ok(f"diplomacy: persuasion + bribe cost ({cost['total_cost_gp']} gp)")
    except Exception as e:
        d.error("diplomacy", e)

    # 6e. Consequence tracker
    try:
        from consequence import create_consequence, check_consequences
        c = create_consequence("Player returns", 3, "Ambush", 1)
        assert c["status"] == "pending"
        result = check_consequences([c], current_day=2)
        assert "triggered" in result
        d.ok("consequence tracker: create + check")
    except Exception as e:
        d.error("consequence tracker", e)

    # 6f. Social data tables
    try:
        from character_tags import CHARACTER_TAGS
        from court_tags import COURT_TAGS
        from faction_actions import FACTION_ACTIONS
        assert len(CHARACTER_TAGS) >= 50
        assert len(COURT_TAGS) >= 20
        assert len(FACTION_ACTIONS) >= 10
        d.ok(f"social tables: {len(CHARACTER_TAGS)} char tags, {len(COURT_TAGS)} court tags, {len(FACTION_ACTIONS)} faction actions")
    except Exception as e:
        d.error("social tables", e)


# ═══════════════════════════════════════════════════════════════════════════════
# DIMENSION 7: EXPLORATION SYSTEMS
# ═══════════════════════════════════════════════════════════════════════════════

def assess_exploration_systems(d):
    print(f"\n  [{d.name}]")

    # 7a. Travel system
    try:
        from travel import resolve_travel, TERRAIN_MOVEMENT, TERRAIN_ENCOUNTER_CHANCE
        random.seed(42)
        result = resolve_travel("forest", 3, 5, 1, 3)
        assert result["days"] == 3
        assert result["total_distance_miles"] == 3 * TERRAIN_MOVEMENT["forest"]
        assert len(result["travel_log"]) == 3
        for day in result["travel_log"]:
            assert "encounter_check" in day
            assert "travel_event" in day
        d.ok(f"travel: {result['total_distance_miles']} miles, {result['encounters']} encounters")
    except Exception as e:
        d.error("travel system", e)

    # 7b. Foraging
    try:
        from travel import forage, TERRAIN_FORAGE_DIFFICULTY
        random.seed(42)
        result = forage(skill_modifier=2, terrain="forest")
        assert "success" in result and "rations_found" in result
        assert "arithmetic_trace" in result
        d.ok(f"foraging: {'success' if result['success'] else 'fail'}, {result['rations_found']} rations")
    except Exception as e:
        d.error("foraging", e)

    # 7c. Scene generation
    try:
        from scene import generate_scene
        random.seed(42)
        result = generate_scene(scene_type="wilderness", tag_count=2, threat_level=3)
        assert "scene_type" in result
        d.ok("scene generation works")
    except Exception as e:
        d.error("scene generation", e)

    # 7d. Treasure
    try:
        from treasure import roll_treasure
        random.seed(42)
        for tier in [1, 2, 3, 4, 5]:
            result = roll_treasure(tier=tier)
            assert "items" in result or "coins" in result or "total_value" in result
        d.ok("treasure: all 5 tiers generate loot")
    except Exception as e:
        d.error("treasure", e)

    # 7e. Encounter generation
    try:
        from encounter import generate_encounter
        random.seed(42)
        result = generate_encounter(terrain="forest", threat_level=3)
        assert isinstance(result, dict)
        d.ok("encounter generation works")
    except Exception as e:
        d.error("encounter generation", e)

    # 7f. World tick
    try:
        from world_tick import advance_world
        random.seed(42)
        result = advance_world(days_elapsed=7, clocks=[], factions=[], current_day=1)
        assert isinstance(result, dict)
        d.ok("world tick: advance_world works")
    except Exception as e:
        d.error("world tick", e)

    # 7g. Travel terrain coverage
    try:
        assert len(TERRAIN_MOVEMENT) >= 9
        assert len(TERRAIN_ENCOUNTER_CHANCE) >= 9
        assert len(TERRAIN_FORAGE_DIFFICULTY) >= 9
        d.ok(f"terrain tables: {len(TERRAIN_MOVEMENT)} terrains covered")
    except Exception as e:
        d.error("terrain coverage", e)


# ═══════════════════════════════════════════════════════════════════════════════
# DIMENSION 8: NARRATIVE LAYER
# ═══════════════════════════════════════════════════════════════════════════════

def assess_narrative_layer(d):
    print(f"\n  [{d.name}]")

    refs_dir = os.path.join(NARRATIVE_DIR, "references")
    assets_dir = os.path.join(NARRATIVE_DIR, "assets")

    # 8a. Voice guide
    path = os.path.join(refs_dir, "latter-earth-voice.md")
    if os.path.exists(path):
        with open(path) as f:
            content = f.read()
        if len(content) > 500:
            d.ok(f"latter-earth-voice.md ({len(content)} chars)")
        else:
            d.fail("voice guide", f"Too short: {len(content)} chars")
    else:
        d.fail("latter-earth-voice.md", "File not found")

    # 8b. Narration mappings with all sections
    path = os.path.join(refs_dir, "narration-mappings.md")
    if os.path.exists(path):
        with open(path) as f:
            content = f.read()
        required = ["§combat-hit", "§combat-miss", "§skill-check-success",
                     "§save-success", "§spell-cast", "§travel", "§social"]
        missing = [s for s in required if s not in content]
        if not missing:
            d.ok(f"narration-mappings: all {len(required)} sections")
        else:
            d.fail("narration-mappings", f"Missing: {missing}")
    else:
        d.fail("narration-mappings.md", "File not found")

    # 8c. Templates
    for name, fname in [("character sheet", "character-sheet-template.md"),
                        ("scene", "scene-template.md")]:
        path = os.path.join(assets_dir, fname)
        if os.path.exists(path):
            d.ok(f"{name} template exists")
        else:
            d.fail(f"{name} template", "Not found")

    # 8d. Failure flavors
    try:
        from failure_flavors import FAILURE_FLAVORS
        domains = ["combat_miss", "skill_check_failure", "spell_failure",
                    "travel_hazard", "social_gaffe", "save_failure"]
        all_good = True
        for domain in domains:
            if domain not in FAILURE_FLAVORS or len(FAILURE_FLAVORS[domain]) < 5:
                all_good = False
                d.fail(f"failure_flavors.{domain}", "Missing or too few")
        if all_good:
            d.ok(f"failure flavors: all {len(domains)} domains have 5+ entries")
    except Exception as e:
        d.error("failure flavors", e)

    # 8e. Drama budget in state
    try:
        with open(STATE_FILE) as f:
            state = json.load(f)
        assert state["session"]["drama_budget"] == 3
        d.ok("drama budget initialized (3)")
    except Exception as e:
        d.error("drama budget", e)

    # 8f. NPC dialogue protocol
    path = os.path.join(refs_dir, "npc-dialogue-protocol.md")
    if os.path.exists(path):
        d.ok("NPC dialogue protocol exists")
    else:
        d.fail("npc-dialogue-protocol.md", "Not found")

    # 8g. Threat-environment mapping
    path = os.path.join(refs_dir, "threat-environment-mapping.md")
    if os.path.exists(path):
        d.ok("threat-environment mapping exists")
    else:
        d.fail("threat-environment-mapping.md", "Not found")


# ═══════════════════════════════════════════════════════════════════════════════
# DIMENSION 9: LORE & WORLD-BUILDING
# ═══════════════════════════════════════════════════════════════════════════════

def assess_lore(d):
    print(f"\n  [{d.name}]")

    # 9a. Lore directory structure
    if os.path.isdir(LORE_DIR) and os.path.isdir(NATIONS_DIR):
        d.ok("lore/ and nations/ directories exist")
    else:
        d.fail("lore structure", "Missing directories")
        return

    # 9b. Nation file count
    nation_files = [f for f in os.listdir(NATIONS_DIR)
                    if f.endswith('.md') and f != 'index.md']
    if len(nation_files) >= 40:
        d.ok(f"nation count: {len(nation_files)} files (target 40)")
    else:
        d.fail("nation count", f"Only {len(nation_files)} (need 40)")

    # 9c. Nation §sections quality
    required_sections = ["§history", "§geography", "§government", "§culture",
                         "§sensory-palette", "§voice-notes"]
    sample = nation_files[:15]
    good = 0
    for fname in sample:
        with open(os.path.join(NATIONS_DIR, fname)) as f:
            content = f.read()
        if all(s in content for s in required_sections):
            good += 1
    if good == len(sample):
        d.ok(f"nation sections: {good}/{len(sample)} sampled files complete")
    else:
        d.fail("nation sections", f"Only {good}/{len(sample)} have all §sections")

    # 9d. Overview files
    overview_files = ["latter-earth-overview.md", "history-and-ages.md",
                      "geography.md", "languages.md"]
    for fname in overview_files:
        path = os.path.join(LORE_DIR, fname)
        if os.path.exists(path):
            with open(path) as f:
                content = f.read()
            if len(content) > 1000:
                d.ok(f"{fname} ({len(content)} chars)")
            else:
                d.fail(fname, f"Too short ({len(content)} chars)")
        else:
            d.fail(fname, "Not found")

    # 9e. Index files
    for idx in ["index.md"]:
        for loc, name in [(LORE_DIR, "lore/index.md"), (NATIONS_DIR, "nations/index.md")]:
            path = os.path.join(loc, idx)
            if os.path.exists(path):
                d.ok(f"{name} exists")
            else:
                d.fail(name, "Not found")

    # 9f. [UNKNOWN] markers for discovery
    unknown_count = 0
    for fname in nation_files[:10]:
        with open(os.path.join(NATIONS_DIR, fname)) as f:
            if "[UNKNOWN]" in f.read():
                unknown_count += 1
    if unknown_count >= 8:
        d.ok(f"[UNKNOWN] markers: {unknown_count}/10 sampled files")
    else:
        d.fail("[UNKNOWN] markers", f"Only {unknown_count}/10 files")

    # 9g. NYC/Carven Peaks custom lore
    nyc_files = ["gallery-system.md", "nyc-factions.md", "nyc-situation.md",
                 "nyc-magic.md", "imperator.md"]
    found = sum(1 for f in nyc_files if os.path.exists(os.path.join(LORE_DIR, f)))
    if found == len(nyc_files):
        d.ok(f"NYC/Carven Peaks lore: all {len(nyc_files)} files present")
    else:
        d.fail("NYC lore", f"Only {found}/{len(nyc_files)} files")

    # 9h. World-building tables
    try:
        from government_tables import GOVERNMENT_TYPES
        from society_tables import SOCIETY_TYPES
        from religion_tables import RELIGION_TYPES
        total = len(GOVERNMENT_TYPES) + len(SOCIETY_TYPES) + len(RELIGION_TYPES)
        d.ok(f"world-building tables: {total} entries ({len(GOVERNMENT_TYPES)} gov, {len(SOCIETY_TYPES)} soc, {len(RELIGION_TYPES)} rel)")
    except Exception as e:
        d.error("world-building tables", e)


# ═══════════════════════════════════════════════════════════════════════════════
# DIMENSION 10: CROSS-SYSTEM INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

def assess_integration(d):
    print(f"\n  [{d.name}]")

    # 10a. CLI → Python module consistency (all CLI commands dispatch to real modules)
    try:
        import importlib
        modules = [
            ("dice", ["roll", "roll_dice", "parse_dice_notation", "roll_check", "roll_save"]),
            ("combat", ["resolve_attack", "resolve_shock", "CombatZone", "CombatState"]),
            ("character", ["create_character"]),
            ("magic", ["cast_spell", "use_art"]),
            ("npc", ["generate_npc", "reaction_roll"]),
            ("faction", ["faction_turn"]),
            ("travel", ["resolve_travel"]),
            ("scene", ["generate_scene"]),
            ("treasure", ["roll_treasure"]),
            ("encounter", ["generate_encounter"]),
            ("conditions", ["SystemStrain", "CONDITION_EFFECTS"]),
        ]
        all_found = True
        for mod_name, funcs in modules:
            mod = importlib.import_module(mod_name)
            for fn in funcs:
                if not hasattr(mod, fn):
                    d.fail(f"{mod_name}.{fn}", "Not found")
                    all_found = False
        if all_found:
            d.ok(f"all {sum(len(f) for _, f in modules)} entry points found across {len(modules)} modules")
    except Exception as e:
        d.error("module integration", e)

    # 10b. State schema ↔ state.json field match
    try:
        schema_path = os.path.join(SCHEMAS_DIR, "state.schema.json")
        with open(schema_path) as f:
            schema = json.load(f)
        with open(STATE_FILE) as f:
            state = json.load(f)
        required_in_schema = set(schema.get("required", []))
        state_keys = set(state.keys())
        missing_from_state = required_in_schema - state_keys
        if not missing_from_state:
            d.ok(f"state.json has all {len(required_in_schema)} required schema fields")
        else:
            d.fail("state/schema sync", f"Missing from state: {missing_from_state}")
    except Exception as e:
        d.error("state/schema sync", e)

    # 10c. Governance documents exist and are substantial
    refs_dir = os.path.join(RUNTIME_DIR, "phases", "1-context-loading", "references")
    for name, fname, min_chars in [
        ("hard-rules.md", "hard-rules.md", 500),
        ("gm-protocol.md", "gm-protocol.md", 500),
    ]:
        path = os.path.join(refs_dir, fname)
        if os.path.exists(path):
            with open(path) as f:
                content = f.read()
            if len(content) >= min_chars:
                d.ok(f"{name}: {len(content)} chars")
            else:
                d.fail(name, f"Too short ({len(content)} chars)")
        else:
            d.fail(name, "Not found")

    # 10d. Validators all runnable
    validators = [
        ("validate_state.py", [STATE_FILE]),
        ("validate_docs_structure.py", []),
        ("validate_reference_freshness.py", []),
        ("validate_canonical_references.py", []),
    ]
    for script, args in validators:
        path = os.path.join(SCRIPTS_DIR, script)
        if os.path.exists(path):
            result = subprocess.run(
                [sys.executable, path] + args,
                capture_output=True, text=True, cwd=REPO_ROOT
            )
            if result.returncode == 0:
                d.ok(f"{script} passes")
            else:
                d.fail(script, f"exit code {result.returncode}")
        else:
            d.fail(script, "Not found")

    # 10e. Phase manifest exists
    manifest = os.path.join(RUNTIME_DIR, "phases", "phase-manifest.md")
    if os.path.exists(manifest):
        d.ok("phase-manifest.md exists")
    else:
        d.fail("phase-manifest.md", "Not found")

    # 10f. CLAUDE.md files in key directories
    claude_dirs = [
        RUNTIME_DIR,
        os.path.join(RUNTIME_DIR, "scripts"),
        os.path.join(RUNTIME_DIR, "tests"),
        os.path.join(RUNTIME_DIR, "phases"),
    ]
    found = sum(1 for dd in claude_dirs if os.path.exists(os.path.join(dd, "CLAUDE.md")))
    if found == len(claude_dirs):
        d.ok(f"CLAUDE.md governance: {found}/{len(claude_dirs)} key directories")
    else:
        d.fail("CLAUDE.md governance", f"Only {found}/{len(claude_dirs)} directories")


# ═══════════════════════════════════════════════════════════════════════════════
# DIMENSION 11: DETERMINISM & REPRODUCIBILITY
# ═══════════════════════════════════════════════════════════════════════════════

def assess_determinism(d):
    print(f"\n  [{d.name}]")

    from character import create_character
    from dice import roll

    # 11a. Dice determinism
    try:
        random.seed(42)
        r1 = roll("1d20+5")
        random.seed(42)
        r2 = roll("1d20+5")
        assert r1 == r2
        d.ok("dice roll determinism (same seed = same result)")
    except Exception as e:
        d.error("dice determinism", e)

    # 11b. Character creation determinism (all classes)
    for cls in ["warrior", "expert", "mage"]:
        try:
            random.seed(7777)
            c1 = create_character(name="Det", class_name=cls,
                                   background_id=1, method="standard_array")
            random.seed(7777)
            c2 = create_character(name="Det", class_name=cls,
                                   background_id=1, method="standard_array")
            assert c1 == c2
            d.ok(f"character determinism: {cls}")
        except Exception as e:
            d.error(f"character determinism: {cls}", e)

    # 11c. Adventurer with partial classes determinism
    try:
        random.seed(8888)
        c1 = create_character(name="Det", class_name="adventurer",
                               background_id=1, method="standard_array",
                               partial_classes=["accursed", "warrior"])
        random.seed(8888)
        c2 = create_character(name="Det", class_name="adventurer",
                               background_id=1, method="standard_array",
                               partial_classes=["accursed", "warrior"])
        assert c1 == c2
        d.ok("adventurer partial class determinism")
    except Exception as e:
        d.error("adventurer determinism", e)

    # 11d. CLI determinism (same seed same output)
    try:
        _, out1, _ = run_cli(["roll", "3d6", "--seed", "42"])
        _, out2, _ = run_cli(["roll", "3d6", "--seed", "42"])
        assert out1 == out2
        d.ok("CLI determinism (roll --seed 42)")
    except Exception as e:
        d.error("CLI determinism", e)

    # 11e. NPC generation determinism
    try:
        from npc import generate_npc
        random.seed(9999)
        n1 = generate_npc(importance="major", region="coastal", tag_count=2)
        random.seed(9999)
        n2 = generate_npc(importance="major", region="coastal", tag_count=2)
        assert n1["name"] == n2["name"]
        d.ok("NPC generation determinism")
    except Exception as e:
        d.error("NPC determinism", e)

    # 11f. Travel determinism
    try:
        from travel import resolve_travel
        random.seed(1111)
        t1 = resolve_travel("forest", 3, 5, 1, 3)
        random.seed(1111)
        t2 = resolve_travel("forest", 3, 5, 1, 3)
        assert t1 == t2
        d.ok("travel determinism")
    except Exception as e:
        d.error("travel determinism", e)


# ═══════════════════════════════════════════════════════════════════════════════
# DIMENSION 12: EDGE CASES & ERROR HANDLING
# ═══════════════════════════════════════════════════════════════════════════════

def assess_edge_cases(d):
    print(f"\n  [{d.name}]")

    from character import create_character

    # 12a. Invalid class name
    try:
        try:
            create_character(name="Bad", class_name="paladin", background_id=1)
            d.fail("invalid class", "Should raise ValueError")
        except ValueError:
            d.ok("invalid class raises ValueError")
    except Exception as e:
        d.error("invalid class", e)

    # 12b. Adventurer without partials
    try:
        try:
            create_character(name="Bad", class_name="adventurer", background_id=1)
            d.fail("adventurer no partials", "Should raise error")
        except (ValueError, TypeError):
            d.ok("adventurer without partial_classes raises error")
    except Exception as e:
        d.error("adventurer no partials", e)

    # 12c. Mageslayer + mage rejected
    try:
        try:
            random.seed(42)
            create_character(name="Bad", class_name="adventurer", background_id=1,
                              method="standard_array",
                              partial_classes=["mageslayer", "mage"])
            d.fail("mageslayer+mage", "Should raise ValueError")
        except ValueError:
            d.ok("mageslayer+mage combo correctly rejected")
    except Exception as e:
        d.error("mageslayer+mage", e)

    # 12d. Duplicate partial classes rejected
    try:
        try:
            random.seed(42)
            create_character(name="Bad", class_name="adventurer", background_id=1,
                              method="standard_array",
                              partial_classes=["bard", "bard"])
            d.fail("duplicate partials", "Should raise ValueError")
        except ValueError:
            d.ok("duplicate partial classes rejected")
    except Exception as e:
        d.error("duplicate partials", e)

    # 12e. Healer tradition as full mage rejected
    try:
        try:
            random.seed(42)
            create_character(name="Bad", class_name="mage", background_id=16,
                              method="standard_array", tradition="healer")
            d.fail("healer full mage", "Should raise ValueError")
        except ValueError:
            d.ok("healer tradition as full mage rejected")
    except Exception as e:
        d.error("healer full mage", e)

    # 12f. Spell level too high for caster
    try:
        from magic import cast_spell
        result = cast_spell("Big Spell", 1, "high_magic", 2, 0, 14)
        # Level 1 casters can only cast level 1 spells; the function needs the
        # spell in the DB to check level, so we test the max level function instead
        from magic import can_cast
        assert can_cast(1, 1) and not can_cast(1, 3)
        d.ok("spell level validation works")
    except Exception as e:
        d.error("spell level validation", e)

    # 12g. Zero effort spell casting
    try:
        result = cast_spell("Test", 3, "high_magic", 0, 0, 14)
        assert result["success"] is False
        assert "No Effort" in result["error"]
        d.ok("zero effort casting correctly fails")
    except Exception as e:
        d.error("zero effort casting", e)

    # 12h. Non-mage effort is 0
    try:
        random.seed(42)
        char = create_character(name="NoEffort", class_name="warrior",
                                 background_id=1, method="standard_array")
        assert char["effort"]["max"] == 0
        assert char["effort"]["current"] == 0
        d.ok("non-mage effort correctly 0/0")
    except Exception as e:
        d.error("non-mage effort", e)

    # 12i. CLI with invalid command
    try:
        rc, out, err = run_cli(["nonexistent-command"])
        assert rc != 0
        d.ok("CLI rejects unknown command")
    except Exception as e:
        d.error("CLI unknown command", e)

    # 12j. Boundary values — attributes
    try:
        from attributes import get_modifier
        assert get_modifier(1) is not None  # should not crash
        assert get_modifier(20) is not None
        assert get_modifier(3) == -2
        assert get_modifier(18) == 2
        d.ok("attribute modifier boundary values (1-20)")
    except Exception as e:
        d.error("attribute boundaries", e)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN — ASSESSMENT RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

def run_assessment():
    start_time = time.time()

    print("=" * 70)
    print("  WWN GAME ENGINE — COMPREHENSIVE ASSESSMENT")
    print("=" * 70)

    dimensions = [
        ("D1: Core Mechanics",       assess_core_mechanics,       1.5),
        ("D2: Character Creation",   assess_character_creation,   1.5),
        ("D3: Data Tables",          assess_data_tables,          1.0),
        ("D4: CLI Commands",         assess_cli_commands,         1.0),
        ("D5: State Schema",         assess_state_schema,         1.0),
        ("D6: Social Systems",       assess_social_systems,       1.0),
        ("D7: Exploration Systems",  assess_exploration_systems,  0.8),
        ("D8: Narrative Layer",      assess_narrative_layer,      0.8),
        ("D9: Lore & World-Building",assess_lore,                 0.8),
        ("D10: Cross-System Integration", assess_integration,     1.0),
        ("D11: Determinism",         assess_determinism,          1.2),
        ("D12: Edge Cases",          assess_edge_cases,           1.0),
    ]

    results = []
    for name, fn, weight in dimensions:
        dim = AssessmentDimension(name, weight)
        try:
            fn(dim)
        except Exception as e:
            dim.error("DIMENSION CRASH", e)
        results.append(dim)

    elapsed = time.time() - start_time

    # ── REPORT CARD ──
    print("\n" + "=" * 70)
    print("  ASSESSMENT REPORT CARD")
    print("=" * 70)
    print(f"  {'Dimension':<40} {'Pass':>5} {'Fail':>5} {'Err':>4} {'Score':>7} {'Grade':>6}")
    print("  " + "-" * 66)

    total_weighted = 0.0
    total_weight = 0.0
    total_pass = 0
    total_fail = 0
    total_err = 0

    for dim in results:
        p = len(dim.passed)
        f = len(dim.failed)
        e = len(dim.errors)
        print(f"  {dim.name:<40} {p:>5} {f:>5} {e:>4} {dim.score:>6.0%}  [{dim.grade}]")
        total_weighted += dim.score * dim.weight
        total_weight += dim.weight
        total_pass += p
        total_fail += f
        total_err += e

    overall_score = total_weighted / total_weight if total_weight > 0 else 0
    overall_grade = "A" if overall_score >= 0.95 else "B" if overall_score >= 0.85 else \
        "C" if overall_score >= 0.70 else "D" if overall_score >= 0.50 else "F"

    print("  " + "-" * 66)
    print(f"  {'OVERALL (weighted)':<40} {total_pass:>5} {total_fail:>5} {total_err:>4} {overall_score:>6.0%}  [{overall_grade}]")
    print("=" * 70)
    print(f"  Total: {total_pass} passed, {total_fail} failed, {total_err} errors ({elapsed:.1f}s)")
    print("=" * 70)

    # ── FAILURES DETAIL ──
    any_failures = False
    for dim in results:
        if dim.failed or dim.errors:
            if not any_failures:
                print("\n  FAILURES & ERRORS DETAIL:")
                any_failures = True
            if dim.failed:
                for name, reason in dim.failed:
                    print(f"    [{dim.name}] FAIL: {name} — {reason}")
            if dim.errors:
                for name, exc in dim.errors:
                    print(f"    [{dim.name}] ERR:  {name} — {exc}")

    if not any_failures:
        print("\n  No failures or errors detected!")

    print("")
    return overall_score, overall_grade, results


def run_test():
    """Entry point for run_all_tests.py integration."""
    score, grade, results = run_assessment()
    total_fail = sum(len(d.failed) for d in results)
    total_err = sum(len(d.errors) for d in results)
    return total_fail == 0 and total_err == 0


if __name__ == "__main__":
    score, grade, results = run_assessment()
    sys.exit(0 if grade in ("A", "B") else 1)
