# AGENTS

## Session Start Priority

1. Read `mods/boar-loot/docs/AI_HANDOFF.md` first.
2. Use `modding_tools/windrose_mod_cli.py` commands before ad-hoc workflows.
3. Preserve reproducibility: document changes in `mods/boar-loot/docs/`.

## Project Context

- Workspace root: `Windrose Modding` repo root
- Active project path: `mods/boar-loot`
- Tooling: `modding_tools` (`repak`, `retoc`, `u4pak`, Python CLI)
- Output mod path: `R5\Content\Paks\~mods\BoarLoot_P.pak`

## Canonical Workflow

1. Prepare/update boar hide override JSON from encrypted pak:
   - `prepare-boar-hide-json-mod --aes-key ... --multiplier ...`
2. Build and install:
   - `build-install --config ".local/boar-loot.build.json" --backup-first`
3. Validate in game.
4. If needed, restore from backup with `mods/boar-loot/scripts/restore_mods.ps1`.

## Critical Technical Notes

- Do not assume all assets are under `/Game/...`.
- This project uses plugin-mounted loot data under:
  - `R5/Plugins/R5BusinessRules/Content/LootTables/...`
- JSON discovered in pak is used as the editable override payload in this workflow.

## Continuity Rules

- Update `mods/boar-loot/docs/AI_HANDOFF.md` whenever:
  - command behavior changes,
  - paths change,
  - AES/mappings assumptions change,
  - test outcomes change.
- Keep commands copy-paste ready.
- Prefer small, reversible edits and keep backup/restore path valid.
- Never commit active AES keys into tracked docs/files; use placeholders and local untracked notes.
