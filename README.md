# Windrose Modding Monorepo

This repository is structured to support multiple Windrose mods over time, while sharing a single reusable tooling stack.

## Recommended Layout

- `modding_tools/` - shared CLI/scripts used by all mods.
- `mods/boar-loot/` - active boar loot mod project.
- `docs/` - repo-level guides and conventions.

## Start Here

- Project continuity and current boar workflow:
  - `mods/boar-loot/docs/AI_HANDOFF.md`
- Tooling usage:
  - `modding_tools/README.md`

## Publishing Notes

- Keep secrets out of git (`.gitignore` already excludes local config and secret files).
- Use `mods/boar-loot/docs/build_config.example.json` as the tracked template.
- Keep real local runtime config in `.local/` (example templates in `config/`).
- Keep generated artifacts (`output/`, backups) out of version control.

## CI and Release Automation

- GitHub Actions CI runs `pytest` on every push to `main` and on every pull request.
- `release-please` is configured for conventional-commit driven releases and changelog generation.
- Release tags follow `vX.Y.Z` for the monorepo; changelog is written to `CHANGELOG.md`.
