# AI RPG Engine Template

## What This Is

Template for building AI-led RPGs with a deterministic CLI mechanics engine. All dice rolls, damage calculations, enemy behavior, and state mutations are executed through Python scripts — never estimated or improvised.

Two operating modes govern all work in this repository.

## Mode Selection

- **Development mode**: editing code, schemas, docs, tests, scripts, or CI behavior → governed by this file
- **Runtime (play) mode**: executing game turns without system changes → governed by `runtime/CLAUDE.md`

## Development Mode — Workflow

1. **Classify the change**: determine type (mechanic, lore, skill, script, hook, structural) and identify the owning phase. → `development/change-integration-checklist.md` §1
2. **Plan placement and integration**: list files to create/edit, integration touchpoints to update, and done criteria. → `development/change-integration-checklist.md` §2. If the change touches 2+ major surfaces (see §3), write an execution plan in `development/ongoing-plans/plans/active/` using the template before implementing.
3. **Implement smallest viable diff**: avoid unrelated cleanup/refactors unless explicitly requested.
4. **Wire into runtime**: update all discovery and integration touchpoints so runtime Claude can find and follow the change. New content goes in the owning phase directory.
5. **Run checks**: execute required validators/tests for touched surfaces.
6. **Review pass**: diff review + verify runtime discoverability (new content appears in phase CLAUDE.md tables, phase-manifest.md, script registry as applicable).
7. **Summarize for PR**: include what changed, why, integration points updated, checks run, and remaining risks. If this completes an execution plan, move it from `plans/active/` to `plans/completed/`. → `development/ongoing-plans/CLAUDE.md`

## Development Mode — Guardrails

- **Approval gates** (stop and confirm before proceeding): destructive operations, dependency/build system changes, `schema_version` bumps, migrations/backfills that rewrite canonical state, turn-loop contract changes.
- **Durable truth policy**: persist decisions in repo artifacts (docs, schemas, tests), never only in conversation.
- **Scope rules**: keep changes scoped to the requested objective. If a change touches more than two major surfaces (state schema, rules logic, renderer/derived output, validation/CI), split into phased PRs.
- **Determinism**: preserve stable ordering in machine outputs and registries. Any randomness must be seedable; the seed must be recorded in state/turn records.
- For **structural changes** (file moves, new directories, architecture PRs), see `development/repo-maintenance-policy.md`.
- For **content changes** (mechanics, skills, lore, scripts), see `development/change-integration-checklist.md`.

## Development Mode — File Conventions

Three navigation/governance file types are used in this repository. Follow these roles strictly:

- **`CLAUDE.md`** — Claude operating instructions for this scope. One per directory. Auto-loaded.
- **`AGENTS.md`** — Subagent overrides only. Create only when subagent behavior differs from CLAUDE.md. Currently none exist.
- **`index.md`** — Content inventory and navigation hub. THE discovery entry point for any directory.

Do not create `README.md` or `START-HERE.md` for new directories. Use `index.md` instead. When touching an existing directory, consolidate its README/START-HERE into `index.md` if practical.

> Full rationale: `development/design-docs/design-principles.md` §6

## Development Mode — How to Run Things

- **Tests**: `python runtime/tests/run_all_tests.py 1` (phase 1, mandatory)
- **State validator**: `python runtime/scripts/validate_state.py <state.json>`
- **Reference freshness**: `python runtime/scripts/validate_reference_freshness.py`
- **Docs structure**: `python runtime/scripts/validate_docs_structure.py`
- **Canonical references**: `python runtime/scripts/validate_canonical_references.py`
- **CI**: 3 jobs — `ci:smoke-balance`, `ci:state-validators`, `ci:regen-check`

## Development Surfaces

- Development hub: `development/index.md`
- Architecture: `development/design-docs/repo-architecture.md`
- Design docs: `development/design-docs/`
- Quality/CI docs: `development/quality/`
- Maintenance policy: `development/repo-maintenance-policy.md`
- Ongoing plans: `development/ongoing-plans/`

## Runtime Surfaces

- Turn loop: `runtime/turn-loop.md`
- Play runbook: `runtime/play-runbook.md`
- Script registry: `runtime/scripts/CLAUDE.md`
- Runtime hub: `runtime/index.md`
- Phase manifest: `runtime/phases/phase-manifest.md`

## Runtime Turn Loop (Mandatory Sequence)

Every game turn follows this sequence. No steps may be skipped or reordered.

0. **World preamble** — `check-triggers`. Fire high-priority commands.
1. **Capture + classify** — Player intent → CLI command via `action-classification.md`.
   Every action maps to a CLI command. `skill-check` is the universal fallback (Hard Rule #14).
2. **Expand** — `expand-action` → pre-commands + primary + declared chains.
3. **Validate input** — Provenance check.
4. **Snapshot** — `state-snapshot` (for delta detection).
5. **Execute** — pre-commands → primary → post-chains. Track `executed_commands`.
6. **★ Select GM move** — `select-move` on primary result.
   - EVERY player-action turn produces minimum Tier 1.
   - Tier 1: soft move (foreshadow, telegraph, opportunity, information).
   - Tier 2: hard move (consequence lands, telegraph escalates). Forced after 5 Tier 1 turns.
   - Tier 3: world move (clock/faction/environment shift). Forced after 8 Tier 1 turns.
   - Source: `gm-move-taxonomy.md`. Script: `gm_moves.py`.
7. **Narrate** — Phase 4, informed by move selection output.
8. **Persist** — Phase 5. Includes move mutations (telegraphs, escalations, element usage, counter updates).
9. **Post-resolution** — `post-resolution` safety net. Up to 3 iterations.
10. **Validate** — `validate-state`.
11. **Receipt** — Log full command sequence + move selection + seeds.

Detail: `runtime/turn-loop.md`. Phase instructions: `runtime/phases/<N>/CLAUDE.md`.

## Repository Map

- `runtime/`             → Game system (6-phase GM pipeline)
- `runtime/phases/`      → Pipeline phases (1-context-loading through 6-validation)
- `runtime/scripts/`     → CLI entry points (emergence_cli.py + validators)
- `runtime/tests/`       → Validation test suite
- `development/`         → Development documentation (architecture, design docs, quality, planning)
- `archives/`            → Archived backups
