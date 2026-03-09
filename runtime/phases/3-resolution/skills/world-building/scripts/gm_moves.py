"""Anti-stagnation GM move system — deterministic move selection.

Every player-action turn produces a minimum Tier 1 move. The system
tracks consecutive Tier 1 turns and forces escalation at thresholds:
  - Tier 2 (hard move) forced at turns_since_hard_move >= 5
  - Tier 3 (world move) forced at turns_since_hard_move >= 8

Six command dispatchers handle the player-action primaries:
  skill-check, attack, save, cast-spell, reaction-roll, travel

No dispatcher returns tier 0. The Tier 1 floor is absolute.
"""

import sys
import os

_this_dir = os.path.dirname(os.path.abspath(__file__))
_combat_scripts = os.path.join(
    os.path.dirname(os.path.dirname(_this_dir)), "combat", "scripts"
)
if _combat_scripts not in sys.path:
    sys.path.insert(0, _combat_scripts)

from behavior import get_profile_for_creature, get_profile_description, BEHAVIOR_PROFILES


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TIER2_THRESHOLD = 5   # consecutive Tier 1 turns before forced Tier 2
TIER3_THRESHOLD = 8   # consecutive Tier 1 turns before forced Tier 3

# Gate-type → consequence flavor mapping for natural Tier 2 from skill-check
GATE_CONSEQUENCES = {
    "access": {
        "success_move": "The way opens, but something stirs beyond",
        "failure_consequence": "close_path",
        "failure_desc": "The path closes — access denied or barred",
    },
    "discovery": {
        "success_move": "You learn what you sought, but the search drew attention",
        "failure_consequence": "misinformation",
        "failure_desc": "Wrong conclusion persisted — misinformation",
    },
    "social": {
        "success_move": "They cooperate, but your inquiry touched a nerve",
        "failure_consequence": "update_favor",
        "failure_desc": "NPC hostility — relationship damaged",
    },
    "survival": {
        "success_move": "You endure, but the effort cost something",
        "failure_consequence": "immediate_resource_cost",
        "failure_desc": "Resource loss — supplies, HP, or equipment damaged",
    },
    "combat_setup": {
        "success_move": "Advantage secured, but the enemy adapts",
        "failure_consequence": "ambush_reversed",
        "failure_desc": "Ambush reversed — enemies get surprise (+2 threat)",
    },
    "pure_test": {
        "success_move": "Success, but the environment shifts",
        "failure_consequence": "immediate_resource_cost",
        "failure_desc": "Minor environmental hazard",
    },
}


# ---------------------------------------------------------------------------
# Telegraph management
# ---------------------------------------------------------------------------

def record_telegraph(description, source_element, current_turn):
    """Create a new telegraphed threat entry.

    Args:
        description: sensory detail of the foreshadowed danger
        source_element: scene element key (e.g. "enemies.patrol")
        current_turn: current game turn number

    Returns:
        Telegraph dict with status "active"
    """
    return {
        "id": f"telegraph_{source_element.replace('.', '_')}_{current_turn}",
        "description": description,
        "turn_created": current_turn,
        "source_element": source_element,
        "status": "active",
    }


# ---------------------------------------------------------------------------
# Escalation check
# ---------------------------------------------------------------------------

def check_escalation(turns_since_hard_move, telegraphed_threats, clocks, factions):
    """Check if forced escalation is needed.

    Args:
        turns_since_hard_move: consecutive Tier 1 turns since last Tier 2+
        telegraphed_threats: list of active telegraph dicts
        clocks: list of clock dicts from state
        factions: list of faction dicts from state

    Returns:
        dict with forced_tier, move_type, directive, target_telegraph (if applicable)
        or None if no forced escalation
    """
    if turns_since_hard_move >= TIER3_THRESHOLD:
        return {
            "forced_tier": 3,
            "move_type": "world_event",
            "directive": (
                "The world acts. Advance a clock, fire a faction action "
                "on-screen, or shift the environment fundamentally."
            ),
        }

    if turns_since_hard_move >= TIER2_THRESHOLD:
        # Prefer escalating oldest telegraph
        active = [t for t in telegraphed_threats if t.get("status") == "active"]
        if active:
            target = sorted(active, key=lambda t: t["turn_created"])[0]
            return {
                "forced_tier": 2,
                "move_type": "telegraph_escalates",
                "target_telegraph": target["id"],
                "directive": (
                    f"Escalate telegraph '{target['description']}' into a "
                    f"hard consequence. The warning becomes real."
                ),
            }
        else:
            return {
                "forced_tier": 2,
                "move_type": "world_consequence",
                "directive": (
                    "A clock portent or faction action creates a consequence "
                    "that touches the PC directly."
                ),
            }

    return None


