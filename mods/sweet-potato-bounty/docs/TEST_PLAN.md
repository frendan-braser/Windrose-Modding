# Sweet Potato Bounty Test Plan

## Automated

Run toolkit tests:

```powershell
powershell -ExecutionPolicy Bypass -File ".\modding_tools\scripts\run_tests.ps1"
```

## Manual In-Game

1. Build/install the mod from `scripts/build_install.ps1`.
2. Verify changed behavior in game matches the mod goal.
3. Confirm no startup/load crashes after install.
4. Remove mod and confirm baseline behavior returns.

## Regression Checklist

- Build/install script still resolves config correctly.
- Backup/restore scripts still work.
- Staged files are in mount-correct paths under `input/staged`.
