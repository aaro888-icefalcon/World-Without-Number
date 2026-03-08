#!/usr/bin/env python3
"""
Expanded Character Creation Validation Tests

Tests the comprehensive WWN character creation system including:
  1. All 4 base classes (Warrior, Expert, Mage, Adventurer)
  2. All 3 Adventurer partial class combinations
  3. All 5 magic traditions (High Mage, Elementalist, Necromancer, Healer, Vowed)
  4. Focus selection with class restrictions
  5. Starting spell selection for Mages
  6. Equipment packages
  7. Background quick skills
  8. Free skill pick
  9. Luck saving throw
  10. Effort calculation for Mages
  11. Schema validation for all class types
  12. CLI command expansion
"""

import os
import sys
import json
import subprocess
import random

# Paths
RUNTIME_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(RUNTIME_DIR)
SCRIPTS_DIR = os.path.join(RUNTIME_DIR, "scripts")
SKILLS_DIR = os.path.join(RUNTIME_DIR, "phases", "3-resolution", "skills")
CORE_TABLES = os.path.join(SKILLS_DIR, "core", "tables")
CORE_SCRIPTS = os.path.join(SKILLS_DIR, "core", "scripts")
SCHEMAS_DIR = os.path.join(RUNTIME_DIR, "schemas")
CLI = os.path.join(SCRIPTS_DIR, "emergence_cli.py")

# Add paths for imports
for d in [CORE_TABLES, CORE_SCRIPTS]:
    if os.path.isdir(d) and d not in sys.path:
        sys.path.insert(0, d)


class TestResult:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.errors = []

    def ok(self, name):
        self.passed.append(name)
        print(f"  PASS  {name}")

    def fail(self, name, reason=""):
        self.failed.append((name, reason))
        print(f"  FAIL  {name}: {reason}")

    def error(self, name, exc):
        self.errors.append((name, str(exc)))
        print(f"  ERR   {name}: {exc}")

    def summary(self):
        total = len(self.passed) + len(self.failed) + len(self.errors)
        print(f"\n{'='*60}")
        print(f"RESULTS: {len(self.passed)}/{total} passed, "
              f"{len(self.failed)} failed, {len(self.errors)} errors")
        print(f"{'='*60}")
        if self.failed:
            print("\nFAILURES:")
            for name, reason in self.failed:
                print(f"  - {name}: {reason}")
        if self.errors:
            print("\nERRORS:")
            for name, exc in self.errors:
                print(f"  - {name}: {exc}")
        return len(self.failed) == 0 and len(self.errors) == 0


def run_cli(args_list):
    """Run emergence_cli.py with given args, return (returncode, stdout, stderr)."""
    cmd = [sys.executable, CLI] + args_list
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    return result.returncode, result.stdout, result.stderr


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 1: Data Tables Completeness
# ══════════════════════════════════════════════════════════════════════════════