# ---------------------------------------------------------------------------
# Move output builder
# ---------------------------------------------------------------------------

def _make_move(tier, move_type, narrative_directive, source_elements=None,
               suggested_mutations=None, suggested_chain=None,
               forced_consequence=False, arithmetic_trace=""):
    """Build a standardized move output dict."""
    return {
        "tier": tier,
        "move_type": move_type,
        "narrative_directive": narrative_directive,
        "source_elements": source_elements or [],
        "suggested_mutations": suggested_mutations or [],
        "suggested_chain": suggested_chain,
        "forced_consequence": forced_consequence,
        "counter_update": {
            "action": "reset" if tier >= 2 else "increment",
            "turns_since_hard_move": 0 if tier >= 2 else None,
        },
        "arithmetic_trace": arithmetic_trace,
    }


# ---------------------------------------------------------------------------
# Command dispatchers
# ---------------------------------------------------------------------------

def _move_for_skill_check(command_result, gate_type=None, scene_elements=None,
                          telegraphed_threats=None, combat_state=None,
                          chain_results=None, pre_command_results=None):
    """Dispatch for skill-check results."""
    success = command_result.get("success", False)
    margin = command_result.get("margin", 0)
    gate = gate_type or "pure_test"
    gate_info = GATE_CONSEQUENCES.get(gate, GATE_CONSEQUENCES["pure_test"])

    if success:
        return _make_move(
            tier=1,
            move_type="gate_success_foreshadow",
            narrative_directive=gate_info["success_move"],
            source_elements=[f"gate.{gate}"],
            arithmetic_trace=f"Skill-check success (margin +{margin}), gate={gate}. Tier 1: foreshadow.",
        )

    # Failure paths
    if margin <= -5:
        # Catastrophic — always Tier 2 regardless of telegraph state
        return _make_move(
            tier=2,
            move_type="catastrophic_failure",
            narrative_directive=(
                f"Catastrophic failure. {gate_info['failure_desc']}. "
                f"The consequence is binding."
            ),
            forced_consequence=True,
            suggested_mutations=[{"type": gate_info["failure_consequence"]}],
            arithmetic_trace=f"Skill-check catastrophic failure (margin {margin}), gate={gate}. Tier 2 forced.",
        )

    if margin <= -3:
        # Moderate failure — escalate telegraph if available
        active = [t for t in (telegraphed_threats or []) if t.get("status") == "active"]
        if active:
            target = sorted(active, key=lambda t: t["turn_created"])[0]
            return _make_move(
                tier=2,
                move_type="telegraph_escalates",
                narrative_directive=(
                    f"Telegraph '{target['description']}' escalates into reality. "
                    f"The prior warning becomes a hard consequence."
                ),
                suggested_mutations=[
                    {"type": "escalate_telegraph", "telegraph_id": target["id"]},
                ],
                forced_consequence=True,
                arithmetic_trace=f"Skill-check fail (margin {margin}), gate={gate}. Active telegraph found. Tier 2: escalate.",
            )
        else:
            # No telegraph to escalate — record a new one (Tier 1)
            return _make_move(
                tier=1,
                move_type="failure_telegraph",
                narrative_directive=(
                    f"Failure. Record a telegraph — foreshadow the {gate} "
                    f"consequence that will come if pressure continues."
                ),
                suggested_mutations=[{"type": "record_telegraph"}],
                arithmetic_trace=f"Skill-check fail (margin {margin}), gate={gate}. No active telegraph. Tier 1: record new.",
            )

    # margin -1 to -2 — mild failure, telegraph
    return _make_move(
        tier=1,
        move_type="mild_failure_telegraph",
        narrative_directive=(
            f"Mild failure. Telegraph danger from scene_elements — "
            f"the {gate} attempt didn't succeed and something shifts."
        ),
        suggested_mutations=[{"type": "record_telegraph"}],
        arithmetic_trace=f"Skill-check mild failure (margin {margin}), gate={gate}. Tier 1: telegraph.",
    )


