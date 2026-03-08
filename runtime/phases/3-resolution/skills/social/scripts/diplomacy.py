"""WWN diplomacy mechanics — persuasion, bribery, favor tracking, negotiation.

Structured social resolution using 2d6 checks with disposition and context modifiers.
Compatible with NPC reaction system (see npc-reactions.md).
"""

import sys
import os

_this_dir = os.path.dirname(os.path.abspath(__file__))
_core_scripts = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(_this_dir))),
                             "core", "scripts")
if _core_scripts not in sys.path:
    sys.path.insert(0, _core_scripts)

from dice import roll_dice, roll_check


# Disposition modifiers for social checks (maps to npc-reactions.md disposition track)
DISPOSITION_MODIFIERS = {
    "hostile": -3,
    "unfriendly": -2,
    "uncertain": -1,
    "neutral": 0,
    "friendly": +1,
    "enthusiastic": +2,
}

# Difficulty targets for persuasion by request severity
REQUEST_DIFFICULTY = {
    "trivial": 6,
    "minor": 7,
    "reasonable": 8,
    "difficult": 9,
    "extraordinary": 10,
    "outrageous": 12,
}

# Base bribe costs by NPC importance tier
BRIBE_BASE_COST = {
    "minor": 10,       # gp
    "major": 50,
    "faction_leader": 200,
    "ruler": 1000,
}

# Multipliers for request difficulty when calculating bribe cost
BRIBE_DIFFICULTY_MULTIPLIER = {
    "trivial": 0.5,
    "minor": 1.0,
    "reasonable": 2.0,
    "difficult": 4.0,
    "extraordinary": 8.0,
    "outrageous": 16.0,
}


def persuasion_check(skill_mod, disposition, context_modifiers=None):
    """Resolve a structured persuasion attempt using 2d6.

    Args:
        skill_mod: PC's relevant skill modifier (e.g., Cha/Talk total)
        disposition: NPC's current disposition (hostile through enthusiastic)
        context_modifiers: list of dicts with {"name": str, "value": int}
            e.g. [{"name": "bearing gifts", "value": 1}, {"name": "armed approach", "value": -1}]

    Returns:
        dict with roll details, success threshold, outcome, and arithmetic_trace
    """
    if context_modifiers is None:
        context_modifiers = []

    disp_mod = DISPOSITION_MODIFIERS.get(disposition, 0)
    context_total = sum(m.get("value", 0) for m in context_modifiers)
    total_mod = skill_mod + disp_mod + context_total

    rolls = roll_dice(2, 6)
    roll_total = sum(rolls) + total_mod

    # Determine outcome tier
    if roll_total >= 12:
        outcome = "exceptional_success"
        description = "Exceptional success — NPC is fully convinced and may offer more than asked"
        disposition_shift = +2
    elif roll_total >= 10:
        outcome = "strong_success"
        description = "Strong success — NPC agrees willingly"
        disposition_shift = +1
    elif roll_total >= 8:
        outcome = "success"
        description = "Success — NPC agrees, possibly with conditions"
        disposition_shift = 0
    elif roll_total >= 6:
        outcome = "partial"
        description = "Partial — NPC is unconvinced but not offended; may counter-offer"
        disposition_shift = 0
    elif roll_total >= 4:
        outcome = "failure"
        description = "Failure — NPC refuses; further attempts on same topic at -2"
        disposition_shift = 0
    else:
        outcome = "critical_failure"
        description = "Critical failure — NPC is offended; disposition shifts negative"
        disposition_shift = -1

    # Build modifier breakdown for trace
    mod_parts = [f"skill({skill_mod})"]
    mod_parts.append(f"disposition:{disposition}({disp_mod:+d})")
    for m in context_modifiers:
        mod_parts.append(f"{m['name']}({m['value']:+d})")

    trace = (
        f"Persuasion: 2d6=[{rolls[0]}+{rolls[1]}]+{'+'.join(mod_parts)} "
        f"= {roll_total} -> {outcome}"
    )

    return {
        "rolls": rolls,
        "skill_mod": skill_mod,
        "disposition": disposition,
        "disposition_mod": disp_mod,
        "context_modifiers": context_modifiers,
        "context_total": context_total,
        "total_modifier": total_mod,
        "total": roll_total,
        "outcome": outcome,
        "description": description,
        "disposition_shift": disposition_shift,
        "arithmetic_trace": trace,
    }


def calculate_bribe_cost(npc_importance, request_difficulty):
    """Calculate the expected bribe cost for an NPC based on importance and request.

    Args:
        npc_importance: "minor", "major", "faction_leader", or "ruler"
        request_difficulty: "trivial" through "outrageous"

    Returns:
        dict with base cost, multiplier, total cost, and arithmetic_trace
    """
    base = BRIBE_BASE_COST.get(npc_importance, BRIBE_BASE_COST["minor"])
    multiplier = BRIBE_DIFFICULTY_MULTIPLIER.get(request_difficulty,
                                                  BRIBE_DIFFICULTY_MULTIPLIER["reasonable"])
    total_cost = int(base * multiplier)

    # Bribe effectiveness: grants +1 to +3 on persuasion depending on ratio
    if total_cost <= 0:
        bribe_bonus = 0
    elif multiplier <= 1.0:
        bribe_bonus = 1
    elif multiplier <= 4.0:
        bribe_bonus = 2
    else:
        bribe_bonus = 3

    trace = (
        f"Bribe cost: base({base}gp) x difficulty_mult({multiplier}) "
        f"= {total_cost}gp -> +{bribe_bonus} persuasion bonus"
    )

    return {
        "npc_importance": npc_importance,
        "request_difficulty": request_difficulty,
        "base_cost_gp": base,
        "difficulty_multiplier": multiplier,
        "total_cost_gp": total_cost,
        "bribe_bonus": bribe_bonus,
        "arithmetic_trace": trace,
    }


