# Windrose Modding CLI Toolkit

Reusable command-line helpers for investigating Windrose Unreal Engine assets and building repeatable mod packages.

## Design Goals

- Reusable across future mods (not boar-only)
- Deterministic outputs (`.json`) for patch-to-patch diffs
- Relative-path friendly commands for multi-machine use

## Requirements

- Python 3.10+
- Read access to Windrose `R5/Content/Paks`

## Suggested Project Layout

For each mod project:

- `mods/<mod-name>/input/`
- `mods/<mod-name>/output/`
- `mods/<mod-name>/docs/`
- `mods/<mod-name>/scripts/`

## Environment Variables (recommended)

```powershell
$env:WINDROSE_PAKS_DIR="<WINDROSE_INSTALL_DIR>\R5\Content\Paks"
$env:WINDROSE_MODS_DIR="$env:WINDROSE_PAKS_DIR\~mods"
$env:WINDROSE_AES_KEY="0xYOUR_AES_KEY_HERE"
```

You can source a local script:

```powershell
powershell -ExecutionPolicy Bypass -File ".\.local\secrets.ps1"
```

Or use dotenv style:

1) copy `.local/.env.example` -> `.local/.env`
2) set values
3) run CLI commands normally; `windrose_mod_cli.py` auto-loads `.local/.env`

## Core Commands

Tool detection:

```powershell
python ".\modding_tools\windrose_mod_cli.py" tools-info
```

Install/update toolchain:

```powershell
powershell -ExecutionPolicy Bypass -File ".\modding_tools\scripts\install_toolchain.ps1"
```

Initialize project:

```powershell
python ".\modding_tools\windrose_mod_cli.py" init-project --project-dir ".\mods\boar-loot"
python ".\modding_tools\windrose_mod_cli.py" setup-boar-template --project-dir ".\mods\boar-loot"
```

Initialize a new reusable mod scaffold:

```powershell
python ".\modding_tools\windrose_mod_cli.py" init-mod --name "My New Mod"
```

Initialize a mob bounty mod with recipe metadata:

```powershell
python ".\modding_tools\windrose_mod_cli.py" init-mob-bounty --name "Goat Bounty" --mob-keywords "goat" --resources "goat meat, leather, bezoar, horns"
```

Discover mob loot tables before making a mod:

```powershell
python ".\modding_tools\windrose_mod_cli.py" discover-mob-loot --keyword "goat"
```

Build a recipe-driven mod, including variants and zip packages:

```powershell
python ".\modding_tools\windrose_mod_cli.py" build-mod --project-dir ".\mods\goat-bounty" --backup-first
```

Generate the Nexus Mods description from `docs/mod_recipe.json`:

```powershell
python ".\modding_tools\windrose_mod_cli.py" generate-nexus-description --project-dir ".\mods\goat-bounty"
```

Prepare boar resource overrides (example 3x leather + meat + tusk):

```powershell
python ".\modding_tools\windrose_mod_cli.py" prepare-boar-hide-json-mod --project-dir ".\mods\boar-loot" --multiplier 3.0 --resource-types "leather,meat,tusk"
```

Build repeatable multiplier variants (example 2x, 3x, 5x, 10x):

```powershell
python ".\modding_tools\windrose_mod_cli.py" build-variants --config ".\.local\boar-loot.build.json" --multipliers "2,3,5,10" --project-dir ".\mods\boar-loot" --prepare-command-template "python .\modding_tools\windrose_mod_cli.py prepare-boar-hide-json-mod --project-dir {project_dir_quoted} --staged-root {variant_staged_dir_quoted} --multiplier {multiplier} --resource-types leather,meat,tusk"
```

Prepare cayenne pepper overrides (example 3x):

```powershell
python ".\modding_tools\windrose_mod_cli.py" prepare-cayenne-pepper-json-mod --project-dir ".\mods\cayenne-pepper-yield" --multiplier 3.0
```

Prepare sweet potato overrides (example 3x):

```powershell
python ".\modding_tools\windrose_mod_cli.py" prepare-sweet-potato-json-mod --project-dir ".\mods\sweet-potato-bounty" --multiplier 3.0
```

Prepare generic mob RSS overrides (example crocodile 3x):

```powershell
python ".\modding_tools\windrose_mod_cli.py" prepare-mob-rss-json-mod --mob-keywords "crocodile,corruptedcrocodile,whitecrocodile" --project-dir ".\mods\crocodile-bounty" --report-name "crocodile_loot_edit_report" --multiplier 3.0
```

Build + install:

```powershell
python ".\modding_tools\windrose_mod_cli.py" build-install --config ".\.local\boar-loot.build.json" --backup-first
```

Backup / restore:

```powershell
python ".\modding_tools\windrose_mod_cli.py" backup-mods --backup-dir ".\mods\boar-loot\output\mods_backups"
python ".\modding_tools\windrose_mod_cli.py" restore-mods --backup-dir ".\mods\boar-loot\output\mods_backups\mods_backup_YYYYMMDD_HHMMSS" --clear-existing
```

## Test Coverage

Run automated tests:

```powershell
powershell -ExecutionPolicy Bypass -File ".\modding_tools\scripts\run_tests.ps1"
```

The suite covers:

- `.local/.env` loading behavior
- token/env config expansion and path resolution
- template/bootstrap generation
- build/install config wiring
- boar JSON extraction/edit logic

## Notes

- This toolkit discovers and correlates Unreal object paths in containers.
- It does not perform general `.uasset` authoring workflows.
- Plugin-mounted assets are common; do not assume only `/Game/...` paths.
- Build config supports tokens in path fields (`input_dir`, `output_pak`, `mods_dir`, `backup_dir`):
  - `<REPO_ROOT>`
  - `<WORKSPACE_ROOT>`
  - `<MODDING_TOOLS_ROOT>`
  - `<WINDROSE_MODS_DIR>`
  - `<WINDROSE_PAKS_DIR>`
