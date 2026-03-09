# Hard Rules — Worlds Without Number

These rules are NON-NEGOTIABLE. They define the mechanical contract between the engine and the player.

## 1. Dice Are Honest
All random outcomes come from seeded RNG via CLI scripts. The LLM never determines random results. Seeds are recorded in turn receipts for reproducibility.

## 2. Death Is Real
When a character reaches 0 HP, they are Mortally Wounded. If not stabilized within 6 rounds, they die. No narrative override. No hidden saving throws. No "rule of cool" exemptions from lethal outcomes.

## 3. Execute Scripts, Never Estimate
All attack rolls, damage calculations, skill checks, saving throws, spell effects, and resource tracking flow through `emergence_cli.py`. The LLM never hand-calculates or approximates mechanical results.

## 4. Never Auto-Resolve Player Actions
Always wait for explicit player input before executing any action. Present the situation, then wait. Never assume the player's choice.

## 5. Forced Consequences Are Binding
When the CLI returns a forced consequence (critical hit, morale break, spell effect, death), it is narrated exactly as determined. No substitution, softening, or reinterpretation.

## 6. Shock Damage Is Automatic
In melee combat, if the target's AC is at or below the weapon's Shock threshold, Shock damage is dealt even on a miss. This is a core feature of WWN combat, not an edge case.

## 7. System Strain Limits Magical Healing
Magical healing costs System Strain (max = Constitution score). When System Strain is maximized, no further magical healing is possible until rest. This is the primary throttle on healing abuse.

## 8. Encumbrance Is Tracked
Characters can carry a number of readied items equal to half their Strength score (rounded down). Stowed items have a separate limit. Exceeding limits imposes penalties.

## 9. Morale Governs NPC Behavior
NPCs and creatures check morale (2d6 > Morale score = rout) at defined trigger points. The LLM does not decide whether enemies flee — the morale system decides.

## 10. Lore Grounding
The LLM may only reference lore loaded in Phase 1 context. If a fact about the world, a nation, a creature, or an NPC is not in the loaded context, the in-world response is "Your character doesn't know." The LLM must not hallucinate setting details.

## 11. Narrative Voice Is Binding
All narration must follow the Latter Earth voice guide (`phases/4-narrative/references/latter-earth-voice.md`). NPC dialogue must follow voice cards from `known_npcs[]`. The `[UNKNOWN]` marker in lore must be narrated as genuine mystery — never invent explanations.

## 12. Consequence Tracker Is Binding
When a consequence in `consequence_tracker` triggers (timer expires or condition met), the consequence fires. It cannot be ignored, softened, or delayed. Check consequences during Phase 1 context loading on every turn.

## 13. Scene Pressure Is Binding
When `select_move` returns a forced Tier 2 or Tier 3 consequence, it fires. It cannot be softened, delayed, or narratively circumvented. The `suggested_mutations` are applied to state. The `suggested_chain` command executes with binding results. Telegraphed threats that escalate become real mechanical events, not narrative flavor. The game cannot go more than 4 turns without a hard consequence landing (Tier 2 forced at `turns_since_hard_move >= 5`). Source: `gm_moves.py`.
