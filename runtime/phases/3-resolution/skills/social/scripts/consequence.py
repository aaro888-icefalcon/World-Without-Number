"""WWN consequence tracker — manage delayed consequences from social actions.

Tracks timer-based consequences that trigger after a set number of in-game days.
Used for: broken promises, faction retaliation, scheme exposure, debt collection,
favor decay, and other delayed social effects.
"""

import sys
import os
import random

_this_dir = os.path.dirname(os.path.abspath(__file__))
_core_scripts = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(_this_dir))),
                             "core", "scripts")
if _core_scripts not in sys.path:
    sys.path.insert(0, _core_scripts)

from dice import roll_dice


def create_consequence(trigger_condition, timer_days, consequence_description, source_turn):
    """Create a new consequence entry for tracking.

    Args:
        trigger_condition: string describing what triggers this consequence
            e.g. "broken_promise", "faction_retaliation", "debt_due", "scheme_exposure"
        timer_days: number of in-game days until the consequence triggers
            (0 = immediate, checked each day)
        consequence_description: human-readable description of what happens
        source_turn: the turn number that created this consequence

    Returns:
        dict representing a consequence entry, JSON-serializable
    """
    consequence_id = f"csq_{source_turn}_{random.randint(100, 999)}"

    return {
        "id": consequence_id,
        "trigger_condition": trigger_condition,
        "timer_days": timer_days,
        "days_remaining": timer_days,
        "description": consequence_description,
        "source_turn": source_turn,
        "status": "pending",
        "resolution": None,
        "arithmetic_trace": (
            f"Consequence created: [{consequence_id}] "
            f"trigger='{trigger_condition}' timer={timer_days}d "
            f"from turn {source_turn}"
        ),
    }


def check_consequences(consequence_tracker, current_day):
    """Check all consequences and return any that have triggered.

    Decrements days_remaining for timer-based consequences and returns
    those that have reached zero.

    Args:
        consequence_tracker: list of consequence dicts (from state)
        current_day: the current in-game day number

    Returns:
        dict with triggered consequences, updated tracker, and arithmetic_trace
    """
    triggered = []
    still_pending = []
    already_resolved = []

    for csq in consequence_tracker:
        if csq.get("status") != "pending":
            already_resolved.append(csq)
            continue

        # Decrement timer
        days_left = csq.get("days_remaining", 0) - 1

        if days_left <= 0:
            # Consequence triggers
            csq_copy = dict(csq)
            csq_copy["status"] = "triggered"
            csq_copy["days_remaining"] = 0
            csq_copy["triggered_on_day"] = current_day
            triggered.append(csq_copy)
        else:
            csq_copy = dict(csq)
            csq_copy["days_remaining"] = days_left
            still_pending.append(csq_copy)

    updated_tracker = already_resolved + still_pending + triggered

    trigger_ids = [c["id"] for c in triggered]
    trace = (
        f"Consequence check (day {current_day}): "
        f"{len(consequence_tracker)} total, "
        f"{len(triggered)} triggered{': ' + ', '.join(trigger_ids) if trigger_ids else ''}, "
        f"{len(still_pending)} pending"
    )

    return {
        "current_day": current_day,
        "triggered": triggered,
        "still_pending": still_pending,
        "updated_tracker": updated_tracker,
        "arithmetic_trace": trace,
    }


def resolve_consequence(consequence_id, resolution, consequence_tracker=None):
    """Mark a consequence as resolved.

    Args:
        consequence_id: the ID of the consequence to resolve
        resolution: string describing how the consequence was resolved
            e.g. "paid_debt", "negotiated_truce", "suffered_penalty", "averted"
        consequence_tracker: optional list of consequence dicts; if provided,
            returns the updated tracker with the resolved consequence

    Returns:
        dict with resolution details and arithmetic_trace
    """
    result = {
        "consequence_id": consequence_id,
        "resolution": resolution,
        "status": "resolved",
        "arithmetic_trace": (
            f"Consequence resolved: [{consequence_id}] -> {resolution}"
        ),
    }

    if consequence_tracker is not None:
        updated = []
        found = False
        for csq in consequence_tracker:
            csq_copy = dict(csq)
            if csq_copy.get("id") == consequence_id:
                csq_copy["status"] = "resolved"
                csq_copy["resolution"] = resolution
                found = True
            updated.append(csq_copy)

        result["updated_tracker"] = updated
        result["found"] = found
        if not found:
            result["arithmetic_trace"] += " (WARNING: consequence ID not found in tracker)"

    return result
