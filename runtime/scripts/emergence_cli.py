#!/usr/bin/env python3
"""
RPG ENGINE — Unified CLI for Worlds Without Number
Single entry point for all game mechanics. Outputs JSON for artifact population.

Usage:
    python emergence_cli.py <command> [options]

Commands:
    roll             Roll dice (e.g., 1d20+3, 2d6, 1d8-1)
    skill-check      Make a 2d6 skill check
    save             Make a saving throw (physical/evasion/mental)
    attack           Resolve a combat attack
    create-character Create a new WWN character
    cast-spell       Cast a spell using Effort
    encounter        Generate a random encounter
    travel           Resolve multi-day overland travel
    generate-scene   Generate a scene from tags
    treasure         Roll treasure by tier
    world-tick       Advance world state between sessions
    generate-npc     Generate an NPC with voice card
    reaction-roll    Roll NPC reaction (2d6)
    faction-turn     Run a faction turn
    check-triggers   Evaluate all pending trigger conditions
    expand-action    Expand classified action into command sequence (step 1.5)
    post-resolution  Detect state deltas and suggest follow-ups (step 5.5)
    state-snapshot   Create pre-resolution state snapshot
    initialize-game  Initialize a new game (character + world state)
"""

import argparse
import json
import sys
import os
import random

# Ensure script directory is in path for imports
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

