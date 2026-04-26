# Boar Loot Test Plan

## Automated (CLI/tooling)

Run:

```powershell
powershell -ExecutionPolicy Bypass -File ".\modding_tools\scripts\run_tests.ps1"
```

Expected:

- All tests pass
- No errors in config token expansion/env loading
- JSON scaling behavior remains stable

## Manual In-Game Validation

1. Install latest mod:
   - `powershell -ExecutionPolicy Bypass -File ".\mods\boar-loot\scripts\build_install.ps1"`
2. Launch game and kill:
   - normal boar
   - boarF (if available)
   - boarMega (if available)
3. Confirm leather/hide drop count matches configured multiplier.
4. Confirm no crash on load and no obvious loot regressions.

## Regression Checklist

- Backup/restore scripts still function.
- `prepare-boar-hide-json-mod` still finds boar leather tables.
- `boar_hide_edit_report.json` is generated and values are scaled correctly.
