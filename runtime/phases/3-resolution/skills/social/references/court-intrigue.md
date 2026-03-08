# Court Intrigue Reference (D-EXT-6)

Derived from WWN social mechanics and faction rules. Canonical source for court-level political maneuvering.

## Court Structure

Every seat of power has a court — formal or informal — organized in concentric rings of influence.

### Court Tiers

| Tier | Role | Access | Typical NPCs |
|------|------|--------|-------------|
| **Ruler** | Final authority; makes binding decisions | Always present (or represented) | Monarch, warlord, high priest, guild sovereign |
| **Inner Circle** | Trusted advisors; shape the ruler's decisions directly | Private audience at will | Chancellor, spymaster, war marshal, consort, heir |
| **Outer Court** | Officials and nobles who attend court regularly | Attend formal sessions; request audience | Lesser nobles, ambassadors, guild masters, military officers |
| **Petitioners** | Outsiders seeking the court's attention or favor | Must be granted audience or find a patron | Merchants, adventurers, emissaries, supplicants |

### Access Rules

- PCs start as **Petitioners** unless faction standing or reputation grants higher access.
- Moving up one tier requires a patron from the target tier OR a notable service to the court.
- Falling one tier happens automatically if a patron withdraws support or the PC causes a scandal.

## Social Maneuvering Rules

### Influence Actions

Each court session (typically one per in-game week), a character may attempt ONE of the following influence actions:

| Action | Skill Check | Target | Effect |
|--------|------------|--------|--------|
| **Petition** | Cha/Talk vs 8 | Ruler or Inner Circle | Present a request; success means it is heard and considered |
| **Cultivate Ally** | Cha/Connect vs 9 | Any courtier | Shift their disposition one step positive (see `npc-reactions.md`) |
| **Gather Intelligence** | Int/Connect vs 8 | Court at large | Learn one piece of court gossip, a faction's current scheme, or an NPC's motivation |
| **Undermine Rival** | Cha/Talk vs 10 | Specific courtier | Shift the court's opinion of the target one step negative; if detected, PC loses 1 favor |
| **Call in Favor** | None (spend favor) | Any NPC with positive favor | Spend 1+ favor to request a specific action from the NPC |
| **Display Wealth/Power** | Spend resources | Court at large | Gain +1 temporary disposition bonus with all courtiers for 1 week; costs 50+ gp or equivalent |

### Contested Maneuvering

When two characters pursue opposing goals in court, resolve as a contested check:

1. Both roll 2d6 + relevant skill modifier + favor bonus (1 per 3 favor points with the court)
2. Higher total wins; ties favor the character with higher court tier
3. Loser suffers -1 disposition with the contested NPC or faction

## Favor and Debt Tracking

### Favor

Favor is tracked per NPC. It represents accumulated goodwill, owed debts, and political capital.

| Favor | Standing | Effect |
|-------|----------|--------|
| -3 or less | Enmity | NPC actively works against the PC; -2 to all social checks with them |
| -2 to -1 | Disfavor | NPC is uncooperative; -1 to social checks |
| 0 | Neutral | No bonus or penalty |
| 1 to 2 | Goodwill | NPC is inclined to help; +1 to social checks |
| 3 to 4 | Indebted | NPC owes a notable favor; +2 to social checks; can be called in |
| 5+ | Devoted | NPC is a reliable ally; +3 to social checks; will take risks for the PC |

### Gaining Favor

| Action | Favor Gained |
|--------|-------------|
| Complete a task for the NPC | +1 |
| Save NPC from danger or scandal | +2 |
| Provide valuable information | +1 |
| Give a significant gift (50+ gp value to the NPC) | +1 |
| Support the NPC publicly at personal cost | +1 |
| Successful Cultivate Ally action | +1 |

### Losing Favor

| Action | Favor Lost |
|--------|-----------|
| Break a promise to the NPC | -1 |
| Get caught in a lie or scheme against them | -2 |
| Publicly embarrass or undermine the NPC | -1 |
| Support their rival publicly | -1 |
| Fail to repay a called-in favor | -2 |
| Cause harm to NPC's allies or interests | -2 |

### Calling in Favors

Spending favor requires a minimum balance:

| Request Difficulty | Favor Cost | Examples |
|-------------------|-----------|----------|
| Trivial | 1 | Pass along a message, make an introduction |
| Minor | 2 | Provide non-sensitive information, lend minor resources |
| Significant | 3 | Arrange a private audience, vouch for the PC, provide a loan |
| Major | 4 | Take a political risk, commit faction resources, obstruct a rival |
| Extraordinary | 5+ | Betray their own faction, risk their life, change a major policy |

