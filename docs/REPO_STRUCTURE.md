# Repository Structure

## Why one repo

A single repo is recommended while mod count is still growing:

- shared tooling across all mods
- one issue tracker/wiki/release flow
- easier onboarding for collaborators

If tooling eventually needs independent release cadence, split `modding_tools/` later.

## Current practical layout

- `modding_tools/` - shared CLI/toolchain.
- `mods/boar-loot/` - active boar mod project path.
- `docs/` - high-level repository docs.

## Future expansion

When adding more mods, use:

- `mods/<mod-name>/docs`
- `mods/<mod-name>/input`
- `mods/<mod-name>/output`
- `mods/<mod-name>/scripts`
