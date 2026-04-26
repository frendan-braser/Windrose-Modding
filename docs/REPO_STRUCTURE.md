# Repository Structure

## Why One Repo

A single repo keeps the learning material, shared CLI, and example mods together:

- shared tooling across all mods
- one place to compare recipes and staged override patterns
- easier onboarding for people learning Windrose modding
- one test suite for the reusable workflow

If the tooling ever needs its own release cadence, `modding_tools/` can be split later.

## Top-Level Layout

- `modding_tools/` - shared Python CLI, scripts, tests, and bundled helper executables.
- `mods/` - one folder per mod project.
- `docs/` - repo-level guides and conventions.
- `config/` - example config files that can be copied into `.local/`.
- `.local/` - local-only configuration templates. Real local files should remain untracked.

## Mod Project Layout

Each mod follows the same shape:

- `mods/<mod-name>/docs` - recipe, Nexus text, build config examples, test plan, and notes.
- `mods/<mod-name>/input/staged` - tracked source staged files when a mod needs a baseline.
- `mods/<mod-name>/output` - generated paks, zips, reports, and backups. Only `.gitkeep` should be tracked here.
- `mods/<mod-name>/scripts` - convenience PowerShell wrappers.

The main recipe file is:

```text
mods/<mod-name>/docs/mod_recipe.json
```

`build-mod` reads this recipe and handles staging, variant builds, validation, packaging, and optional installation.

## Generated Files

These should not be committed:

- `mods/*/output/generated/`
- `mods/*/output/*.pak`
- `mods/*/output/*.zip`
- `mods/*/output/variant_build_report.json`
- `mods/*/docs/*_edit_report*.json`
- `mods/*/docs/*_discovery_report.json`
- `mods/*/docs/build_config.json`
- `mods/*/docs/build_config.local.json`

Tracked files should be examples, recipes, source code, docs, tests, and intentional staged override sources.
