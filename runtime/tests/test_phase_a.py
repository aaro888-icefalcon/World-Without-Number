#!/usr/bin/env python3
"""
Phase A Validation Test — Comprehensive acceptance test for the WWN AI RPG plan.

Tests all Phase A deliverables from the execution plan:
  1. Extracted data tables (attributes, skills, equipment, classes, backgrounds, foci, bestiary)
  2. dice.py — seedable dice roller
  3. character.py — character creation
  4. combat.py — attack resolution with zones
  5. conditions.py — status effects and System Strain
  6. State schema v7 — WWN character fields
  7. hard-rules.md and gm-protocol.md — governance documents
  8. validate_extraction.py — data integrity smoke tests
  9. CLI commands (roll, create-character, attack, skill-check, save)
 10. Zone-based combat position tracking
"""

import os
import sys
import json
import subprocess
import importlib

# Paths
RUNTIME_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(RUNTIME_DIR)
SCRIPTS_DIR = os.path.join(RUNTIME_DIR, "scripts")
SKILLS_DIR = os.path.join(RUNTIME_DIR, "phases", "3-resolution", "skills")
CORE_TABLES = os.path.join(SKILLS_DIR, "core", "tables")
CORE_SCRIPTS = os.path.join(SKILLS_DIR, "core", "scripts")
COMBAT_TABLES = os.path.join(SKILLS_DIR, "combat", "tables")
COMBAT_SCRIPTS = os.path.join(SKILLS_DIR, "combat", "scripts")
SCHEMAS_DIR = os.path.join(RUNTIME_DIR, "schemas")
REFS_DIR = os.path.join(RUNTIME_DIR, "phases", "1-context-loading", "references")
CLI = os.path.join(SCRIPTS_DIR, "emergence_cli.py")
STATE_FILE = os.path.join(RUNTIME_DIR, "state.json")

# Add paths for imports
for d in [CORE_TABLES, CORE_SCRIPTS, COMBAT_TABLES, COMBAT_SCRIPTS]:
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
# TEST GROUP 1: Extracted Data Tables
# ══════════════════════════════════════════════════════════════════════════════