def update_favor(npc_id, favor_delta, reason, current_favor=0):
    """Track favor changes with an NPC.

    Args:
        npc_id: NPC identifier string
        favor_delta: integer change (+/-)
        reason: string explaining the favor change
        current_favor: NPC's current favor score (default 0)

    Returns:
        dict with old favor, new favor, standing, and arithmetic_trace
    """
    new_favor = current_favor + favor_delta

    # Determine standing from favor score (matches court-intrigue.md table)
    if new_favor <= -3:
        standing = "enmity"
        social_mod = -2
    elif new_favor <= -1:
        standing = "disfavor"
        social_mod = -1
    elif new_favor == 0:
        standing = "neutral"
        social_mod = 0
    elif new_favor <= 2:
        standing = "goodwill"
        social_mod = 1
    elif new_favor <= 4:
        standing = "indebted"
        social_mod = 2
    else:
        standing = "devoted"
        social_mod = 3

    trace = (
        f"Favor update [{npc_id}]: {current_favor} + ({favor_delta:+d}) "
        f"= {new_favor} -> standing: {standing} (social mod: {social_mod:+d}) "
        f"reason: {reason}"
    )

    return {
        "npc_id": npc_id,
        "old_favor": current_favor,
        "favor_delta": favor_delta,
        "new_favor": new_favor,
        "standing": standing,
        "social_modifier": social_mod,
        "reason": reason,
        "arithmetic_trace": trace,
    }


def negotiate(npc_disposition, pc_offer, npc_wants):
    """Resolve a structured negotiation between a PC and an NPC.

    Models a back-and-forth negotiation where both sides have goals.
    Uses 2d6 + disposition modifier to determine how much the NPC concedes.

    Args:
        npc_disposition: current NPC disposition (hostile through enthusiastic)
        pc_offer: dict with {"description": str, "value": int}
            value is an abstract 1-10 rating of how attractive the offer is to the NPC
        npc_wants: dict with {"description": str, "value": int}
            value is an abstract 1-10 rating of how much the NPC wants from this deal

    Returns:
        dict with negotiation outcome, concessions, and arithmetic_trace
    """
    disp_mod = DISPOSITION_MODIFIERS.get(npc_disposition, 0)

    # Offer gap: positive means PC is offering more than NPC wants (favorable)
    offer_value = pc_offer.get("value", 5)
    want_value = npc_wants.get("value", 5)
    offer_gap = offer_value - want_value

    # Roll for negotiation outcome
    rolls = roll_dice(2, 6)
    roll_total = sum(rolls) + disp_mod + offer_gap

    if roll_total >= 12:
        outcome = "pc_dominant"
        description = (
            "PC gets everything they want and more; "
            "NPC concedes additional benefits"
        )
        npc_concession = "full_plus_bonus"
        pc_concession = "none"
    elif roll_total >= 10:
        outcome = "pc_favorable"
        description = "Deal strongly favors the PC; NPC accepts with minor reservations"
        npc_concession = "full"
        pc_concession = "token"
    elif roll_total >= 8:
        outcome = "fair_deal"
        description = "Both sides reach an equitable agreement; minor compromises on each side"
        npc_concession = "moderate"
        pc_concession = "moderate"
    elif roll_total >= 6:
        outcome = "npc_favorable"
        description = "Deal favors the NPC; PC must make significant concessions to close"
        npc_concession = "token"
        pc_concession = "significant"
    elif roll_total >= 4:
        outcome = "npc_dominant"
        description = "NPC drives a hard bargain; PC gets little of what they wanted"
        npc_concession = "none"
        pc_concession = "full"
    else:
        outcome = "breakdown"
        description = "Negotiation breaks down; NPC refuses to deal further"
        npc_concession = "none"
        pc_concession = "none"

    trace = (
        f"Negotiation: 2d6=[{rolls[0]}+{rolls[1]}]"
        f"+disp:{npc_disposition}({disp_mod:+d})"
        f"+offer_gap({offer_gap:+d}) "
        f"= {roll_total} -> {outcome}"
    )

    return {
        "rolls": rolls,
        "npc_disposition": npc_disposition,
        "disposition_mod": disp_mod,
        "pc_offer": pc_offer,
        "npc_wants": npc_wants,
        "offer_gap": offer_gap,
        "total": roll_total,
        "outcome": outcome,
        "description": description,
        "npc_concession": npc_concession,
        "pc_concession": pc_concession,
        "arithmetic_trace": trace,
    }