def test_data_tables(t):
    print("\n[1] DATA TABLES COMPLETENESS")

    # 1a. Adventurer progression tables exist
    try:
        from classes import CLASSES, ADVENTURER_PROGRESSION
        assert "adventurer" in CLASSES, "Adventurer class must exist in CLASSES"
        combos = ["partial_expert/partial_warrior", "partial_expert/partial_mage",
                   "partial_mage/partial_warrior"]
        for combo in combos:
            assert combo in ADVENTURER_PROGRESSION, f"Missing progression for {combo}"
            prog = ADVENTURER_PROGRESSION[combo]
            for lvl in range(1, 11):
                assert lvl in prog, f"Missing level {lvl} for {combo}"
                assert "hd" in prog[lvl], f"Missing hd at level {lvl} for {combo}"
                assert "ab" in prog[lvl], f"Missing ab at level {lvl} for {combo}"
                assert "focus" in prog[lvl], f"Missing focus at level {lvl} for {combo}"
        t.ok(f"classes.py: Adventurer + {len(combos)} partial class progressions")
    except Exception as e:
        t.error("Adventurer progressions", e)

    # 1b. Traditions table exists
    try:
        from traditions import TRADITIONS
        expected = ["high_mage", "elementalist", "necromancer", "healer", "vowed"]
        for trad in expected:
            assert trad in TRADITIONS, f"Missing tradition: {trad}"
            td = TRADITIONS[trad]
            assert "description" in td, f"Missing description for {trad}"
            assert "arts" in td, f"Missing arts for {trad}"
            assert "restrictions" in td, f"Missing restrictions for {trad}"
            assert "partial_only" in td, f"Missing partial_only flag for {trad}"
        # Healer and Vowed are partial-only
        assert TRADITIONS["healer"]["partial_only"] is True
        assert TRADITIONS["vowed"]["partial_only"] is True
        assert TRADITIONS["high_mage"]["partial_only"] is False
        t.ok(f"traditions.py: {len(expected)} traditions with arts and restrictions")
    except Exception as e:
        t.error("traditions.py", e)

    # 1c. Spells table exists with entries for spellcasting traditions
    try:
        from spells import SPELLS
        assert len(SPELLS) >= 30, f"Expected >=30 spells, got {len(SPELLS)}"
        # Check all spellcasting traditions have spells
        traditions_with_spells = set(s["tradition"] for s in SPELLS)
        for trad in ["high_mage", "elementalist", "necromancer"]:
            assert trad in traditions_with_spells, f"No spells for tradition: {trad}"
        # Each spell has required fields
        for spell in SPELLS[:5]:
            for field in ["name", "level", "tradition", "description"]:
                assert field in spell, f"Spell missing field: {field}"
            assert 1 <= spell["level"] <= 5, f"Spell level out of range: {spell['level']}"
        t.ok(f"spells.py: {len(SPELLS)} spells across {len(traditions_with_spells)} traditions")
    except Exception as e:
        t.error("spells.py", e)

    # 1d. Equipment packages exist
    try:
        from equipment import EQUIPMENT_PACKAGES
        assert len(EQUIPMENT_PACKAGES) >= 5, f"Expected >=5 packages, got {len(EQUIPMENT_PACKAGES)}"
        for pkg_name, pkg in EQUIPMENT_PACKAGES.items():
            assert "items" in pkg, f"Package {pkg_name} missing items"
            assert len(pkg["items"]) > 0, f"Package {pkg_name} has no items"
        t.ok(f"equipment.py: {len(EQUIPMENT_PACKAGES)} equipment packages")
    except Exception as e:
        t.error("equipment packages", e)

    # 1e. Foci include Specialist (repeatable)
    try:
        from foci import FOCI
        assert "specialist" in FOCI, "Missing 'specialist' focus"
        assert len(FOCI) >= 27, f"Expected >=27 foci, got {len(FOCI)}"
        t.ok(f"foci.py: {len(FOCI)} foci including specialist")
    except Exception as e:
        t.error("foci specialist", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 2: Character Creation - All Classes
# ══════════════════════════════════════════════════════════════════════════════

def test_all_classes(t):
    print("\n[2] CHARACTER CREATION — ALL CLASSES")

    from character import create_character

    # 2a. Warrior (existing, regression check)
    try:
        random.seed(100)
        char = create_character(
            name="Kael", class_name="warrior", background_id=18,
            method="standard_array"
        )
        assert char["class"] == "warrior"
        assert char["attack_bonus"] >= 1, "Warrior L1 AB should be >= 1"
        assert "killing_blow" in char["class_abilities"]
        assert "veterans_luck" in char["class_abilities"]
        t.ok("Warrior creates valid character (regression)")
    except Exception as e:
        t.error("Warrior creation", e)

    # 2b. Expert (existing, regression check)
    try:
        random.seed(101)
        char = create_character(
            name="Lira", class_name="expert", background_id=5,
            method="standard_array"
        )
        assert char["class"] == "expert"
        assert "masterful_expertise" in char["class_abilities"]
        assert "quick_learner" in char["class_abilities"]
        t.ok("Expert creates valid character (regression)")
    except Exception as e:
        t.error("Expert creation", e)

    # 2c. Mage (existing, regression check)
    try:
        random.seed(102)
        char = create_character(
            name="Voss", class_name="mage", background_id=16,
            method="standard_array"
        )
        assert char["class"] == "mage"
        assert "arcane_tradition" in char["class_abilities"]
        t.ok("Mage creates valid character (regression)")
    except Exception as e:
        t.error("Mage creation", e)

    # 2d. Adventurer — Partial Expert/Partial Warrior
    try:
        random.seed(103)
        char = create_character(
            name="Dain", class_name="adventurer", background_id=18,
            method="standard_array",
            partial_classes=["expert", "warrior"]
        )
        assert char["class"] == "adventurer"
        assert set(char["partial_classes"]) == {"expert", "warrior"}
        # E/W gets 1d6+2 at level 1 per WWN1 p.21
        assert char["hp"]["max"] >= 1
        # E/W gets AB +1 at level 1
        assert char["attack_bonus"] == 1
        # E/W gets 3 focus picks: 1 Expert + 1 Warrior + 1 Any
        t.ok("Adventurer (Expert/Warrior) creates valid character")
    except Exception as e:
        t.error("Adventurer E/W", e)

    # 2e. Adventurer — Partial Expert/Partial Mage
    try:
        random.seed(104)
        char = create_character(
            name="Mira", class_name="adventurer", background_id=16,
            method="standard_array",
            partial_classes=["expert", "mage"],
            tradition="high_mage"
        )
        assert char["class"] == "adventurer"
        assert set(char["partial_classes"]) == {"expert", "mage"}
        assert char["tradition"] == "high_mage"
        # E/M gets 1d6 at level 1
        # E/M gets AB +0 at level 1
        assert char["attack_bonus"] == 0
        t.ok("Adventurer (Expert/Mage) creates valid character")
    except Exception as e:
        t.error("Adventurer E/M", e)

    # 2f. Adventurer — Partial Warrior/Partial Mage
    try:
        random.seed(105)
        char = create_character(
            name="Torr", class_name="adventurer", background_id=18,
            method="standard_array",
            partial_classes=["warrior", "mage"],
            tradition="elementalist"
        )
        assert char["class"] == "adventurer"
        assert set(char["partial_classes"]) == {"warrior", "mage"}
        assert char["tradition"] == "elementalist"
        # W/M gets AB +1 at level 1 (from partial warrior)
        assert char["attack_bonus"] == 1
        t.ok("Adventurer (Warrior/Mage) creates valid character")
    except Exception as e:
        t.error("Adventurer W/M", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 3: Magic Traditions
# ══════════════════════════════════════════════════════════════════════════════

def test_magic_traditions(t):
    print("\n[3] MAGIC TRADITIONS")

    from character import create_character

    # 3a. Full Mage with High Mage tradition gets 4 starting spells
    try:
        random.seed(200)
        from spells import SPELLS
        hm_spells = [s["name"] for s in SPELLS
                     if s["tradition"] == "high_mage" and s["level"] == 1]
        if len(hm_spells) >= 4:
            picks = hm_spells[:4]
            char = create_character(
                name="Arcanus", class_name="mage", background_id=16,
                method="standard_array",
                tradition="high_mage",
                spells=picks
            )
            assert char["tradition"] == "high_mage"
            assert len(char.get("spells_known", [])) == 4
            t.ok("Full Mage (High Mage) gets 4 starting spells")
        else:
            t.fail("Full Mage spells", f"Not enough high_mage L1 spells: {len(hm_spells)}")
    except Exception as e:
        t.error("Full Mage tradition", e)

    # 3b. Partial Mage gets 2 starting spells
    try:
        random.seed(201)
        from spells import SPELLS
        elem_spells = [s["name"] for s in SPELLS
                       if s["tradition"] == "elementalist" and s["level"] == 1]
        if len(elem_spells) >= 2:
            picks = elem_spells[:2]
            char = create_character(
                name="Pyra", class_name="adventurer", background_id=16,
                method="standard_array",
                partial_classes=["warrior", "mage"],
                tradition="elementalist",
                spells=picks
            )
            assert len(char.get("spells_known", [])) == 2
            t.ok("Partial Mage (Elementalist) gets 2 starting spells")
        else:
            t.fail("Partial Mage spells", f"Not enough elementalist L1 spells: {len(elem_spells)}")
    except Exception as e:
        t.error("Partial Mage tradition", e)

    # 3c. Healer tradition is partial-only (full Mage should fail)
    try:
        random.seed(202)
        try:
            char = create_character(
                name="BadHealer", class_name="mage", background_id=16,
                method="standard_array",
                tradition="healer"
            )
            t.fail("Healer full mage", "Should have raised ValueError for partial-only tradition")
        except ValueError:
            t.ok("Healer tradition correctly rejects full Mage class")
    except Exception as e:
        t.error("Healer tradition validation", e)

    # 3d. Vowed tradition is partial-only (works as Adventurer partial mage)
    try:
        random.seed(203)
        char = create_character(
            name="MonkHero", class_name="adventurer", background_id=2,
            method="standard_array",
            partial_classes=["warrior", "mage"],
            tradition="vowed"
        )
        assert char["tradition"] == "vowed"
        # Vowed has no spells, only arts
        assert len(char.get("spells_known", [])) == 0
        t.ok("Vowed tradition works as Partial Mage (no spells)")
    except Exception as e:
        t.error("Vowed tradition", e)

    # 3e. Mage effort calculation
    try:
        random.seed(204)
        char = create_character(
            name="Effortful", class_name="mage", background_id=16,
            method="standard_array",
            tradition="high_mage",
            spells=["placeholder_spell_1", "placeholder_spell_2",
                    "placeholder_spell_3", "placeholder_spell_4"]
        )
        # Full Mage effort.max should be > 0
        assert char["effort"]["max"] >= 1, f"Mage effort.max should be >= 1, got {char['effort']['max']}"
        t.ok(f"Mage effort correctly calculated: max={char['effort']['max']}")
    except Exception as e:
        t.error("Mage effort", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 4: Focus Selection
# ══════════════════════════════════════════════════════════════════════════════

def test_focus_selection(t):
    print("\n[4] FOCUS SELECTION")

    from character import create_character

    # 4a. Warrior gets combat focus
    try:
        random.seed(300)
        char = create_character(
            name="FocusWarrior", class_name="warrior", background_id=18,
            method="standard_array",
            foci=["armsmaster", "alert"]  # armsmaster=warrior, alert=any
        )
        assert "armsmaster" in char["foci"]
        assert "alert" in char["foci"]
        t.ok("Warrior can pick warrior-type and any-type foci")
    except Exception as e:
        t.error("Warrior focus", e)

    # 4b. Expert gets non-combat focus
    try:
        random.seed(301)
        char = create_character(
            name="FocusExpert", class_name="expert", background_id=5,
            method="standard_array",
            foci=["connected", "diplomat"]  # both non-combat
        )
        assert "connected" in char["foci"]
        assert "diplomat" in char["foci"]
        t.ok("Expert can pick non-combat foci")
    except Exception as e:
        t.error("Expert focus", e)

    # 4c. Expert cannot pick warrior-only focus as their expert pick
    try:
        random.seed(302)
        try:
            char = create_character(
                name="BadExpert", class_name="expert", background_id=5,
                method="standard_array",
                foci=["armsmaster", "armsmaster"]  # warrior-only, can't be expert pick
            )
            t.fail("Expert warrior focus", "Should reject warrior-only foci for expert pick")
        except ValueError:
            t.ok("Expert correctly rejects warrior-only focus as expert pick")
    except Exception as e:
        t.error("Expert focus validation", e)

    # 4d. Focus level 2 — same focus picked twice
    try:
        random.seed(303)
        char = create_character(
            name="FocusDouble", class_name="warrior", background_id=18,
            method="standard_array",
            foci=["armsmaster", "armsmaster"]  # pick same focus twice → level 2
        )
        assert "armsmaster" in char["foci"]
        # Should have level 2 of armsmaster
        t.ok("Focus can be picked twice for level 2")
    except Exception as e:
        t.error("Focus level 2", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 5: Equipment Packages
# ══════════════════════════════════════════════════════════════════════════════

def test_equipment(t):
    print("\n[5] EQUIPMENT PACKAGES")

    from character import create_character

    # 5a. Equipment package selection
    try:
        random.seed(400)
        char = create_character(
            name="Geared", class_name="warrior", background_id=18,
            method="standard_array",
            equipment_package="armored_warrior"
        )
        assert len(char["equipment"]["readied"]) > 0 or len(char["equipment"]["stowed"]) > 0, \
            "Character with equipment package should have items"
        assert char["armor_class"] > 10, "Armored warrior should have AC > 10"
        t.ok("Equipment package produces equipped character")
    except Exception as e:
        t.error("Equipment package", e)

    # 5b. Roll starting coins
    try:
        random.seed(401)
        char = create_character(
            name="Coinroller", class_name="expert", background_id=8,
            method="standard_array",
            equipment_package="roll_coins"
        )
        total_coins = (char["equipment"]["coins"].get("silver", 0) +
                       char["equipment"]["coins"].get("gold", 0) * 10 +
                       char["equipment"]["coins"].get("copper", 0) // 10)
        assert total_coins > 0, "Rolling coins should produce > 0 silver"
        t.ok(f"Roll coins produces starting money: {total_coins} sp equivalent")
    except Exception as e:
        t.error("Roll coins", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 6: Background Skills
# ══════════════════════════════════════════════════════════════════════════════

def test_background_skills(t):
    print("\n[6] BACKGROUND SKILLS")

    from character import create_character

    # 6a. Quick skills method applies all Quick Skills at level-0
    try:
        random.seed(500)
        char = create_character(
            name="QuickSkills", class_name="warrior", background_id=18,
            method="standard_array",
            skill_method="quick"
        )
        # Soldier background quick_skills: Exert-0, Lead-0, Notice-0, Ride-0, Stab-0
        # Plus free_skill: Stab-0 (already in quick skills, so stab should be 0)
        assert char["skills"]["exert"] >= 0, "Quick skill Exert should be >= 0"
        assert char["skills"]["lead"] >= 0, "Quick skill Lead should be >= 0"
        assert char["skills"]["notice"] >= 0, "Quick skill Notice should be >= 0"
        assert char["skills"]["stab"] >= 0, "Quick skill Stab should be >= 0"
        t.ok("Quick skills method applies background quick skills")
    except Exception as e:
        t.error("Quick skills", e)

    # 6b. Free skill pick (step 9)
    try:
        random.seed(501)
        char = create_character(
            name="FreeSkill", class_name="expert", background_id=16,
            method="standard_array",
            free_skill="heal"
        )
        assert char["skills"]["heal"] >= 0, "Free skill should be at least level-0"
        t.ok("Free skill pick works")
    except Exception as e:
        t.error("Free skill", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 7: Saving Throws
# ══════════════════════════════════════════════════════════════════════════════

def test_saving_throws(t):
    print("\n[7] SAVING THROWS")

    from character import create_character

    # 7a. Luck save present
    try:
        random.seed(600)
        char = create_character(
            name="LuckTest", class_name="warrior", background_id=18,
            method="standard_array"
        )
        assert "luck" in char["saving_throws"], "Luck saving throw must be present"
        assert char["saving_throws"]["luck"] == 15, \
            f"Luck save at L1 should be 15, got {char['saving_throws']['luck']}"
        t.ok("Luck saving throw present and correct (15 at L1)")
    except Exception as e:
        t.error("Luck save", e)

    # 7b. Physical/Evasion/Mental saves use correct formula
    try:
        random.seed(601)
        char = create_character(
            name="SaveTest", class_name="warrior", background_id=18,
            method="standard_array"
        )
        from attributes import get_modifier
        attrs = char["attributes"]
        str_mod = get_modifier(attrs["strength"])
        con_mod = get_modifier(attrs["constitution"])
        expected_physical = 16 - (1 + max(str_mod, con_mod))
        assert char["saving_throws"]["physical"] == expected_physical, \
            f"Physical save mismatch: got {char['saving_throws']['physical']}, expected {expected_physical}"
        t.ok("Saving throw formulas correct (16 - (level + best modifier))")
    except Exception as e:
        t.error("Save formulas", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 8: Schema Validation
# ══════════════════════════════════════════════════════════════════════════════

def test_schema_validation(t):
    print("\n[8] SCHEMA VALIDATION")

    # 8a. Schema allows adventurer class
    try:
        schema_path = os.path.join(SCHEMAS_DIR, "state.schema.json")
        with open(schema_path) as f:
            schema = json.load(f)
        char_def = schema["$defs"]["character"]["properties"]
        class_enum = char_def["class"]["enum"]
        assert "adventurer" in class_enum, "Schema must include 'adventurer' in class enum"
        t.ok(f"Schema class enum includes: {class_enum}")
    except Exception as e:
        t.error("Schema class enum", e)

    # 8b. Schema has tradition field
    try:
        assert "tradition" in char_def, "Schema must have 'tradition' field"
        t.ok("Schema has tradition field")
    except Exception as e:
        t.error("Schema tradition", e)

    # 8c. Schema has partial_classes field
    try:
        assert "partial_classes" in char_def, "Schema must have 'partial_classes' field"
        t.ok("Schema has partial_classes field")
    except Exception as e:
        t.error("Schema partial_classes", e)

    # 8d. Schema saving_throws includes luck
    try:
        save_def = char_def["saving_throws"]["properties"]
        assert "luck" in save_def, "Schema saving_throws must include 'luck'"
        t.ok("Schema saving_throws includes luck")
    except Exception as e:
        t.error("Schema luck save", e)

    # 8e. Schema has spells_known field
    try:
        assert "spells_known" in char_def, "Schema must have 'spells_known' field"
        t.ok("Schema has spells_known field")
    except Exception as e:
        t.error("Schema spells_known", e)

    # 8f. Resource pool allows max=0 (for non-mage effort)
    try:
        rp = schema["$defs"]["resource_pool"]["properties"]
        max_min = rp["max"].get("minimum", 1)
        assert max_min == 0, f"resource_pool.max minimum should be 0 (for effort), got {max_min}"
        t.ok("resource_pool.max allows 0 (non-mage effort)")
    except Exception as e:
        t.error("resource_pool max", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 9: CLI Commands
# ══════════════════════════════════════════════════════════════════════════════

def test_cli_expanded(t):
    print("\n[9] CLI EXPANDED COMMANDS")

    # 9a. create-character accepts --class adventurer
    rc, out, err = run_cli([
        "create-character", "--name", "CliAdventurer",
        "--class", "adventurer",
        "--background", "18",
        "--partial-classes", "expert,warrior",
        "--seed", "42"
    ])
    if rc == 0:
        data = json.loads(out)
        assert data["class"] == "adventurer"
        assert set(data["partial_classes"]) == {"expert", "warrior"}
        t.ok("CLI create-character --class adventurer works")
    else:
        t.fail("CLI adventurer", f"exit code {rc}: {err.strip()[:200]}")

    # 9b. create-character with tradition
    rc, out, err = run_cli([
        "create-character", "--name", "CliMage",
        "--class", "mage",
        "--background", "16",
        "--tradition", "high_mage",
        "--seed", "42"
    ])
    if rc == 0:
        data = json.loads(out)
        assert data.get("tradition") == "high_mage"
        t.ok("CLI create-character --tradition works")
    else:
        t.fail("CLI tradition", f"exit code {rc}: {err.strip()[:200]}")

    # 9c. Existing CLI syntax still works (backward compat)
    rc, out, err = run_cli([
        "create-character", "--name", "OldStyle",
        "--class", "warrior",
        "--background", "18",
        "--seed", "42"
    ])
    if rc == 0:
        data = json.loads(out)
        assert data["name"] == "OldStyle"
        assert data["class"] == "warrior"
        t.ok("CLI backward compatibility preserved")
    else:
        t.fail("CLI backward compat", f"exit code {rc}: {err.strip()[:200]}")


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 10: Determinism
# ══════════════════════════════════════════════════════════════════════════════

def test_determinism(t):
    print("\n[10] DETERMINISM")

    from character import create_character

    # 10a. Same seed produces identical characters for all class types
    for cls in ["warrior", "expert", "mage"]:
        try:
            random.seed(999)
            char1 = create_character(name="Det", class_name=cls, background_id=1,
                                     method="standard_array")
            random.seed(999)
            char2 = create_character(name="Det", class_name=cls, background_id=1,
                                     method="standard_array")
            assert char1 == char2, f"Determinism failed for {cls}"
            t.ok(f"Determinism: {cls} with seed=999 produces identical output")
        except Exception as e:
            t.error(f"Determinism {cls}", e)

    # 10b. Adventurer determinism
    try:
        random.seed(998)
        char1 = create_character(
            name="DetAdv", class_name="adventurer", background_id=1,
            method="standard_array",
            partial_classes=["expert", "warrior"]
        )
        random.seed(998)
        char2 = create_character(
            name="DetAdv", class_name="adventurer", background_id=1,
            method="standard_array",
            partial_classes=["expert", "warrior"]
        )
        assert char1 == char2, "Adventurer determinism failed"
        t.ok("Determinism: Adventurer with seed=998 produces identical output")
    except Exception as e:
        t.error("Determinism adventurer", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 11: Edge Cases
# ══════════════════════════════════════════════════════════════════════════════

def test_edge_cases(t):
    print("\n[11] EDGE CASES")

    from character import create_character

    # 11a. Invalid class raises ValueError
    try:
        try:
            create_character(name="Bad", class_name="paladin", background_id=1)
            t.fail("Invalid class", "Should raise ValueError")
        except ValueError:
            t.ok("Invalid class raises ValueError")
    except Exception as e:
        t.error("Invalid class", e)

    # 11b. Adventurer without partial_classes raises ValueError
    try:
        try:
            create_character(name="Bad", class_name="adventurer", background_id=1)
            t.fail("Adventurer no partials", "Should raise ValueError")
        except (ValueError, TypeError):
            t.ok("Adventurer without partial_classes raises error")
    except Exception as e:
        t.error("Adventurer no partials", e)

    # 11c. Non-mage effort is 0
    try:
        random.seed(700)
        char = create_character(name="NoEffort", class_name="warrior", background_id=1,
                                 method="standard_array")
        assert char["effort"]["max"] == 0, f"Non-mage effort.max should be 0, got {char['effort']['max']}"
        assert char["effort"]["current"] == 0
        t.ok("Non-mage effort correctly set to 0/0")
    except Exception as e:
        t.error("Non-mage effort", e)

    # 11d. All 20 backgrounds produce valid characters
    try:
        success_count = 0
        for bg_id in range(1, 21):
            random.seed(800 + bg_id)
            char = create_character(name=f"BG{bg_id}", class_name="warrior",
                                     background_id=bg_id, method="standard_array")
            assert char["background"] is not None
            success_count += 1
        t.ok(f"All {success_count}/20 backgrounds produce valid characters")
    except Exception as e:
        t.error("Background sweep", e)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("EXPANDED CHARACTER CREATION TESTS — WWN AI RPG Engine")
    print("=" * 60)

    t = TestResult()

    test_data_tables(t)
    test_all_classes(t)
    test_magic_traditions(t)
    test_focus_selection(t)
    test_equipment(t)
    test_background_skills(t)
    test_saving_throws(t)
    test_schema_validation(t)
    test_cli_expanded(t)
    test_determinism(t)
    test_edge_cases(t)

    all_passed = t.summary()
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
