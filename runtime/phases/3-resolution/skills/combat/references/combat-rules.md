# Combat Rules Reference

Extracted from WWN 1 pp.42-48. Canonical source for all combat mechanics.

## Combat Round Sequence

1. **Roll Initiative**: Each side rolls 1d8 + best Dex modifier. Highest goes first. Ties go to PCs.
2. **Take Turns**: Each combatant gets 1 Main Action + 1 Move Action + unlimited On Turn/Instant actions per round.
3. **Resolve**: Apply damage, check morale, apply conditions.

## Action Types

### Main Actions
- **Make Melee Attack**: 1d20 + AB + combat skill + attribute mod >= target AC
- **Make Ranged Attack**: Same, but uses Shoot skill; standard range no penalty, long range -2
- **Cast a Spell**: Most spells require a Main Action
- **Ready/Stow Item**: Draw or put away a weapon or other item
- **Reload Weapon**: Reload a ranged weapon (bows, crossbows)
- **Use a Skill**: Attempt a non-combat skill check
- **Make a Fighting Withdrawal**: Retreat from melee without provoking free attacks
- **Make a Swarm Attack**: Multiple weak attackers gang up on one target (+2 per ally, max +4)
- **Shatter a Shield**: Destroy an enemy's shield (must hit AC 15 + shield bonus)

### Move Actions
- **Run**: Move up to 30 feet (or your Move rate)
- **Screen an Ally**: Move to block attacks against a nearby ally
- **Pick Up Item**: Grab something from the ground
- **Stand Up**: Rise from prone
- **Hold An Action**: Ready an action to trigger on a condition

### On Turn Actions (free, once per round)
- **Go Prone**: Drop to the ground
- **Delay an Action**: Act later in the initiative order

### Instant Actions (free, can interrupt)
- **Total Defense**: -4 to all attacks until next turn, +2 AC
- **Make a Snap Attack**: Quick melee attack at -4 penalty
- **Drop an Item**: Release something held

### Special Actions
- **Charge**: Combine a Move and Main Action to move + melee attack in one action

## §hit-roll — Attack Resolution

**Hit Roll** = 1d20 + attack bonus + combat skill level + attribute modifier

Compare to target's **Armor Class (AC)**. If hit roll >= AC, the attack hits.

### Hit Roll Modifiers
| Situation | Modifier |
|-----------|----------|
| Target is prone in melee | +2 |
| Target has cover | -2 (partial) or -4 (substantial) |
| Target is prone at range | -2 |
| Thrown weapon while in melee | -4 |
| Visibility is poor | -2 |
| Two-weapon fighting | -1 to hit, +2 to damage |

## §damage — Damage Resolution

**Damage** = weapon damage die + attribute modifier

- Warriors add half their level (rounded up) to damage and Shock via Killing Blow.
- Two-weapon fighting: +2 damage, -1 to hit (requires Stab-1 or Punch-1).
- PM (Precisely Murderous) weapons: add combat skill level to damage on a hit.

## §shock — Shock Damage

Shock is automatic melee damage dealt even on a miss, IF the target's AC is at or below the weapon's Shock AC threshold.

- **Shock format**: damage/AC_threshold (e.g., "2/15" means 2 Shock damage to targets with AC 15 or less)
- Shock damage includes attribute modifier
- Warriors add Killing Blow bonus to Shock
- Shock is NOT dealt against targets behind cover, or when the attacker is prone

## §morale — Morale Checks

NPCs and creatures check morale when:
- They take their first casualty
- They lose half their number
- Their leader is killed or incapacitated

**Morale Check**: 2d6 > Morale score = the creature/NPC **routs** (flees or surrenders).

## §saving-throws — Saving Throws

Three save categories:
- **Physical**: Resist poison, disease, exhaustion = 16 - (level + best of Str/Con modifier)
- **Evasion**: Dodge area effects, traps = 16 - (level + best of Int/Dex modifier)
- **Mental**: Resist mind control, fear, illusions = 16 - (level + best of Wis/Cha modifier)

Roll 1d20 >= saving throw target to succeed.

## §injury — Injury and Death

- **0 HP**: The character is **Mortally Wounded**. They will die at the end of the sixth round unless stabilized.
- **Stabilization**: An ally makes a Dex/Heal or Int/Heal check (difficulty 8) as a Main Action. Stabilized characters are unconscious with 1 HP.
- **Death**: If not stabilized by end of round 6, the character dies.
- **Healing**: Characters recover 1 HP per full night's rest. The Heal skill can restore additional HP (Int/Heal check, difficulty varies).

## §system-strain — System Strain

System Strain represents the body's tolerance for magical healing, potions, and supernatural effects.

- Max System Strain = Constitution score
- Magical healing costs 1 System Strain per instance
- System Strain recovers at 1 point per full night's rest
- If System Strain is maximized, no further magical healing is possible
