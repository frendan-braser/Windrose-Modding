# Windrose Modding

This repository is a learning-focused Windrose modding workspace. It contains a reusable CLI toolkit, repeatable mod recipes, and several example bounty mods that increase specific loot quantities while preserving vanilla drop chances.

The goal is to make Windrose `.pak` modding less mysterious: discover the relevant game loot tables, stage JSON overrides, build multiplier variants, and package them consistently.

## What Is Included

- `modding_tools/` - Python CLI and helper scripts for discovery, staging, building, packaging, and testing.
- `mods/` - individual mod projects with recipes, docs, staged overrides, and Nexus description text.
- `docs/` - repo-level structure and conventions.
- `.local/*.example` - local configuration templates. Real `.local` secrets/config files should stay untracked.

## Current Mods

| Mod | What it changes |
| --- | --- |
| `boar-loot` | Boar leather, meat, and tusk quantities |
| `cayenne-pepper-yield` | Cayenne pepper harvest quantities |
| `crab-bounty` | Crab, Thorn Fiddler, and drowned crab loot quantities |
| `crocodile-bounty` | Crocodile and corrupted crocodile loot quantities |
| `goat-bounty` | Goat meat, leather, bezoar, horn, and elite head quantities |
| `sweet-potato-bounty` | Sweet potato harvest quantities |
| `wolf-bounty` | Wolf and alpha wolf loot quantities |

Most mods are available as `2x`, `3x`, `5x`, and `10x` variants. Quantity changes are applied to `Min`/`Max` values; loot table weights and drop chances are left unchanged.

## Beginner Quickstart

Requirements:

- Python 3.10+
- Windrose installed locally
- Access to the game `R5\Content\Paks` folder
- The required AES key for reading encrypted game packages

Set up local environment values:

```powershell
Copy-Item ".\.local\.env.example" ".\.local\.env"
notepad ".\.local\.env"
```

Check tool paths:

```powershell
python ".\modding_tools\windrose_mod_cli.py" tools-info
```

Discover goat loot tables:

```powershell
python ".\modding_tools\windrose_mod_cli.py" discover-mob-loot --keyword "goat"
```

Build a mod from its recipe:

```powershell
python ".\modding_tools\windrose_mod_cli.py" build-mod --project-dir ".\mods\goat-bounty"
```

Build and install the recipe's default test variant:

```powershell
python ".\modding_tools\windrose_mod_cli.py" build-mod --project-dir ".\mods\goat-bounty" --backup-first
```

## How This Style Of Mod Works

Windrose uses Unreal Engine package files. For these loot mods, the useful data can be exported as JSON-like cooked assets and repacked into a `.pak` file that overrides the original asset path.

The basic flow is:

1. Find the relevant loot table JSON paths in the game pak.
2. Copy the matching assets into a mod's generated staging folder.
3. Scale only the intended quantity fields, usually `Min` and `Max`.
4. Keep `Weight`, drop chances, seeds, and `0/0` no-drop entries unchanged unless a mod intentionally says otherwise.
5. Pack the staged files into a `.pak`.
6. Install one variant `.pak` into the correct Windrose `Paks` folder.

Plugin-mounted assets are common in Windrose. Do not assume every asset lives under `/Game`; many useful business-rule assets map to paths under `R5/Plugins/R5BusinessRules/Content/...`.

## Make Your Own Mob Bounty Mod

Create a new recipe-backed mob bounty project:

```powershell
python ".\modding_tools\windrose_mod_cli.py" init-mob-bounty --name "Goat Bounty" --mob-keywords "goat" --resources "goat meat, leather, bezoar, horns"
```

Inspect what the game exposes:

```powershell
python ".\modding_tools\windrose_mod_cli.py" discover-mob-loot --keyword "goat" --output ".\mods\goat-bounty\docs\goat_discovery_report.json"
```

Build all configured variants:

```powershell
python ".\modding_tools\windrose_mod_cli.py" build-mod --project-dir ".\mods\goat-bounty"
```

Regenerate the Nexus description from recipe metadata:

```powershell
python ".\modding_tools\windrose_mod_cli.py" generate-nexus-description --project-dir ".\mods\goat-bounty"
```

The important file is `docs/mod_recipe.json` inside each mod. It defines the workflow type, target mob keywords/resources, variants, default install variant, packaging behavior, and Nexus description metadata.

## Install Paths

Use one `.pak` variant at a time.

- Single-player: `Windrose\R5\Content\Paks\~mods`
- Multiplayer server: `Windrose\R5\Builds\WindowsServer\R5\Content\Paks\~mods`
- Dedicated server: `Windrose Dedicated Server\R5\Content\Paks`

For dedicated servers, you can place the `.pak` directly in the listed folder without creating a `~mods` folder.

## Safety Notes

- Do not commit active AES keys, API keys, tokens, or personal local paths.
- Keep real machine-specific config in `.local/`.
- Keep generated `.pak`, `.zip`, edit reports, and backups out of version control.
- Commit recipe/config examples, docs, tests, and source code instead.

## Glossary

- `.pak`: Unreal package archive loaded by the game.
- Staged files: Files arranged in the folder structure they should have inside the pak.
- Loot table: Game data that describes possible drops.
- RSS table: Resource sub-table used by many mob loot tables.
- `Min` / `Max`: Quantity range for a drop.
- `Weight`: Vanilla selection/drop chance weighting. These mods generally leave this unchanged.
- Variant: A multiplier build such as `2x`, `3x`, `5x`, or `10x`.
- Mount point: The root path repak uses when packing files.

## More Docs

- CLI reference: `modding_tools/README.md`
- Repo layout: `docs/REPO_STRUCTURE.md`
- Mod projects: `mods/README.md`

## CI and Release Automation

- GitHub Actions CI runs `pytest` on every push to `main` and on every pull request.
- `release-please` is configured for conventional-commit driven releases and changelog generation.
- Release tags follow `vX.Y.Z` for the monorepo; changelog is written to `CHANGELOG.md`.