def _move_for_attack(command_result, gate_type=None, scene_elements=None,
                     telegraphed_threats=None, combat_state=None,
                     chain_results=None, pre_command_results=None):
    """Dispatch for attack results. Every combat round evolves the battlefield."""
    target_down = command_result.get("target_down", False)
    cs = combat_state or {}

    if target_down:
        # Check if all enemies are down
        enemies = cs.get("enemies", [])
        alive = [e for e in enemies if e.get("hp_current", 0) > 0]

        if not alive:
            # Combat ends — aftermath
            return _make_move(
                tier=1,
                move_type="combat_aftermath",
                narrative_directive=(
                    "Combat ends. Foreshadow what the scene holds beyond combat. "
                    "Draw from scene_elements."
                ),
                arithmetic_trace="Attack: target down, all enemies down. Tier 1: aftermath.",
            )
        else:
            # Enemies remain — foreshadow via behavior profile
            next_enemy = alive[0]
            profile_name = get_profile_for_creature(next_enemy)
            foreshadow = get_profile_description(profile_name)
            return _make_move(
                tier=1,
                move_type="target_down_foreshadow",
                narrative_directive=(
                    f"Target down, but enemies remain. {foreshadow}. "
                    f"Draw from behavior profile: {profile_name}."
                ),
                source_elements=[f"behavior.{profile_name}"],
                arithmetic_trace=f"Attack: target down, {len(alive)} enemies remain. Profile: {profile_name}. Tier 1: foreshadow.",
            )

    # Standard combat round — battlefield evolves
    return _make_move(
        tier=1,
        move_type="battlefield_evolves",
        narrative_directive=(
            "Draw one combat complication from scene_elements: terrain shifts, "
            "enemy reveals capability, environment reacts, position changes."
        ),
        arithmetic_trace=f"Attack: {'hit' if command_result.get('hit') else 'miss'}, combat continues. Tier 1: battlefield evolves.",
    )


def _move_for_save(command_result, gate_type=None, scene_elements=None,
                   telegraphed_threats=None, combat_state=None,
                   chain_results=None, pre_command_results=None):
    """Dispatch for save results. Saves are reactive — resolve a prior threat."""
    success = command_result.get("success", False)
    margin = command_result.get("margin", 0)

    if success:
        return _make_move(
            tier=1,
            move_type="environment_reacts",
            narrative_directive=(
                "The threat was averted, but the event changed something in the scene. "
                "Draw from scene_elements — what shifted because of the near-miss."
            ),
            arithmetic_trace=f"Save success (margin +{margin}). Tier 1: event leaves a mark.",
        )

    # Failure — check severity
    if margin <= -3:
        # Severe failure — Tier 2
        return _make_move(
            tier=2,
            move_type="severe_save_failure",
            narrative_directive=(
                "Severe save failure. The forced consequence lands with full weight. "
                "Telegraph what caused it or what comes next."
            ),
            forced_consequence=True,
            suggested_mutations=[{"type": "record_telegraph"}],
            arithmetic_trace=f"Save failure (margin {margin}, severe). Tier 2: consequence + telegraph.",
        )

    # Standard failure — Tier 1 with forced consequence
    return _make_move(
        tier=1,
        move_type="consequence_plus_telegraph",
        narrative_directive=(
            "The prior move's consequence lands (Hard Rule #5, binding). "
            "Telegraph what caused it or what comes next."
        ),
        forced_consequence=True,
        suggested_mutations=[{"type": "record_telegraph"}],
        arithmetic_trace=f"Save failure (margin {margin}). Tier 1: forced consequence + telegraph.",
    )


