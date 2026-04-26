# Mods Directory

Each folder here is either a Windrose mod project or a scaffold template for future mods.

## Current Mods

- `boar-loot/` - boar leather, meat, and tusk quantity variants.
- `cayenne-pepper-yield/` - cayenne pepper harvest quantity variants.
- `crab-bounty/` - crab, Thorn Fiddler, and drowned crab loot variants.
- `crocodile-bounty/` - crocodile and corrupted crocodile loot variants.
- `goat-bounty/` - goat loot variants.
- `sweet-potato-bounty/` - sweet potato harvest quantity variants.
- `wolf-bounty/` - wolf and alpha wolf loot variants.

## Templates

- `new-mod-template/` - scaffold source used by `init-mod`.

## Standard Layout

When adding new mods, use:

- `mods/<mod-name>/docs`
- `mods/<mod-name>/input`
- `mods/<mod-name>/output`
- `mods/<mod-name>/scripts`

The preferred recipe file is:

```text
mods/<mod-name>/docs/mod_recipe.json
```

## Create A New Mob Bounty

Use the recipe-backed command for new mob loot mods:

```powershell
python ".\modding_tools\windrose_mod_cli.py" init-mob-bounty --name "Goat Bounty" --mob-keywords "goat" --resources "goat meat, leather, bezoar, horns"
```

Then build all configured variants:

```powershell
python ".\modding_tools\windrose_mod_cli.py" build-mod --project-dir ".\mods\goat-bounty"
```

Use the lower-level scaffold only when you need a custom workflow:

```powershell
python ".\modding_tools\windrose_mod_cli.py" init-mod --name "My New Mod"
```