def test_data_tables(t):
    print("\n[1] EXTRACTED DATA TABLES")

    # 1a. Attributes
    try:
        from attributes import ATTRIBUTE_MODIFIERS, ATTRIBUTES, get_modifier
        assert len(ATTRIBUTES) == 6, f"Expected 6 attributes, got {len(ATTRIBUTES)}"
        assert get_modifier(3) == -2
        assert get_modifier(10) == 0
        assert get_modifier(18) == 2
        t.ok("attributes.py: ATTRIBUTES (6 attrs), modifiers, get_modifier()")
    except Exception as e:
        t.error("attributes.py", e)

    # 1b. Skills
    try:
        from skills import SKILLS, SKILL_CHECK_DIFFICULTIES
        assert len(SKILLS) >= 20, f"Expected >=20 skills, got {len(SKILLS)}"
        assert "stab" in SKILLS
        assert "shoot" in SKILLS
        assert "magic" in SKILLS
        t.ok(f"skills.py: {len(SKILLS)} skills loaded")
    except Exception as e:
        t.error("skills.py", e)

    # 1c. Equipment
    try:
        from equipment import WEAPONS, ARMOR, WEAPON_TRAITS
        assert len(WEAPONS) >= 25, f"Expected >=25 weapons, got {len(WEAPONS)}"
        assert len(ARMOR) >= 10, f"Expected >=10 armor, got {len(ARMOR)}"
        # Verify weapon structure
        sword = next(w for w in WEAPONS if "Long" in w["name"] and "Sword" in w["name"])
        assert "damage" in sword and "shock" in sword and "cost_sp" in sword
        t.ok(f"equipment.py: {len(WEAPONS)} weapons, {len(ARMOR)} armor")
    except Exception as e:
        t.error("equipment.py", e)

    # 1d. Classes
    try:
        from classes import CLASSES, XP_TABLE, FULL_MAGE_CASTING
        assert "warrior" in CLASSES
        assert "expert" in CLASSES
        assert "mage" in CLASSES
        assert len(XP_TABLE) == 10
        t.ok(f"classes.py: {len(CLASSES)} classes, XP table, casting tables")
    except Exception as e:
        t.error("classes.py", e)

    # 1e. Backgrounds
    try:
        from backgrounds import BACKGROUNDS
        assert len(BACKGROUNDS) == 20, f"Expected 20 backgrounds, got {len(BACKGROUNDS)}"
        bg1 = BACKGROUNDS[1]
        assert "name" in bg1 and "free_skill" in bg1 and "growth" in bg1
        t.ok(f"backgrounds.py: {len(BACKGROUNDS)} backgrounds")
    except Exception as e:
        t.error("backgrounds.py", e)

    # 1f. Foci
    try:
        from foci import FOCI
        assert len(FOCI) >= 15, f"Expected >=15 foci, got {len(FOCI)}"
        # Check structure
        some_focus = list(FOCI.values())[0]
        assert "level_1" in some_focus and "level_2" in some_focus
        t.ok(f"foci.py: {len(FOCI)} foci loaded")
    except Exception as e:
        t.error("foci.py", e)

    # 1g. Bestiary
    try:
        from bestiary import CREATURES, HUMAN_TEMPLATES, REACTION_TABLE
        assert len(CREATURES) >= 15, f"Expected >=15 creatures, got {len(CREATURES)}"
        assert len(HUMAN_TEMPLATES) >= 5
        assert len(REACTION_TABLE) >= 10
        # Check stat block structure
        c = CREATURES[0]
        for field in ["name", "hd", "ac", "atk", "dmg", "move", "ml", "save"]:
            assert field in c, f"Missing field '{field}' in creature stat block"
        t.ok(f"bestiary.py: {len(CREATURES)} creatures, {len(HUMAN_TEMPLATES)} templates")
    except Exception as e:
        t.error("bestiary.py", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 2: Core Domain Scripts
# ══════════════════════════════════════════════════════════════════════════════

def test_domain_scripts(t):
    print("\n[2] CORE DOMAIN SCRIPTS")

    # 2a. dice.py
    try:
        from dice import roll, roll_dice, parse_dice_notation
        # Deterministic test: same seed → same result
        import random
        random.seed(42)
        r1 = roll("1d20+3")
        random.seed(42)
        r2 = roll("1d20+3")
        assert r1 == r2, f"Dice not deterministic: {r1} != {r2}"
        assert "total" in r1, "roll() must return dict with 'total'"
        assert "rolls" in r1, "roll() must return dict with 'rolls'"
        assert "expression" in r1, "roll() must return dict with 'expression'"
        # Parse various notations
        parsed = parse_dice_notation("2d6+4")
        assert parsed["count"] == 2 and parsed["sides"] == 6 and parsed["modifier"] == 4
        t.ok("dice.py: roll(), parse_dice_notation(), deterministic with seed")
    except Exception as e:
        t.error("dice.py", e)

    # 2b. character.py
    try:
        from character import create_character
        import random
        random.seed(99)
        char = create_character(
            name="Kyra",
            class_name="warrior",
            background_id=18,  # Soldier
            method="standard_array"
        )
        assert char["name"] == "Kyra"
        assert char["class"] == "warrior"
        assert char["level"] == 1
        # Must have all 6 attributes
        for attr in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            assert attr in char["attributes"], f"Missing attribute: {attr}"
        assert "hp" in char and isinstance(char["hp"], dict)
        assert "current" in char["hp"] and "max" in char["hp"]
        assert char["hp"]["max"] > 0
        assert "skills" in char
        assert "equipment" in char
        assert "attack_bonus" in char
        assert "armor_class" in char
        assert "saving_throws" in char
        assert "system_strain" in char
        t.ok("character.py: create_character() produces valid WWN character")
    except Exception as e:
        t.error("character.py", e)

    # 2c. combat.py
    try:
        from combat import resolve_attack, resolve_shock
        import random
        random.seed(42)
        result = resolve_attack(
            attacker={"attack_bonus": 3, "skill_level": 1, "attribute_mod": 1,
                       "weapon": {"damage": "1d8", "shock": "2/15", "traits": []}},
            defender={"armor_class": 14, "hp": {"current": 10, "max": 10}},
        )
        assert "hit_roll" in result, "resolve_attack must return hit_roll"
        assert "total_roll" in result, "resolve_attack must return total_roll"
        assert "hit" in result, "resolve_attack must return hit (bool)"
        assert "damage" in result, "resolve_attack must return damage"
        assert "shock_applied" in result, "resolve_attack must return shock_applied"
        assert "arithmetic_trace" in result, "resolve_attack must include arithmetic trace"
        t.ok("combat.py: resolve_attack() returns full combat result with trace")
    except Exception as e:
        t.error("combat.py", e)

    # 2d. conditions.py
    try:
        from conditions import SystemStrain, apply_condition, CONDITION_EFFECTS
        ss = SystemStrain(max_strain=14)
        assert ss.current == 0
        assert ss.can_heal() is True
        ss.add(1)
        assert ss.current == 1
        ss_full = SystemStrain(max_strain=3)
        ss_full.add(3)
        assert ss_full.can_heal() is False
        assert len(CONDITION_EFFECTS) >= 3, "Should define at least 3 conditions"
        t.ok("conditions.py: SystemStrain, apply_condition, CONDITION_EFFECTS")
    except Exception as e:
        t.error("conditions.py", e)

    # 2e. Zone-based combat positions
    try:
        from combat import CombatZone, CombatState
        cs = CombatState()
        cs.add_combatant("pc_1", zone=CombatZone.MELEE)
        cs.add_combatant("goblin_1", zone=CombatZone.NEAR)
        assert cs.get_zone("pc_1") == CombatZone.MELEE
        assert cs.get_zone("goblin_1") == CombatZone.NEAR
        assert cs.can_melee_attack("pc_1", "goblin_1") is False
        cs.move_combatant("goblin_1", CombatZone.MELEE)
        assert cs.can_melee_attack("pc_1", "goblin_1") is True
        t.ok("combat.py: CombatZone (MELEE/NEAR/FAR/DISTANT), CombatState")
    except Exception as e:
        t.error("combat.py zones", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 3: CLI Commands
# ══════════════════════════════════════════════════════════════════════════════

def test_cli_commands(t):
    print("\n[3] CLI COMMANDS")

    # 3a. roll command
    rc, out, err = run_cli(["roll", "1d20+3", "--seed", "42"])
    if rc == 0:
        data = json.loads(out)
        assert "total" in data, "roll output must include 'total'"
        assert "rolls" in data, "roll output must include 'rolls'"
        assert "seed" in data, "roll output must include 'seed'"
        # Determinism check
        rc2, out2, _ = run_cli(["roll", "1d20+3", "--seed", "42"])
        data2 = json.loads(out2)
        assert data["total"] == data2["total"], "Same seed must produce same roll"
        t.ok(f"CLI roll 1d20+3 --seed 42 → total={data['total']} (deterministic)")
    else:
        t.fail("CLI roll", f"exit code {rc}: {err.strip()}")

    # 3b. skill-check command
    rc, out, err = run_cli(["skill-check", "--attribute-mod", "1", "--skill-level", "1",
                             "--difficulty", "8", "--seed", "42"])
    if rc == 0:
        data = json.loads(out)
        assert "success" in data
        assert "rolls" in data
        assert "target" in data
        t.ok(f"CLI skill-check → success={data['success']}, total={data['total']}")
    else:
        t.fail("CLI skill-check", f"exit code {rc}: {err.strip()}")

    # 3c. save command
    rc, out, err = run_cli(["save", "--type", "physical", "--level", "3",
                             "--modifier", "1", "--seed", "42"])
    if rc == 0:
        data = json.loads(out)
        assert "success" in data
        assert "roll" in data
        assert "target" in data
        t.ok(f"CLI save --type physical → success={data['success']}")
    else:
        t.fail("CLI save", f"exit code {rc}: {err.strip()}")

    # 3d. attack command
    rc, out, err = run_cli(["attack", "--attack-bonus", "3", "--skill-level", "1",
                             "--attribute-mod", "1", "--weapon-damage", "1d8",
                             "--shock", "2/15", "--target-ac", "14",
                             "--target-hp", "10", "--seed", "42"])
    if rc == 0:
        data = json.loads(out)
        assert "hit" in data
        assert "damage" in data
        assert "arithmetic_trace" in data
        t.ok(f"CLI attack → hit={data['hit']}, damage={data['damage']}")
    else:
        t.fail("CLI attack", f"exit code {rc}: {err.strip()}")

    # 3e. create-character command
    rc, out, err = run_cli(["create-character", "--name", "TestHero",
                             "--class", "warrior", "--background", "18",
                             "--method", "standard_array", "--seed", "42"])
    if rc == 0:
        data = json.loads(out)
        assert data["name"] == "TestHero"
        assert data["class"] == "warrior"
        assert data["level"] == 1
        assert "attributes" in data
        assert "hp" in data
        t.ok(f"CLI create-character → {data['name']} (Lvl {data['level']} {data['class']})")
    else:
        t.fail("CLI create-character", f"exit code {rc}: {err.strip()}")


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 4: State Schema v7
# ══════════════════════════════════════════════════════════════════════════════

def test_state_schema(t):
    print("\n[4] STATE SCHEMA V7")

    # 4a. Schema has WWN character fields
    try:
        schema_path = os.path.join(SCHEMAS_DIR, "state.schema.json")
        with open(schema_path) as f:
            schema = json.load(f)
        char_def = schema.get("$defs", {}).get("character", {})
        char_props = char_def.get("properties", {})
        required = char_def.get("required", [])

        wwn_fields = ["attributes", "hp", "armor_class", "attack_bonus",
                      "skills", "equipment", "saving_throws", "system_strain"]
        missing = [f for f in wwn_fields if f not in char_props]
        if missing:
            t.fail("Schema v7 character fields", f"Missing: {missing}")
        else:
            t.ok(f"Schema v7 has all WWN character fields: {wwn_fields}")
    except Exception as e:
        t.error("Schema v7", e)

    # 4b. State validates with WWN character
    try:
        rc, out, err = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS_DIR, "validate_state.py"), STATE_FILE],
            capture_output=True, text=True, cwd=REPO_ROOT
        ).returncode, "", ""
        # Just check it doesn't crash
        result = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS_DIR, "validate_state.py"), STATE_FILE],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        if result.returncode == 0:
            t.ok("validate_state.py passes on state.json")
        else:
            t.fail("validate_state.py", result.stderr.strip()[:200])
    except Exception as e:
        t.error("validate_state.py", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 5: Governance Documents
# ══════════════════════════════════════════════════════════════════════════════

def test_governance_docs(t):
    print("\n[5] GOVERNANCE DOCUMENTS")

    # 5a. hard-rules.md exists and has required content
    hr_path = os.path.join(REFS_DIR, "hard-rules.md")
    if os.path.isfile(hr_path):
        with open(hr_path) as f:
            content = f.read()
        required_topics = ["death", "dice", "script", "shock", "morale", "system strain"]
        found = [topic for topic in required_topics if topic.lower() in content.lower()]
        if len(found) >= 5:
            t.ok(f"hard-rules.md: covers {len(found)}/{len(required_topics)} required topics")
        else:
            t.fail("hard-rules.md", f"Only covers {found}, missing some of {required_topics}")
    else:
        t.fail("hard-rules.md", "File does not exist")

    # 5b. gm-protocol.md exists and has required content
    gm_path = os.path.join(REFS_DIR, "gm-protocol.md")
    if os.path.isfile(gm_path):
        with open(gm_path) as f:
            content = f.read()
        required_topics = ["yes, and", "telegraph danger", "failure", "pacing", "voice"]
        found = [topic for topic in required_topics if topic.lower() in content.lower()]
        if len(found) >= 4:
            t.ok(f"gm-protocol.md: covers {len(found)}/{len(required_topics)} required topics")
        else:
            t.fail("gm-protocol.md", f"Only covers {found}")
    else:
        t.fail("gm-protocol.md", "File does not exist")

    # 5c. combat-rules.md exists with §section anchors
    cr_path = os.path.join(SKILLS_DIR, "combat", "references", "combat-rules.md")
    if os.path.isfile(cr_path):
        with open(cr_path) as f:
            content = f.read()
        sections = ["§hit-roll", "§damage", "§shock", "§morale", "§saving-throws"]
        found = [s for s in sections if s in content]
        if len(found) >= 4:
            t.ok(f"combat-rules.md: {len(found)}/{len(sections)} §section anchors")
        else:
            t.fail("combat-rules.md sections", f"Only found {found}")
    else:
        t.fail("combat-rules.md", "File does not exist")


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 6: Extraction Validator
# ══════════════════════════════════════════════════════════════════════════════

def test_extraction_validator(t):
    print("\n[6] EXTRACTION VALIDATOR")

    validator_path = os.path.join(SCRIPTS_DIR, "validate_extraction.py")
    if os.path.isfile(validator_path):
        result = subprocess.run(
            [sys.executable, validator_path],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        if result.returncode == 0:
            t.ok(f"validate_extraction.py passes: {result.stdout.strip()[:100]}")
        else:
            t.fail("validate_extraction.py", result.stderr.strip()[:200])
    else:
        t.fail("validate_extraction.py", "File does not exist")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("PHASE A VALIDATION TEST — WWN AI RPG Engine")
    print("=" * 60)

    t = TestResult()

    test_data_tables(t)
    test_domain_scripts(t)
    test_cli_commands(t)
    test_state_schema(t)
    test_governance_docs(t)
    test_extraction_validator(t)

    all_passed = t.summary()
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
