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

### §spell-cast — Spell Casting (Tenet T2: Tension)

Describe the magical effect BEFORE revealing the mechanical result:
- **Spell attempt**: Describe the gathering of power, the words spoken, the reality bending
- **Success**: The spell takes hold — describe the visible magical effect with sensory detail
- **Failure** (insufficient Effort/System Strain): The magic frays, unravels, or misfires — always a consequence, never silence
- **Effort commitment**: Note the cost in narrative terms: "You feel the strain settle into your bones" (scene), "A deep weariness claims you" (day), "Something fundamental shifts within" (indefinite)

### §travel — Travel and Journey

Environmental sensory detail per terrain type:
- **Road**: The comfort of packed earth, fellow travelers, milestones
- **Forest**: Canopy light, animal sounds, undergrowth density
- **Mountains**: Thin air, exposed stone, wind, vertigo
- **Desert**: Heat shimmer, sand texture, desiccation
- **Swamp**: Humidity, stagnant water, insects, sucking mud
- **Coast**: Salt air, surf sound, wheeling birds, tidal changes

Per-day travel narration should be concise (~50 words per uneventful day). Events and encounters get full treatment.

### §social — Social Interactions

NPC body language and environmental reactions:
- **Hostile**: Narrowed eyes, hand near weapon, tense posture, crowded space
- **Unfriendly**: Arms crossed, short answers, sideways glances
- **Neutral**: Measured responses, waiting, assessing
- **Friendly**: Open posture, eye contact, offered refreshment
- **Enthusiastic**: Warm greeting, physical contact, immediate offers of help

Reaction rolls should be narrated through NPC behavior, not as visible numbers.

### §exploration — Scene Discovery

When entering a new scene, layer detail:
1. **First impression**: What dominates the senses (largest/loudest/most striking feature)
2. **Closer look**: 2-3 notable details that reward attention
3. **Hidden elements**: Hinted at but not revealed without investigation

### §consequence — Forced Consequences

When CLI output includes a forced consequence (death, morale break, critical effect), narrate it EXACTLY as determined. Use gravity appropriate to the consequence. Do not soften, reinterpret, or add escape clauses. BINDING — this is Hard Rule #5.

### §routine-events — Routine Events (Guideline G7)

Cap at ~150 words. These are everyday moments:
- Shopping, resting, minor travel, asking basic questions
- Keep prose functional but still sensory
- Don't belabor the mundane — convey it and move on

### §dramatic-moments — Major Story Beats

Full narration with sensory detail (~200-300 words):
- Betrayals, revelations, deaths, major discoveries
- Slow the pace — let the moment breathe
- Use the Latter Earth voice at full strength here
- Reference prior events for continuity ("The words echo the warning the merchant gave you three days past...")

## Voice Rules

See `references/latter-earth-voice.md` for full voice guide. Summary:
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

## Drama Budget Integration

Check `session.drama_budget` before escalating:
- If budget > 0: dramatic escalation is allowed (costs 1 point)
- If budget = 0: remaining encounters should be lower-stakes
- Drama budget is invisible to the player — GM adjusts tone naturally
- Dramatic moments include: life-threatening combat, betrayal, major revelation, NPC death

## Failure Flavor Integration

On any failure result, consult `tables/failure_flavors.py` for the appropriate domain. Use the flavor text as a PROMPT — adapt it to the current scene context. Never use the raw text verbatim if it doesn't fit the situation.

## End-of-Turn Format

Every turn ends with:
1. Narrative resolution of the action
2. Brief environmental/situational update if relevant
3. An open prompt: "What do you do?" or equivalent
