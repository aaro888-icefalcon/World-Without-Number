"""WWN combat resolution engine.

Handles attack rolls, damage, shock, morale, and zone-based positioning.
All combat mechanics flow through this module — the LLM never calculates combat.
"""

import sys
import os
import random
from enum import Enum

# Add sibling script dirs to path for imports
_this_dir = os.path.dirname(os.path.abspath(__file__))
_core_scripts = os.path.join(os.path.dirname(os.path.dirname(_this_dir)), "core", "scripts")
if _core_scripts not in sys.path:
    sys.path.insert(0, _core_scripts)

from dice import roll, roll_dice, roll_attack, parse_dice_notation


# ═══════════════════════════════════════════════════════════════════════════════
# ZONE-BASED COMBAT POSITIONING
# ═══════════════════════════════════════════════════════════════════════════════

class CombatZone(Enum):
    """Abstract combat zones per AI limitation L8 (no spatial reasoning)."""
    MELEE = "melee"      # Adjacent, within 5'
    NEAR = "near"        # 30' — one Move action away
    FAR = "far"          # 100' — two Move actions away
    DISTANT = "distant"  # 300'+ — ranged weapons only


# Movement costs between zones (number of Move actions required)
ZONE_MOVEMENT = {
    (CombatZone.MELEE, CombatZone.NEAR): 1,
    (CombatZone.NEAR, CombatZone.MELEE): 1,
    (CombatZone.NEAR, CombatZone.FAR): 1,
    (CombatZone.FAR, CombatZone.NEAR): 1,
    (CombatZone.FAR, CombatZone.DISTANT): 1,
    (CombatZone.DISTANT, CombatZone.FAR): 1,
    (CombatZone.MELEE, CombatZone.FAR): 2,
    (CombatZone.FAR, CombatZone.MELEE): 2,
    (CombatZone.NEAR, CombatZone.DISTANT): 2,
    (CombatZone.DISTANT, CombatZone.NEAR): 2,
    (CombatZone.MELEE, CombatZone.DISTANT): 3,
    (CombatZone.DISTANT, CombatZone.MELEE): 3,
}


class CombatState:
    """Track combatant positions in abstract zones."""

    def __init__(self):
        self.combatants = {}  # id -> CombatZone

    def add_combatant(self, combatant_id, zone=CombatZone.NEAR):
        self.combatants[combatant_id] = zone

    def get_zone(self, combatant_id):
        return self.combatants.get(combatant_id)

    def move_combatant(self, combatant_id, new_zone):
        self.combatants[combatant_id] = new_zone

    def can_melee_attack(self, attacker_id, defender_id):
        """Both must be in MELEE zone to melee attack."""
        return (self.combatants.get(attacker_id) == CombatZone.MELEE and
                self.combatants.get(defender_id) == CombatZone.MELEE)

    def can_ranged_attack(self, attacker_id, defender_id, max_range_zone=CombatZone.FAR):
        """Check if defender is within max range zone."""
        zone_order = [CombatZone.MELEE, CombatZone.NEAR, CombatZone.FAR, CombatZone.DISTANT]
        def_zone = self.combatants.get(defender_id)
        if def_zone is None:
            return False
        return zone_order.index(def_zone) <= zone_order.index(max_range_zone)

    def to_dict(self):
        return {cid: zone.value for cid, zone in self.combatants.items()}


# ═══════════════════════════════════════════════════════════════════════════════
# SHOCK DAMAGE
# ═══════════════════════════════════════════════════════════════════════════════

def parse_shock(shock_str):
    """Parse shock notation like '2/15' into (damage, ac_threshold).
    Returns None if no shock."""
    if shock_str is None or shock_str == "None":
        return None
    parts = shock_str.split("/")
    if len(parts) != 2:
        return None
    dmg = int(parts[0])
    ac_threshold = None if parts[1] == "-" else int(parts[1])
    return {"damage": dmg, "ac_threshold": ac_threshold}


