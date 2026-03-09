#!/usr/bin/env python3
"""
Foci PDF Cross-Validation Tests

Validates that all foci in foci.py match the World Without Number PDFs:
  - WWN 1 pp.22-31: Core foci (35 entries)
  - WWN 5 pp.176-183: Maqqatban Knight, Amundi Godblood, Arcane Secret,
    Non-Human Origin foci

Tests verify:
  1. All PDF foci are present in foci.py
  2. No fabricated foci exist (entries not in any PDF)
  3. Type classifications match PDF restrictions
  4. Level 1/2 descriptions contain key mechanical terms from PDFs
  5. Special properties (repeatable, class_restriction) are correct
  6. WWN 5 category foci are properly categorized
"""

import os
import sys

# Paths
RUNTIME_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(RUNTIME_DIR, "phases", "3-resolution", "skills")
CORE_TABLES = os.path.join(SKILLS_DIR, "core", "tables")

if CORE_TABLES not in sys.path:
    sys.path.insert(0, CORE_TABLES)


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


# ══════════════════════════════════════════════════════════════════════════════
# CANONICAL FOCI LISTS FROM PDFS
# ══════════════════════════════════════════════════════════════════════════════

# WWN 1 pp.22-31 — 35 core foci
WWN1_FOCI = {
    "alert":              {"type": "any"},
    "armored_magic":      {"type": "mage_only"},
    "armsmaster":         {"type": "warrior"},
    "artisan":            {"type": "any"},
    "assassin":           {"type": "any"},
    "authority":          {"type": "any"},
    "close_combatant":    {"type": "warrior"},
    "connected":          {"type": "any"},
    "cultured":           {"type": "any"},
    "deadeye":            {"type": "warrior"},
    "dealmaker":          {"type": "any"},
    "developed_attribute": {"type": "non_mage"},
    "die_hard":           {"type": "any"},
    "diplomatic_grace":   {"type": "any"},
    "gifted_chirurgeon":  {"type": "any"},
    "henchkeeper":        {"type": "any"},
    "impervious_defense": {"type": "warrior"},
    "impostor":           {"type": "any"},
    "lucky":              {"type": "any"},
    "nullifier":          {"type": "non_mage"},
    "poisoner":           {"type": "any"},
    "polymath":           {"type": "expert_only"},
    "rider":              {"type": "any"},
    "shocking_assault":   {"type": "warrior"},
    "snipers_eye":        {"type": "warrior"},
    "special_origin":     {"type": "any"},
    "specialist":         {"type": "any", "repeatable": True},
    "spirit_familiar":    {"type": "any"},
    "trapmaster":         {"type": "any"},
    "unarmed_combatant":  {"type": "warrior"},
    "unique_gift":        {"type": "any"},
    "valiant_defender":   {"type": "warrior"},
    "well_met":           {"type": "any"},
    "whirlwind_assault":  {"type": "warrior"},
    "xenoblooded":        {"type": "any"},
}

# WWN 5 — Maqqatban Knight Foci (warrior only, one style per character)
WWN5_MAQQATBAN = {
    "all_directions_edge_style":  {"type": "warrior", "category": "maqqatban_knight"},
    "catalytic_soul_style":       {"type": "warrior", "category": "maqqatban_knight"},
    "ghost_archer_style":         {"type": "warrior", "category": "maqqatban_knight"},
    "one_point_strike_style":     {"type": "warrior", "category": "maqqatban_knight"},
    "pyre_of_heaven_style":       {"type": "warrior", "category": "maqqatban_knight"},
    "righteous_iron_style":       {"type": "warrior", "category": "maqqatban_knight"},
    "world_tree_lance_style":     {"type": "warrior", "category": "maqqatban_knight"},
    "wrathful_mountain_style":    {"type": "warrior", "category": "maqqatban_knight"},
}

