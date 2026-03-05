"""WWN dice roller — seedable, deterministic, with arithmetic trace.

All randomness in the engine flows through this module.
"""

import random
import re


def parse_dice_notation(expression):
    """Parse dice notation like '2d6+4', '1d20-1', '1d8', '3d6'.

    Returns dict with count, sides, modifier.
    """
    expression = expression.strip().lower()
    m = re.match(r'^(\d+)d(\d+)\s*([+\-]\s*\d+)?$', expression)
    if not m:
        raise ValueError(f"Invalid dice notation: '{expression}'")
    count = int(m.group(1))
    sides = int(m.group(2))
    modifier = int(m.group(3).replace(' ', '')) if m.group(3) else 0
    return {"count": count, "sides": sides, "modifier": modifier}


def roll_dice(count, sides):
    """Roll count dice of given sides. Returns list of individual rolls."""
    return [random.randint(1, sides) for _ in range(count)]


def roll(expression):
    """Roll dice from a notation string. Returns structured result.

    Args:
        expression: Dice notation string like '1d20+3', '2d6', '1d8-1'

    Returns:
        dict with keys: expression, rolls, modifier, total, arithmetic_trace
    """
    parsed = parse_dice_notation(expression)
    rolls = roll_dice(parsed["count"], parsed["sides"])
    dice_sum = sum(rolls)
    total = dice_sum + parsed["modifier"]

    # Build arithmetic trace for narration
    rolls_str = "+".join(str(r) for r in rolls)
    if parsed["modifier"] > 0:
        trace = f"[{rolls_str}]+{parsed['modifier']} = {total}"
    elif parsed["modifier"] < 0:
        trace = f"[{rolls_str}]{parsed['modifier']} = {total}"
    else:
        trace = f"[{rolls_str}] = {total}"

    return {
        "expression": expression,
        "rolls": rolls,
        "modifier": parsed["modifier"],
        "total": total,
        "arithmetic_trace": trace,
    }


def roll_check(modifier=0, target=None):
    """Roll 2d6 + modifier for a skill check.

    Returns dict with roll details and success/failure if target provided.
    """
    rolls = roll_dice(2, 6)
    total = sum(rolls) + modifier

    result = {
        "rolls": rolls,
        "modifier": modifier,
        "total": total,
        "arithmetic_trace": f"[{rolls[0]}+{rolls[1]}]+{modifier} = {total}",
    }

    if target is not None:
        result["target"] = target
        result["success"] = total >= target
        result["margin"] = total - target

    return result


def roll_save(save_target):
    """Roll 1d20 for a saving throw against a target number.

    Returns dict with roll, target, and success.
    """
    die = roll_dice(1, 20)[0]
    return {
        "roll": die,
        "target": save_target,
        "success": die >= save_target,
        "arithmetic_trace": f"d20=[{die}] vs target {save_target}",
    }


def roll_attack(attack_bonus):
    """Roll 1d20 + attack bonus for an attack roll.

    Returns dict with die, bonus, total.
    """
    die = roll_dice(1, 20)[0]
    total = die + attack_bonus
    return {
        "die": die,
        "bonus": attack_bonus,
        "total": total,
        "natural_20": die == 20,
        "natural_1": die == 1,
        "arithmetic_trace": f"d20=[{die}]+{attack_bonus} = {total}",
    }
