"""WWN treasure generation — roll treasure by tier and context.

Treasure tiers correspond roughly to dungeon depth / threat level.
"""

import sys
import os
import random

_this_dir = os.path.dirname(os.path.abspath(__file__))
_core_scripts = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(_this_dir))),
                             "core", "scripts")
if _core_scripts not in sys.path:
    sys.path.insert(0, _core_scripts)

from dice import roll, roll_dice


# Treasure tables by tier (simplified from WWN 3)
COIN_TABLES = {
    1: {"silver": "3d6",    "gold": "0"},
    2: {"silver": "3d6*5",  "gold": "1d6"},
    3: {"silver": "3d6*10", "gold": "2d6"},
    4: {"silver": "3d6*20", "gold": "3d6*2"},
    5: {"silver": "3d6*50", "gold": "3d6*5"},
}

MUNDANE_ITEMS = [
    "A well-made rope (50 feet)",
    "A sealed clay jar of preserved food",
    "A set of lockpicks in a leather case",
    "A brass spyglass, slightly dented",
    "A bundle of torches (6)",
    "A healer's kit with bandages and salve",
    "A waterproof map case (empty)",
    "A steel mirror, small enough to pocket",
    "A set of dice, carved from bone",
    "A coil of fine wire",
    "A tinderbox with flint and steel",
    "An iron crowbar",
]

MINOR_TREASURES = [
    "A silver ring set with a blue stone (10 sp)",
    "A carved ivory figurine of a beast (15 sp)",
    "A gold-chased dagger in a tooled sheath (25 sp)",
    "A bolt of fine silk, slightly faded (20 sp)",
    "An ancient coin collection in a velvet pouch (30 sp)",
    "A silver holy symbol of a forgotten faith (15 sp)",
    "A jeweled hairpin (20 sp)",
    "A crystal vial of rare perfume (10 sp)",
    "A set of gold earrings (25 sp)",
    "A small painting on ivory, very old (40 sp)",
]

MAJOR_TREASURES = [
    "A gold-and-sapphire necklace (200 sp)",
    "A jeweled crown fragment (150 sp)",
    "A masterwork longsword with silver inlay (100 sp)",
    "A bolt of cloth-of-gold (175 sp)",
    "A large cut gemstone (250 sp)",
    "A set of golden tableware (200 sp)",
    "A jeweled scepter of ancient make (300 sp)",
    "An illuminated manuscript on vellum (150 sp)",
]


def _roll_coins(tier):
    """Roll coins for a treasure tier."""
    table = COIN_TABLES.get(tier, COIN_TABLES[1])
    silver = 0
    gold = 0

    silver_expr = table["silver"]
    if silver_expr != "0":
        if "*" in silver_expr:
            base, mult = silver_expr.split("*")
            r = roll(base)
            silver = r["total"] * int(mult)
        else:
            r = roll(silver_expr)
            silver = r["total"]

    gold_expr = table["gold"]
    if gold_expr != "0":
        if "*" in gold_expr:
            base, mult = gold_expr.split("*")
            r = roll(base)
            gold = r["total"] * int(mult)
        else:
            r = roll(gold_expr)
            gold = r["total"]

    return {"silver": silver, "gold": gold}


def roll_treasure(tier, context="dungeon"):
    """Roll treasure for a given tier.

    Args:
        tier: 1-5, representing treasure quality
        context: "dungeon", "wilderness", "quest" — affects item mix

    Returns:
        dict with coins, items, and total estimated value
    """
    tier = max(1, min(5, tier))

    coins = _roll_coins(tier)
    items = []

    # Mundane items (always 1-2)
    mundane_count = random.randint(1, 2)
    items.extend(random.sample(MUNDANE_ITEMS, min(mundane_count, len(MUNDANE_ITEMS))))

    # Minor treasures (tier 2+)
    if tier >= 2:
        minor_count = random.randint(0, min(tier - 1, 2))
        if minor_count > 0:
            items.extend(random.sample(MINOR_TREASURES, min(minor_count, len(MINOR_TREASURES))))

    # Major treasures (tier 4+)
    if tier >= 4:
        major_count = random.randint(0, 1)
        if major_count > 0:
            items.extend(random.sample(MAJOR_TREASURES, min(major_count, len(MAJOR_TREASURES))))

    total_value = coins["silver"] + coins["gold"] * 10

    return {
        "tier": tier,
        "context": context,
        "coins": coins,
        "items": items,
        "estimated_value_sp": total_value,
        "arithmetic_trace": f"Treasure (tier {tier}): {coins['silver']}sp + {coins['gold']}gp + {len(items)} items = ~{total_value}sp total",
    }