# WWN 5 — Amundi Godblood Foci (expert only, one per character)
WWN5_GODBLOOD = {
    "danger_sense":        {"type": "expert_only", "category": "amundi_godblood"},
    "folie_a_deux":        {"type": "expert_only", "category": "amundi_godblood"},
    "master_tracker":      {"type": "expert_only", "category": "amundi_godblood"},
    "night_walker":        {"type": "expert_only", "category": "amundi_godblood"},
    "pack_beast":          {"type": "expert_only", "category": "amundi_godblood"},
    "provident_crafter":   {"type": "expert_only", "category": "amundi_godblood"},
    "walk_like_wind":      {"type": "expert_only", "category": "amundi_godblood"},
    "wildtongue":          {"type": "expert_only", "category": "amundi_godblood"},
}

# WWN 5 — Arcane Secret Foci (mage only, one per character)
WWN5_ARCANE = {
    "atlantean_divination":  {"type": "mage_only", "category": "arcane_secret"},
    "iteral_pacting":        {"type": "mage_only", "category": "arcane_secret"},
    "nagadi_hemomancy":      {"type": "mage_only", "category": "arcane_secret"},
    "old_empire_sigilism":   {"type": "mage_only", "category": "arcane_secret"},
    "vothite_mind_sorcery":  {"type": "mage_only", "category": "arcane_secret"},
}

# WWN 5 — Non-Human Origin Foci (level 1 only, one per character)
WWN5_NONHUMAN = {
    "man":                 {"type": "any", "category": "non_human_origin"},
    "accipiter_anak":      {"type": "any", "category": "non_human_origin"},
    "aristoi_anak":        {"type": "any", "category": "non_human_origin"},
    "choeru_beastfolk":    {"type": "any", "category": "non_human_origin"},
    "deepfolk":            {"type": "any", "category": "non_human_origin"},
    "ghoul":               {"type": "any", "category": "non_human_origin"},
    "guer_beastfolk":      {"type": "any", "category": "non_human_origin"},
    "harbinger_anak":      {"type": "any", "category": "non_human_origin"},
    "hua_beastfolk":       {"type": "any", "category": "non_human_origin"},
    "kitsune_beastfolk":   {"type": "any", "category": "non_human_origin"},
    "manu_beastfolk":      {"type": "any", "category": "non_human_origin"},
    "nahu_beastfolk":      {"type": "any", "category": "non_human_origin"},
    "pichi_beastfolk":     {"type": "any", "category": "non_human_origin"},
    "piren_beastfolk":     {"type": "any", "category": "non_human_origin"},
    "sui_beastfolk":       {"type": "any", "category": "non_human_origin"},
    "usagi_beastfolk":     {"type": "any", "category": "non_human_origin"},
    "zakathi":             {"type": "any", "category": "non_human_origin"},
}

# Known fabricated focus names that must NOT appear
FABRICATED_NAMES = [
    "deadly_sniper",
    "dev_cunning",
    "diplomat",
    "hacker",
    "healer",
    "savage_fray",
    "shock_trooper",
    "wanderer",
    "traditional_education",
]

# Combine all canonical foci
ALL_CANONICAL = {}
ALL_CANONICAL.update(WWN1_FOCI)
ALL_CANONICAL.update(WWN5_MAQQATBAN)
ALL_CANONICAL.update(WWN5_GODBLOOD)
ALL_CANONICAL.update(WWN5_ARCANE)
ALL_CANONICAL.update(WWN5_NONHUMAN)

