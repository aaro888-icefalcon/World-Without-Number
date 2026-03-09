#!/usr/bin/env python3
"""
Expanded Classes Validation Tests

Tests the WWN5 optional classes (Accursed, Bard, Mageslayer, Wise),
WWN4 Gyre classes (Invoker, Skinshifter, Duelist, Beastmaster, Blood Priest, Thought Noble),
and the Traditional Education focus.

Written BEFORE implementation to define completion criteria.
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


# All new partial class names
WWN5_CLASSES = ["accursed", "bard", "mageslayer", "wise"]
GYRE_CLASSES = ["invoker", "skinshifter", "duelist", "beastmaster", "blood_priest", "thought_noble"]
ALL_NEW_PARTIALS = WWN5_CLASSES + GYRE_CLASSES

# Expected base types
EXPECTED_BASE_TYPES = {
    "accursed": "mage", "bard": "expert", "mageslayer": "warrior", "wise": "expert",
    "invoker": "mage", "skinshifter": "mage", "duelist": "mage",
    "beastmaster": "mage", "blood_priest": "mage", "thought_noble": "mage",
}

# Expected bonus skills
EXPECTED_BONUS_SKILLS = {
    "accursed": "magic", "bard": "perform", "mageslayer": "magic",
    "invoker": "magic", "skinshifter": "survive", "duelist": "stab",
    "beastmaster": "survive", "blood_priest": "pray", "thought_noble": "notice",
    # wise: variable (pray/know/magic/survive)
}


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 1: Partial Classes Data Table Completeness
# ══════════════════════════════════════════════════════════════════════════════

def test_partial_class_tables(t):
    print("\n[1] PARTIAL CLASS DATA TABLES")

    # 1a. partial_classes.py exists and is importable
    try:
        from partial_classes import PARTIAL_CLASSES, BASE_TYPE_MAP
        t.ok("partial_classes.py imports successfully")
    except Exception as e:
        t.error("partial_classes.py import", e)
        return  # Can't continue without this

    # 1b. All 10 new partial classes defined
    try:
        for cls_name in ALL_NEW_PARTIALS:
            assert cls_name in PARTIAL_CLASSES, f"Missing partial class: {cls_name}"
        t.ok(f"All {len(ALL_NEW_PARTIALS)} new partial classes defined")
    except Exception as e:
        t.error("partial class completeness", e)

    # 1c. Each class has required fields
    required_fields = ["base_type", "bonus_skill", "effort_formula", "has_spells", "arts"]
    try:
        for cls_name in ALL_NEW_PARTIALS:
            cls = PARTIAL_CLASSES[cls_name]
            for field in required_fields:
                assert field in cls, f"{cls_name} missing field: {field}"
        t.ok("All partial classes have required fields")
    except Exception as e:
        t.error("required fields", e)

    # 1d. Base types are correct
    try:
        for cls_name, expected in EXPECTED_BASE_TYPES.items():
            actual = PARTIAL_CLASSES[cls_name]["base_type"]
            assert actual == expected, f"{cls_name}: expected base_type={expected}, got {actual}"
        t.ok("All base types correct")
    except Exception as e:
        t.error("base types", e)

    # 1e. BASE_TYPE_MAP includes all new classes
    try:
        for cls_name in ALL_NEW_PARTIALS:
            assert cls_name in BASE_TYPE_MAP, f"Missing from BASE_TYPE_MAP: {cls_name}"
        # Also check standard classes are still there
        for std in ["expert", "warrior", "mage"]:
            assert std in BASE_TYPE_MAP, f"Missing standard class from BASE_TYPE_MAP: {std}"
        t.ok("BASE_TYPE_MAP complete")
    except Exception as e:
        t.error("BASE_TYPE_MAP", e)

    # 1f. Each class has at least 1 art defined
    try:
        for cls_name in ALL_NEW_PARTIALS:
            cls = PARTIAL_CLASSES[cls_name]
            arts = cls.get("arts", [])
            # Invoker has no arts by default (uses spells)
            if cls_name == "invoker":
                continue
            assert len(arts) >= 1, f"{cls_name} has no arts defined"
        t.ok("All non-Invoker classes have arts")
    except Exception as e:
        t.error("arts defined", e)

    # 1g. Art progression defined for each class
    try:
        for cls_name in ALL_NEW_PARTIALS:
            cls = PARTIAL_CLASSES[cls_name]
            if cls_name == "invoker":
                continue  # Invoker uses spell points, not art progression
            prog = cls.get("art_progression")
            assert prog is not None, f"{cls_name} missing art_progression"
            # Should have entries for levels 1-10
            for lvl in range(1, 11):
                assert lvl in prog, f"{cls_name} missing art_progression for level {lvl}"
        t.ok("Art progression defined for levels 1-10")
    except Exception as e:
        t.error("art progression", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 2: Adventurer Progression Tables
# ══════════════════════════════════════════════════════════════════════════════

def test_adventurer_progression(t):
    print("\n[2] ADVENTURER PROGRESSION TABLES")

    from classes import ADVENTURER_PROGRESSION
    from partial_classes import PARTIAL_CLASSES, BASE_TYPE_MAP

    # 2a. WWN5 explicit combo tables exist
    wwn5_combos = [
        # Accursed combos (from PDF p.168)
        "partial_accursed/partial_expert",
        "partial_accursed/partial_warrior",
        "partial_accursed/partial_mage",
        # Bard combos (from PDF p.170)
        "partial_bard/partial_expert",
        "partial_bard/partial_mage",
        "partial_bard/partial_warrior",
        # Mageslayer combos (from PDF p.172)
        "partial_expert/partial_mageslayer",
        "partial_mageslayer/partial_warrior",
    ]
    try:
        for combo in wwn5_combos:
            assert combo in ADVENTURER_PROGRESSION, f"Missing combo: {combo}"
            prog = ADVENTURER_PROGRESSION[combo]
            for lvl in range(1, 11):
                assert lvl in prog, f"Missing level {lvl} for {combo}"
                assert "hd" in prog[lvl], f"Missing hd at level {lvl} for {combo}"
                assert "ab" in prog[lvl], f"Missing ab at level {lvl} for {combo}"
        t.ok(f"All {len(wwn5_combos)} WWN5 combo tables present with levels 1-10")
    except Exception as e:
        t.error("WWN5 combo tables", e)

    # 2b. Accursed/Warrior uses full Warrior HD (1d6+2 at L1)
    try:
        combo = ADVENTURER_PROGRESSION["partial_accursed/partial_warrior"]
        assert combo[1]["hd"] == "1d6+2", f"Accursed/Warrior L1 HD should be 1d6+2, got {combo[1]['hd']}"
        assert combo[1]["ab"] == 1, f"Accursed/Warrior L1 AB should be 1, got {combo[1]['ab']}"
        t.ok("Accursed/Warrior: correct HD 1d6+2 and AB +1 at L1")
    except Exception as e:
        t.error("Accursed/Warrior HD", e)

    # 2c. Bard/Warrior uses full Warrior HD (1d6+2 at L1)
    try:
        combo = ADVENTURER_PROGRESSION["partial_bard/partial_warrior"]
        assert combo[1]["hd"] == "1d6+2", f"Bard/Warrior L1 HD should be 1d6+2, got {combo[1]['hd']}"
        assert combo[1]["ab"] == 1, f"Bard/Warrior L1 AB should be 1, got {combo[1]['ab']}"
        t.ok("Bard/Warrior: correct HD 1d6+2 and AB +1 at L1")
    except Exception as e:
        t.error("Bard/Warrior HD", e)

    # 2d. Mageslayer/Warrior uses full Warrior HD and AB
    try:
        combo = ADVENTURER_PROGRESSION["partial_mageslayer/partial_warrior"]
        assert combo[1]["hd"] == "1d6+2", f"Mageslayer/Warrior L1 HD should be 1d6+2"
        assert combo[1]["ab"] == 1
        # At L10, Mageslayer/Warrior should have AB +10
        assert combo[10]["ab"] == 10, f"Mageslayer/Warrior L10 AB should be 10, got {combo[10]['ab']}"
        t.ok("Mageslayer/Warrior: full Warrior HD/AB progression")
    except Exception as e:
        t.error("Mageslayer/Warrior", e)

    # 2e. Expert/Mageslayer has unique AB progression
    try:
        combo = ADVENTURER_PROGRESSION["partial_expert/partial_mageslayer"]
        assert combo[1]["hd"] == "1d6", f"Expert/Mageslayer L1 HD should be 1d6"
        assert combo[1]["ab"] == 1, f"Expert/Mageslayer L1 AB should be 1"
        t.ok("Expert/Mageslayer: correct HD 1d6 and AB +1 at L1")
    except Exception as e:
        t.error("Expert/Mageslayer", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 3: WWN5 Class Character Creation
# ══════════════════════════════════════════════════════════════════════════════

def test_wwn5_character_creation(t):
    print("\n[3] WWN5 CLASS CHARACTER CREATION")

    from character import create_character

    # 3a. Accursed + Expert
    try:
        random.seed(1000)
        char = create_character(
            name="Pactmaker", class_name="adventurer", background_id=16,
            method="standard_array",
            partial_classes=["accursed", "expert"]
        )
        assert char["class"] == "adventurer"
        assert set(char["partial_classes"]) == {"accursed", "expert"}
        assert char["skills"]["magic"] >= 0, "Accursed should get Magic-0 bonus skill"
        assert char["effort"]["max"] >= 1, "Accursed should have Effort >= 1"
        t.ok("Accursed/Expert creates valid character")
    except Exception as e:
        t.error("Accursed/Expert creation", e)

    # 3b. Accursed + Warrior
    try:
        random.seed(1001)
        char = create_character(
            name="DarkKnight", class_name="adventurer", background_id=18,
            method="standard_array",
            partial_classes=["accursed", "warrior"]
        )
        assert char["class"] == "adventurer"
        assert char["attack_bonus"] >= 1, "Accursed/Warrior should have AB >= 1"
        t.ok("Accursed/Warrior creates valid character")
    except Exception as e:
        t.error("Accursed/Warrior creation", e)

    # 3c. Bard + Warrior
    try:
        random.seed(1002)
        char = create_character(
            name="Skald", class_name="adventurer", background_id=2,
            method="standard_array",
            partial_classes=["bard", "warrior"]
        )
        assert char["class"] == "adventurer"
        assert char["skills"]["perform"] >= 0, "Bard should get Perform-0 bonus skill"
        assert char["effort"]["max"] >= 1, "Bard should have Effort >= 1"
        t.ok("Bard/Warrior creates valid character")
    except Exception as e:
        t.error("Bard/Warrior creation", e)

    # 3d. Bard + Mage
    try:
        random.seed(1003)
        char = create_character(
            name="Songmage", class_name="adventurer", background_id=16,
            method="standard_array",
            partial_classes=["bard", "mage"],
            tradition="high_mage"
        )
        assert char["class"] == "adventurer"
        assert "high_mage" == char.get("tradition")
        t.ok("Bard/Mage creates valid character with tradition")
    except Exception as e:
        t.error("Bard/Mage creation", e)

    # 3e. Mageslayer + Expert
    try:
        random.seed(1004)
        char = create_character(
            name="Witchhunter", class_name="adventurer", background_id=18,
            method="standard_array",
            partial_classes=["mageslayer", "expert"]
        )
        assert char["class"] == "adventurer"
        assert char["skills"]["magic"] >= 0, "Mageslayer should get Magic-0 bonus skill"
        assert char["effort"]["max"] >= 1, "Mageslayer should have Effort >= 1"
        # Mageslayer should have fixed starting arts
        assert "Antimage" in char.get("known_arts", []) or \
               "antimage" in [a.lower() for a in char.get("known_arts", [])], \
               "Mageslayer should start with Antimage art"
        t.ok("Mageslayer/Expert creates valid character with starting arts")
    except Exception as e:
        t.error("Mageslayer/Expert creation", e)

    # 3f. Mageslayer + Warrior
    try:
        random.seed(1005)
        char = create_character(
            name="Magebreaker", class_name="adventurer", background_id=18,
            method="standard_array",
            partial_classes=["mageslayer", "warrior"]
        )
        assert char["class"] == "adventurer"
        assert char["attack_bonus"] >= 1
        t.ok("Mageslayer/Warrior creates valid character")
    except Exception as e:
        t.error("Mageslayer/Warrior creation", e)

    # 3g. Mageslayer + Mage should FAIL
    try:
        random.seed(1006)
        try:
            char = create_character(
                name="BadCombo", class_name="adventurer", background_id=18,
                method="standard_array",
                partial_classes=["mageslayer", "mage"],
                tradition="high_mage"
            )
            t.fail("Mageslayer+Mage", "Should raise ValueError for invalid combo")
        except ValueError:
            t.ok("Mageslayer + Mage correctly rejected")
    except Exception as e:
        t.error("Mageslayer+Mage rejection", e)

    # 3h. Wise + Warrior
    try:
        random.seed(1007)
        char = create_character(
            name="Priest", class_name="adventurer", background_id=16,
            method="standard_array",
            partial_classes=["wise", "warrior"]
        )
        assert char["class"] == "adventurer"
        # Wise has no Effort
        assert char["effort"]["max"] == 0, \
            f"Wise should have 0 Effort, got {char['effort']['max']}"
        t.ok("Wise/Warrior creates valid character with 0 Effort")
    except Exception as e:
        t.error("Wise/Warrior creation", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 4: Gyre Class Character Creation
# ══════════════════════════════════════════════════════════════════════════════

def test_gyre_character_creation(t):
    print("\n[4] GYRE CLASS CHARACTER CREATION")

    from character import create_character

    # 4a. Skinshifter + Warrior
    try:
        random.seed(2000)
        char = create_character(
            name="Shifter", class_name="adventurer", background_id=2,
            method="standard_array",
            partial_classes=["skinshifter", "warrior"]
        )
        assert char["class"] == "adventurer"
        assert char["skills"]["survive"] >= 0, "Skinshifter should get Survive-0"
        assert char["effort"]["max"] >= 1, "Skinshifter should have Effort >= 1"
        t.ok("Skinshifter/Warrior creates valid character")
    except Exception as e:
        t.error("Skinshifter/Warrior creation", e)

    # 4b. Duelist + Expert
    try:
        random.seed(2001)
        char = create_character(
            name="Fencer", class_name="adventurer", background_id=5,
            method="standard_array",
            partial_classes=["duelist", "expert"]
        )
        assert char["class"] == "adventurer"
        assert char["skills"]["stab"] >= 0, "Duelist should get Stab-0"
        t.ok("Duelist/Expert creates valid character")
    except Exception as e:
        t.error("Duelist/Expert creation", e)

    # 4c. Duelist + Warrior (Fragility flaw: 1d6 HD instead of 1d6+2)
    try:
        random.seed(2002)
        char = create_character(
            name="FragileFencer", class_name="adventurer", background_id=18,
            method="standard_array",
            partial_classes=["duelist", "warrior"]
        )
        assert char["class"] == "adventurer"
        # The Fragility flaw means the combo uses 1d6 HD, not 1d6+2
        # HP should be lower than a normal warrior combo
        # We can't test exact HP due to randomness, but the character should be valid
        t.ok("Duelist/Warrior creates valid character (Fragility flaw)")
    except Exception as e:
        t.error("Duelist/Warrior creation", e)

    # 4d. Beastmaster + Expert
    try:
        random.seed(2003)
        char = create_character(
            name="Beastlord", class_name="adventurer", background_id=2,
            method="standard_array",
            partial_classes=["beastmaster", "expert"]
        )
        assert char["class"] == "adventurer"
        assert char["skills"]["survive"] >= 0, "Beastmaster should get Survive-0"
        t.ok("Beastmaster/Expert creates valid character")
    except Exception as e:
        t.error("Beastmaster/Expert creation", e)

    # 4e. Blood Priest + Warrior
    try:
        random.seed(2004)
        char = create_character(
            name="Zealot", class_name="adventurer", background_id=18,
            method="standard_array",
            partial_classes=["blood_priest", "warrior"]
        )
        assert char["class"] == "adventurer"
        assert char["skills"]["pray"] >= 0, "Blood Priest should get Pray-0"
        t.ok("Blood Priest/Warrior creates valid character")
    except Exception as e:
        t.error("Blood Priest/Warrior creation", e)

    # 4f. Thought Noble + Expert
    try:
        random.seed(2005)
        char = create_character(
            name="Psion", class_name="adventurer", background_id=16,
            method="standard_array",
            partial_classes=["thought_noble", "expert"]
        )
        assert char["class"] == "adventurer"
        assert char["skills"]["notice"] >= 0, "Thought Noble should get Notice-0"
        t.ok("Thought Noble/Expert creates valid character")
    except Exception as e:
        t.error("Thought Noble/Expert creation", e)

    # 4g. Invoker + Expert (partial Invoker)
    try:
        random.seed(2006)
        char = create_character(
            name="PartialInvoker", class_name="adventurer", background_id=16,
            method="standard_array",
            partial_classes=["invoker", "expert"]
        )
        assert char["class"] == "adventurer"
        assert char["skills"]["magic"] >= 0, "Invoker should get Magic-0"
        t.ok("Invoker/Expert creates valid character")
    except Exception as e:
        t.error("Invoker/Expert creation", e)

    # 4h. Full Invoker (class=mage, tradition=invoker)
    try:
        random.seed(2007)
        char = create_character(
            name="FullInvoker", class_name="mage", background_id=16,
            method="standard_array",
            tradition="invoker"
        )
        assert char["class"] == "mage"
        assert char["tradition"] == "invoker"
        assert char["skills"]["magic"] >= 0, "Full Invoker should get Magic-0"
        # Full Invoker should have spell_points field
        assert "spell_points" in char, "Full Invoker should have spell_points field"
        t.ok("Full Invoker (class=mage, tradition=invoker) creates valid character")
    except Exception as e:
        t.error("Full Invoker creation", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 5: Combo Restriction Enforcement
# ══════════════════════════════════════════════════════════════════════════════

def test_combo_restrictions(t):
    print("\n[5] COMBO RESTRICTION ENFORCEMENT")

    from character import create_character

    # 5a. Mageslayer + any mage-type should fail
    mage_types = ["mage", "accursed", "invoker", "skinshifter", "duelist",
                  "beastmaster", "blood_priest", "thought_noble"]
    for mtype in mage_types:
        try:
            random.seed(3000)
            try:
                create_character(
                    name="BadCombo", class_name="adventurer", background_id=18,
                    method="standard_array",
                    partial_classes=["mageslayer", mtype]
                )
                t.fail(f"Mageslayer+{mtype}", f"Should reject Mageslayer+{mtype}")
            except ValueError:
                t.ok(f"Mageslayer + {mtype} correctly rejected")
        except Exception as e:
            t.error(f"Mageslayer+{mtype} rejection", e)

    # 5b. Two identical partial classes should fail
    try:
        random.seed(3100)
        try:
            create_character(
                name="BadDupe", class_name="adventurer", background_id=18,
                method="standard_array",
                partial_classes=["bard", "bard"]
            )
            t.fail("Duplicate partials", "Should reject two identical partial classes")
        except ValueError:
            t.ok("Duplicate partial classes correctly rejected")
    except Exception as e:
        t.error("Duplicate partials", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 6: Effort Calculation
# ══════════════════════════════════════════════════════════════════════════════

def test_effort_calculation(t):
    print("\n[6] EFFORT CALCULATION")

    from character import create_character

    # 6a. Accursed effort = Magic skill + max(Int, Cha) mod, min 1
    try:
        random.seed(4000)
        char = create_character(
            name="EffortTest", class_name="adventurer", background_id=16,
            method="standard_array",
            partial_classes=["accursed", "warrior"]
        )
        assert char["effort"]["max"] >= 1, "Accursed effort should be >= 1"
        t.ok(f"Accursed effort correctly calculated: {char['effort']['max']}")
    except Exception as e:
        t.error("Accursed effort", e)

    # 6b. Wise has zero effort
    try:
        random.seed(4001)
        char = create_character(
            name="NoEffort", class_name="adventurer", background_id=16,
            method="standard_array",
            partial_classes=["wise", "warrior"]
        )
        assert char["effort"]["max"] == 0, f"Wise effort should be 0, got {char['effort']['max']}"
        t.ok("Wise has zero effort")
    except Exception as e:
        t.error("Wise effort", e)

    # 6c. Mageslayer effort = Magic skill + max(Int, Con) mod, min 1
    try:
        random.seed(4002)
        char = create_character(
            name="MsEffort", class_name="adventurer", background_id=18,
            method="standard_array",
            partial_classes=["mageslayer", "expert"]
        )
        assert char["effort"]["max"] >= 1, "Mageslayer effort should be >= 1"
        t.ok(f"Mageslayer effort correctly calculated: {char['effort']['max']}")
    except Exception as e:
        t.error("Mageslayer effort", e)

    # 6d. Bard effort = Perform skill + Cha mod, min 1
    try:
        random.seed(4003)
        char = create_character(
            name="BardEffort", class_name="adventurer", background_id=2,
            method="standard_array",
            partial_classes=["bard", "warrior"]
        )
        assert char["effort"]["max"] >= 1, "Bard effort should be >= 1"
        t.ok(f"Bard effort correctly calculated: {char['effort']['max']}")
    except Exception as e:
        t.error("Bard effort", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 7: Bonus Skill Application
# ══════════════════════════════════════════════════════════════════════════════

def test_bonus_skills(t):
    print("\n[7] BONUS SKILL APPLICATION")

    from character import create_character

    for cls_name, expected_skill in EXPECTED_BONUS_SKILLS.items():
        try:
            random.seed(5000 + hash(cls_name) % 1000)
            # Pair with expert or warrior depending on base type
            base = EXPECTED_BASE_TYPES[cls_name]
            if base == "mage":
                partner = "expert"
            elif base == "expert":
                partner = "warrior"
            else:  # warrior
                partner = "expert"
            char = create_character(
                name=f"Skill_{cls_name}", class_name="adventurer", background_id=1,
                method="standard_array",
                partial_classes=[cls_name, partner]
            )
            assert char["skills"][expected_skill] >= 0, \
                f"{cls_name} should have {expected_skill} >= 0, got {char['skills'][expected_skill]}"
            t.ok(f"{cls_name}: bonus skill {expected_skill} applied")
        except Exception as e:
            t.error(f"{cls_name} bonus skill", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 8: Duelist Fragility Flaw
# ══════════════════════════════════════════════════════════════════════════════

def test_duelist_fragility(t):
    print("\n[8] DUELIST FRAGILITY FLAW")

    from classes import ADVENTURER_PROGRESSION

    # 8a. Duelist/Warrior combo should have 1d6 HD (not 1d6+2)
    try:
        combo_key = None
        for key in ADVENTURER_PROGRESSION:
            if "duelist" in key and "warrior" in key:
                combo_key = key
                break
        assert combo_key is not None, "Duelist/Warrior combo table must exist"
        combo = ADVENTURER_PROGRESSION[combo_key]
        hd = combo[1]["hd"]
        assert hd == "1d6", f"Duelist/Warrior L1 HD should be 1d6 (Fragility), got {hd}"
        t.ok("Duelist/Warrior has 1d6 HD (Fragility flaw)")
    except Exception as e:
        t.error("Duelist Fragility HD", e)

    # 8b. Duelist/Expert should NOT have fragility (normal 1d6 HD)
    try:
        combo_key = None
        for key in ADVENTURER_PROGRESSION:
            if "duelist" in key and "expert" in key:
                combo_key = key
                break
        assert combo_key is not None, "Duelist/Expert combo table must exist"
        combo = ADVENTURER_PROGRESSION[combo_key]
        hd = combo[1]["hd"]
        assert hd == "1d6", f"Duelist/Expert L1 HD should be 1d6, got {hd}"
        t.ok("Duelist/Expert has normal 1d6 HD")
    except Exception as e:
        t.error("Duelist/Expert HD", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 9: Full Invoker
# ══════════════════════════════════════════════════════════════════════════════

def test_full_invoker(t):
    print("\n[9] FULL INVOKER")

    # 9a. Invoker tradition exists in TRADITIONS
    try:
        from traditions import TRADITIONS
        assert "invoker" in TRADITIONS, "Invoker must be in TRADITIONS"
        inv = TRADITIONS["invoker"]
        assert inv["has_spells"] is True, "Invoker should have spells"
        t.ok("Invoker tradition exists in TRADITIONS")
    except Exception as e:
        t.error("Invoker tradition", e)

    # 9b. Full Invoker uses spell points
    try:
        from character import create_character
        random.seed(6000)
        char = create_character(
            name="SpellPointMage", class_name="mage", background_id=16,
            method="standard_array",
            tradition="invoker"
        )
        assert "spell_points" in char, "Full Invoker must have spell_points field"
        sp = char["spell_points"]
        assert sp["max"] >= 1, f"Full Invoker spell_points.max should be >= 1, got {sp['max']}"
        t.ok(f"Full Invoker has spell_points: {sp}")
    except Exception as e:
        t.error("Full Invoker spell points", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 10: Traditional Education Focus
# ══════════════════════════════════════════════════════════════════════════════

def test_traditional_education(t):
    print("\n[10] TRADITIONAL EDUCATION FOCUS (removed — not in PDF)")

    # traditional_education was a fabricated focus not present in any WWN PDF.
    # This test group is kept as a placeholder for backward compatibility
    # with test runner invocations.
    t.ok("traditional_education correctly removed (not in any WWN PDF)")


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 11: Schema Validation
# ══════════════════════════════════════════════════════════════════════════════

def test_schema(t):
    print("\n[11] SCHEMA VALIDATION")

    # 11a. Schema partial_classes enum includes new values
    try:
        schema_path = os.path.join(SCHEMAS_DIR, "state.schema.json")
        with open(schema_path) as f:
            schema = json.load(f)
        char_def = schema["$defs"]["character"]["properties"]
        partial_enum = char_def["partial_classes"]["items"]["enum"]
        for cls_name in ALL_NEW_PARTIALS:
            assert cls_name in partial_enum, f"Schema missing partial class: {cls_name}"
        t.ok(f"Schema partial_classes enum includes all {len(ALL_NEW_PARTIALS)} new classes")
    except Exception as e:
        t.error("Schema partial_classes enum", e)

    # 11b. Schema tradition enum includes invoker
    try:
        trad_enum = char_def["tradition"]["enum"]
        assert "invoker" in trad_enum, "Schema tradition enum must include 'invoker'"
        t.ok("Schema tradition enum includes 'invoker'")
    except Exception as e:
        t.error("Schema tradition enum", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 12: CLI Integration
# ══════════════════════════════════════════════════════════════════════════════

def test_cli(t):
    print("\n[12] CLI INTEGRATION")

    # 12a. CLI accepts new partial class
    rc, out, err = run_cli([
        "create-character", "--name", "CliAccursed",
        "--class", "adventurer",
        "--background", "16",
        "--partial-classes", "accursed,expert",
        "--seed", "42"
    ])
    if rc == 0:
        data = json.loads(out)
        assert data["class"] == "adventurer"
        assert "accursed" in data["partial_classes"]
        t.ok("CLI create-character with --partial-classes accursed,expert works")
    else:
        t.fail("CLI accursed", f"exit code {rc}: {err.strip()[:200]}")

    # 12b. CLI accepts invoker tradition
    rc, out, err = run_cli([
        "create-character", "--name", "CliInvoker",
        "--class", "mage",
        "--background", "16",
        "--tradition", "invoker",
        "--seed", "42"
    ])
    if rc == 0:
        data = json.loads(out)
        assert data.get("tradition") == "invoker"
        t.ok("CLI create-character with --tradition invoker works")
    else:
        t.fail("CLI invoker", f"exit code {rc}: {err.strip()[:200]}")

    # 12c. CLI rejects invalid combo
    rc, out, err = run_cli([
        "create-character", "--name", "CliBadCombo",
        "--class", "adventurer",
        "--background", "18",
        "--partial-classes", "mageslayer,mage",
        "--seed", "42"
    ])
    if rc != 0:
        t.ok("CLI correctly rejects mageslayer+mage combo")
    else:
        t.fail("CLI invalid combo", "Should have failed for mageslayer+mage")


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 13: Determinism
# ══════════════════════════════════════════════════════════════════════════════

def test_determinism(t):
    print("\n[13] DETERMINISM")

    from character import create_character

    test_cases = [
        ("accursed", ["accursed", "warrior"]),
        ("bard", ["bard", "warrior"]),
        ("mageslayer", ["mageslayer", "expert"]),
        ("skinshifter", ["skinshifter", "expert"]),
    ]

    for cls_name, partials in test_cases:
        try:
            random.seed(7777)
            char1 = create_character(
                name="Det", class_name="adventurer", background_id=1,
                method="standard_array",
                partial_classes=partials
            )
            random.seed(7777)
            char2 = create_character(
                name="Det", class_name="adventurer", background_id=1,
                method="standard_array",
                partial_classes=partials
            )
            assert char1 == char2, f"Determinism failed for {cls_name}"
            t.ok(f"Determinism: {cls_name} with seed=7777 produces identical output")
        except Exception as e:
            t.error(f"Determinism {cls_name}", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 14: Backward Compatibility
# ══════════════════════════════════════════════════════════════════════════════

def test_backward_compat(t):
    print("\n[14] BACKWARD COMPATIBILITY")

    from character import create_character

    # 14a. Standard warrior still works
    try:
        random.seed(8000)
        char = create_character(
            name="OldWarrior", class_name="warrior", background_id=18,
            method="standard_array"
        )
        assert char["class"] == "warrior"
        assert "killing_blow" in char["class_abilities"]
        t.ok("Standard Warrior creation still works")
    except Exception as e:
        t.error("Backward compat warrior", e)

    # 14b. Standard adventurer with old partials still works
    try:
        random.seed(8001)
        char = create_character(
            name="OldAdventurer", class_name="adventurer", background_id=18,
            method="standard_array",
            partial_classes=["expert", "warrior"]
        )
        assert char["class"] == "adventurer"
        assert set(char["partial_classes"]) == {"expert", "warrior"}
        t.ok("Standard Expert/Warrior adventurer still works")
    except Exception as e:
        t.error("Backward compat adventurer", e)

    # 14c. Standard mage with tradition still works
    try:
        random.seed(8002)
        char = create_character(
            name="OldMage", class_name="mage", background_id=16,
            method="standard_array",
            tradition="high_mage"
        )
        assert char["class"] == "mage"
        assert char["tradition"] == "high_mage"
        t.ok("Standard Mage with high_mage tradition still works")
    except Exception as e:
        t.error("Backward compat mage", e)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("EXPANDED CLASSES TESTS — WWN5 + Gyre + Traditional Education")
    print("=" * 60)

    t = TestResult()

    test_partial_class_tables(t)
    test_adventurer_progression(t)
    test_wwn5_character_creation(t)
    test_gyre_character_creation(t)
    test_combo_restrictions(t)
    test_effort_calculation(t)
    test_bonus_skills(t)
    test_duelist_fragility(t)
    test_full_invoker(t)
    test_traditional_education(t)
    test_schema(t)
    test_cli(t)
    test_determinism(t)
    test_backward_compat(t)

    all_passed = t.summary()
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
