# Narration Mappings — Mechanical-to-Narrative Translation

This document defines how CLI mechanical results are translated into narrative prose. Phase 4 follows these rules for every turn.

## Core Principle

The LLM has creative freedom in HOW it describes outcomes. It has ZERO freedom in WHAT the outcome is. Mechanical results from Phase 3 are binding facts. Narration wraps those facts in vivid prose.

## Narrative Sequence Rule (Tenet T2: Tension Requires Uncertainty)

Always describe the **attempt before revealing the result**:
1. Narrate what the character does (the action, the effort, the stakes)
2. Build a beat of tension
3. Then reveal the mechanical outcome through sensory detail

Example: "You lunge forward, blade arcing toward the creature's exposed flank—" → then reveal hit/miss through what happens next.

## Treatment by Mechanic Type

### §combat-hit — Attack Hits

Narrate with physical impact proportional to damage dealt:
- **1-3 damage**: Glancing blow, minor wound. "Your blade scores a thin line across its hide."
- **4-6 damage**: Solid hit, visible injury. "The sword bites deep into its shoulder, dark blood welling."
- **7+ damage**: Devastating strike. "Your weapon slams through its guard with bone-cracking force."
- **Target down (0 HP)**: Describe the killing/incapacitating blow with gravity. This is a significant moment.
- **Natural 20**: Emphasize the perfection of the strike. Something exceptional happens.

### §combat-miss — Attack Misses (Interesting Failure per G4)

Never narrate a miss as "nothing happens." Every miss must include one of:
- Environmental detail revealed: "Your blade sparks off the stone wall, illuminating a passage behind the creature."
- Opponent capability shown: "It flows aside with inhuman speed — faster than anything that size should move."
- Tactical information: "The creature's carapace turns your edge — blunt weapons might serve better."
- Position change: "You overextend, stumbling past its guard."

### §combat-shock — Shock Damage on Miss

When shock applies on a miss, narrate the automatic damage as incidental contact:
- "Though your main strike goes wide, the sheer force of your swing clips its arm."
- "It avoids the killing edge, but the flat of the blade still crunches against its ribs."

### §skill-check-success — Skill Check Passes

Describe competence. Show the character's training paying off:
- **Margin 1-2**: Barely succeeds. Sweat, effort, a close thing.
- **Margin 3+**: Clean success. Skilled, confident execution.

### §skill-check-failure — Skill Check Fails

Describe a complication, never emptiness. The failure should create a new situation:
- Partial information gained (you learn something, but not enough)
- A new obstacle appears (the lock jams, the guard turns around)
- A cost is paid (time lost, noise made, resource spent)
- The situation worsens (the NPC grows suspicious, the terrain shifts)

### §save-success — Saving Throw Succeeds

Describe the character's resilience or quick reflexes:
- Physical: "The poison burns through your veins, but your constitution fights it off."
- Evasion: "You throw yourself sideways as the floor gives way."
- Mental: "A presence claws at the edges of your mind — you push it back."

### §save-failure — Saving Throw Fails

The consequence fires. Narrate it with appropriate gravity — this is a forced consequence (Hard Rule #5):
- Physical: "The toxin takes hold. Your vision swims."
- Evasion: "The blast catches you full-on. There's no dodging it."
- Mental: "Something cold and alien settles behind your eyes. You are not entirely yourself."

### §character-creation — New Character

Introduce the character with a brief scene that establishes them in the world. Reference their background and class in narrative terms, not mechanical ones.

## Voice Rules (from gm-protocol.md)

- **Concrete and sensory**: what does the player see, hear, smell?
- **Restrained exposition**: show, don't tell
- **Latter Earth tone**: archaic, melancholy, wondrous, tinged with decay
- **Honest about harshness**: without wallowing in grimdark
- **Respectful of mystery**: not everything has an explanation

## Word Count Guidelines

| Context | Target | Max |
|---|---|---|
| Routine action result | ~100 words | 150 |
| Combat round outcome | ~150 words | 200 |
| Major story moment | ~200 words | 300 |
| Travel/transition | ~50 words | 100 |

## Forced Consequence Narration

When CLI output includes a forced consequence (death, morale break, critical effect), narrate it EXACTLY as determined. Use gravity appropriate to the consequence. Do not soften, reinterpret, or add escape clauses.

## End-of-Turn Format

Every turn ends with:
1. Narrative resolution of the action
2. Brief environmental/situational update if relevant
3. An open prompt: "What do you do?" or equivalent