def _move_for_cast_spell(command_result, gate_type=None, scene_elements=None,
                         telegraphed_threats=None, combat_state=None,
                         chain_results=None, pre_command_results=None):
    """Dispatch for cast-spell results. Don't double-tax spell costs."""
    success = command_result.get("success", False)
    in_combat = (combat_state or {}).get("active", False)

    if success:
        if in_combat:
            return _make_move(
                tier=1,
                move_type="spell_combat_ripple",
                narrative_directive=(
                    "The spell succeeds in combat. Spell effect ripples — "
                    "enemies reposition, terrain altered, collateral occurs."
                ),
                arithmetic_trace="Cast-spell success (in combat). Tier 1: combat ripple.",
            )
        else:
            return _make_move(
                tier=1,
                move_type="magic_ripple",
                narrative_directive=(
                    "The spell succeeds. The world responds — draw complication "
                    "from scene_elements. Magic is loud in a low-magic world."
                ),
                arithmetic_trace="Cast-spell success (non-combat). Tier 1: magic ripple.",
            )

    # Failure — attempt noticed
    return _make_move(
        tier=1,
        move_type="failed_magic_noticed",
        narrative_directive=(
            "The spell fails, but the attempt itself was noticed. "
            "Arcane discharge, residue, or attention drawn."
        ),
        arithmetic_trace="Cast-spell failure. Tier 1: attempt noticed.",
    )


def _move_for_reaction_roll(command_result, gate_type=None, scene_elements=None,
                            telegraphed_threats=None, combat_state=None,
                            chain_results=None, pre_command_results=None):
    """Dispatch for reaction-roll results. The reaction IS the move."""
    disposition = command_result.get("disposition", "neutral")
    total = command_result.get("total", 7)

    if disposition == "hostile":
        return _make_move(
            tier=2,
            move_type="npc_hostile",
            narrative_directive=(
                "NPC acts against the PC. Create consequence if NPC has power. "
                "This is a hard move — the hostility is real."
            ),
            suggested_mutations=[
                {"type": "update_favor", "delta": -2, "reason": "hostile reaction"},
                {"type": "create_consequence"},
            ],
            arithmetic_trace=f"Reaction-roll: hostile (total {total}). Tier 2: NPC acts against PC.",
        )

    if disposition == "unfriendly":
        return _make_move(
            tier=1,
            move_type="npc_obstructs",
            narrative_directive=(
                "NPC is obstructive. Telegraph that continued interaction "
                "will cost something. Record leverage if NPC has any."
            ),
            suggested_mutations=[
                {"type": "update_favor", "delta": -1, "reason": "cold reception"},
                {"type": "record_telegraph"},
            ],
            arithmetic_trace=f"Reaction-roll: unfriendly (total {total}). Tier 1: NPC obstructs.",
        )

    if disposition == "neutral":
        return _make_move(
            tier=1,
            move_type="npc_gives_information",
            narrative_directive=(
                "Transactional NPC still reveals something: a rumor from "
                "world_pulse, a detail about the location, or an observation "
                "about recent events."
            ),
            arithmetic_trace=f"Reaction-roll: neutral (total {total}). Tier 1: NPC gives information.",
        )

    if disposition == "friendly":
        return _make_move(
            tier=1,
            move_type="npc_offers_opportunity",
            narrative_directive=(
                "NPC offers something — information, a lead, a minor favor. "
                "Draw from scene_elements or world_pulse rumors."
            ),
            suggested_mutations=[
                {"type": "update_favor", "delta": 1, "reason": "warm reception"},
            ],
            arithmetic_trace=f"Reaction-roll: friendly (total {total}). Tier 1: NPC offers opportunity.",
        )

    # enthusiastic (12+) or unknown disposition
    return _make_move(
        tier=1,
        move_type="npc_active_help",
        narrative_directive=(
            "NPC actively helps — strong opportunity. May offer quest hook "
            "from campaign_arcs. Update favor positively."
        ),
        suggested_mutations=[
            {"type": "update_favor", "delta": 2, "reason": "enthusiastic"},
        ],
        arithmetic_trace=f"Reaction-roll: enthusiastic (total {total}). Tier 1: active help.",
    )


