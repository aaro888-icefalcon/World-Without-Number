# NPC Dialogue Protocol

Step-by-step procedure for generating NPC dialogue that is consistent, memorable, and grounded in state.

## Step 1: Load NPC Record

Read the NPC entry from `known_npcs[]` matching the speaking character. Extract:

| Field | Dialogue Use |
|---|---|
| `name` | How they are addressed and how they refer to themselves |
| `faction` | Ideological framing — what they defend, what they distrust |
| `role` | Social register — a merchant speaks differently than a warden-captain |
| `disposition` | Current emotional stance toward the PC (friendly, neutral, hostile, fearful, etc.) |
| `trust` | 0-10 scale governing what they will reveal. Below 3: guarded, evasive. 3-6: transactional, honest within limits. 7+: candid, may volunteer information |
| `motivation` | What they want — shapes what they ask for, offer, or withhold |
| `secret` | What they hide — never spoken directly, but may leak through subtext, deflection, or contradiction |
| `last_seen` | Where and when the PC last encountered them — informs opening line |

If the NPC has no `known_npcs` entry (first encounter), generate dialogue from scene context and role alone. Create the entry in Phase 5.

## Step 2: Derive Voice Profile

Since voice cards are not stored in state, derive speech characteristics from the NPC's role, faction, and disposition:

**By Role:**
- *Commoner/laborer*: Simple syntax, concrete vocabulary, local idiom. Short sentences.
- *Merchant/artisan*: Precise, transactional language. Numbers and quantities come naturally. Polite but calculating.
- *Scholar/priest*: Formal register, longer sentences, references to texts or doctrine. May lecture.
- *Soldier/guard*: Clipped, imperative. Comfortable with silence. Says less than they know.
- *Noble/official*: Elaborate courtesy masking authority. Uses "we" and passive constructions. Expects deference.
- *Outcast/wanderer*: Elliptical, guarded. Offers information sideways. Watches more than speaks.

**By Disposition:**
- *Friendly*: Offers information before asked. Uses the PC's name. Body language is open.
- *Neutral*: Responds to questions but does not volunteer. Polite, measured. Waits.
- *Hostile*: Short answers, challenges, deflection. Arms crossed. May refuse to engage.
- *Fearful*: Whispers, glances at exits, contradicts themselves. Speaks too fast or too slow.

## Step 3: Generate Dialogue

Follow these principles:

1. **Open with context**: The NPC's first line should acknowledge the situation — time of day, location, the PC's appearance, or their last interaction. Never open with a generic greeting unless the NPC is generic.

2. **Speech reflects knowledge**: NPCs only know what they could reasonably know. A farmer does not discuss arcane theory. A hermit does not know city politics. Respect information boundaries.

3. **Subtext over exposition**: NPCs with secrets do not deliver them in monologue. They hesitate, change subjects, or tell partial truths. Trust level gates how close to the truth they will approach.

4. **Distinctive patterns**: Give each NPC at least one speech habit:
   - A repeated phrase ("The road provides," "As my mother's mother said...")
   - A verbal tic (clearing throat before lying, trailing off mid-sentence)
   - A topic they always return to (their trade, their children, the weather as omen)

5. **Latter Earth register**: All dialogue uses the setting voice. No modern slang, no gaming terminology. A blacksmith says "I can mend that edge" not "I'll repair your weapon for you."

## Step 4: Body Language and Environment

Every dialogue line should include at least one non-verbal detail:

- **Physical action**: what the NPC does while speaking (polishing a blade, stirring a pot, not meeting your eyes)
- **Environmental reaction**: how the setting responds (a fire pops, rain begins, a dog growls)
- **Spatial relationship**: where the NPC positions themselves relative to the PC (behind a counter, blocking a doorway, keeping distance)

Examples:
> *"You want passage north." She does not look up from the nets she is mending. Her fingers work the knots with mechanical precision. "The north does not want you."*

> *The old man sets down his cup with exaggerated care, as though the ceramic might shatter. "I remember your face," he says. "You were here in the autumn. Before the trouble."*

## Step 5: Continuity Check

Before finalizing dialogue, verify:

1. **Last interaction consistency**: If `last_seen` references a prior encounter, the NPC should acknowledge it — even obliquely. "You came back" or a change in demeanor is sufficient.
2. **Trust trajectory**: If trust has changed since last encounter (due to quest outcomes, faction shifts), the NPC's openness should reflect the current value, not the previous one.
3. **World state alignment**: If events have occurred that the NPC would know about (faction conflict, deaths, environmental changes), reference them. NPCs exist in the world even when the PC is not present.
4. **Secret leakage control**: At trust 0-4, secrets never surface in dialogue. At trust 5-7, indirect hints may appear (a hesitation, a too-quick change of subject). At trust 8+, the NPC may confide partially under the right circumstances.

## Quick Reference: Trust Thresholds

| Trust | Dialogue Behavior |
|---|---|
| 0-2 | Minimal engagement. May refuse to speak. Lies freely. |
| 3-4 | Transactional. Answers direct questions. Omits unfavorable details. |
| 5-6 | Conversational. Volunteers relevant information. Honest within limits. |
| 7-8 | Candid. Shares opinions and concerns. May warn of danger. |
| 9-10 | Confiding. Reveals motivations. May share partial secrets under duress or trust. |

## Formatting

Present NPC dialogue in italicized blocks with speaker attribution and body language:

> *Maren sets down the candle she has been trimming and turns to face you fully. "The cellar," she says, her voice dropping. "Something has been moving in the cellar for three nights now. I barred the door." She pauses. "I do not think the door will hold much longer."*

For extended conversations, alternate between NPC speech and brief PC-facing prompts to maintain interactivity. Do not generate more than 3-4 NPC lines before returning agency to the player.