## Schemes and Counter-Schemes

### Scheme Structure

A scheme is a multi-step plan pursued over several court sessions. Track each scheme as a clock.

```
Scheme Clock: [_][_][_][_]  (4 segments by default)
```

| Scheme Type | Segments | Example |
|-------------|----------|---------|
| Minor Intrigue | 3 | Spread a rumor, discredit a petitioner |
| Court Maneuver | 4 | Install an ally in a position, secure a trade contract |
| Major Plot | 6 | Depose an advisor, forge an alliance, expose a conspiracy |
| Grand Conspiracy | 8 | Overthrow a ruler, trigger a war, reshape a faction |

### Advancing a Scheme

Each court session, the schemer may attempt to advance their scheme:

1. Roll 2d6 + Cunning modifier (Int or Cha, whichever applies)
2. Target number depends on scheme difficulty:
   - Minor: 7
   - Court Maneuver: 8
   - Major Plot: 9
   - Grand Conspiracy: 10
3. Success: +1 segment
4. Failure by 1-3: No progress
5. Failure by 4+: -1 segment AND the scheme risks exposure (see Detection below)

### Detection

Schemes risk exposure when they fail badly or when a counter-schemer actively investigates.

**Passive Detection**: Each court session, there is a flat 1-in-6 chance that an active scheme is noticed by someone in the court. Roll 1d6; on a 1, one NPC becomes suspicious.

**Active Investigation**: A character can spend their court action to investigate suspected schemes:
- Roll 2d6 + Int/Connect vs scheme's current segment count + 6
- Success: Learn the scheme's nature and who is behind it
- Failure: Learn nothing; the schemer is NOT alerted

### Counter-Schemes

Once a scheme is detected, opponents can launch a counter-scheme:

1. The counter-schemer declares their opposition and method
2. Each session, both sides roll contested 2d6 + relevant modifier
3. Winner advances their clock by 1; loser's clock retreats by 1
4. If the counter-scheme clock fills first, the original scheme is thwarted
5. If the original scheme fills first, it succeeds despite opposition

## Court Event Generation

### Random Court Events

Roll 1d12 at the start of each court session (or when the GM needs to inject dynamism):

| Roll | Event | Effect |
|------|-------|--------|
| 1 | **Scandal erupts** | A courtier's secret is exposed; all schemes involving them gain +1 detection risk |
| 2 | **Foreign envoy arrives** | New faction enters the court; new alliance or rivalry opportunities |
| 3 | **Assassination attempt** | Someone tries to kill a prominent courtier; court security tightens; -1 to Scheme actions this session |
| 4 | **Feast or tournament** | Social event; all Cultivate Ally checks gain +1 this session |
| 5 | **Tax crisis** | Wealth-related requests are harder (difficulty +1); Gather Resources actions gain urgency |
| 6 | **Border threat** | Military matters dominate court attention; Force-related factions gain +1 to petitions |
| 7 | **Religious dispute** | Ideological tension; faith-aligned factions gain influence; others lose -1 to petitions |
| 8 | **Trade opportunity** | Wealth-related proposals gain +1 to checks; merchants and guilds gain temporary influence |
| 9 | **Succession question** | Heir's legitimacy or competence questioned; Inner Circle members choose sides |
| 10 | **Court reshuffling** | A position opens up; courtiers compete to fill it; opportunity for PCs to advance tier |
| 11 | **Secret alliance exposed** | Two factions revealed to be cooperating; all disposition checks with those factions shift by -1 |
| 12 | **The ruler decides** | The ruler makes an unexpected decree affecting a current scheme or petition; roll 1d6 for favorable (4+) or unfavorable (1-3) |

### Seasonal Court Shifts

Courts change character over time. Every in-game season (3 months), roll or choose one:

| Season Shift | Effect |
|-------------|--------|
| **New Power Rises** | An Outer Court member joins the Inner Circle; existing dynamics shift |
| **Faction Weakens** | One faction loses 1 HP or 1 attribute point; their courtiers lose 1 favor with the ruler |
| **External Pressure** | A neighboring power makes demands; the court must respond collectively |
| **Internal Reform** | The ruler changes a policy; some courtiers benefit, others lose standing |
