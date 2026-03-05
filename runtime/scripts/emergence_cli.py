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
# COMMAND HANDLERS
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
    char = create_character(
        name=args.name,
        class_name=getattr(args, 'class'),
        background_id=args.background,
        method=args.method,
    )
    char["seed"] = args.seed
    print(json.dumps(char, indent=2, default=str))


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
    p_char.add_argument("--class", type=str, required=True, choices=["warrior", "expert", "mage"])
    p_char.add_argument("--background", type=int, required=True)
    p_char.add_argument("--method", type=str, default="standard_array", choices=["standard_array", "roll_3d6"])

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