def _move_for_travel(command_result, gate_type=None, scene_elements=None,
                     telegraphed_threats=None, combat_state=None,
                     chain_results=None, pre_command_results=None):
    """Dispatch for travel results. Promote the most dramatic event."""
    supplies_end = command_result.get("supplies_end", 1)
    travel_log = command_result.get("travel_log", [])
    chain = chain_results or {}

    # Check for privation first — Tier 2
    if supplies_end is not None and supplies_end <= 0:
        return _make_move(
            tier=2,
            move_type="travel_privation",
            narrative_directive=(
                "Supplies exhausted during travel. Resource consequence lands. "
                "apply_privation already computed the damage."
            ),
            forced_consequence=True,
            arithmetic_trace=f"Travel: privation (supplies_end={supplies_end}). Tier 2: resource consequence.",
        )

    # Check chain_results for world-tick portent
    world_tick = chain.get("world-tick", {})
    triggered_events = world_tick.get("triggered_events", [])
    if triggered_events:
        return _make_move(
            tier=1,
            move_type="travel_portent",
            narrative_directive=(
                "A clock portent fired during travel. This is the featured "
                "beat — portents outrank travel events."
            ),
            source_elements=["clock_portent"],
            arithmetic_trace=f"Travel: world-tick portent fired ({len(triggered_events)} events). Tier 1: portent featured.",
        )

    # Check for encounter in travel log
    encounters = [day for day in travel_log if day.get("has_encounter")]
    if encounters:
        return _make_move(
            tier=1,
            move_type="travel_encounter",
            narrative_directive=(
                "Encounter triggered during travel. The encounter command "
                "handles it — this IS the move."
            ),
            arithmetic_trace="Travel: encounter triggered in travel_log. Tier 1: encounter handles.",
        )

    # Check for notable travel events
    notable_events = [day for day in travel_log
                      if day.get("travel_event") and
                      day["travel_event"] != "Unremarkable terrain"]
    if notable_events:
        return _make_move(
            tier=1,
            move_type="travel_notable_event",
            narrative_directive=(
                "Promote the most dramatic travel event as the featured beat "
                "for narration."
            ),
            arithmetic_trace=f"Travel: {len(notable_events)} notable events. Tier 1: promote most dramatic.",
        )

    # Uneventful — world_pulse rumor
    return _make_move(
        tier=1,
        move_type="travel_world_pulse",
        narrative_directive=(
            "Uneventful travel. Feature a world_pulse rumor as the "
            "narrative beat. If no rumors available, the landscape itself "
            "tells a story."
        ),
        arithmetic_trace="Travel: uneventful. Tier 1: world_pulse rumor.",
    )


def _move_narrative_fallback(command_result, gate_type=None, scene_elements=None,
                             telegraphed_threats=None, combat_state=None,
                             chain_results=None, pre_command_results=None):
    """Fallback for narrative pseudo-commands (no CLI). Always Tier 1."""
    return _make_move(
        tier=1,
        move_type="world_breathes",
        narrative_directive=(
            "The world breathes. Draw from scene_elements sensory detail "
            "or world_pulse rumor. Even quiet moments reveal something."
        ),
        arithmetic_trace="Narrative (no CLI command). Tier 1: world breathes.",
    )


# ---------------------------------------------------------------------------
# Main dispatcher
# ---------------------------------------------------------------------------

_DISPATCH = {
    "skill-check": _move_for_skill_check,
    "attack": _move_for_attack,
    "save": _move_for_save,
    "cast-spell": _move_for_cast_spell,
    "reaction-roll": _move_for_reaction_roll,
    "travel": _move_for_travel,
}


def select_move(command_name, command_result, gate_type=None,
                scene_elements=None, telegraphed_threats=None,
                combat_state=None, chain_results=None,
                pre_command_results=None):
    """Select a GM move based on the primary command's result.

    Every player-action turn produces minimum Tier 1.
    No dispatcher returns tier 0.

    Args:
        command_name: which primary just ran (e.g. "skill-check")
        command_result: its JSON output dict
        gate_type: only for skill-check (access/discovery/social/survival/combat_setup)
        scene_elements: current scene's element menu
        telegraphed_threats: active telegraph dicts
        combat_state: for attack/spell combat context
        chain_results: results from post-chains (e.g. world-tick after travel)
        pre_command_results: results from pre-commands (e.g. generate-npc)

    Returns:
        Move dict with tier, move_type, narrative_directive, source_elements,
        suggested_mutations, suggested_chain, forced_consequence,
        counter_update, arithmetic_trace
    """
    handler = _DISPATCH.get(command_name, _move_narrative_fallback)
    return handler(
        command_result,
        gate_type=gate_type,
        scene_elements=scene_elements,
        telegraphed_threats=telegraphed_threats,
        combat_state=combat_state,
        chain_results=chain_results,
        pre_command_results=pre_command_results,
    )
