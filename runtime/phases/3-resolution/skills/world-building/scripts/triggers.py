"""WWN trigger evaluator — check all pending trigger conditions against current state.

Read-only analysis of state.json to surface:
  - Clock portents that should fire (at <= current, fired=false)
  - Consequences whose timers have expired (days_remaining <= 0)
  - Campaign arc beats with mechanically-evaluable trigger conditions
  - Proactive GM command suggestions (encounter, faction-turn, world-tick)

Does NOT mutate state. Returns a list of suggested commands for the GM to execute.
"""

import re
import sys
import os

_this_dir = os.path.dirname(os.path.abspath(__file__))
_social_scripts = os.path.join(
    os.path.dirname(os.path.dirname(_this_dir)), "social", "scripts"
)
if _social_scripts not in sys.path:
    sys.path.insert(0, _social_scripts)

from consequence import check_consequences


# ─────────────────────────────────────────────────────────────────────────────
# Clock portent evaluation
# ─────────────────────────────────────────────────────────────────────────────

def check_clock_portents(clocks):
    """Find unfired portents at or below current clock value.

    These represent events that should have already triggered but were missed,
    or portents that are newly reachable.

    Returns list of dicts: {clock, clock_id, portent, mechanical, at, current}.
    """
    missed = []
    for clock in clocks:
        if clock.get("status") != "active":
            continue
        current = clock.get("current", 0)
        for portent in clock.get("portents", []):
            if not portent.get("fired") and portent["at"] <= current:
                missed.append({
                    "clock": clock.get("name", "unknown"),
                    "clock_id": clock.get("id", "unknown"),
                    "portent": portent["event"],
                    "mechanical": portent.get("mechanical", ""),
                    "at": portent["at"],
                    "current": current,
                })
    return missed


def get_clock_status(clocks):
    """Return summary of all active clocks with next unfired portent.

    Returns list of dicts: {name, id, current, max, status, next_portent}.
    """
    summaries = []
    for clock in clocks:
        summary = {
            "name": clock.get("name", "unknown"),
            "id": clock.get("id", "unknown"),
            "current": clock.get("current", 0),
            "max": clock.get("max", 0),
            "status": clock.get("status", "unknown"),
        }
        # Find next unfired portent
        next_portent = None
        for portent in clock.get("portents", []):
            if not portent.get("fired"):
                if next_portent is None or portent["at"] < next_portent["at"]:
                    next_portent = portent
        if next_portent:
            summary["next_portent"] = {
                "at": next_portent["at"],
                "event": next_portent["event"],
            }
        else:
            summary["next_portent"] = None
        summaries.append(summary)
    return summaries


# ─────────────────────────────────────────────────────────────────────────────
# Campaign arc beat evaluation
# ─────────────────────────────────────────────────────────────────────────────

# Pattern: "Clock Name clock hits N" or "Clock Name reaches N"
_CLOCK_TRIGGER_RE = re.compile(
    r"(.+?)\s+clock\s+(?:hits|reaches)\s+(\d+)",
    re.IGNORECASE,
)