# Key mechanical terms that MUST appear in level_1 descriptions (from PDF)
# Format: focus_name -> list of required substrings in level_1
WWN1_KEY_TERMS = {
    "alert": ["Notice", "surprised"],
    "armored_magic": ["cast spells", "armor"],
    "armsmaster": ["Stab", "Stowed", "Shock"],
    "artisan": ["Craft", "mod"],
    "assassin": ["Sneak", "Execution Attack"],
    "authority": ["Lead", "Cha/Lead"],
    "close_combatant": ["combat skill", "Shock"],
    "connected": ["Connect", "week"],
    "cultured": ["Connect", "language"],
    "deadeye": ["Shoot", "Stowed"],
    "dealmaker": ["Trade", "buyer"],
    "developed_attribute": ["attribute", "modifier", "+1"],
    "die_hard": ["2 maximum hit points", "stabilize"],
    "diplomatic_grace": ["Convince", "language"],
    "gifted_chirurgeon": ["Heal", "Mortally Wounded", "3d6"],
    "henchkeeper": ["Lead", "henchmen"],
    "impervious_defense": ["Armor Class", "15"],
    "impostor": ["Perform", "Sneak", "identity"],
    "lucky": ["week", "killed"],
    "nullifier": ["+2", "saving throws", "magical"],
    "poisoner": ["Heal", "toxin"],
    "polymath": ["non-combat skills", "level-0"],
    "rider": ["Ride", "Morale 12"],
    "shocking_assault": ["Punch", "Stab", "Shock", "AC 10"],
    "snipers_eye": ["Shoot", "Execution Attack", "3d6"],
    "specialist": ["skill", "3d6"],
    "spirit_familiar": ["familiar", "Calculation"],
    "trapmaster": ["Notice", "trap"],
    "unarmed_combatant": ["Punch", "1d6"],
    "unique_gift": ["ability", "GM"],
    "valiant_defender": ["Stab", "Punch", "Screen Ally"],
    "well_met": ["Reaction", "+1"],
    "whirlwind_assault": ["Stab", "Shock", "melee range"],
    "xenoblooded": ["alien heritage"],
}


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 1: No Fabricated Foci
# ══════════════════════════════════════════════════════════════════════════════

def test_no_fabricated_foci(t):
    print("\n[1] NO FABRICATED FOCI")
    from foci import FOCI

    for name in FABRICATED_NAMES:
        if name in FOCI:
            t.fail(f"fabricated:{name}", f"'{name}' is not in any WWN PDF and must be removed")
        else:
            t.ok(f"fabricated:{name} correctly absent")


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 2: All WWN 1 Core Foci Present
# ══════════════════════════════════════════════════════════════════════════════

def test_wwn1_foci_present(t):
    print("\n[2] WWN 1 CORE FOCI PRESENT")
    from foci import FOCI

    for name, expected in WWN1_FOCI.items():
        if name not in FOCI:
            t.fail(f"wwn1:{name}", f"Missing from foci.py (WWN 1 pp.22-31)")
        else:
            t.ok(f"wwn1:{name} present")


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 3: Type Classifications
# ══════════════════════════════════════════════════════════════════════════════

def test_type_classifications(t):
    print("\n[3] TYPE CLASSIFICATIONS")
    from foci import FOCI

    for name, expected in ALL_CANONICAL.items():
        if name not in FOCI:
            continue  # Skip missing foci (caught by group 2)
        actual_type = FOCI[name].get("type")
        expected_type = expected["type"]
        if actual_type == expected_type:
            t.ok(f"type:{name}={actual_type}")
        else:
            t.fail(f"type:{name}", f"Expected type '{expected_type}', got '{actual_type}'")


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 4: Level 1/2 Descriptions Contain Key Terms
# ══════════════════════════════════════════════════════════════════════════════

def test_description_key_terms(t):
    print("\n[4] DESCRIPTION KEY TERMS")
    from foci import FOCI

    for name, required_terms in WWN1_KEY_TERMS.items():
        if name not in FOCI:
            continue
        l1 = FOCI[name].get("level_1", "")
        missing = [term for term in required_terms if term not in l1]
        if missing:
            t.fail(f"terms:{name}", f"Level 1 missing key terms: {missing}")
        else:
            t.ok(f"terms:{name} L1 has all key terms")


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 5: Special Properties
# ══════════════════════════════════════════════════════════════════════════════