def resolve_shock(shock_str, attribute_mod=0, target_ac=10, killing_blow_bonus=0):
    """Calculate shock damage dealt.

    Shock is dealt on a MISS if the target's AC <= weapon's shock AC threshold.
    Total shock = base + attribute_mod + killing_blow_bonus.
    """
    parsed = parse_shock(shock_str)
    if parsed is None:
        return {"shock_applied": False, "shock_damage": 0, "reason": "Weapon has no shock"}

    # Shock with AC threshold of '-' always applies
    if parsed["ac_threshold"] is not None and target_ac > parsed["ac_threshold"]:
        return {
            "shock_applied": False,
            "shock_damage": 0,
            "reason": f"Target AC {target_ac} > shock threshold {parsed['ac_threshold']}",
        }

    total_shock = parsed["damage"] + attribute_mod + killing_blow_bonus
    total_shock = max(0, total_shock)  # Shock can't be negative
    return {
        "shock_applied": True,
        "shock_damage": total_shock,
        "reason": f"Shock {parsed['damage']}+{attribute_mod}(attr)+{killing_blow_bonus}(KB) = {total_shock}",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ATTACK RESOLUTION
# ═══════════════════════════════════════════════════════════════════════════════

def resolve_attack(attacker, defender):
    """Resolve a complete melee or ranged attack.

    Args:
        attacker: dict with keys:
            - attack_bonus (int)
            - skill_level (int)
            - attribute_mod (int)
            - weapon: dict with damage (str), shock (str or None), traits (list)
            - killing_blow_bonus (int, optional, default 0)
        defender: dict with keys:
            - armor_class (int)
            - hp: dict with current, max

    Returns:
        dict with full combat result including arithmetic trace.
    """
    ab = attacker["attack_bonus"]
    skill = attacker["skill_level"]
    attr_mod = attacker["attribute_mod"]
    weapon = attacker["weapon"]
    kb_bonus = attacker.get("killing_blow_bonus", 0)
    target_ac = defender["armor_class"]

    total_bonus = ab + skill + attr_mod
    atk_result = roll_attack(total_bonus)

    hit = atk_result["total"] >= target_ac or atk_result["natural_20"]
    auto_miss = atk_result["natural_1"]
    if auto_miss:
        hit = False

    result = {
        "hit_roll": atk_result["die"],
        "total_roll": atk_result["total"],
        "attack_bonus_breakdown": f"AB={ab} + Skill={skill} + Attr={attr_mod} = +{total_bonus}",
        "target_ac": target_ac,
        "natural_20": atk_result["natural_20"],
        "natural_1": atk_result["natural_1"],
        "hit": hit,
        "damage": 0,
        "shock_applied": False,
        "shock_damage": 0,
        "arithmetic_trace": atk_result["arithmetic_trace"],
    }

    if hit:
        # Roll damage
        dmg_roll = roll(weapon["damage"])
        base_damage = dmg_roll["total"] + attr_mod + kb_bonus
        base_damage = max(1, base_damage)  # Minimum 1 damage on hit

        result["damage"] = base_damage
        result["damage_roll"] = dmg_roll["rolls"]
        result["damage_trace"] = (
            f"{weapon['damage']}={dmg_roll['total']}+{attr_mod}(attr)"
            f"+{kb_bonus}(KB) = {base_damage}"
        )
        result["arithmetic_trace"] += f" → HIT! Damage: {result['damage_trace']}"
    else:
        # Check shock on miss
        shock_result = resolve_shock(
            weapon.get("shock"),
            attribute_mod=attr_mod,
            target_ac=target_ac,
            killing_blow_bonus=kb_bonus,
        )
        result["shock_applied"] = shock_result["shock_applied"]
        result["shock_damage"] = shock_result["shock_damage"]
        if shock_result["shock_applied"]:
            result["damage"] = shock_result["shock_damage"]
            result["arithmetic_trace"] += f" → MISS, but Shock: {shock_result['reason']}"
        else:
            result["arithmetic_trace"] += f" → MISS. No shock: {shock_result['reason']}"

    # Calculate resulting HP
    new_hp = max(0, defender["hp"]["current"] - result["damage"])
    result["target_hp_before"] = defender["hp"]["current"]
    result["target_hp_after"] = new_hp
    result["target_down"] = new_hp <= 0

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# MORALE CHECK
# ═══════════════════════════════════════════════════════════════════════════════

def check_morale(morale_score):
    """Roll 2d6 against morale score. If roll > morale, creature routs.

    Returns dict with roll, morale, result.
    """
    rolls = roll_dice(2, 6)
    total = sum(rolls)
    routs = total > morale_score

    return {
        "rolls": rolls,
        "total": total,
        "morale_score": morale_score,
        "routs": routs,
        "arithmetic_trace": f"2d6=[{rolls[0]}+{rolls[1]}]={total} vs ML {morale_score} → {'ROUT' if routs else 'HOLDS'}",
    }
