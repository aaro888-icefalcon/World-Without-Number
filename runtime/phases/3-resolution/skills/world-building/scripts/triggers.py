"""WWN trigger evaluator — check all pending trigger conditions against current state.

Read-only analysis of state.json to surface:
  - Clock portents that should fire (at <= current, fired=false)
  - Consequences whose timers have expired (days_remaining <= 0)
  - Campaign arc beats with mechanically-evaluable trigger conditions
  - Proactive GM command suggestions (encounter, faction-turn, world-tick)
  - Post-resolution state-delta detection (day change, location change, etc.)

Does NOT mutate state. Returns a list of suggested commands for the GM to execute.

Two entry points:
  - check_all_triggers(state)              — pre-turn evaluation (turn loop step 0)
  - check_post_resolution(pre_snap, post)  — post-resolution safety net (turn loop step 5.5)
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


# ─────────────────────────────────────────────────────────────────────────────
# State snapshot (for post-resolution delta detection)
# ─────────────────────────────────────────────────────────────────────────────

# Fields tracked for delta detection. These are the state paths that, when
# changed during a turn, indicate follow-up commands are needed.
_SNAPSHOT_FIELDS = [
    "current_day",
    "current_scene.location",
    "current_scene.threat_level",
    "combat_state.active",
    "combat_state.enemies",
]


def create_state_snapshot(state):
    """Capture a lightweight snapshot of state fields relevant to delta detection.

    Call this BEFORE step 4 (mechanical resolution). Pass the snapshot to
    check_post_resolution() after step 5 (persist) to detect what changed.

    Args:
        state: full state.json dict

    Returns:
        dict with snapshot values for tracked fields
    """
    snap = {}
    for field_path in _SNAPSHOT_FIELDS:
        parts = field_path.split(".")
        value = state
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = None
                break
        snap[field_path] = value

    # Snapshot XP for level-up detection
    character = state.get("character", {})
    snap["character.xp"] = character.get("xp", 0)
    snap["character.level"] = character.get("level", 1)

    # Snapshot known_npcs count for NPC generation detection
    snap["known_npcs_count"] = len(state.get("known_npcs", []))

    # Snapshot known_locations count
    snap["known_locations_count"] = len(state.get("known_locations", []))

    return snap


# ─────────────────────────────────────────────────────────────────────────────
# Post-resolution delta detection (Layer 3 safety net)
# ─────────────────────────────────────────────────────────────────────────────

# XP thresholds for WWN leveling (cumulative XP required for each level)
_XP_THRESHOLDS = {
    2: 3, 3: 6, 4: 12, 5: 18, 6: 27, 7: 39, 8: 54, 9: 72, 10: 93,
}


def check_post_resolution(pre_snapshot, post_state, already_executed=None):
    """Detect state changes from the just-completed command and suggest follow-ups.

    This is the Layer 3 safety net. It runs after step 5 (persist) and catches
    chain reactions that the chain registry (Layer 2) might have missed.

    Args:
        pre_snapshot: dict from create_state_snapshot() taken before step 4
        post_state: full state.json dict after step 5 (persist)
        already_executed: set of command names already executed/queued this turn
                         (for deduplication — prevents double-firing)

    Returns:
        dict with:
          - deltas: list of detected state changes
          - commands_to_fire: list of follow-up command suggestions
          - arithmetic_trace: string summary
    """
    if already_executed is None:
        already_executed = set()

    post_snapshot = create_state_snapshot(post_state)
    deltas = []
    commands = []

    # 1. Day changed → world-tick needed (if not already run)
    pre_day = pre_snapshot.get("current_day")
    post_day = post_snapshot.get("current_day")
    if pre_day is not None and post_day is not None and post_day > pre_day:
        days_advanced = post_day - pre_day
        deltas.append({
            "field": "current_day",
            "before": pre_day,
            "after": post_day,
            "description": f"Day advanced by {days_advanced}",
        })
        if "world-tick" not in already_executed:
            commands.append({
                "command": "world-tick",
                "args": {"days": days_advanced},
                "reason": f"In-game day advanced ({pre_day} → {post_day})",
                "source": "post_resolution_delta",
                "priority": "high",
            })

    # 2. Location changed → check if generate-scene needed
    pre_loc = pre_snapshot.get("current_scene.location")
    post_loc = post_snapshot.get("current_scene.location")
    if pre_loc != post_loc and post_loc is not None:
        deltas.append({
            "field": "current_scene.location",
            "before": pre_loc,
            "after": post_loc,
            "description": f"Location changed to {post_loc}",
        })
        # Check if new location is unknown
        known_locs = {
            loc.get("name", "").lower()
            for loc in post_state.get("known_locations", [])
        }
        if post_loc.lower() not in known_locs and "generate-scene" not in already_executed:
            commands.append({
                "command": "generate-scene",
                "args": {
                    "scene_type": "community",
                    "threat_level": post_state.get("current_scene", {}).get("threat_level", 3),
                },
                "reason": f"Entered unknown location: {post_loc}",
                "source": "post_resolution_delta",
                "priority": "high",
            })

        # New location with high threat → encounter check
        post_threat = post_snapshot.get("current_scene.threat_level", 0)
        if post_threat and post_threat >= 2 and "encounter" not in already_executed:
            terrain = _infer_terrain(post_state.get("current_scene", {}))
            commands.append({
                "command": "encounter",
                "args": {"terrain": terrain, "threat_level": post_threat},
                "reason": f"Entered area with threat_level={post_threat}",
                "source": "post_resolution_delta",
                "priority": "medium",
            })

    # 3. Combat ended (was active, now not) → treasure check
    pre_combat = pre_snapshot.get("combat_state.active")
    post_combat = post_snapshot.get("combat_state.active")
    if pre_combat and not post_combat:
        deltas.append({
            "field": "combat_state.active",
            "before": True,
            "after": False,
            "description": "Combat ended",
        })
        if "treasure" not in already_executed:
            commands.append({
                "command": "treasure",
                "args": {"tier": 1},
                "reason": "Combat ended — loot check (GM confirms if loot exists)",
                "source": "post_resolution_delta",
                "priority": "medium",
            })

    # 4. XP threshold crossed → prompt level-up
    pre_xp = pre_snapshot.get("character.xp", 0)
    post_xp = post_snapshot.get("character.xp", 0)
    current_level = post_snapshot.get("character.level", 1)
    if post_xp > pre_xp and current_level < 10:
        next_level = current_level + 1
        threshold = _XP_THRESHOLDS.get(next_level)
        if threshold is not None and post_xp >= threshold:
            deltas.append({
                "field": "character.xp",
                "before": pre_xp,
                "after": post_xp,
                "description": f"XP reached {post_xp} (level {next_level} threshold: {threshold})",
            })
            if "level-up" not in already_executed:
                commands.append({
                    "command": "level-up",
                    "args": {},
                    "reason": f"XP ({post_xp}) meets level {next_level} threshold ({threshold})",
                    "source": "post_resolution_delta",
                    "priority": "high",
                })

    # 5. Run check-triggers if any high-priority command was suggested
    #    (catches cascading effects from the commands above)
    high_priority = [c for c in commands if c["priority"] == "high"]
    if high_priority and "check-triggers" not in already_executed:
        commands.append({
            "command": "check-triggers",
            "args": {},
            "reason": f"{len(high_priority)} high-priority follow-up(s) detected — re-evaluate triggers",
            "source": "post_resolution_delta",
            "priority": "low",
        })

    # Build trace
    trace_parts = [
        f"{len(deltas)} delta(s) detected",
        f"{len(commands)} follow-up(s) suggested",
        f"{len(already_executed)} already executed",
    ]
    if deltas:
        delta_summary = ", ".join(d["field"] for d in deltas)
        trace_parts.append(f"Changed: {delta_summary}")

    return {
        "deltas": deltas,
        "commands_to_fire": commands,
        "already_executed": list(already_executed),
        "arithmetic_trace": " | ".join(trace_parts),
    }
