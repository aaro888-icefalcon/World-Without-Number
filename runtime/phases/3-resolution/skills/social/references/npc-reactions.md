# NPC Reactions Reference (D-EXT-4)

Extracted from WWN pp.111-112. Canonical source for NPC reaction and disposition mechanics.

## 2d6 Reaction Table

Roll 2d6 when PCs first encounter an NPC or group whose attitude is unknown.

| Roll | Disposition | Behavior |
|------|-------------|----------|
| 2 | Hostile | Attacks immediately if not clearly overpowered; otherwise plots ambush or betrayal |
| 3-5 | Unfriendly | Aggressive posture; may attack if provoked or if odds seem favorable |
| 6-8 | Uncertain | Wary but willing to talk; can be swayed by good arguments or incentives |
| 9-10 | Neutral | Open to fair dealing and negotiation; no strong feelings either way |
| 11 | Friendly | Positively disposed; inclined to help if the cost is not too high |
| 12 | Enthusiastic | Eagerly helpful; may volunteer aid, information, or resources unprompted |

## Context Modifiers

Apply before rolling. Multiple modifiers stack.

| Condition | Modifier |
|-----------|----------|
| Approaching armed and armored | -1 |
| Clearly outnumbering the NPC | -1 |
| Known enemies of NPC's faction | -2 |
| Bearing gifts or trade goods | +1 |
| Bearing gifts of significant value | +2 |
| Shared faction or known allies | +1 |
| High Charisma modifier (speaker) | +Cha mod |
| Relevant social skill (Connect, Talk, Lead) | +skill level |
| Prior positive interaction | +1 per notable favor |
| Prior negative interaction | -1 per notable offense |
| NPC is in danger and PCs can help | +1 |
| NPC has been warned about PCs (negative) | -2 |
| NPC has been warned about PCs (positive) | +1 |
| Cultural or language barrier | -1 |
| PCs have a credible introduction | +1 |

## Follow-Up Interaction Rules

### After the Initial Reaction Roll

1. **Hostile (2)**: Combat is likely unless PCs immediately de-escalate. A successful Cha/Talk check (difficulty 10) can shift disposition to Unfriendly. Failure means the NPC acts on their hostility.

2. **Unfriendly (3-5)**: NPC will not cooperate without strong incentive. A successful Cha/Talk or Cha/Connect check (difficulty 9) can shift disposition to Uncertain. Bribes grant +1 to +3 depending on value.

3. **Uncertain (6-8)**: The default negotiation state. PCs can attempt persuasion, offer deals, or provide information to shift the NPC toward Neutral or Friendly. Standard skill checks apply (difficulty 8).

4. **Neutral (9-10)**: NPC engages in fair dealing. No check needed for reasonable requests. Unreasonable requests require Cha/Talk (difficulty 8) or appropriate leverage.

5. **Friendly (11)**: NPC is willing to help with most reasonable requests. Only extraordinary asks require a check (difficulty 7).

6. **Enthusiastic (12)**: NPC actively wants to assist. They may offer information or resources the PCs did not ask for. Checks only needed if the request would endanger the NPC.

### Re-Rolling Reactions

Do NOT re-roll reactions for the same NPC in the same encounter. Disposition can shift through roleplay and skill checks, but the baseline is set by the initial roll.

A new reaction roll is appropriate when:
- Significant time has passed (days or weeks)
- Circumstances have dramatically changed
- The NPC learns major new information about the PCs

## Disposition Changes Over Time

### Disposition Track

Dispositions form a track. Shifts move one step at a time unless an extraordinary event occurs.

```
Hostile <-> Unfriendly <-> Uncertain <-> Neutral <-> Friendly <-> Enthusiastic
```

### Triggers for Disposition Shift (Positive)

| Trigger | Shift |
|---------|-------|
| PC completes a favor for the NPC | +1 step |
| PC saves the NPC's life | +2 steps |
| PC provides valuable information | +1 step |
| PC demonstrates shared values | +1 step |
| Successful persuasion check | +1 step |
| Significant gift (worth 10+ gp to NPC) | +1 step |

### Triggers for Disposition Shift (Negative)

| Trigger | Shift |
|---------|-------|
| PC breaks a promise | -1 step |
| PC harms NPC's allies or interests | -2 steps |
| PC is caught lying or stealing | -1 step |
| PC threatens the NPC | -1 step |
| Failed persuasion by 4+ | -1 step |
| PC's faction attacks NPC's faction | -2 steps |

### Decay Over Time

- Without interaction, dispositions decay toward Uncertain at a rate of one step per month.
- Exceptions: Hostile and Enthusiastic dispositions caused by major events (life-saving, betrayal) are sticky and do not decay for at least 3 months.

## Morale Interaction

NPC disposition affects morale behavior in threatening situations.

### When Do NPCs Fight?

| Disposition | Combat Behavior |
|-------------|----------------|
| Hostile | Attacks without hesitation; morale check only after losing half their number or leader falls |
| Unfriendly | Fights if they believe they can win; morale check after first casualty |
| Uncertain | Only fights if cornered or protecting something vital; morale check immediately if combat starts |
| Neutral | Avoids combat; only fights in self-defense; flees at first opportunity if losing |
| Friendly | Will not initiate combat against PCs; may fight alongside them if stakes are clear |
| Enthusiastic | Actively assists PCs in combat if able; high morale when fighting alongside PCs |

### When Do NPCs Flee?

Standard morale check: 2d6 > Morale score = NPC routs (flees or surrenders).

Morale modifiers from disposition:

| Disposition | Morale Modifier |
|-------------|----------------|
| Hostile | +2 to morale (harder to break) |
| Unfriendly | +1 to morale |
| Uncertain | +0 |
| Neutral | -1 to morale (easier to break) |
| Friendly (fighting PCs) | -2 to morale |

### When Do NPCs Negotiate?

- **Hostile**: Only negotiates if clearly outmatched (outnumbered 2:1 or more, or key leader is defeated)
- **Unfriendly**: Willing to negotiate if combat is going poorly (failed morale check or lost half HP)
- **Uncertain**: Prefers negotiation over combat; will suggest a deal if fighting seems likely
- **Neutral**: Always willing to negotiate; seeks mutually beneficial arrangements
- **Friendly/Enthusiastic**: Open to almost any reasonable conversation; may accept unfavorable terms to maintain relationship