def check_arc_beats(campaign_arcs, clocks):
    """Evaluate pending campaign arc beats against current clock values.

    Mechanically evaluable: trigger_condition matches "X clock hits N" pattern.
    Others returned as requires_gm_judgment.

    Returns dict with:
      - triggered: beats whose conditions are met
      - pending_mechanical: beats with clock conditions not yet met
      - requires_gm_judgment: beats with non-mechanical conditions
    """
    # Build clock lookup: name (lowercase) -> current value
    clock_lookup = {}
    for clock in clocks:
        clock_lookup[clock.get("name", "").lower()] = clock.get("current", 0)

    triggered = []
    pending_mechanical = []
    requires_gm_judgment = []

    for arc in campaign_arcs:
        if arc.get("status") not in ("active", None):
            continue
        for beat in arc.get("beats", []):
            if beat.get("status") != "pending":
                continue

            condition = beat.get("trigger_condition", "")
            match = _CLOCK_TRIGGER_RE.search(condition)

            if match:
                clock_name = match.group(1).strip().lower()
                threshold = int(match.group(2))
                current_val = clock_lookup.get(clock_name)

                if current_val is not None and current_val >= threshold:
                    triggered.append({
                        "arc": arc.get("name", "unknown"),
                        "arc_id": arc.get("id", "unknown"),
                        "beat": beat["beat_name"],
                        "trigger_condition": condition,
                        "payoff": beat.get("payoff_description", ""),
                        "evaluation": "met",
                        "clock_value": current_val,
                        "threshold": threshold,
                    })
                else:
                    pending_mechanical.append({
                        "arc": arc.get("name", "unknown"),
                        "arc_id": arc.get("id", "unknown"),
                        "beat": beat["beat_name"],
                        "trigger_condition": condition,
                        "evaluation": "not_met",
                        "clock_value": current_val,
                        "threshold": threshold,
                    })
            else:
                requires_gm_judgment.append({
                    "arc": arc.get("name", "unknown"),
                    "arc_id": arc.get("id", "unknown"),
                    "beat": beat["beat_name"],
                    "trigger_condition": condition,
                    "evaluation": "requires_gm_judgment",
                })

    return {
        "triggered": triggered,
        "pending_mechanical": pending_mechanical,
        "requires_gm_judgment": requires_gm_judgment,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Proactive command suggestions
# ─────────────────────────────────────────────────────────────────────────────

def suggest_proactive_commands(state):
    """Analyze state and suggest CLI commands the GM should proactively run.

    Checks:
      - High threat location -> encounter
      - Days since last faction turn -> faction-turn
      - Session gap -> world-tick
      - New/unknown location -> generate-scene

    Returns list of dicts: {command, args, reason, priority}.
    Priority: "high" (should run now), "medium" (consider running), "low" (optional).
    """
    suggestions = []

    # 1. Encounter check: threat_level >= 2 at current location
    scene = state.get("current_scene", {})
    threat_level = scene.get("threat_level", 0)
    if threat_level >= 2:
        terrain = _infer_terrain(scene)
        suggestions.append({
            "command": "encounter",
            "args": {"terrain": terrain, "threat_level": threat_level},
            "reason": f"Current location threat_level={threat_level} (>= 2)",
            "priority": "medium",
        })

    # 2. Faction turn check: look at faction turn_history or clock_log
    current_day = state.get("current_day", 1)
    last_faction_day = _find_last_faction_turn_day(state)
    days_since_faction = current_day - last_faction_day
    if days_since_faction >= 7:
        suggestions.append({
            "command": "faction-turn",
            "args": {},
            "reason": f"{days_since_faction} days since last faction turn (threshold: 7)",
            "priority": "high",
        })

    # 3. World tick check: session gap detection
    meta = state.get("meta", {})
    last_played = meta.get("last_played", "")
    session_number = meta.get("session_number", 0)
    if session_number > 1 and last_played:
        suggestions.append({
            "command": "world-tick",
            "args": {"days": 1},
            "reason": "Session boundary — check if world time should advance",
            "priority": "low",
        })

    return suggestions


def _infer_terrain(scene):
    """Infer terrain type from scene data for encounter command."""
    scene_type = scene.get("scene_type", "")
    region = scene.get("region", "").lower()

    if "urban" in region or "manhattan" in region or "nyc" in region:
        return "urban"
    if scene_type == "wilderness":
        return "wilderness"
    if scene_type == "ruin":
        return "ruins"
    if "dungeon" in scene_type:
        return "dungeon"
    return "urban"  # default for this campaign


def _find_last_faction_turn_day(state):
    """Find the most recent day a faction turn was run.

    Checks human_factions turn_history, then falls back to day 0.
    """
    last_day = 0
    for faction in state.get("human_factions", []):
        for entry in faction.get("turn_history", []):
            day = entry.get("day", 0)
            if day > last_day:
                last_day = day
    return last_day


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────

def check_all_triggers(state):
    """Evaluate all trigger conditions against current state.

    Args:
        state: full state.json dict

    Returns:
        dict with all trigger evaluation results and suggested commands.
    """
    clocks = state.get("clocks", [])
    consequence_tracker = state.get("consequence_tracker", [])
    campaign_arcs = state.get("campaign_arcs", [])
    current_day = state.get("current_day", 1)

    # 1. Clock portents
    missed_portents = check_clock_portents(clocks)

    # 2. Consequences (reuse existing function)
    consequence_result = check_consequences(consequence_tracker, current_day)
    triggered_consequences = consequence_result.get("triggered", [])
    pending_consequences = consequence_result.get("still_pending", [])

    # 3. Arc beats
    arc_result = check_arc_beats(campaign_arcs, clocks)

    # 4. Proactive suggestions
    suggestions = suggest_proactive_commands(state)

    # Build suggested commands list
    commands_to_fire = []

    for portent in missed_portents:
        commands_to_fire.append({
            "command": "world-tick",
            "args": {"days": 0},
            "reason": f"Missed portent on {portent['clock']}: "
                      f"'{portent['portent']}' (at={portent['at']}, "
                      f"current={portent['current']})",
            "source": "clock_portent",
            "priority": "high",
        })

    for csq in triggered_consequences:
        commands_to_fire.append({
            "command": "resolve-consequence",
            "args": {"consequence_id": csq["id"]},
            "reason": f"Consequence timer expired: {csq.get('description', csq['id'])}",
            "source": "consequence",
            "priority": "high",
        })

    for beat in arc_result["triggered"]:
        commands_to_fire.append({
            "command": "narrative-beat",
            "args": {"arc": beat["arc_id"], "beat": beat["beat"]},
            "reason": f"Arc beat condition met: {beat['trigger_condition']}",
            "source": "campaign_arc",
            "priority": "high",
        })

    for suggestion in suggestions:
        commands_to_fire.append({
            **suggestion,
            "source": "proactive",
        })

    # Arithmetic trace
    trace_parts = [
        f"Day {current_day}",
        f"{len(missed_portents)} missed portent(s)",
        f"{len(triggered_consequences)} triggered consequence(s)",
        f"{len(pending_consequences)} pending consequence(s)",
        f"{len(arc_result['triggered'])} triggered arc beat(s)",
        f"{len(arc_result['requires_gm_judgment'])} beat(s) need GM judgment",
        f"{len(suggestions)} proactive suggestion(s)",
        f"{len(commands_to_fire)} total command(s) to fire",
    ]

    return {
        "current_day": current_day,
        "missed_portents": missed_portents,
        "triggered_consequences": triggered_consequences,
        "pending_consequences": pending_consequences,
        "arc_beats": arc_result,
        "proactive_suggestions": suggestions,
        "clock_status": get_clock_status(clocks),
        "commands_to_fire": commands_to_fire,
        "arithmetic_trace": " | ".join(trace_parts),
    }
