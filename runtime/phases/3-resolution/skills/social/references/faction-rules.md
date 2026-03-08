# Faction Rules Reference (D-EXT-5)

Extracted from WWN pp.130-139. Canonical source for faction turn mechanics and management.

## Faction Attributes

Every faction has four core attributes:

| Attribute | Description | Range |
|-----------|-------------|-------|
| Force | Military strength, enforcers, martial capacity | 1-8 |
| Cunning | Espionage, subtlety, covert operations, information networks | 1-8 |
| Wealth | Economic resources, trade connections, liquid assets | 1-8 |
| HP | Faction health; represents cohesion, morale, and structural integrity | Derived from highest attribute |

### Faction HP Calculation

Base HP = 4 + highest attribute rating among Force, Cunning, and Wealth.

When HP reaches 0, the faction is **destroyed**, **absorbed**, or **collapses** into irrelevance.

### Faction Power Level

Power level is a simplified rating (1-10) derived from attributes:
- Power = floor((Force + Cunning + Wealth) / 3)
- Used for quick action resolution bonuses: bonus = min(3, power / 3)

## Faction Turn Structure

Faction turns occur between sessions or during downtime. Each faction turn follows this sequence:

### 1. Choose Action

Each faction selects one action based on its goals, personality (archetype), and current state:

| Action | Description | Primary Attribute |
|--------|-------------|-------------------|
| Expand Influence | Extend reach into new territory or sphere | Cunning |
| Gather Resources | Accumulate wealth or materials for future use | Wealth |
| Attack Rival | Take direct action against another faction | Force |
| Defend Territory | Fortify holdings against incoming threats | Force |
| Recruit | Bring in new members or hire mercenaries | Wealth |
| Scheme | Covert operations and intelligence gathering | Cunning |
| Build | Construct infrastructure or establish institutions | Wealth |

### 2. Execute Action

Roll 2d6 + power bonus (min 0, max +3). Result of 8+ = success.

### 3. Resolve Conflicts

If two factions take opposing actions (e.g., Attack Rival vs Defend Territory), resolve as a contested roll:
- Both factions roll 2d6 + relevant attribute modifier
- Higher total wins; ties favor the defender
- Loser suffers consequences based on the margin of failure

| Margin | Consequence |
|--------|-------------|
| 1-2 | Minor setback: -1 clock progress or small resource loss |
| 3-4 | Significant setback: -1 HP or loss of an asset |
| 5+ | Major defeat: -2 HP and loss of an asset |

## Asset Management

### Buying Assets

Factions can acquire assets by spending attribute points or resources:

| Asset Type | Cost | Effect |
|------------|------|--------|
| Military Unit | 2 Wealth | +1 Force for one conflict |
| Spy Network | 2 Cunning | Learn one rival's current action before choosing |
| Trade Route | 2 Wealth | +1 Wealth income per faction turn |
| Fortification | 2 Force | +2 to Defend Territory rolls |
| Propaganda | 1 Cunning | Shift public opinion; +1 to Expand Influence |
| Alliance | Variable | Coordinate actions with another faction |

### Maintaining Assets

Each asset costs 1 point from its primary attribute per faction turn to maintain. Factions that cannot pay maintenance lose the asset.

### Using Assets

Assets provide bonuses to specific actions. A faction may use up to 2 assets per faction turn. Each asset can only be used once per turn.

## Faction Conflict Resolution

### Direct Conflict (Attack Rival)

1. Attacker rolls 2d6 + Force modifier + asset bonuses
2. Defender rolls 2d6 + Force modifier + asset bonuses (Fortifications apply)
3. Compare totals; higher total wins
4. Loser takes damage based on margin (see Resolve Conflicts above)

### Covert Conflict (Scheme vs Counter-scheme)

1. Schemer rolls 2d6 + Cunning modifier
2. Target rolls 2d6 + Cunning modifier (Spy Network grants +2)
3. If schemer wins: learn target's goal, current action, or one secret
4. If target wins: scheme is detected; target may retaliate next turn

### Economic Conflict (Trade War)

1. Both factions roll 2d6 + Wealth modifier
2. Winner gains +1 Wealth income; loser suffers -1 Wealth income for one turn
3. Prolonged trade wars (3+ turns) risk collateral damage to the region

## How Faction Actions Affect the Game World

### World Pulse Events

Each successful faction action generates a **world pulse event** that players may observe:

| Faction Action | Observable Event |
|----------------|-----------------|
| Expand Influence | New faction banners/agents seen in a region; locals talk about new power |
| Gather Resources | Increased merchant activity; supply shortages for rivals |
| Attack Rival | Reports of skirmishes; refugees; damaged property |
| Defend Territory | Visible fortifications; increased patrols; checkpoints |
| Recruit | Strangers arriving in town; recruitment posters; mercenary camps |
| Scheme | Rumors of espionage; missing documents; unexplained meetings |
| Build | Construction activity; new buildings; infrastructure improvements |

### Player Interaction with Factions

- PCs can work for factions, gaining faction standing and rewards
- PCs can oppose factions, reducing their clock progress or HP
- PCs can mediate between factions to prevent conflicts
- Faction disposition toward PCs follows the NPC reaction rules (see `npc-reactions.md`)

## Clock Integration

Each faction's primary goal is tracked as a **clock** (progress tracker):

### Clock Structure

```json
{
  "name": "Faction goal description",
  "current": 0,
  "max": 6,
  "status": "active"
}
```

### Clock Advancement

| Event | Clock Change |
|-------|-------------|
| Successful "Expand Influence" action | +1 segment |
| Critical success (roll 12+) on any action | +1 segment |
| PC assists faction with goal | +1 segment |
| Rival faction's "Attack Rival" succeeds | -1 segment |
| PC opposes faction's goal | -1 segment |
| Major setback (5+ margin defeat) | -2 segments |

### Clock Completion

When a faction clock fills:
1. The faction achieves its goal (narrative consequence)
2. The GM narrates the outcome and its effects on the world
3. The faction either sets a new goal (new clock) or becomes dormant
4. Completed faction goals may trigger new clocks for other factions

### Clock Status Values

| Status | Meaning |
|--------|---------|
| `active` | Faction is pursuing this goal |
| `paused` | Goal temporarily suspended (faction is distracted or weakened) |
| `completed` | Goal achieved |
| `failed` | Goal abandoned or made impossible |
