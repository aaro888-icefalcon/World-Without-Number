#!/usr/bin/env python3
"""
Game Initialization — Generate a valid starting state.json.

Creates a complete, schema-valid state.json with:
- A fully built character (via create-character)
- Campaign metadata
- Initial scene (campaign-appropriate)
- World seeding (clocks, factions, situation) for the selected campaign
- Empty but valid containers for all required state fields

Usage:
    python initialize_game.py --name "Kael" --class warrior --background 1 \
        --campaign nyc --seed 42

The output is a JSON object suitable for writing to state.json.
"""

import argparse
import json
import sys
import os
import random
from datetime import datetime

# Path setup — same as emergence_cli.py
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

_parent_dir = os.path.dirname(_script_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

_skills_dir = os.path.join(_parent_dir, 'phases', '3-resolution', 'skills')
if os.path.isdir(_skills_dir):
    for _domain in os.listdir(_skills_dir):
        for _subdir in ['scripts', 'tables']:
            _p = os.path.join(_skills_dir, _domain, _subdir)
            if os.path.isdir(_p) and _p not in sys.path:
                sys.path.insert(0, _p)


# ═══════════════════════════════════════════════════════════════════════════════
# NYC CAMPAIGN SEED DATA
# ═══════════════════════════════════════════════════════════════════════════════

NYC_INITIAL_CLOCKS = [
    {
        "id": "clock_food_crisis",
        "name": "Food Crisis",
        "current": 0,
        "max": 6,
        "owner": "nyc_population",
        "goal": "Starvation spiral",
        "completion_effect": "Mass starvation, total social collapse",
        "hidden": False,
        "status": "active",
        "history": [],
        "portents": [
            {"at": 2, "event": "Rationing begins, social tension rises", "mechanical": "Social checks +1 difficulty", "fired": False},
            {"at": 4, "event": "Food riots break out in outer boroughs", "mechanical": "Urban threat level +2", "fired": False},
            {"at": 6, "event": "Starvation spiral begins", "mechanical": "Mass casualties, faction collapse", "fired": False},
        ],
    },
    {
        "id": "clock_verdancy_front",
        "name": "Verdancy Western Front",
        "current": 0,
        "max": 8,
        "owner": "the_verdancy",
        "goal": "Overrun western boroughs",
        "completion_effect": "Western boroughs overrun, population retreat",
        "hidden": False,
        "status": "active",
        "history": [],
        "portents": [
            {"at": 2, "event": "Spore-drifts cross western passes", "mechanical": "Western travel hazard +1", "fired": False},
            {"at": 4, "event": "Carnivorous creatures appear", "mechanical": "Western encounters shift to Verdancy types", "fired": False},
            {"at": 6, "event": "Western valleys contested", "mechanical": "Western borough threat level +3", "fired": False},
        ],
    },
    {
        "id": "clock_pelegrinian",
        "name": "Pelegrinian Pressure",
        "current": 0,
        "max": 10,
        "owner": "pelegrin",
        "goal": "Subdue or vassalize NYC",
        "completion_effect": "Military confrontation or forced vassalage",
        "hidden": True,
        "status": "active",
        "history": [],
        "portents": [
            {"at": 3, "event": "Economic pressure begins", "mechanical": "Trade prices +20%", "fired": False},
            {"at": 6, "event": "Diplomatic isolation deepens", "mechanical": "External faction disposition -2", "fired": False},
            {"at": 9, "event": "Military buildup on border", "mechanical": "Threat of invasion imminent", "fired": False},
        ],
    },
    {
        "id": "clock_gallery_seals",
        "name": "Gallery Seal Degradation",
        "current": 0,
        "max": 8,
        "owner": "imperator",
        "goal": "Weaken containment",
        "completion_effect": "Major surge event, Level 1 overrun",
        "hidden": True,
        "status": "active",
        "history": [],
        "portents": [
            {"at": 2, "event": "Surge frequency increases", "mechanical": "Gallery encounter rate +1", "fired": False},
            {"at": 5, "event": "Deeper servitors appear on upper levels", "mechanical": "Gallery creature tier +1", "fired": False},
            {"at": 8, "event": "Seals fail, massive surge", "mechanical": "Level 1 overrun, evacuation required", "fired": False},
        ],
    },
    {
        "id": "clock_manthva_succession",
        "name": "Manthva Succession",
        "current": 0,
        "max": 6,
        "owner": "manthva_houses",
        "goal": "Resolve succession",
        "completion_effect": "Succession resolved (winner depends on NYC actions)",
        "hidden": True,
        "status": "active",
        "history": [],
        "portents": [
            {"at": 2, "event": "House tensions escalate", "mechanical": "Manthva diplomacy checks +1 difficulty", "fired": False},
            {"at": 4, "event": "Intelligence becomes conditional", "mechanical": "Manthva info requires favors", "fired": False},
        ],
    },
    {
        "id": "clock_borough_divergence",
        "name": "Borough Divergence",
        "current": 0,
        "max": 6,
        "owner": "nyc_boroughs",
        "goal": "Full borough independence",
        "completion_effect": "Full borough independence, Council dissolution",
        "hidden": False,
        "status": "active",
        "history": [],
        "portents": [
            {"at": 2, "event": "Borough autonomy increases", "mechanical": "Cross-borough cooperation checks +1 difficulty", "fired": False},
            {"at": 4, "event": "Council authority weakens", "mechanical": "Central directives ignored 50% of the time", "fired": False},
        ],
    },
]

NYC_INITIAL_SCENE = {
    "scene_id": "scene_001",
    "location": "Carven Peaks — Lower Manhattan",
    "region": "carven-peaks",
    "region_id": "carven-peaks",
    "threat_level": 3,
    "scene_type": "exploration",
}

NYC_CAMPAIGN_META = {
    "name": "NYC — Carven Peaks Campaign",
    "current_day": 1,
    "current_time": "08:00",
    "current_location": "Carven Peaks — Lower Manhattan",
}

NYC_WORLD_SITUATION = {
    "transport_day": 0,
    "days_since_transport": 1,
    "food_supply_days": 8,
    "technology_status": "all_electronics_dead",
    "government_status": "fragmented",
    "population": 9500000,
    "surge_status": "initial_breach_contained",
    "verdancy_status": "spore_drifts_approaching",
    "revelations_count": 0,
}


# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT (GENERIC) CAMPAIGN SEED DATA
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_INITIAL_SCENE = {
    "scene_id": "scene_001",
    "location": "Crossroads Inn",
    "region": "starting",
    "threat_level": 1,
    "scene_type": "social",
}

DEFAULT_CAMPAIGN_META = {
    "name": "Latter Earth Campaign",
    "current_day": 1,
    "current_time": "08:00",
    "current_location": "Crossroads Inn",
}


# ═══════════════════════════════════════════════════════════════════════════════
# STATE GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

def generate_initial_state(character_data, campaign="default", seed=None):
    """Build a complete, schema-valid state.json from character data and campaign selection.

    Args:
        character_data: dict from create_character()
        campaign: "default" or "nyc"
        seed: RNG seed used (for recording)

    Returns:
        Complete state.json dict
    """
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    # Select campaign-specific data
    if campaign == "nyc":
        scene = dict(NYC_INITIAL_SCENE)
        campaign_meta = dict(NYC_CAMPAIGN_META)
        clocks = [dict(c) for c in NYC_INITIAL_CLOCKS]
        world_situation = dict(NYC_WORLD_SITUATION)
    else:
        scene = dict(DEFAULT_INITIAL_SCENE)
        campaign_meta = dict(DEFAULT_CAMPAIGN_META)
        clocks = []
        world_situation = {}

    campaign_meta["start_date"] = datetime.utcnow().strftime("%Y-%m-%d")

    state = {
        "schema_version": "7.5.0",
        "content_version": "1.0.0",
        "meta": {
            "last_played": now,
            "session_number": 1,
        },
        "character": character_data,
        "world": {},
        "current_scene": scene,
        "campaign": campaign_meta,
        "current_day": campaign_meta["current_day"],
        "current_time": campaign_meta["current_time"],
        "clocks": clocks,
        "world_situation": world_situation,
        "inter_group_relations": [],
        "pc_standing": [],
        "human_factions": [],
        "external_threats": [],
        "meta_clocks": [],
        "faction_relationships": [],
        "known_npcs": [],
        "known_locations": [],
        "campaign_arcs": [],
        "active_quests": [],
        "chronicle": [
            {
                "day": 1,
                "time": campaign_meta["current_time"],
                "event": f"Campaign begins. {character_data['name']} enters the world.",
                "significance": "major",
                "tags": ["campaign_start", "character_creation"],
            }
        ],
        "clock_log": [],
        "combat_state": {"active": False},
        "consequence_tracker": [],
        "session": {
            "drama_budget": 3,
            "drama_events": [],
        },
        "world_pulse": {
            "day": 1,
            "news": "A new story begins.",
            "rumors": [],
            "trends": [],
            "arrivals": [],
        },
        "last_played": now,
    }

    return state


def initialize_game(name, class_name, background_id, method="standard_array",
                     campaign="default", partial_classes=None, tradition=None,
                     foci=None, spells=None, equipment_package=None,
                     skill_method=None, free_skill=None, seed=None):
    """Full game initialization: create character + generate world state.

    Returns:
        dict with "state" (complete state.json), "character_summary", and "initialization_report"
    """
    from character import create_character

    # Create the character
    character = create_character(
        name=name,
        class_name=class_name,
        background_id=background_id,
        method=method,
        partial_classes=partial_classes,
        tradition=tradition,
        foci=foci,
        spells=spells,
        equipment_package=equipment_package,
        skill_method=skill_method,
        free_skill=free_skill,
    )

    # Build the complete state
    state = generate_initial_state(character, campaign=campaign, seed=seed)

    # Build summary report
    summary = {
        "name": character["name"],
        "class": character["class"],
        "level": character["level"],
        "background": character.get("background", "Unknown"),
        "hp": f"{character['hp']['current']}/{character['hp']['max']}",
        "ac": character["armor_class"],
        "foci": character.get("foci", []),
        "campaign": campaign,
        "starting_location": state["current_scene"]["location"],
        "starting_clocks": len(state["clocks"]),
    }

    if character.get("partial_classes"):
        summary["partial_classes"] = character["partial_classes"]
    if character.get("tradition"):
        summary["tradition"] = character["tradition"]

    return {
        "state": state,
        "character_summary": summary,
        "initialization_report": {
            "status": "success",
            "campaign": campaign,
            "character_created": True,
            "world_seeded": campaign != "default" or True,
            "clocks_initialized": len(state["clocks"]),
            "starting_scene": state["current_scene"]["location"],
            "seed": seed,
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new game — create character and seed world state"
    )
    parser.add_argument("--name", required=True, help="Character name")
    parser.add_argument("--class", dest="class_name", required=True,
                        choices=["warrior", "expert", "mage", "adventurer"])
    parser.add_argument("--background", type=int, required=True, help="Background ID (1-20)")
    parser.add_argument("--method", default="standard_array",
                        choices=["standard_array", "roll_3d6"])
    parser.add_argument("--campaign", default="default",
                        choices=["default", "nyc"],
                        help="Campaign to initialize (default: generic Latter Earth)")
    parser.add_argument("--partial-classes", default=None,
                        help="Comma-separated partial classes for adventurer")
    parser.add_argument("--tradition", default=None,
                        choices=["high_mage", "elementalist", "necromancer", "healer", "vowed", "invoker"])
    parser.add_argument("--foci", default=None, help="Comma-separated focus names")
    parser.add_argument("--spells", default=None, help="Comma-separated starting spells")
    parser.add_argument("--equipment-package", default=None)
    parser.add_argument("--skill-method", default=None, choices=["quick"])
    parser.add_argument("--free-skill", default=None)
    parser.add_argument("--seed", type=int, default=None, help="RNG seed")

    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    partial_classes = None
    if args.partial_classes:
        partial_classes = [p.strip() for p in args.partial_classes.split(",")]

    foci = None
    if args.foci:
        foci = [f.strip() for f in args.foci.split(",")]

    spells = None
    if args.spells:
        spells = [s.strip() for s in args.spells.split(",")]

    result = initialize_game(
        name=args.name,
        class_name=args.class_name,
        background_id=args.background,
        method=args.method,
        campaign=args.campaign,
        partial_classes=partial_classes,
        tradition=args.tradition,
        foci=foci,
        spells=spells,
        equipment_package=args.equipment_package,
        skill_method=args.skill_method,
        free_skill=args.free_skill,
        seed=args.seed,
    )

    result["seed"] = args.seed
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