# Parent directory (runtime/)
_parent_dir = os.path.dirname(_script_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Phase 3 domain script and table directories (physical co-location)
_skills_dir = os.path.join(_parent_dir, 'phases', '3-resolution', 'skills')
if os.path.isdir(_skills_dir):
    for _domain in os.listdir(_skills_dir):
        for _subdir in ['scripts', 'tables']:
            _p = os.path.join(_skills_dir, _domain, _subdir)
            if os.path.isdir(_p) and _p not in sys.path:
                sys.path.insert(0, _p)


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE A — CORE COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

def cmd_roll(args):
    """Roll dice using standard notation."""
    from dice import roll
    result = roll(args.expression)
    result["seed"] = args.seed
    print(json.dumps(result, indent=2, default=str))


def cmd_skill_check(args):
    """Make a 2d6 + skill + attribute modifier check against a difficulty."""
    from dice import roll_check
    modifier = args.attribute_mod + args.skill_level
    result = roll_check(modifier=modifier, target=args.difficulty)
    result["attribute_mod"] = args.attribute_mod
    result["skill_level"] = args.skill_level
    result["difficulty"] = args.difficulty
    result["seed"] = args.seed
    print(json.dumps(result, indent=2, default=str))


def cmd_save(args):
    """Make a saving throw."""
    from dice import roll_save
    save_target = 16 - (args.level + args.modifier)
    result = roll_save(save_target)
    result["save_type"] = args.type
    result["level"] = args.level
    result["modifier"] = args.modifier
    result["seed"] = args.seed
    print(json.dumps(result, indent=2, default=str))


def cmd_attack(args):
    """Resolve a combat attack."""
    from combat import resolve_attack
    attacker = {
        "attack_bonus": args.attack_bonus,
        "skill_level": args.skill_level,
        "attribute_mod": args.attribute_mod,
        "weapon": {
            "damage": args.weapon_damage,
            "shock": args.shock if args.shock != "none" else None,
            "traits": [],
        },
        "killing_blow_bonus": args.killing_blow or 0,
    }
    defender = {
        "armor_class": args.target_ac,
        "hp": {"current": args.target_hp, "max": args.target_hp},
    }
    result = resolve_attack(attacker, defender)
    result["seed"] = args.seed
    print(json.dumps(result, indent=2, default=str))


def cmd_create_character(args):
    """Create a new WWN character."""
    from character import create_character
    partial_classes = None
    if args.partial_classes:
        partial_classes = [p.strip() for p in args.partial_classes.split(",")]
    foci = None
    if args.foci:
        foci = [f.strip() for f in args.foci.split(",")]
    spells = None
    if args.spells:
        spells = [s.strip() for s in args.spells.split(",")]
    char = create_character(
        name=args.name,
        class_name=getattr(args, 'class'),
        background_id=args.background,
        method=args.method,
        partial_classes=partial_classes,
        tradition=args.tradition,
        foci=foci,
        spells=spells,
        equipment_package=args.equipment_package,
        skill_method=args.skill_method,
        free_skill=args.free_skill,
    )
    char["seed"] = args.seed
    print(json.dumps(char, indent=2, default=str))


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE B — MAGIC & ENCOUNTER HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

def cmd_cast_spell(args):
    """Cast a spell using the Effort system."""
    from magic import cast_spell
    result = cast_spell(
        spell_name=args.spell_name,
        caster_level=args.caster_level,
        tradition=args.tradition,
        effort_current=args.current_effort,
        system_strain_current=args.system_strain,
        system_strain_max=args.system_strain_max,
    )
    result["seed"] = args.seed
    print(json.dumps(result, indent=2, default=str))


def cmd_encounter(args):
    """Generate a random encounter for terrain and threat level."""
    from encounter import generate_encounter
    result = generate_encounter(
        terrain=args.terrain,
        threat_level=args.threat_level,
    )
    result["seed"] = args.seed
    print(json.dumps(result, indent=2, default=str))


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE C — EXPLORATION HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

def cmd_travel(args):
    """Resolve multi-day overland travel."""
    from travel import resolve_travel
    result = resolve_travel(
        terrain=args.terrain,
        days=args.days,
        supplies=args.supplies,
        forage_modifier=args.forage_mod,
        threat_level=args.threat_level,
    )
    result["seed"] = args.seed
    print(json.dumps(result, indent=2, default=str))


def cmd_generate_scene(args):
    """Generate a playable scene from tags."""
    from scene import generate_scene
    result = generate_scene(
        scene_type=args.scene_type,
        tag_count=args.tag_count,
        threat_level=args.threat_level,
    )
    result["seed"] = args.seed
    print(json.dumps(result, indent=2, default=str))


def cmd_treasure(args):
    """Roll treasure by tier."""
    from treasure import roll_treasure
    result = roll_treasure(tier=args.tier)
    result["seed"] = args.seed
    print(json.dumps(result, indent=2, default=str))


def cmd_world_tick(args):
    """Advance world state between sessions."""
    from world_tick import advance_world

    # Load current state for clocks and factions
    state_path = os.path.join(_parent_dir, "state.json")
    state = {}
    if os.path.exists(state_path):
        with open(state_path) as f:
            state = json.load(f)

    clocks = state.get("clocks", [])
    factions = state.get("factions", [])

    current_day = state.get("campaign_day", 1)
    result = advance_world(
        days_elapsed=args.days,
        clocks=clocks,
        factions=factions,
        current_day=current_day,
    )
    result["seed"] = args.seed
    print(json.dumps(result, indent=2, default=str))


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE D — SOCIAL & FACTION HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

def cmd_generate_npc(args):
    """Generate an NPC with voice card and personality."""
    from npc import generate_npc
    result = generate_npc(
        importance=args.importance,
        region=args.region,
        tag_count=args.tags,
    )
    result["seed"] = args.seed
    print(json.dumps(result, indent=2, default=str))


def cmd_reaction_roll(args):
    """Roll NPC reaction (2d6 + modifier)."""
    from npc import reaction_roll
    result = reaction_roll(modifier=args.modifier)
    result["seed"] = args.seed
    print(json.dumps(result, indent=2, default=str))


def cmd_faction_turn(args):
    """Run a faction turn for all factions."""
    from faction import faction_turn

    # Load factions from state
    state_path = os.path.join(_parent_dir, "state.json")
    state = {}
    if os.path.exists(state_path):
        with open(state_path) as f:
            state = json.load(f)

    factions = state.get("factions", [])
    result = faction_turn(factions=factions)
    result["seed"] = args.seed
    print(json.dumps(result, indent=2, default=str))


def cmd_level_up(args):
    """Handle level-up command."""
    from character import level_up, calculate_saving_throws
    attributes = json.loads(args.attributes)
    character = {
        "name": args.name,
        "class": args.class_name,
        "level": args.current_level,
        "attributes": attributes,
        "hp": {"current": args.hp_max, "max": args.hp_max},
        "attack_bonus": args.attack_bonus,
        "saving_throws": calculate_saving_throws(args.current_level, attributes),
        "foci": [],
    }
    if args.tradition:
        character["tradition"] = args.tradition
    if args.partial_classes:
        character["partial_classes"] = sorted(args.partial_classes)
    result = level_up(character, args.target_level)
    result["seed"] = args.seed
    print(json.dumps(result, indent=2, default=str))


def cmd_generate_dungeon(args):
    """Handle generate-dungeon command."""
    from dungeon import generate_dungeon
    result = generate_dungeon(depth=args.depth, theme=args.theme)
    result["seed"] = args.seed
    print(json.dumps(result, indent=2, default=str))


def cmd_check_triggers(args):
    """Check all trigger conditions against current state."""
    from triggers import check_all_triggers

    # Load current state
    state_path = args.state_path
    if not os.path.isabs(state_path):
        state_path = os.path.join(_parent_dir, state_path)

    state = {}
    if os.path.exists(state_path):
        with open(state_path) as f:
            state = json.load(f)

    # Optional day override for hypothetical checks
    if args.current_day is not None:
        state["current_day"] = args.current_day

    result = check_all_triggers(state)
    result["seed"] = args.seed
    print(json.dumps(result, indent=2, default=str))


def cmd_expand_action(args):
    """Expand a classified action into a full command sequence."""
    from chain_registry import expand_action

    # Load current state
    state_path = args.state_path
    if not os.path.isabs(state_path):
        state_path = os.path.join(_parent_dir, state_path)

    state = {}
    if os.path.exists(state_path):
        with open(state_path) as f:
            state = json.load(f)

    result = expand_action(args.action, state)
    result["seed"] = args.seed
    print(json.dumps(result, indent=2, default=str))


def cmd_post_resolution(args):
    """Check for state changes after command execution and suggest follow-ups."""
    from triggers import check_post_resolution, create_state_snapshot

    # Load pre-snapshot
    pre_path = args.pre_snapshot
    if not os.path.isabs(pre_path):
        pre_path = os.path.join(_parent_dir, pre_path)

    with open(pre_path) as f:
        pre_snapshot = json.load(f)

    # Load current (post) state
    state_path = args.state_path
    if not os.path.isabs(state_path):
        state_path = os.path.join(_parent_dir, state_path)

    state = {}
    if os.path.exists(state_path):
        with open(state_path) as f:
            state = json.load(f)

    # Parse already-executed commands
    already_executed = set()
    if args.already_executed:
        already_executed = {cmd.strip() for cmd in args.already_executed.split(",")}

    result = check_post_resolution(pre_snapshot, state, already_executed)
    result["seed"] = args.seed
    print(json.dumps(result, indent=2, default=str))


def cmd_state_snapshot(args):
    """Create a state snapshot for post-resolution delta detection."""
    from triggers import create_state_snapshot

    # Load current state
    state_path = args.state_path
    if not os.path.isabs(state_path):
        state_path = os.path.join(_parent_dir, state_path)

    state = {}
    if os.path.exists(state_path):
        with open(state_path) as f:
            state = json.load(f)

    snapshot = create_state_snapshot(state)
    snapshot["seed"] = args.seed
    print(json.dumps(snapshot, indent=2, default=str))


def cmd_initialize_game(args):
    """Initialize a new game — create character and seed world state."""
    from initialize_game import initialize_game
    partial_classes = None
    if args.partial_classes:
        partial_classes = [p.strip() for p in args.partial_classes.split(",")]
    foci = None
    if args.foci:
        foci = [f.strip() for f in args.foci.split(",")]
    spells = None
    if args.spells:
        spells = [s.strip() for s in args.spells.split(",")]
    attribute_assignments = None
    if args.attribute_assignments:
        attribute_assignments = {}
        for pair in args.attribute_assignments.split(","):
            attr, val = pair.strip().split("=")
            attribute_assignments[attr.strip()] = int(val.strip())
    background_skills = None
    if args.background_skills:
        background_skills = [s.strip() for s in args.background_skills.split(",")]
    result = initialize_game(
        name=args.name,
        class_name=getattr(args, 'class'),
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
        attribute_assignments=attribute_assignments,
        background_skills=background_skills,
        physical_boost=args.physical_boost,
        mental_boost=args.mental_boost,
    )
    result["seed"] = args.seed
    print(json.dumps(result, indent=2, default=str))


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN — ARGUMENT PARSER
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="RPG Engine — Worlds Without Number CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--seed", type=int,
        help="Set RNG seed for reproducible command output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Shared --seed argument for all subcommands (allows --seed after subcommand)
    seed_parent = argparse.ArgumentParser(add_help=False)
    seed_parent.add_argument("--seed", type=int, help="Set RNG seed for reproducible output")

    # ── Phase A commands ──────────────────────────────────────────────────────

    # roll
    p_roll = subparsers.add_parser("roll", parents=[seed_parent], help="Roll dice (e.g., 1d20+3)")
    p_roll.add_argument("expression", type=str, help="Dice notation (e.g., 1d20+3, 2d6)")

    # skill-check
    p_skill = subparsers.add_parser("skill-check", parents=[seed_parent], help="2d6 skill check")
    p_skill.add_argument("--attribute-mod", type=int, required=True)
    p_skill.add_argument("--skill-level", type=int, required=True)
    p_skill.add_argument("--difficulty", type=int, required=True)

    # save
    p_save = subparsers.add_parser("save", parents=[seed_parent], help="Saving throw")
    p_save.add_argument("--type", type=str, required=True, choices=["physical", "evasion", "mental"])
    p_save.add_argument("--level", type=int, required=True)
    p_save.add_argument("--modifier", type=int, required=True)

    # attack
    p_attack = subparsers.add_parser("attack", parents=[seed_parent], help="Resolve combat attack")
    p_attack.add_argument("--attack-bonus", type=int, required=True)
    p_attack.add_argument("--skill-level", type=int, required=True)
    p_attack.add_argument("--attribute-mod", type=int, required=True)
    p_attack.add_argument("--weapon-damage", type=str, required=True)
    p_attack.add_argument("--shock", type=str, default="none")
    p_attack.add_argument("--target-ac", type=int, required=True)
    p_attack.add_argument("--target-hp", type=int, required=True)
    p_attack.add_argument("--killing-blow", type=int, default=0)

    # create-character
    p_char = subparsers.add_parser("create-character", parents=[seed_parent], help="Create a new character")
    p_char.add_argument("--name", type=str, required=True)
    p_char.add_argument("--class", type=str, required=True, choices=["warrior", "expert", "mage", "adventurer"])
    p_char.add_argument("--background", type=int, required=True)
    p_char.add_argument("--method", type=str, default="standard_array", choices=["standard_array", "roll_3d6"])
    p_char.add_argument("--partial-classes", type=str, default=None,
                         help="Comma-separated partial classes for adventurer (e.g., 'expert,warrior' or 'accursed,warrior')")
    p_char.add_argument("--tradition", type=str, default=None,
                         choices=["high_mage", "elementalist", "necromancer", "healer", "vowed", "invoker"])
    p_char.add_argument("--foci", type=str, default=None,
                         help="Comma-separated focus names")
    p_char.add_argument("--spells", type=str, default=None,
                         help="Comma-separated starting spell names")
    p_char.add_argument("--equipment-package", type=str, default=None)
    p_char.add_argument("--skill-method", type=str, default=None, choices=["quick"])
    p_char.add_argument("--free-skill", type=str, default=None)

    # ── Phase B commands ──────────────────────────────────────────────────────

    # cast-spell
    p_spell = subparsers.add_parser("cast-spell", parents=[seed_parent], help="Cast a spell using Effort")
    p_spell.add_argument("--spell-name", type=str, required=True)
    p_spell.add_argument("--caster-level", type=int, required=True)
    p_spell.add_argument("--tradition", type=str, required=True,
                         choices=["high_magic", "elementalist", "necromancer", "healer"])
    p_spell.add_argument("--current-effort", type=int, required=True)
    p_spell.add_argument("--system-strain", type=int, required=True)
    p_spell.add_argument("--system-strain-max", type=int, required=True)

    # encounter
    p_enc = subparsers.add_parser("encounter", parents=[seed_parent], help="Generate random encounter")
    p_enc.add_argument("--terrain", type=str, required=True,
                       choices=["forest", "plains", "mountains", "desert", "swamp",
                                "coast", "ruins", "urban", "dungeon", "wilderness"])
    p_enc.add_argument("--threat-level", type=int, required=True)

    # ── Phase C commands ──────────────────────────────────────────────────────

    # travel
    p_travel = subparsers.add_parser("travel", parents=[seed_parent], help="Resolve overland travel")
    p_travel.add_argument("--terrain", type=str, required=True,
                          choices=["road", "plains", "forest", "hills", "mountains",
                                   "desert", "swamp", "coast", "jungle"])
    p_travel.add_argument("--days", type=int, required=True)
    p_travel.add_argument("--supplies", type=int, required=True)
    p_travel.add_argument("--forage-mod", type=int, default=0)
    p_travel.add_argument("--threat-level", type=int, default=3)

    # generate-scene
    p_scene = subparsers.add_parser("generate-scene", parents=[seed_parent], help="Generate scene from tags")
    p_scene.add_argument("--scene-type", type=str, required=True,
                         choices=["wilderness", "ruin", "community"])
    p_scene.add_argument("--tag-count", type=int, default=2)
    p_scene.add_argument("--threat-level", type=int, default=3)

    # treasure
    p_treasure = subparsers.add_parser("treasure", parents=[seed_parent], help="Roll treasure by tier")
    p_treasure.add_argument("--tier", type=int, required=True, choices=[1, 2, 3, 4, 5])

    # world-tick
    p_tick = subparsers.add_parser("world-tick", parents=[seed_parent], help="Advance world state")
    p_tick.add_argument("--days", type=int, required=True)

    # check-triggers
    p_triggers = subparsers.add_parser("check-triggers", parents=[seed_parent],
                                       help="Evaluate all pending trigger conditions")
    p_triggers.add_argument("--state-path", type=str, default="state.json",
                            help="Path to state.json (default: runtime/state.json)")
    p_triggers.add_argument("--current-day", type=int, default=None,
                            help="Override current_day for hypothetical checks")

    # ── Phase D commands ──────────────────────────────────────────────────────

    # generate-npc
    p_npc = subparsers.add_parser("generate-npc", parents=[seed_parent], help="Generate NPC with voice card")
    p_npc.add_argument("--importance", type=str, default="minor",
                       choices=["minor", "major", "faction_leader"])
    p_npc.add_argument("--region", type=str, default="unknown")
    p_npc.add_argument("--tags", type=int, default=1)

    # reaction-roll
    p_react = subparsers.add_parser("reaction-roll", parents=[seed_parent], help="NPC reaction roll")
    p_react.add_argument("--modifier", type=int, default=0)

    # faction-turn
    p_faction = subparsers.add_parser("faction-turn", parents=[seed_parent], help="Run faction turn")

    # level-up
    p_levelup = subparsers.add_parser("level-up", parents=[seed_parent], help="Level up a character")
    p_levelup.add_argument("--name", required=True, help="Character name")
    p_levelup.add_argument("--class-name", required=True, help="Character class")
    p_levelup.add_argument("--current-level", type=int, required=True, help="Current level")
    p_levelup.add_argument("--target-level", type=int, required=True, help="Target level")
    p_levelup.add_argument("--attributes", type=str, required=True, help="JSON attributes dict")
    p_levelup.add_argument("--hp-max", type=int, required=True, help="Current max HP")
    p_levelup.add_argument("--attack-bonus", type=int, default=0, help="Current attack bonus")
    p_levelup.add_argument("--tradition", type=str, default=None, help="Magic tradition (if mage)")
    p_levelup.add_argument("--partial-classes", nargs="*", default=None, help="Partial classes (adventurer)")

    # generate-dungeon
    p_dungeon = subparsers.add_parser("generate-dungeon", parents=[seed_parent], help="Generate a procedural dungeon")
    p_dungeon.add_argument("--depth", type=int, required=True, help="Dungeon depth (affects rooms and threat)")
    p_dungeon.add_argument("--theme", type=str, default=None, help="Dungeon theme (or random)")

    # ── Phase F commands — Action Routing ────────────────────────────────────

    # expand-action
    p_expand = subparsers.add_parser("expand-action", parents=[seed_parent],
                                      help="Expand classified action into command sequence")
    p_expand.add_argument("--action", type=str, required=True,
                          help="Classified action type (e.g., travel, attack, reaction-roll)")
    p_expand.add_argument("--state-path", type=str, default="state.json",
                          help="Path to state.json")

    # post-resolution
    p_post = subparsers.add_parser("post-resolution", parents=[seed_parent],
                                    help="Detect state changes and suggest follow-up commands")
    p_post.add_argument("--pre-snapshot", type=str, required=True,
                        help="Path to pre-resolution state snapshot JSON")
    p_post.add_argument("--state-path", type=str, default="state.json",
                        help="Path to current state.json (post-resolution)")
    p_post.add_argument("--already-executed", type=str, default=None,
                        help="Comma-separated list of already-executed command names")

    # state-snapshot
    p_snap = subparsers.add_parser("state-snapshot", parents=[seed_parent],
                                    help="Create state snapshot for delta detection")
    p_snap.add_argument("--state-path", type=str, default="state.json",
                        help="Path to state.json")

    # ── Phase E commands — Initialization ─────────────────────────────────────

    # initialize-game
    p_init = subparsers.add_parser("initialize-game", parents=[seed_parent], help="Initialize a new game")
    p_init.add_argument("--name", type=str, required=True, help="Character name")
    p_init.add_argument("--class", type=str, required=True, choices=["warrior", "expert", "mage", "adventurer"])
    p_init.add_argument("--background", type=int, required=True, help="Background ID (1-20)")
    p_init.add_argument("--method", type=str, default="boosted_3d6",
                         choices=["boosted_3d6", "standard_array", "roll_3d6"])
    p_init.add_argument("--campaign", type=str, default="nyc", choices=["default", "nyc"],
                         help="Campaign to initialize (default: nyc)")
    p_init.add_argument("--partial-classes", type=str, default=None,
                         help="Comma-separated partial classes for adventurer")
    p_init.add_argument("--tradition", type=str, default=None,
                         choices=["high_mage", "elementalist", "necromancer", "healer", "vowed", "invoker"])
    p_init.add_argument("--foci", type=str, default=None, help="Comma-separated focus names")
    p_init.add_argument("--spells", type=str, default=None, help="Comma-separated starting spells")
    p_init.add_argument("--equipment-package", type=str, default=None)
    p_init.add_argument("--skill-method", type=str, default=None, choices=["quick"])
    p_init.add_argument("--free-skill", type=str, default=None)
    p_init.add_argument("--attribute-assignments", type=str, default=None,
                         help="Comma-separated attr=score pairs, e.g. 'strength=14,dexterity=12,...'")
    p_init.add_argument("--background-skills", type=str, default=None,
                         help="Comma-separated 2 skill names granted by background")
    p_init.add_argument("--physical-boost", type=str, default=None,
                         choices=["strength", "dexterity", "constitution"],
                         help="Physical attribute to boost +2 from background")
    p_init.add_argument("--mental-boost", type=str, default=None,
                         choices=["intelligence", "wisdom", "charisma"],
                         help="Mental attribute to boost +2 from background")

    # ── Parse and dispatch ────────────────────────────────────────────────────

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.seed is not None:
        random.seed(args.seed)

    commands = {
        "roll": cmd_roll,
        "skill-check": cmd_skill_check,
        "save": cmd_save,
        "attack": cmd_attack,
        "create-character": cmd_create_character,
        "cast-spell": cmd_cast_spell,
        "encounter": cmd_encounter,
        "travel": cmd_travel,
        "generate-scene": cmd_generate_scene,
        "treasure": cmd_treasure,
        "world-tick": cmd_world_tick,
        "generate-npc": cmd_generate_npc,
        "reaction-roll": cmd_reaction_roll,
        "faction-turn": cmd_faction_turn,
        "check-triggers": cmd_check_triggers,
        "expand-action": cmd_expand_action,
        "post-resolution": cmd_post_resolution,
        "state-snapshot": cmd_state_snapshot,
        "level-up": cmd_level_up,
        "generate-dungeon": cmd_generate_dungeon,
        "initialize-game": cmd_initialize_game,
    }

    if args.command not in commands:
        print(json.dumps({
            "error": True,
            "message": f"Unknown command: {args.command}"
        }, indent=2), file=sys.stderr)
        sys.exit(1)

    try:
        commands[args.command](args)
    except Exception as e:
        error_output = {
            "error": True,
            "command": args.command,
            "message": str(e),
            "type": type(e).__name__
        }
        print(json.dumps(error_output, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
