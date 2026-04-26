# Boar Loot

This is the active boar loot mod project.

## Configure AES key in shell

```powershell
powershell -ExecutionPolicy Bypass -File "..\..\.local\secrets.ps1"
```

Alternative (recommended): use `.local/.env` and let the CLI auto-load it.

```powershell
Copy-Item "..\..\.local\.env.example" "..\..\.local\.env"
```

## Preferred recipe workflow

```powershell
python ".\modding_tools\windrose_mod_cli.py" build-mod --project-dir ".\mods\boar-loot" --backup-first
```

The recipe lives in `docs/mod_recipe.json` and builds the 2x, 3x, 5x, and 10x variants with zipped release packages.

## Prepare 3x boar loot overrides (leather + meat + tusk)

```powershell
python "..\..\modding_tools\windrose_mod_cli.py" prepare-boar-hide-json-mod --project-dir ".\" --multiplier 3.0 --resource-types "leather,meat,tusk"
```

## Build multiple variants (2x, 3x, 5x, 10x)

```powershell
python "..\..\modding_tools\windrose_mod_cli.py" build-variants --config "..\..\.local\boar-loot.build.json" --multipliers "2,3,5,10" --project-dir "." --prepare-command-template "python ..\..\modding_tools\windrose_mod_cli.py prepare-boar-hide-json-mod --project-dir {project_dir_quoted} --staged-root {variant_staged_dir_quoted} --multiplier {multiplier} --resource-types leather,meat,tusk"
```

## Config source

`scripts/build_install.ps1` uses this priority:

1. `..\..\.local\boar-loot.build.json`
2. `docs/build_config.local.json`
3. `docs/build_config.json`

These configs support tokens:

- `<REPO_ROOT>`
- `<WINDROSE_MODS_DIR>`

## Build + Install

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\build_install.ps1"
```

## Nexus Mods description

Use the BBCode-ready text in:

- `docs/NEXUS_DESCRIPTION.txt`

## Backup Mods

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\backup_mods.ps1"
```

## Restore Mods

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\restore_mods.ps1" -BackupDir ".\output\mods_backups\mods_backup_YYYYMMDD_HHMMSS"
```
