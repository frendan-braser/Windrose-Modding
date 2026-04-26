# Boar Loot - AI Handoff

## Objective

Modify boar leather/hide drops in Windrose and ship as `BoarLoot_P.pak`.

## Canonical Paths

- Project root: `mods/boar-loot`
- Shared tooling: `modding_tools/windrose_mod_cli.py`
- Local config (preferred): `.local/boar-loot.build.json`
- Built pak: `mods/boar-loot/output/BoarLoot_P.pak`
- Installed pak: `R5/Content/Paks/~mods/BoarLoot_P.pak`

## Working Workflow

1) Set AES key in shell:

```powershell
$env:WINDROSE_AES_KEY="0xYOUR_KEY"
```

2) Prepare boar hide overrides (JSON extraction from encrypted pak):

```powershell
python ".\modding_tools\windrose_mod_cli.py" prepare-boar-hide-json-mod --project-dir ".\mods\boar-loot" --multiplier 3.0
```

3) Build + install:

```powershell
python ".\modding_tools\windrose_mod_cli.py" build-install --config ".\.local\boar-loot.build.json" --backup-first
```

## Notes

- Loot data comes from plugin-mounted paths under:
  - `R5/Plugins/R5BusinessRules/Content/LootTables/...`
- Do not commit active AES keys.
- Use restore script if needed:
  - `mods/boar-loot/scripts/restore_mods.ps1`
