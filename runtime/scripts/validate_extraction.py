#!/usr/bin/env python3
"""
Extraction Validator — Smoke tests for extracted WWN data integrity.

Verifies that all extracted tables have expected counts and required fields.
Run: python runtime/scripts/validate_extraction.py
"""

import sys
import os

# Set up paths
_script_dir = os.path.dirname(os.path.abspath(__file__))
_runtime_dir = os.path.dirname(_script_dir)
_skills_dir = os.path.join(_runtime_dir, 'phases', '3-resolution', 'skills')
for _domain in ['core', 'combat']:
    for _subdir in ['scripts', 'tables']:
        _p = os.path.join(_skills_dir, _domain, _subdir)
        if os.path.isdir(_p) and _p not in sys.path:
            sys.path.insert(0, _p)


def check(name, condition, detail=""):
    if condition:
        print(f"  OK  {name}")
        return True
    else:
        print(f"  FAIL {name}: {detail}")
        return False


def main():
    print("Extraction Validation — Smoke Tests")
    print("=" * 50)
    all_ok = True

    # 1. Attributes
    from attributes import ATTRIBUTES, ATTRIBUTE_MODIFIERS, get_modifier
    all_ok &= check("attributes count", len(ATTRIBUTES) == 6, f"got {len(ATTRIBUTES)}")
    all_ok &= check("modifier(3)=-2", get_modifier(3) == -2)
    all_ok &= check("modifier(18)=2", get_modifier(18) == 2)

    # 2. Skills
    from skills import SKILLS
    all_ok &= check(f"skills count >= 20", len(SKILLS) >= 20, f"got {len(SKILLS)}")
    for s in ["stab", "shoot", "magic", "notice", "heal"]:
        all_ok &= check(f"skill '{s}' exists", s in SKILLS)

    # 3. Equipment
    from equipment import WEAPONS, ARMOR, WEAPON_TRAITS
    all_ok &= check(f"weapons count >= 25", len(WEAPONS) >= 25, f"got {len(WEAPONS)}")
    all_ok &= check(f"armor count >= 10", len(ARMOR) >= 10, f"got {len(ARMOR)}")
    for w in WEAPONS:
        all_ok &= check(f"weapon '{w['name']}' has damage", "damage" in w, f"missing damage field")

    # 4. Classes
    from classes import CLASSES, XP_TABLE
    all_ok &= check("3 classes", len(CLASSES) == 3, f"got {len(CLASSES)}")
    all_ok &= check("XP table has 10 levels", len(XP_TABLE) == 10)
    for c in ["warrior", "expert", "mage"]:
        all_ok &= check(f"class '{c}' exists", c in CLASSES)

    # 5. Backgrounds
    from backgrounds import BACKGROUNDS
    all_ok &= check("20 backgrounds", len(BACKGROUNDS) == 20, f"got {len(BACKGROUNDS)}")
    for bg_id, bg in BACKGROUNDS.items():
        all_ok &= check(f"bg {bg_id} has name", "name" in bg)

    # 6. Foci
    from foci import FOCI
    all_ok &= check(f"foci count >= 15", len(FOCI) >= 15, f"got {len(FOCI)}")
    for name, f in FOCI.items():
        all_ok &= check(f"focus '{name}' has level_1/level_2",
                        "level_1" in f and "level_2" in f)

    # 7. Bestiary
    from bestiary import CREATURES, HUMAN_TEMPLATES, REACTION_TABLE
    all_ok &= check(f"creatures >= 15", len(CREATURES) >= 15, f"got {len(CREATURES)}")
    all_ok &= check(f"human templates >= 5", len(HUMAN_TEMPLATES) >= 5)
    all_ok &= check(f"reaction table entries >= 10", len(REACTION_TABLE) >= 10)
    for c in CREATURES:
        for field in ["name", "hd", "ac", "atk", "dmg", "move", "ml", "save"]:
            all_ok &= check(f"creature '{c['name']}' has '{field}'", field in c)

    print("=" * 50)
    if all_ok:
        print("ALL EXTRACTION CHECKS PASSED")
        return 0
    else:
        print("SOME CHECKS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
