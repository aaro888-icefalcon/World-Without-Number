"""Character creation query engine.

Returns filtered chargen options (foci, arts, class abilities, backgrounds)
from Python tables. Used by the GM to make deterministic picks during
character creation instead of hallucinating from markdown docs.
"""

import sys
import os

_this_dir = os.path.dirname(os.path.abspath(__file__))
_tables_dir = os.path.join(os.path.dirname(_this_dir), "tables")
if _tables_dir not in sys.path:
    sys.path.insert(0, _tables_dir)

from foci import FOCI
from classes import CLASSES, ADVENTURER_PROGRESSION
from backgrounds import BACKGROUNDS
from skills import SKILLS
from partial_classes import PARTIAL_CLASSES, BASE_TYPE_MAP


def query_chargen_options(class_name, partial_classes=None, background_id=None):
    """Return all valid chargen options filtered by class and partial classes.

    Args:
        class_name: warrior, expert, mage, or adventurer.
        partial_classes: List of 2 partial class names (adventurer only).
        background_id: Background ID (1-20) for background-specific info.

    Returns:
        Dict with: foci, arts, class_abilities, backgrounds, skills, class_info.
    """
    # Resolve base types for extended partial classes
    base_types = set()
    if partial_classes:
        for pc in partial_classes:
            base_types.add(BASE_TYPE_MAP.get(pc, pc))

    is_mage = class_name == "mage"
    is_partial_mage = class_name == "adventurer" and "mage" in base_types
    is_expert = class_name == "expert"
    is_partial_expert = class_name == "adventurer" and "expert" in base_types
    is_warrior = class_name == "warrior"
    is_partial_warrior = class_name == "adventurer" and "warrior" in base_types

    # ── Filter foci ──────────────────────────────────────────────────────
    valid_foci = {}
    for name, data in FOCI.items():
        ftype = data.get("type", "any")

        # non_mage: cannot be taken by Mages or Partial Mages
        if ftype == "non_mage" and (is_mage or is_partial_mage):
            continue
        # mage_only: only Mages or Partial Mages
        if ftype == "mage_only" and not (is_mage or is_partial_mage):
            continue
        # expert_only: only Experts or Partial Experts
        if ftype == "expert_only" and not (is_expert or is_partial_expert):
            continue
        # warrior: only Warriors or Partial Warriors
        if ftype == "warrior" and not (is_warrior or is_partial_warrior):
            continue

        valid_foci[name] = {
            "type": ftype,
            "category": data.get("category", "core"),
            "level_1": data.get("level_1", ""),
            "level_2": data.get("level_2", ""),
            "repeatable": data.get("repeatable", False),
        }

    # ── Collect arts from partial classes ─────────────────────────────────
    arts_by_class = {}
    if partial_classes:
        for pc in partial_classes:
            if pc in PARTIAL_CLASSES:
                pc_data = PARTIAL_CLASSES[pc]
                arts = []
                for art in pc_data.get("arts", []):
                    arts.append({
                        "name": art["name"],
                        "description": art["description"],
                        "category": art.get("category", "general"),
                    })
                arts_by_class[pc] = {
                    "arts": arts,
                    "art_progression": pc_data.get("art_progression", {}),
                    "arts_at_level_1": pc_data.get("art_progression", {}).get(1, 0),
                    "fixed_progression": pc_data.get("fixed_progression", False),
                    "fixed_arts_by_level": pc_data.get("fixed_arts_by_level", {}),
                    "mandatory_arts": _get_mandatory_arts(pc),
                }

    # ── Class abilities ──────────────────────────────────────────────────
    class_abilities = []
    if class_name == "adventurer" and partial_classes:
        combo_key = "/".join(sorted(f"partial_{p}" for p in partial_classes))
        prog = ADVENTURER_PROGRESSION.get(combo_key, {})
        class_abilities = list(prog.get("abilities", []))
    elif class_name in CLASSES:
        class_abilities = list(CLASSES[class_name].get("abilities", {}).keys())

    # ── Class info ───────────────────────────────────────────────────────
    class_info = {}
    if class_name == "adventurer" and partial_classes:
        combo_key = "/".join(sorted(f"partial_{p}" for p in partial_classes))
        prog = ADVENTURER_PROGRESSION.get(combo_key, {})
        if prog:
            l1 = prog.get(1, {})
            class_info = {
                "combo_key": combo_key,
                "hit_die": prog.get("hit_die", l1.get("hd", "1d6")),
                "attack_bonus_l1": l1.get("ab", 0),
                "focus_slots_l1": l1.get("focus", ""),
            }
        # Add partial class details
        for pc in partial_classes:
            if pc in PARTIAL_CLASSES:
                pc_data = PARTIAL_CLASSES[pc]
                class_info[f"{pc}_bonus_skill"] = pc_data.get("bonus_skill")
                class_info[f"{pc}_effort_formula"] = pc_data.get("effort_formula")
                class_info[f"{pc}_combat_skill"] = pc_data.get("combat_skill")
    elif class_name in CLASSES:
        cls = CLASSES[class_name]
        l1 = cls["progression"][1]
        class_info = {
            "hit_die": cls["progression"][1]["hd"],
            "attack_bonus_l1": l1["ab"],
            "abilities": {k: v for k, v in cls.get("abilities", {}).items()},
        }

    # ── Background info ──────────────────────────────────────────────────
    bg_info = None
    if background_id and background_id in BACKGROUNDS:
        bg = BACKGROUNDS[background_id]
        bg_info = {
            "id": background_id,
            "name": bg["name"],
            "free_skill": bg["free_skill"],
            "quick_skills": bg["quick_skills"],
        }

    # ── All backgrounds (for GM to pick from) ────────────────────────────
    all_backgrounds = {}
    for bid, bg in BACKGROUNDS.items():
        all_backgrounds[bid] = {
            "name": bg["name"],
            "free_skill": bg["free_skill"],
            "quick_skills": bg["quick_skills"],
        }

    # ── All skills ───────────────────────────────────────────────────────
    all_skills = {}
    for sname, sdata in SKILLS.items():
        all_skills[sname] = {
            "description": sdata.get("description", ""),
            "type": sdata.get("type", "non-combat"),
        }

    return {
        "valid_foci": valid_foci,
        "arts_by_class": arts_by_class,
        "class_abilities": class_abilities,
        "class_info": class_info,
        "background": bg_info,
        "all_backgrounds": all_backgrounds,
        "all_skills": all_skills,
    }


def _get_mandatory_arts(partial_class_name):
    """Return list of mandatory starting arts for a partial class."""
    # Accursed: Blade + Bolt are suggested defaults but not enforced in code
    # Skinshifter: Change Form is mandatory
    # Mageslayer: fixed progression (all arts are mandatory)
    mandatory = {
        "skinshifter": ["Change Form"],
        # Note: Accursed Blade + Bolt are NOT mandatory per user feedback
    }
    return mandatory.get(partial_class_name, [])