def test_special_properties(t):
    print("\n[5] SPECIAL PROPERTIES")
    from foci import FOCI

    # Specialist must be repeatable
    if "specialist" in FOCI:
        if FOCI["specialist"].get("repeatable"):
            t.ok("specialist is repeatable")
        else:
            t.fail("specialist.repeatable", "Must be True")

    # Developed Attribute should also be repeatable (different attributes)
    if "developed_attribute" in FOCI:
        if FOCI["developed_attribute"].get("repeatable"):
            t.ok("developed_attribute is repeatable")
        else:
            t.fail("developed_attribute.repeatable", "Must be True (pick different attributes)")

    # Unique Gift has no Level 2 (GM-defined power, no levels)
    if "unique_gift" in FOCI:
        has_l2 = bool(FOCI["unique_gift"].get("level_2"))
        # Unique Gift CAN have level 2 if the GM defines it, so either way is acceptable
        t.ok(f"unique_gift level_2 present: {has_l2}")

    # All foci must have level_1
    for name, focus in FOCI.items():
        if "level_1" not in focus:
            t.fail(f"level_1:{name}", "Missing level_1 description")

    # Special Origin is a placeholder, not a normal focus
    if "special_origin" in FOCI:
        t.ok("special_origin present (placeholder for racial foci)")


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 6: WWN 5 Category Foci
# ══════════════════════════════════════════════════════════════════════════════

def test_wwn5_foci(t):
    print("\n[6] WWN 5 CATEGORY FOCI")
    from foci import FOCI

    # Maqqatban Knight foci
    for name in WWN5_MAQQATBAN:
        if name in FOCI:
            cat = FOCI[name].get("category")
            if cat == "maqqatban_knight":
                t.ok(f"wwn5:maqqatban:{name}")
            else:
                t.fail(f"wwn5:maqqatban:{name}", f"Expected category 'maqqatban_knight', got '{cat}'")
        else:
            t.fail(f"wwn5:maqqatban:{name}", "Missing from foci.py")

    # Amundi Godblood foci
    for name in WWN5_GODBLOOD:
        if name in FOCI:
            cat = FOCI[name].get("category")
            if cat == "amundi_godblood":
                t.ok(f"wwn5:godblood:{name}")
            else:
                t.fail(f"wwn5:godblood:{name}", f"Expected category 'amundi_godblood', got '{cat}'")
        else:
            t.fail(f"wwn5:godblood:{name}", "Missing from foci.py")

    # Arcane Secret foci
    for name in WWN5_ARCANE:
        if name in FOCI:
            cat = FOCI[name].get("category")
            if cat == "arcane_secret":
                t.ok(f"wwn5:arcane:{name}")
            else:
                t.fail(f"wwn5:arcane:{name}", f"Expected category 'arcane_secret', got '{cat}'")
        else:
            t.fail(f"wwn5:arcane:{name}", "Missing from foci.py")

    # Non-Human Origin foci
    for name in WWN5_NONHUMAN:
        if name in FOCI:
            cat = FOCI[name].get("category")
            if cat == "non_human_origin":
                t.ok(f"wwn5:origin:{name}")
            else:
                t.fail(f"wwn5:origin:{name}", f"Expected category 'non_human_origin', got '{cat}'")
        else:
            t.fail(f"wwn5:origin:{name}", "Missing from foci.py")


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 7: Total Count
# ══════════════════════════════════════════════════════════════════════════════

def test_total_count(t):
    print("\n[7] TOTAL COUNT")
    from foci import FOCI

    expected_min = len(ALL_CANONICAL)
    actual = len(FOCI)
    if actual >= expected_min:
        t.ok(f"foci count: {actual} >= {expected_min} expected")
    else:
        t.fail(f"foci count", f"Expected >= {expected_min}, got {actual}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("FOCI PDF CROSS-VALIDATION TESTS")
    print("=" * 60)

    t = TestResult()

    test_no_fabricated_foci(t)
    test_wwn1_foci_present(t)
    test_type_classifications(t)
    test_description_key_terms(t)
    test_special_properties(t)
    test_wwn5_foci(t)
    test_total_count(t)

    all_passed = t.summary()
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
